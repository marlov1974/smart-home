"""P0036 bounded M4 residual spot model."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import json
import math
import shutil
import sqlite3
from statistics import median
import time
from typing import Iterable


DEFAULT_FEATURE_DB = Path.home() / ".smart-home" / "data" / "spotprice_model_features.sqlite3"
DEFAULT_MODEL_DIR = Path.home() / ".smart-home" / "data" / "spotprice_ml_models" / "m4"
MODEL_DB_NAME = "m4_model.sqlite3"
PACKAGE_ID = "P0036"
MODEL_VERSION = "m4_hgb_train_only_m1_v1"
RIDGE_LAMBDA = 1.0
RANDOM_SEED = 36
TRAIN_END = date(2024, 12, 31)
VALIDATE_END = date(2025, 12, 31)

FEATURE_NAMES = (
    "hour_sin",
    "hour_cos",
    "weekday_sin",
    "weekday_cos",
    "day_of_year_sin",
    "day_of_year_cos",
    "iso_week_sin",
    "iso_week_cos",
    "month_sin",
    "month_cos",
    "is_weekend",
    "week_of_month",
    "train_year_index_clipped",
)

TARGETS = {
    "system_proxy_se1": "target_se1",
    "area_diff_proxy_se3": "target_area_diff",
}


@dataclass(frozen=True)
class TrainingRow:
    utc_hour_start: str
    local_date: str
    local_hour: int
    target_se1: float
    target_area_diff: float
    target_se3: float
    baseline_se1: float
    baseline_area_diff: float
    baseline_se3: float
    full_period_baseline_se1: float = 0.0
    full_period_baseline_area_diff: float = 0.0
    full_period_baseline_se3: float = 0.0
    train_only_raw_baseline_se1: float = 0.0
    train_only_raw_baseline_area_diff: float = 0.0
    train_only_raw_baseline_se3: float = 0.0
    m3b_delta_se1: float = 0.0
    m3b_delta_area_diff: float = 0.0
    special_day_type: str = "normal"
    special_day_name: str = "normal"
    is_special_day: int = 0


def default_model_dir() -> Path:
    return DEFAULT_MODEL_DIR


def model_db_path(model_dir: Path | str) -> Path:
    return Path(model_dir).expanduser() / MODEL_DB_NAME


def connect_model_db(model_dir: Path | str) -> sqlite3.Connection:
    db_path = model_db_path(model_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS m4_model_runs (
          run_id INTEGER PRIMARY KEY AUTOINCREMENT,
          command TEXT NOT NULL,
          started_at TEXT NOT NULL,
          completed_at TEXT,
          status TEXT NOT NULL,
          message TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS m4_feature_matrix_manifest (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS m4_feature_matrix (
          utc_hour_start TEXT PRIMARY KEY,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          split TEXT NOT NULL,
          target_se1 REAL NOT NULL,
          target_area_diff REAL NOT NULL,
          target_se3 REAL NOT NULL,
          baseline_se1 REAL NOT NULL,
          baseline_area_diff REAL NOT NULL,
          baseline_se3 REAL NOT NULL,
          features_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS m4_level_predictions (
          target TEXT NOT NULL,
          period_type TEXT NOT NULL,
          period_key TEXT NOT NULL,
          actual_level REAL NOT NULL,
          predicted_level REAL NOT NULL,
          split TEXT NOT NULL,
          PRIMARY KEY (target, period_type, period_key)
        );
        CREATE TABLE IF NOT EXISTS m4_curve_predictions (
          target TEXT NOT NULL,
          curve_type TEXT NOT NULL,
          curve_key TEXT NOT NULL,
          actual_index REAL NOT NULL,
          predicted_index REAL NOT NULL,
          split TEXT NOT NULL,
          PRIMARY KEY (target, curve_type, curve_key)
        );
        CREATE TABLE IF NOT EXISTS m4_hourly_predictions (
          utc_hour_start TEXT PRIMARY KEY,
          local_date TEXT NOT NULL,
          split TEXT NOT NULL,
          actual_se1 REAL NOT NULL,
          pred_se1 REAL NOT NULL,
          baseline_se1 REAL NOT NULL,
          actual_area_diff REAL NOT NULL,
          pred_area_diff REAL NOT NULL,
          baseline_area_diff REAL NOT NULL,
          actual_se3 REAL NOT NULL,
          pred_se3 REAL NOT NULL,
          baseline_se3 REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS m4_backtest_results (
          metric_scope TEXT NOT NULL,
          target TEXT NOT NULL,
          split TEXT NOT NULL,
          metric TEXT NOT NULL,
          value REAL NOT NULL,
          PRIMARY KEY (metric_scope, target, split, metric)
        );
        CREATE TABLE IF NOT EXISTS m4_artifact_manifest (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        """
    )
    _ensure_column(conn, "m4_feature_matrix", "full_period_baseline_se1", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "m4_feature_matrix", "full_period_baseline_area_diff", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "m4_feature_matrix", "full_period_baseline_se3", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "m4_feature_matrix", "train_only_raw_baseline_se1", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "m4_feature_matrix", "train_only_raw_baseline_area_diff", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "m4_feature_matrix", "train_only_raw_baseline_se3", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "m4_feature_matrix", "m3b_delta_se1", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "m4_feature_matrix", "m3b_delta_area_diff", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "m4_feature_matrix", "special_day_type", "TEXT NOT NULL DEFAULT 'normal'")
    _ensure_column(conn, "m4_feature_matrix", "special_day_name", "TEXT NOT NULL DEFAULT 'normal'")
    _ensure_column(conn, "m4_feature_matrix", "is_special_day", "INTEGER NOT NULL DEFAULT 0")


def load_p0033_training_series(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[TrainingRow]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if _table_exists(conn, "m3ab_normalized_prices"):
            return load_p0036_training_series(conn)
        else:
            rows = conn.execute(
                """
                SELECT
                  utc_hour_start,
                  local_date,
                  local_hour,
                  temp_normalized_price_v1_se1 - normal_price_v1_se1 AS target_se1,
                  temp_normalized_area_diff_v1 - normal_price_v1_area_diff AS target_area_diff,
                  temp_normalized_price_v1_se3 - normal_price_v1_se1 - normal_price_v1_area_diff AS target_se3,
                  normal_price_v1_se1 AS baseline_se1,
                  normal_price_v1_area_diff AS baseline_area_diff,
                  normal_price_v1_se1 + normal_price_v1_area_diff AS baseline_se3,
                  0.0 AS m3b_delta_se1,
                  0.0 AS m3b_delta_area_diff,
                  'normal' AS special_day_type,
                  'normal' AS special_day_name,
                  0 AS is_special_day
                FROM m3_temp_normalized_prices_v1
                ORDER BY utc_hour_start
                """
            ).fetchall()
    return [
        TrainingRow(
            utc_hour_start=row["utc_hour_start"],
            local_date=row["local_date"],
            local_hour=int(row["local_hour"]),
            target_se1=float(row["target_se1"]),
            target_area_diff=float(row["target_area_diff"]),
            target_se3=float(row["target_se3"]),
            baseline_se1=float(row["baseline_se1"]),
            baseline_area_diff=float(row["baseline_area_diff"]),
            baseline_se3=float(row["baseline_se3"]),
            full_period_baseline_se1=float(row["baseline_se1"]),
            full_period_baseline_area_diff=float(row["baseline_area_diff"]),
            full_period_baseline_se3=float(row["baseline_se3"]),
            train_only_raw_baseline_se1=float(row["baseline_se1"]),
            train_only_raw_baseline_area_diff=float(row["baseline_area_diff"]),
            train_only_raw_baseline_se3=float(row["baseline_se3"]),
            m3b_delta_se1=float(row["m3b_delta_se1"]),
            m3b_delta_area_diff=float(row["m3b_delta_area_diff"]),
            special_day_type=str(row["special_day_type"]),
            special_day_name=str(row["special_day_name"]),
            is_special_day=int(row["is_special_day"]),
        )
        for row in rows
    ]


def load_p0035_training_series(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[TrainingRow]:
    return load_p0033_training_series(feature_db)


def load_p0036_training_series(conn: sqlite3.Connection) -> list[TrainingRow]:
    source_rows = load_m3ab_source_rows(conn)
    m1_m3ab_se1 = compute_train_only_m1_predictions(source_rows, "m3ab_normalized_price_se1")
    m1_m3ab_area = compute_train_only_m1_predictions(source_rows, "m3ab_normalized_area_diff")
    m1_raw_se1 = compute_train_only_m1_predictions(source_rows, "actual_se1")
    m1_raw_area = compute_train_only_m1_predictions(source_rows, "actual_area_diff")
    output: list[TrainingRow] = []
    for row in source_rows:
        utc = str(row["utc_hour_start"])
        baseline_se1 = m1_m3ab_se1[utc]
        baseline_area = m1_m3ab_area[utc]
        raw_se1 = m1_raw_se1[utc]
        raw_area = m1_raw_area[utc]
        target_se1 = float(row["m3ab_normalized_price_se1"]) - baseline_se1
        target_area = float(row["m3ab_normalized_area_diff"]) - baseline_area
        output.append(
            TrainingRow(
                utc_hour_start=utc,
                local_date=str(row["local_date"]),
                local_hour=int(row["local_hour"]),
                target_se1=target_se1,
                target_area_diff=target_area,
                target_se3=target_se1 + target_area,
                baseline_se1=baseline_se1,
                baseline_area_diff=baseline_area,
                baseline_se3=baseline_se1 + baseline_area,
                full_period_baseline_se1=float(row["normal_price_v1_se1"]),
                full_period_baseline_area_diff=float(row["normal_price_v1_area_diff"]),
                full_period_baseline_se3=float(row["normal_price_v1_se1"]) + float(row["normal_price_v1_area_diff"]),
                train_only_raw_baseline_se1=raw_se1,
                train_only_raw_baseline_area_diff=raw_area,
                train_only_raw_baseline_se3=raw_se1 + raw_area,
                m3b_delta_se1=float(row["m3b_special_day_delta_se1"]),
                m3b_delta_area_diff=float(row["m3b_special_day_delta_area_diff"]),
                special_day_type=str(row["special_day_type"]),
                special_day_name=str(row["special_day_name"]),
                is_special_day=int(row["is_special_day"]),
            )
        )
    return output


def load_m3ab_source_rows(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = [
        dict(row)
        for row in conn.execute(
            """
            SELECT
              utc_hour_start,
              local_date,
              local_hour,
              actual_se1,
              actual_area_diff,
              actual_se3,
              normal_price_v1_se1,
              normal_price_v1_area_diff,
              m3b_special_day_delta_se1,
              m3b_special_day_delta_area_diff,
              m3ab_normalized_price_se1,
              m3ab_normalized_area_diff,
              m3ab_normalized_se3,
              special_day_type,
              special_day_name,
              is_special_day
            FROM m3ab_normalized_prices
            ORDER BY utc_hour_start
            """
        )
    ]
    for row in rows:
        d = date.fromisoformat(str(row["local_date"]))
        row["iso_week"] = d.isocalendar().week
        row["weekday"] = d.weekday()
        row["split"] = split_for_date(str(row["local_date"]))
    return rows


def compute_train_only_m1_predictions(rows: list[dict[str, object]], value_field: str) -> dict[str, float]:
    train_rows = [row for row in rows if row["split"] == "train"]
    if not train_rows:
        raise ValueError("cannot compute train-only M1 without training rows")
    surface = build_train_only_m1_surface(train_rows, value_field)
    return {
        str(row["utc_hour_start"]): predict_train_only_m1(surface, row)
        for row in rows
    }


def build_train_only_m1_surface(rows: list[dict[str, object]], value_field: str) -> dict[str, object]:
    by_bucket: dict[tuple[int, int, int], list[float]] = defaultdict(list)
    by_hour: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        key = (int(row["iso_week"]), int(row["weekday"]), int(row["local_hour"]))
        value = float(row[value_field])
        by_bucket[key].append(value)
        by_hour[int(row["local_hour"])].append(value)
    bucket_medians: dict[tuple[int, int, int], float] = {}
    for iso_week in range(1, 54):
        for weekday in range(7):
            for hour in range(24):
                values: list[float] = []
                for (candidate_week, candidate_weekday, candidate_hour), bucket_values in by_bucket.items():
                    if candidate_weekday == weekday and candidate_hour == hour and _week_distance(candidate_week, iso_week) <= 2:
                        values.extend(bucket_values)
                if not values:
                    values = by_hour.get(hour, [])
                if values:
                    bucket_medians[(iso_week, weekday, hour)] = float(median(values))
    hour_medians = {hour: float(median(values)) for hour, values in by_hour.items() if values}
    global_median = float(median([float(row[value_field]) for row in rows]))
    return {"bucket_medians": bucket_medians, "hour_medians": hour_medians, "global_median": global_median}


def predict_train_only_m1(surface: dict[str, object], row: dict[str, object]) -> float:
    key = (int(row["iso_week"]), int(row["weekday"]), int(row["local_hour"]))
    bucket_medians = surface["bucket_medians"]
    if key in bucket_medians:
        return float(bucket_medians[key])
    hour_medians = surface["hour_medians"]
    return float(hour_medians.get(int(row["local_hour"]), surface["global_median"]))


def build_calendar_features(rows: list[TrainingRow]) -> dict[str, list[float]]:
    if not rows:
        return {}
    train_years = [date.fromisoformat(row.local_date).year for row in rows if split_for_date(row.local_date) == "train"]
    min_train_year = min(train_years) if train_years else date.fromisoformat(rows[0].local_date).year
    max_train_year = max(train_years) if train_years else min_train_year
    year_span = max(1, max_train_year - min_train_year)
    output: dict[str, list[float]] = {}
    for row in rows:
        d = date.fromisoformat(row.local_date)
        weekday = d.weekday()
        iso_week = d.isocalendar().week
        month = d.month
        doy = d.timetuple().tm_yday
        clipped_year = min(max(d.year, min_train_year), max_train_year)
        values = {
            "hour_sin": math.sin(2 * math.pi * row.local_hour / 24),
            "hour_cos": math.cos(2 * math.pi * row.local_hour / 24),
            "weekday_sin": math.sin(2 * math.pi * weekday / 7),
            "weekday_cos": math.cos(2 * math.pi * weekday / 7),
            "day_of_year_sin": math.sin(2 * math.pi * doy / 366),
            "day_of_year_cos": math.cos(2 * math.pi * doy / 366),
            "iso_week_sin": math.sin(2 * math.pi * iso_week / 53),
            "iso_week_cos": math.cos(2 * math.pi * iso_week / 53),
            "month_sin": math.sin(2 * math.pi * month / 12),
            "month_cos": math.cos(2 * math.pi * month / 12),
            "is_weekend": 1.0 if weekday >= 5 else 0.0,
            "week_of_month": float((d.day - 1) // 7 + 1) / 5.0,
            "train_year_index_clipped": (clipped_year - min_train_year) / year_span,
        }
        output[row.utc_hour_start] = [values[name] for name in FEATURE_NAMES]
    return output


def build_feature_store(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    model_dir: Path | str = DEFAULT_MODEL_DIR,
) -> dict[str, object]:
    rows = load_p0033_training_series(feature_db)
    features = build_calendar_features(rows)
    with connect_model_db(model_dir) as conn:
        initialize_schema(conn)
        _clear_tables(conn)
        run_id = _start_run(conn, "build-features-m4")
        payload = []
        for row in rows:
            payload.append(
                (
                    row.utc_hour_start,
                    row.local_date,
                    row.local_hour,
                    split_for_date(row.local_date),
                    row.target_se1,
                    row.target_area_diff,
                    row.target_se3,
                    row.baseline_se1,
                    row.baseline_area_diff,
                    row.baseline_se3,
                    row.full_period_baseline_se1,
                    row.full_period_baseline_area_diff,
                    row.full_period_baseline_se3,
                    row.train_only_raw_baseline_se1,
                    row.train_only_raw_baseline_area_diff,
                    row.train_only_raw_baseline_se3,
                    row.m3b_delta_se1,
                    row.m3b_delta_area_diff,
                    row.special_day_type,
                    row.special_day_name,
                    row.is_special_day,
                    json.dumps(features[row.utc_hour_start], separators=(",", ":")),
                )
            )
        conn.executemany(
            """
            INSERT INTO m4_feature_matrix
             (utc_hour_start, local_date, local_hour, split, target_se1, target_area_diff, target_se3,
             baseline_se1, baseline_area_diff, baseline_se3,
             full_period_baseline_se1, full_period_baseline_area_diff, full_period_baseline_se3,
             train_only_raw_baseline_se1, train_only_raw_baseline_area_diff, train_only_raw_baseline_se3,
             m3b_delta_se1, m3b_delta_area_diff, special_day_type, special_day_name, is_special_day,
             features_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        manifest = {
            "package_id": PACKAGE_ID,
            "model_version": MODEL_VERSION,
            "feature_names": json.dumps(FEATURE_NAMES),
            "feature_count": str(len(FEATURE_NAMES)),
            "row_count": str(len(rows)),
            "start_date": rows[0].local_date if rows else "",
            "end_date": rows[-1].local_date if rows else "",
            "weather_features": "excluded",
            "m1_baseline_policy": "train_only_m1_m3ab_normalized_primary",
            "forbidden_model_path": "PolynomialFeatures(degree=2)+Ridge primary path disabled",
            "split_policy": "train<=2024-12-31, validate=2025, holdout>=2026",
        }
        conn.executemany(
            "INSERT OR REPLACE INTO m4_feature_matrix_manifest(key, value) VALUES (?, ?)",
            sorted(manifest.items()),
        )
        _finish_run(conn, run_id, "ok", f"feature rows={len(rows)}")
        return {"ok": True, "row_count": len(rows), "feature_count": len(FEATURE_NAMES), "model_db": str(model_db_path(model_dir))}


def train_m4(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    model_dir: Path | str = DEFAULT_MODEL_DIR,
    ridge_lambda: float = RIDGE_LAMBDA,
) -> dict[str, object]:
    build_feature_store(feature_db=feature_db, model_dir=model_dir)
    rows = _load_feature_rows(model_dir)
    train_rows = [row for row in rows if row["split"] == "train"]
    validate_rows = [row for row in rows if row["split"] == "validate"]
    if not train_rows:
        raise ValueError("no training rows")
    models: dict[str, dict[str, object]] = {}
    for target, column in TARGETS.items():
        models[target] = train_m4_target_model(
            target=target,
            target_column=column,
            train_x=[row["features"] for row in train_rows],
            train_y=[float(row[column]) for row in train_rows],
            validate_x=[row["features"] for row in validate_rows],
            validate_y=[float(row[column]) for row in validate_rows],
            ridge_lambda=ridge_lambda,
        )
    _write_model_artifacts(model_dir, models)
    predictions = predict_rows(rows, models)
    quality_gate = evaluate_p0036_quality_gate(predictions)
    with connect_model_db(model_dir) as conn:
        initialize_schema(conn)
        run_id = _start_run(conn, "train-m4")
        _replace_predictions(conn, predictions)
        _replace_level_and_curve(conn, predictions)
        _replace_metrics(conn, predictions)
        _write_artifact_manifest(conn, model_dir, models)
        _finish_run(conn, run_id, "ok", f"trained quality_gate={quality_gate['status']}")
    staged = stage_model_artifacts(Path(model_dir).expanduser())
    if quality_gate["promote_active"]:
        promotion = promote_active_model(Path(model_dir).expanduser(), staging_dir=Path(staged["staging_dir"]))
    else:
        promotion = {
            "ok": True,
            "promoted": False,
            "reason": quality_gate["reason"],
            "active_dir": str(Path(model_dir).expanduser() / "active"),
            "staging_dir": staged["staging_dir"],
        }
    evidence = write_p0036_evidence(
        model_dir=Path(model_dir).expanduser(),
        models=models,
        predictions=predictions,
        quality_gate=quality_gate,
        promotion=promotion,
    )
    return {
        "ok": True,
        "model_dir": str(Path(model_dir).expanduser()),
        "targets": sorted(models),
        "quality_gate": quality_gate,
        "promotion": promotion,
        "evidence": evidence,
    }


def backtest_m4(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    model_dir: Path | str = DEFAULT_MODEL_DIR,
) -> dict[str, object]:
    train_m4(feature_db=feature_db, model_dir=model_dir)
    with connect_model_db(model_dir) as conn:
        metrics = [
            dict(row)
            for row in conn.execute(
                "SELECT metric_scope, target, split, metric, value FROM m4_backtest_results ORDER BY metric_scope, target, split, metric"
            )
        ]
    return {"ok": True, "metrics": metrics, "model_db": str(model_db_path(model_dir))}


def validate_m4_outputs(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    model_dir: Path | str = DEFAULT_MODEL_DIR,
) -> dict[str, object]:
    db_path = model_db_path(model_dir)
    if not db_path.exists():
        return {"ok": False, "error": "model db missing", "model_db": str(db_path)}
    with connect_model_db(model_dir) as conn:
        initialize_schema(conn)
        counts = {
            table: int(conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"])
            for table in (
                "m4_feature_matrix",
                "m4_level_predictions",
                "m4_curve_predictions",
                "m4_hourly_predictions",
                "m4_backtest_results",
                "m4_artifact_manifest",
            )
        }
        feature_names = json.loads(
            conn.execute("SELECT value FROM m4_feature_matrix_manifest WHERE key='feature_names'").fetchone()["value"]
        )
        forbidden = [
            name
            for name in feature_names
            if any(token in name for token in ("temp", "weather", "wind", "solar", "cloud"))
            or name == "days_since_start_scaled"
            or "^2" in name
        ]
        splits = dict(conn.execute("SELECT split, COUNT(*) FROM m4_feature_matrix GROUP BY split").fetchall())
    artifacts = [Path(model_dir).expanduser() / f"{target}_model.json" for target in TARGETS]
    joblib_artifacts: list[Path] = []
    for metadata_path in artifacts:
        if not metadata_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if str(metadata.get("algorithm", "")).startswith("sklearn_"):
            joblib_artifacts.append(metadata_path.with_suffix(".joblib"))
    evidence_paths = [
        Path("requirements/package-runs/P0036/holdout-results.md"),
        Path("requirements/package-runs/P0036/baseline-comparison.md"),
        Path("requirements/package-runs/P0036/candidate-timings.md"),
        Path("requirements/package-runs/P0036/model-selection.md"),
        Path("requirements/package-runs/P0036/model-promotion-summary.md"),
    ]
    evidence_files = {str(path): path.exists() for path in evidence_paths}
    ok = (
        all(count > 0 for count in counts.values())
        and not forbidden
        and all(path.exists() for path in artifacts)
        and all(path.exists() for path in joblib_artifacts)
        and all(evidence_files.values())
    )
    return {
        "ok": ok,
        "model_db": str(db_path),
        "table_counts": counts,
        "splits": splits,
        "feature_count": len(feature_names),
        "forbidden_features": forbidden,
        "artifacts": [str(path) for path in artifacts + joblib_artifacts],
        "evidence_files": evidence_files,
    }


def fit_ridge(x: list[list[float]], y: list[float], ridge_lambda: float) -> list[float]:
    n_features = len(x[0])
    xtx = [[0.0 for _ in range(n_features)] for _ in range(n_features)]
    xty = [0.0 for _ in range(n_features)]
    for row, target in zip(x, y):
        for i in range(n_features):
            xty[i] += row[i] * target
            for j in range(n_features):
                xtx[i][j] += row[i] * row[j]
    for i in range(1, n_features):
        xtx[i][i] += ridge_lambda
    return solve_linear_system(xtx, xty)


def train_m4_target_model(
    *,
    target: str,
    target_column: str,
    train_x: list[list[float]],
    train_y: list[float],
    validate_x: list[list[float]] | None = None,
    validate_y: list[float] | None = None,
    ridge_lambda: float = RIDGE_LAMBDA,
) -> dict[str, object]:
    del ridge_lambda
    validate_x = validate_x or train_x
    validate_y = validate_y or train_y
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
    except Exception as exc:
        raise RuntimeError(f"P0036 requires scikit-learn HistGradientBoostingRegressor: {type(exc).__name__}: {exc}") from exc

    candidates = _hgb_candidate_grid()
    timings: list[dict[str, object]] = []
    best: dict[str, object] | None = None
    for index, params in enumerate(candidates, start=1):
        candidate_id = f"hgb_{target}_{index:03d}"
        started = _now()
        start = time.monotonic()
        try:
            estimator = HistGradientBoostingRegressor(**params)
            estimator.fit(train_x, train_y)
            elapsed = time.monotonic() - start
            predicted = [float(value) for value in estimator.predict(validate_x)]
            validate_mae = mae(validate_y, predicted)
            validate_rmse = rmse(validate_y, predicted)
            timing = {
                "candidate_id": candidate_id,
                "target": target,
                "parameters": params,
                "train_rows": len(train_x),
                "feature_count": len(train_x[0]) if train_x else 0,
                "start_time": started,
                "end_time": _now(),
                "elapsed_seconds": elapsed,
                "status": "ok",
                "reason_selected_or_rejected": "candidate",
                "validate_mae": validate_mae,
                "validate_rmse": validate_rmse,
            }
            if best is None or validate_mae < float(best["validate_mae"]):
                best = {"estimator": estimator, "params": params, "timing": timing, "validate_mae": validate_mae}
        except Exception as exc:
            elapsed = time.monotonic() - start
            timing = {
                "candidate_id": candidate_id,
                "target": target,
                "parameters": params,
                "train_rows": len(train_x),
                "feature_count": len(train_x[0]) if train_x else 0,
                "start_time": started,
                "end_time": _now(),
                "elapsed_seconds": elapsed,
                "status": "failed",
                "reason_selected_or_rejected": f"{type(exc).__name__}: {exc}",
                "validate_mae": None,
                "validate_rmse": None,
            }
        timings.append(timing)

    if best is None:
        raise RuntimeError(f"no HGB candidate succeeded for {target}")
    for timing in timings:
        if timing["candidate_id"] == best["timing"]["candidate_id"]:
            timing["reason_selected_or_rejected"] = "selected: lowest validate residual MAE"
        elif timing["status"] == "ok":
            timing["reason_selected_or_rejected"] = "rejected: higher validate residual MAE"
    return {
        "target": target,
        "target_column": target_column,
        "feature_names": list(FEATURE_NAMES),
        "algorithm": "sklearn_hist_gradient_boosting_regressor",
        "model_version": MODEL_VERSION,
        "random_seed": RANDOM_SEED,
        "parameters": best["params"],
        "timing": best["timing"],
        "candidate_timings": timings,
        "estimator": best["estimator"],
    }


def _hgb_candidate_grid() -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for max_iter in (50, 100):
        for learning_rate in (0.03, 0.05):
            for max_leaf_nodes in (7, 15):
                for l2_regularization in (0.0, 0.1):
                    output.append(
                        {
                            "max_iter": max_iter,
                            "learning_rate": learning_rate,
                            "max_leaf_nodes": max_leaf_nodes,
                            "min_samples_leaf": 100,
                            "l2_regularization": l2_regularization,
                            "early_stopping": True,
                            "random_state": RANDOM_SEED,
                        }
                    )
    return output


def train_ridge_diagnostic_model(
    *,
    target: str,
    target_column: str,
    x: list[list[float]],
    y: list[float],
    ridge_lambda: float = RIDGE_LAMBDA,
) -> dict[str, object]:
    start = time.monotonic()
    coefficients = fit_ridge(x, y, ridge_lambda)
    elapsed = time.monotonic() - start
    return {
        "target": target,
        "target_column": target_column,
        "feature_names": list(FEATURE_NAMES),
        "coefficients": coefficients,
        "ridge_lambda": ridge_lambda,
        "algorithm": "pure_python_ridge_diagnostic_not_primary",
        "model_version": MODEL_VERSION,
        "timing": {
            "candidate": "pure_python_ridge_diagnostic_not_primary",
            "elapsed_seconds": elapsed,
            "row_count": len(x),
            "feature_count": len(x[0]) if x else 0,
            "reason_selected_or_rejected": "diagnostic only; not P0036 primary",
        },
    }


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    mat = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(mat[row][col]))
        if abs(mat[pivot][col]) < 1e-12:
            mat[pivot][col] = 1e-12
        mat[col], mat[pivot] = mat[pivot], mat[col]
        scale = mat[col][col]
        for j in range(col, n + 1):
            mat[col][j] /= scale
        for row in range(n):
            if row == col:
                continue
            factor = mat[row][col]
            for j in range(col, n + 1):
                mat[row][j] -= factor * mat[col][j]
    return [mat[i][n] for i in range(n)]


def predict_rows(rows: list[dict[str, object]], models: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        pred_residual_se1 = predict_m4_target_model(models["system_proxy_se1"], row["features"])
        pred_residual_area = predict_m4_target_model(models["area_diff_proxy_se3"], row["features"])
        actual_se1 = float(row["baseline_se1"]) + float(row["target_se1"])
        actual_area = float(row["baseline_area_diff"]) + float(row["target_area_diff"])
        pred_se1 = float(row["baseline_se1"]) + pred_residual_se1
        pred_area = float(row["baseline_area_diff"]) + pred_residual_area
        output.append(
            {
                **row,
                "pred_residual_se1": pred_residual_se1,
                "pred_residual_area_diff": pred_residual_area,
                "actual_se1": actual_se1,
                "actual_area_diff": actual_area,
                "actual_se3": actual_se1 + actual_area,
                "pred_se1": pred_se1,
                "pred_area_diff": pred_area,
                "pred_se3": pred_se1 + pred_area,
                "eval_actual_se1": actual_se1 + float(row.get("m3b_delta_se1", 0.0)),
                "eval_actual_area_diff": actual_area + float(row.get("m3b_delta_area_diff", 0.0)),
                "eval_pred_se1": pred_se1 + float(row.get("m3b_delta_se1", 0.0)),
                "eval_pred_area_diff": pred_area + float(row.get("m3b_delta_area_diff", 0.0)),
            }
        )
        output[-1]["eval_actual_se3"] = output[-1]["eval_actual_se1"] + output[-1]["eval_actual_area_diff"]
        output[-1]["eval_pred_se3"] = output[-1]["eval_pred_se1"] + output[-1]["eval_pred_area_diff"]
    return output


def predict_m4_target_model(model: dict[str, object], features: list[float]) -> float:
    estimator = model.get("estimator")
    if estimator is not None:
        return float(estimator.predict([features])[0])
    return dot(features, model["coefficients"])


def build_level_targets(rows: list[TrainingRow]) -> dict[tuple[str, str, str], float]:
    values: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        d = date.fromisoformat(row.local_date)
        keys = {
            "week": f"{d.isocalendar().year}-W{d.isocalendar().week:02d}",
            "month": f"{d.year}-{d.month:02d}",
            "year": str(d.year),
        }
        for target, field in (("system_proxy_se1", "target_se1"), ("area_diff_proxy_se3", "target_area_diff")):
            value = getattr(row, field)
            for period_type, period_key in keys.items():
                values[(target, period_type, period_key)].append(value)
    return {key: sum(items) / len(items) for key, items in values.items()}


def build_curve_targets(rows: list[TrainingRow], level_targets: dict[tuple[str, str, str], float]) -> list[dict[str, object]]:
    curves: list[dict[str, object]] = []
    for row in rows:
        d = date.fromisoformat(row.local_date)
        week_key = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
        curve_key = f"{week_key}-{row.local_hour:02d}-{d.weekday()}"
        for target, field in (("system_proxy_se1", "target_se1"), ("area_diff_proxy_se3", "target_area_diff")):
            level = level_targets[(target, "week", week_key)]
            value = getattr(row, field)
            curves.append(
                {
                    "target": target,
                    "curve_type": "intra_week_hour_index",
                    "curve_key": curve_key,
                    "actual_index": _safe_ratio(value, level),
                    "predicted_index": 1.0,
                    "split": split_for_date(row.local_date),
                }
            )
    return curves


def build_week_of_year_indexes(rows: list[TrainingRow]) -> list[dict[str, object]]:
    levels = build_level_targets(rows)
    output: list[dict[str, object]] = []
    for (target, period_type, period_key), value in levels.items():
        if period_type != "week":
            continue
        year = period_key.split("-W")[0]
        month = _week_month(rows, period_key)
        output.append(
            {
                "target": target,
                "curve_type": "week_index_vs_year",
                "curve_key": period_key,
                "actual_index": _safe_ratio(value, levels[(target, "year", year)]),
                "predicted_index": 1.0,
                "split": split_for_period(period_key),
            }
        )
        if month:
            output.append(
                {
                    "target": target,
                    "curve_type": "week_index_within_month",
                    "curve_key": period_key,
                    "actual_index": _safe_ratio(value, levels[(target, "month", month)]),
                    "predicted_index": 1.0,
                    "split": split_for_period(period_key),
                }
            )
    return output


def build_clipped_month_curves(rows: list[TrainingRow], level_targets: dict[tuple[str, str, str], float]) -> list[dict[str, object]]:
    by_month: dict[str, list[TrainingRow]] = defaultdict(list)
    for row in rows:
        d = date.fromisoformat(row.local_date)
        by_month[f"{d.year}-{d.month:02d}"].append(row)
    output: list[dict[str, object]] = []
    for month_key, month_rows in by_month.items():
        for target, field in (("system_proxy_se1", "target_se1"), ("area_diff_proxy_se3", "target_area_diff")):
            level = level_targets[(target, "month", month_key)]
            raw = [(row, _safe_ratio(getattr(row, field), level)) for row in month_rows]
            mean = sum(value for _row, value in raw) / len(raw)
            for row, value in raw:
                d = date.fromisoformat(row.local_date)
                curve_key = f"{month_key}-W{d.isocalendar().week:02d}-{d.weekday()}-{row.local_hour:02d}"
                output.append(
                    {
                        "target": target,
                        "curve_type": "clipped_month_curve",
                        "curve_key": curve_key,
                        "actual_index": _safe_ratio(value, mean),
                        "predicted_index": 1.0,
                        "split": split_for_date(row.local_date),
                    }
                )
    return output


def recompose_se3_predictions(predictions: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return [{**row, "pred_se3": float(row["pred_se1"]) + float(row["pred_area_diff"])} for row in predictions]


def run_walk_forward_backtest(model_dir: Path | str = DEFAULT_MODEL_DIR) -> dict[str, object]:
    return backtest_m4(model_dir=model_dir)


def compare_against_baselines(predictions: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    return {
        "system_proxy_se1": _metric_pair(predictions, "actual_se1", "pred_se1", "baseline_se1"),
        "area_diff_proxy_se3": _metric_pair(predictions, "actual_area_diff", "pred_area_diff", "baseline_area_diff"),
        "recomposed_se3": _metric_pair(predictions, "actual_se3", "pred_se3", "baseline_se3"),
    }


def evaluate_p0036_quality_gate(predictions: list[dict[str, object]]) -> dict[str, object]:
    holdout = [row for row in predictions if row["split"] == "holdout"]
    if not holdout:
        return {"status": "STOP", "promote_active": False, "reason": "no holdout rows"}
    metrics = _baseline_comparison_metrics(holdout)
    area_predicted = [float(row["pred_residual_area_diff"]) for row in holdout]
    area_actual = [float(row["target_area_diff"]) for row in holdout]
    area_pred_mean = sum(area_predicted) / len(area_predicted)
    area_actual_mean = sum(area_actual) / len(area_actual)
    area_blowup_removed = abs(area_pred_mean - area_actual_mean) < 0.75 and area_pred_mean < 1.0
    se3_hgb = metrics["P0036_HGB_residual"]["recomposed_se3"]["mae"]
    se3_train_m1 = metrics["train_only_M1_m3ab_normalized"]["recomposed_se3"]["mae"]
    catastrophic = any(
        metrics["P0036_HGB_residual"][target]["mae"] > 2.0 * metrics["train_only_M1_m3ab_normalized"][target]["mae"] + 0.05
        for target in ("system_proxy_se1", "area_diff_proxy_se3", "recomposed_se3")
    )
    if se3_hgb < se3_train_m1 and not catastrophic and area_blowup_removed:
        status = "PASS"
        promote = True
        reason = "P0036 HGB beats train-only M1 on recomposed SE3 holdout without area_diff blow-up"
    elif area_blowup_removed:
        status = "WARN"
        promote = False
        reason = "P0036 HGB is bounded and removes area_diff blow-up but does not clear all PASS gates"
    else:
        status = "STOP"
        promote = False
        reason = "area_diff residual blow-up remains or metrics are unsafe"
    return {
        "status": status,
        "promote_active": promote,
        "reason": reason,
        "holdout_metrics": metrics,
        "area_diff_predicted_residual_mean": area_pred_mean,
        "area_diff_actual_residual_mean": area_actual_mean,
        "area_diff_blowup_removed": area_blowup_removed,
    }


def write_p0036_evidence(
    *,
    model_dir: Path,
    models: dict[str, dict[str, object]],
    predictions: list[dict[str, object]],
    quality_gate: dict[str, object],
    promotion: dict[str, object],
) -> dict[str, str]:
    evidence_dir = Path("requirements/package-runs/P0036")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    holdout = [row for row in predictions if row["split"] == "holdout"]
    validate = [row for row in predictions if row["split"] == "validate"]
    train = [row for row in predictions if row["split"] == "train"]
    comparison = _baseline_comparison_metrics(holdout)
    special = [row for row in holdout if int(row.get("is_special_day", 0))]
    non_special = [row for row in holdout if not int(row.get("is_special_day", 0))]
    residual_summary = _residual_prediction_summary(predictions)
    candidate_rows = [timing for model in models.values() for timing in model.get("candidate_timings", [])]

    holdout_path = evidence_dir / "holdout-results.md"
    holdout_path.write_text(
        "\n".join(
            [
                "# P0036 holdout results",
                "",
                "## Identity",
                "",
                "```text",
                f"package_id = {PACKAGE_ID}",
                f"model_version = {MODEL_VERSION}",
                "model_class = sklearn HistGradientBoostingRegressor",
                f"status = {quality_gate['status']}",
                f"reason = {quality_gate['reason']}",
                f"feature_db = {DEFAULT_FEATURE_DB}",
                f"model_db = {model_db_path(model_dir)}",
                "split = train<=2024-12-31, validate=2025, holdout>=2026",
                f"train_rows = {len(train)}",
                f"validate_rows = {len(validate)}",
                f"holdout_rows = {len(holdout)}",
                f"random_seed = {RANDOM_SEED}",
                "leakage_control = train_only_M1_m3ab_normalized fitted on train rows only",
                "```",
                "",
                "## Holdout hourly metrics",
                "",
                _format_metric_table(comparison),
                "",
                "## Special-day subset",
                "",
                _format_subset_metrics("special", special),
                "",
                "## Non-special-day subset",
                "",
                _format_subset_metrics("non_special", non_special),
                "",
                "## Residual prediction distribution",
                "",
                _format_residual_summary(residual_summary),
                "",
                "## Largest holdout errors",
                "",
                "### SE1",
                "",
                _format_largest_errors(holdout, "system_proxy_se1"),
                "",
                "### Area Diff",
                "",
                _format_largest_errors(holdout, "area_diff_proxy_se3"),
                "",
                "## Not applicable",
                "",
                "M5/M6/M7 forecast-time temperature/API metrics are out of scope for P0036.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    baseline_path = evidence_dir / "baseline-comparison.md"
    baseline_path.write_text(
        "\n".join(
            [
                "# P0036 baseline comparison",
                "",
                "Primary fair baseline is `train_only_M1_m3ab_normalized`.",
                "",
                _format_metric_table(comparison),
                "",
                "Historical reference from committed evidence:",
                "",
                "| reference | system_proxy_se1 MAE | area_diff_proxy_se3 MAE | recomposed_se3 MAE | note |",
                "|---|---:|---:|---:|---|",
                "| P0034 M4 | see `requirements/package-runs/P0034/holdout-results.md` | see evidence | see evidence | pre-P0035 model |",
                "| P0035 M4 | 0.6079521874402215 | 1.8269617292981122 | 1.6662037682642874 | polynomial Ridge residual blow-up |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    timing_path = evidence_dir / "candidate-timings.md"
    timing_path.write_text(_format_candidate_timings(candidate_rows), encoding="utf-8")

    selection_path = evidence_dir / "model-selection.md"
    selection_path.write_text(
        "\n".join(
            [
                "# P0036 model selection",
                "",
                "| target | selected_candidate | algorithm | parameters | validate_mae | elapsed_seconds |",
                "|---|---|---|---|---:|---:|",
                *[
                    "| {target} | {candidate} | {algorithm} | `{params}` | {mae} | {elapsed} |".format(
                        target=target,
                        candidate=str(model["timing"]["candidate_id"]),
                        algorithm=str(model["algorithm"]),
                        params=json.dumps(model["parameters"], sort_keys=True),
                        mae=_fmt(model["timing"].get("validate_mae")),
                        elapsed=_fmt(model["timing"].get("elapsed_seconds")),
                    )
                    for target, model in sorted(models.items())
                ],
                "",
                "PolynomialFeatures/Ridge is not used as the P0036 primary M4 model.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    promotion_path = evidence_dir / "model-promotion-summary.md"
    promotion_path.write_text(
        "\n".join(
            [
                "# P0036 model promotion summary",
                "",
                "```text",
                f"quality_gate = {quality_gate['status']}",
                f"reason = {quality_gate['reason']}",
                f"promoted = {promotion.get('promoted', promotion.get('ok') and quality_gate.get('promote_active'))}",
                f"active_dir = {promotion.get('active_dir', '')}",
                f"staging_dir = {promotion.get('staging_dir', '')}",
                "```",
                "",
                "Active artifacts are promoted only on PASS. WARN/STOP leaves the existing active model directory untouched.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "holdout": str(holdout_path),
        "baseline": str(baseline_path),
        "timings": str(timing_path),
        "selection": str(selection_path),
        "promotion": str(promotion_path),
    }


def write_model_artifact_manifest(model_dir: Path | str, models: dict[str, dict[str, object]]) -> dict[str, object]:
    _write_model_artifacts(model_dir, models)
    manifest = _artifact_manifest(model_dir, models)
    path = Path(model_dir).expanduser() / "m4_artifact_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def stage_model_artifacts(model_dir: Path | str) -> dict[str, object]:
    base = Path(model_dir).expanduser()
    staging = base / "staging" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    staging.mkdir(parents=True, exist_ok=True)
    files = [
        base / "system_proxy_se1_model.json",
        base / "system_proxy_se1_model.joblib",
        base / "area_diff_proxy_se3_model.json",
        base / "area_diff_proxy_se3_model.joblib",
        base / "m4_artifact_manifest.json",
        base / MODEL_DB_NAME,
    ]
    copied: list[str] = []
    for path in files:
        if path.exists():
            shutil.copy2(path, staging / path.name)
            copied.append(path.name)
    if not copied:
        return {"ok": False, "reason": "no artifacts to stage", "staging_dir": str(staging)}
    return {"ok": True, "staging_dir": str(staging), "files": copied}


def promote_active_model(model_dir: Path | str, staging_dir: Path | str | None = None) -> dict[str, object]:
    base = Path(model_dir).expanduser()
    active = base / "active"
    if staging_dir is None:
        staged = stage_model_artifacts(base)
        if not staged["ok"]:
            return {"ok": False, "reason": staged["reason"], "active_dir": str(active), "staging_dir": staged["staging_dir"]}
        staging = Path(str(staged["staging_dir"]))
        copied = list(staged["files"])
    else:
        staging = Path(staging_dir).expanduser()
        copied = [path.name for path in staging.iterdir() if path.is_file()]
    if not copied:
        return {"ok": False, "reason": "no artifacts to promote", "active_dir": str(active), "staging_dir": str(staging)}
    tmp_active = base / "active.tmp"
    if tmp_active.exists():
        shutil.rmtree(tmp_active)
    tmp_active.mkdir(parents=True)
    for name in copied:
        shutil.copy2(staging / name, tmp_active / name)
    if active.exists():
        shutil.rmtree(active)
    tmp_active.rename(active)
    manifest = {
        "package_id": PACKAGE_ID,
        "model_version": MODEL_VERSION,
        "staging_dir": str(staging),
        "active_dir": str(active),
        "files": copied,
        "promoted_at": _now(),
    }
    (active / "m4_promotion_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"ok": True, **manifest}


def split_for_date(local_date: str) -> str:
    d = date.fromisoformat(local_date)
    if d <= TRAIN_END:
        return "train"
    if d <= VALIDATE_END:
        return "validate"
    return "holdout"


def split_for_period(period_key: str) -> str:
    year = int(period_key[:4])
    if year <= 2024:
        return "train"
    if year == 2025:
        return "validate"
    return "holdout"


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def mae(actual: list[float], predicted: list[float]) -> float:
    return sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)


def rmse(actual: list[float], predicted: list[float]) -> float:
    return math.sqrt(sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual))


def _load_feature_rows(model_dir: Path | str) -> list[dict[str, object]]:
    with connect_model_db(model_dir) as conn:
        initialize_schema(conn)
        rows = conn.execute("SELECT * FROM m4_feature_matrix ORDER BY utc_hour_start").fetchall()
    return [
        {
            **dict(row),
            "features": json.loads(row["features_json"]),
        }
        for row in rows
    ]


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone() is not None


def _replace_predictions(conn: sqlite3.Connection, predictions: list[dict[str, object]]) -> None:
    conn.execute("DELETE FROM m4_hourly_predictions")
    conn.executemany(
        """
        INSERT INTO m4_hourly_predictions
        (utc_hour_start, local_date, split, actual_se1, pred_se1, baseline_se1,
         actual_area_diff, pred_area_diff, baseline_area_diff, actual_se3, pred_se3, baseline_se3)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["utc_hour_start"],
                row["local_date"],
                row["split"],
                row["actual_se1"],
                row["pred_se1"],
                row["baseline_se1"],
                row["actual_area_diff"],
                row["pred_area_diff"],
                row["baseline_area_diff"],
                row["actual_se3"],
                row["pred_se3"],
                row["baseline_se3"],
            )
            for row in predictions
        ],
    )


def _replace_level_and_curve(conn: sqlite3.Connection, predictions: list[dict[str, object]]) -> None:
    conn.execute("DELETE FROM m4_level_predictions")
    conn.execute("DELETE FROM m4_curve_predictions")
    level_rows: list[tuple[object, ...]] = []
    curve_rows: list[tuple[object, ...]] = []
    for target, actual_col, pred_col in (
        ("system_proxy_se1", "actual_se1", "pred_se1"),
        ("area_diff_proxy_se3", "actual_area_diff", "pred_area_diff"),
    ):
        for period_type in ("week", "month"):
            groups: dict[str, list[dict[str, object]]] = defaultdict(list)
            for row in predictions:
                d = date.fromisoformat(str(row["local_date"]))
                key = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}" if period_type == "week" else f"{d.year}-{d.month:02d}"
                groups[key].append(row)
            for key, items in groups.items():
                actual = sum(float(row[actual_col]) for row in items) / len(items)
                pred = sum(float(row[pred_col]) for row in items) / len(items)
                split = str(items[-1]["split"])
                level_rows.append((target, period_type, key, actual, pred, split))
                for row in items:
                    curve_rows.append(
                        (
                            target,
                            f"{period_type}_curve_index",
                            f"{key}-{row['utc_hour_start']}",
                            _safe_ratio(float(row[actual_col]), actual),
                            _safe_ratio(float(row[pred_col]), pred),
                            row["split"],
                        )
                    )
    conn.executemany(
        "INSERT INTO m4_level_predictions VALUES (?, ?, ?, ?, ?, ?)",
        level_rows,
    )
    conn.executemany(
        "INSERT INTO m4_curve_predictions VALUES (?, ?, ?, ?, ?, ?)",
        curve_rows,
    )


def _replace_metrics(conn: sqlite3.Connection, predictions: list[dict[str, object]]) -> None:
    conn.execute("DELETE FROM m4_backtest_results")
    rows: list[tuple[str, str, str, str, float]] = []
    for split in ("train", "validate", "holdout"):
        items = [row for row in predictions if row["split"] == split]
        if not items:
            continue
        for target, actual_col, pred_col, baseline_col in (
            ("system_proxy_se1", "actual_se1", "pred_se1", "baseline_se1"),
            ("area_diff_proxy_se3", "actual_area_diff", "pred_area_diff", "baseline_area_diff"),
            ("recomposed_se3", "actual_se3", "pred_se3", "baseline_se3"),
        ):
            actual = [float(row[actual_col]) for row in items]
            pred = [float(row[pred_col]) for row in items]
            base = [float(row[baseline_col]) for row in items]
            rows.extend(
                [
                    ("hourly", target, split, "mae", mae(actual, pred)),
                    ("hourly", target, split, "rmse", rmse(actual, pred)),
                    ("baseline_m1", target, split, "mae", mae(actual, base)),
                    ("baseline_m1", target, split, "rmse", rmse(actual, base)),
                ]
            )
    for period_type in ("week", "month"):
        level_groups = conn.execute(
            "SELECT target, split, actual_level, predicted_level FROM m4_level_predictions WHERE period_type=?",
            (period_type,),
        ).fetchall()
        _extend_group_metrics(rows, f"{period_type}_level", level_groups, "actual_level", "predicted_level")
    for period_type in ("week", "month"):
        curve_groups = conn.execute(
            "SELECT target, split, actual_index, predicted_index FROM m4_curve_predictions WHERE curve_type=?",
            (f"{period_type}_curve_index",),
        ).fetchall()
        _extend_group_metrics(rows, f"{period_type}_curve_index", curve_groups, "actual_index", "predicted_index")
    _extend_baseline_level_and_curve_metrics(rows, predictions)
    conn.executemany("INSERT INTO m4_backtest_results VALUES (?, ?, ?, ?, ?)", rows)


def _extend_baseline_level_and_curve_metrics(
    output: list[tuple[str, str, str, str, float]],
    predictions: list[dict[str, object]],
) -> None:
    for target, actual_col, baseline_col in (
        ("system_proxy_se1", "actual_se1", "baseline_se1"),
        ("area_diff_proxy_se3", "actual_area_diff", "baseline_area_diff"),
    ):
        for period_type in ("week", "month"):
            groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
            for row in predictions:
                d = date.fromisoformat(str(row["local_date"]))
                key = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}" if period_type == "week" else f"{d.year}-{d.month:02d}"
                groups[(str(row["split"]), key)].append(row)
            for split in ("train", "validate", "holdout"):
                period_items = [items for (group_split, _key), items in groups.items() if group_split == split]
                if not period_items:
                    continue
                actual_levels = [sum(float(row[actual_col]) for row in items) / len(items) for items in period_items]
                baseline_levels = [sum(float(row[baseline_col]) for row in items) / len(items) for items in period_items]
                output.append((f"baseline_m1_{period_type}_level", target, split, "mae", mae(actual_levels, baseline_levels)))
                output.append((f"baseline_m1_{period_type}_level", target, split, "rmse", rmse(actual_levels, baseline_levels)))
                actual_indexes: list[float] = []
                baseline_indexes: list[float] = []
                for items, actual_level, baseline_level in zip(period_items, actual_levels, baseline_levels):
                    for row in items:
                        actual_indexes.append(_safe_ratio(float(row[actual_col]), actual_level))
                        baseline_indexes.append(_safe_ratio(float(row[baseline_col]), baseline_level))
                output.append((f"baseline_m1_{period_type}_curve_index", target, split, "mae", mae(actual_indexes, baseline_indexes)))
                output.append((f"baseline_m1_{period_type}_curve_index", target, split, "rmse", rmse(actual_indexes, baseline_indexes)))


def _extend_group_metrics(
    output: list[tuple[str, str, str, str, float]],
    metric_scope: str,
    rows: Iterable[sqlite3.Row],
    actual_col: str,
    predicted_col: str,
) -> None:
    grouped: dict[tuple[str, str], list[sqlite3.Row]] = defaultdict(list)
    for row in rows:
        grouped[(row["target"], row["split"])].append(row)
    for (target, split), items in grouped.items():
        actual = [float(row[actual_col]) for row in items]
        predicted = [float(row[predicted_col]) for row in items]
        output.append((metric_scope, target, split, "mae", mae(actual, predicted)))
        output.append((metric_scope, target, split, "rmse", rmse(actual, predicted)))


def _write_artifact_manifest(conn: sqlite3.Connection, model_dir: Path | str, models: dict[str, dict[str, object]]) -> None:
    conn.execute("DELETE FROM m4_artifact_manifest")
    manifest = write_model_artifact_manifest(model_dir, models)
    conn.executemany(
        "INSERT OR REPLACE INTO m4_artifact_manifest(key, value) VALUES (?, ?)",
        [(key, json.dumps(value) if isinstance(value, (dict, list)) else str(value)) for key, value in manifest.items()],
    )


def _write_model_artifacts(model_dir: Path | str, models: dict[str, dict[str, object]]) -> None:
    path = Path(model_dir).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    for target, model in models.items():
        metadata = {key: value for key, value in model.items() if key != "estimator"}
        (path / f"{target}_model.json").write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
        estimator = model.get("estimator")
        if estimator is not None:
            try:
                import joblib

                joblib.dump(estimator, path / f"{target}_model.joblib")
            except Exception as exc:
                metadata["joblib_write_error"] = f"{type(exc).__name__}: {exc}"
                (path / f"{target}_model.json").write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")


def _artifact_manifest(model_dir: Path | str, models: dict[str, dict[str, object]]) -> dict[str, object]:
    path = Path(model_dir).expanduser()
    return {
        "package_id": PACKAGE_ID,
        "model_version": MODEL_VERSION,
        "algorithm": sorted({str(model["algorithm"]) for model in models.values()}),
        "targets": sorted(models),
        "artifacts": {
            target: {
                "metadata": str(path / f"{target}_model.json"),
                "joblib": str(path / f"{target}_model.joblib") if model.get("estimator") is not None else "",
            }
            for target, model in models.items()
        },
        "created_at": _now(),
    }


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _clear_tables(conn: sqlite3.Connection) -> None:
    for table in (
        "m4_feature_matrix",
        "m4_feature_matrix_manifest",
        "m4_level_predictions",
        "m4_curve_predictions",
        "m4_hourly_predictions",
        "m4_backtest_results",
        "m4_artifact_manifest",
    ):
        conn.execute(f"DELETE FROM {table}")


def _start_run(conn: sqlite3.Connection, command: str) -> int:
    cursor = conn.execute(
        "INSERT INTO m4_model_runs(command, started_at, status) VALUES (?, ?, 'running')",
        (command, _now()),
    )
    return int(cursor.lastrowid)


def _finish_run(conn: sqlite3.Connection, run_id: int, status: str, message: str) -> None:
    conn.execute(
        "UPDATE m4_model_runs SET completed_at=?, status=?, message=? WHERE run_id=?",
        (_now(), status, message, run_id),
    )


def _safe_ratio(value: float, denominator: float) -> float:
    if abs(denominator) < 1e-9:
        return 1.0
    return value / denominator


def _metric_pair(predictions: list[dict[str, object]], actual_col: str, pred_col: str, baseline_col: str) -> dict[str, float]:
    actual = [float(row[actual_col]) for row in predictions]
    pred = [float(row[pred_col]) for row in predictions]
    base = [float(row[baseline_col]) for row in predictions]
    return {
        "m4_mae": mae(actual, pred),
        "m4_rmse": rmse(actual, pred),
        "baseline_mae": mae(actual, base),
        "baseline_rmse": rmse(actual, base),
    }


def _baseline_comparison_metrics(rows: list[dict[str, object]]) -> dict[str, dict[str, dict[str, float]]]:
    variants = {
        "P0036_HGB_residual": {
            "system_proxy_se1": ("actual_se1", "pred_se1"),
            "area_diff_proxy_se3": ("actual_area_diff", "pred_area_diff"),
            "recomposed_se3": ("actual_se3", "pred_se3"),
        },
        "train_only_M1_m3ab_normalized": {
            "system_proxy_se1": ("actual_se1", "baseline_se1"),
            "area_diff_proxy_se3": ("actual_area_diff", "baseline_area_diff"),
            "recomposed_se3": ("actual_se3", "baseline_se3"),
        },
        "train_only_M1_raw_actual": {
            "system_proxy_se1": ("actual_se1", "train_only_raw_baseline_se1"),
            "area_diff_proxy_se3": ("actual_area_diff", "train_only_raw_baseline_area_diff"),
            "recomposed_se3": ("actual_se3", "train_only_raw_baseline_se3"),
        },
        "full_period_M1_existing": {
            "system_proxy_se1": ("actual_se1", "full_period_baseline_se1"),
            "area_diff_proxy_se3": ("actual_area_diff", "full_period_baseline_area_diff"),
            "recomposed_se3": ("actual_se3", "full_period_baseline_se3"),
        },
    }
    output: dict[str, dict[str, dict[str, float]]] = {}
    for variant, targets in variants.items():
        output[variant] = {}
        for target, (actual_col, pred_col) in targets.items():
            actual = [float(row[actual_col]) for row in rows]
            pred = [float(row[pred_col]) for row in rows]
            output[variant][target] = {"mae": mae(actual, pred), "rmse": rmse(actual, pred)}
    return output


def _format_metric_table(metrics: dict[str, dict[str, dict[str, float]]]) -> str:
    lines = [
        "| variant | target | MAE | RMSE |",
        "|---|---|---:|---:|",
    ]
    for variant, targets in metrics.items():
        for target, values in targets.items():
            lines.append(f"| {variant} | {target} | {_fmt(values['mae'])} | {_fmt(values['rmse'])} |")
    return "\n".join(lines)


def _format_subset_metrics(name: str, rows: list[dict[str, object]]) -> str:
    if not rows:
        return f"No {name} holdout rows."
    return _format_metric_table(_baseline_comparison_metrics(rows))


def _residual_prediction_summary(predictions: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for split in ("train", "validate", "holdout"):
        rows = [row for row in predictions if row["split"] == split]
        if not rows:
            continue
        for target, actual_col, pred_col in (
            ("system_proxy_se1", "target_se1", "pred_residual_se1"),
            ("area_diff_proxy_se3", "target_area_diff", "pred_residual_area_diff"),
        ):
            actual = sorted(float(row[actual_col]) for row in rows)
            pred = sorted(float(row[pred_col]) for row in rows)
            output.append(
                {
                    "split": split,
                    "target": target,
                    "actual_mean": sum(actual) / len(actual),
                    "actual_min": actual[0],
                    "actual_p50": _percentile_sorted(actual, 0.50),
                    "actual_p95": _percentile_sorted(actual, 0.95),
                    "actual_max": actual[-1],
                    "pred_mean": sum(pred) / len(pred),
                    "pred_min": pred[0],
                    "pred_p50": _percentile_sorted(pred, 0.50),
                    "pred_p95": _percentile_sorted(pred, 0.95),
                    "pred_max": pred[-1],
                }
            )
    return output


def _format_residual_summary(rows: list[dict[str, object]]) -> str:
    lines = [
        "| split | target | actual_mean | actual_min | actual_p50 | actual_p95 | actual_max | pred_mean | pred_min | pred_p50 | pred_p95 | pred_max |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {split} | {target} | {actual_mean} | {actual_min} | {actual_p50} | {actual_p95} | {actual_max} | {pred_mean} | {pred_min} | {pred_p50} | {pred_p95} | {pred_max} |".format(
                split=row["split"],
                target=row["target"],
                actual_mean=_fmt(row["actual_mean"]),
                actual_min=_fmt(row["actual_min"]),
                actual_p50=_fmt(row["actual_p50"]),
                actual_p95=_fmt(row["actual_p95"]),
                actual_max=_fmt(row["actual_max"]),
                pred_mean=_fmt(row["pred_mean"]),
                pred_min=_fmt(row["pred_min"]),
                pred_p50=_fmt(row["pred_p50"]),
                pred_p95=_fmt(row["pred_p95"]),
                pred_max=_fmt(row["pred_max"]),
            )
        )
    return "\n".join(lines)


def _format_largest_errors(rows: list[dict[str, object]], target: str) -> str:
    if target == "system_proxy_se1":
        actual_col, pred_col, baseline_col = "actual_se1", "pred_se1", "baseline_se1"
    else:
        actual_col, pred_col, baseline_col = "actual_area_diff", "pred_area_diff", "baseline_area_diff"
    ranked = sorted(rows, key=lambda row: abs(float(row[actual_col]) - float(row[pred_col])), reverse=True)[:20]
    lines = [
        "| local_date | hour | special_day_type | actual | train_only_M1 | M4_pred | abs_error | signed_error |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in ranked:
        signed = float(row[pred_col]) - float(row[actual_col])
        lines.append(
            f"| {row['local_date']} | {row['local_hour']} | {row.get('special_day_type', '')} | {_fmt(row[actual_col])} | {_fmt(row[baseline_col])} | {_fmt(row[pred_col])} | {_fmt(abs(signed))} | {_fmt(signed)} |"
        )
    return "\n".join(lines)


def _format_candidate_timings(rows: list[dict[str, object]]) -> str:
    lines = [
        "# P0036 candidate timings",
        "",
        "| candidate_id | target | train_rows | feature_count | elapsed_seconds | status | validate_mae | validate_rmse | reason | parameters |",
        "|---|---|---:|---:|---:|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {candidate_id} | {target} | {train_rows} | {feature_count} | {elapsed} | {status} | {mae} | {rmse} | {reason} | `{params}` |".format(
                candidate_id=row["candidate_id"],
                target=row["target"],
                train_rows=row["train_rows"],
                feature_count=row["feature_count"],
                elapsed=_fmt(row["elapsed_seconds"]),
                status=row["status"],
                mae=_fmt(row.get("validate_mae")),
                rmse=_fmt(row.get("validate_rmse")),
                reason=str(row["reason_selected_or_rejected"]).replace("|", "/"),
                params=json.dumps(row["parameters"], sort_keys=True),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _percentile_sorted(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, max(0, round((len(values) - 1) * fraction)))
    return values[index]


def _fmt(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.6f}"


def _week_distance(left: int, right: int) -> int:
    direct = abs(left - right)
    return min(direct, 53 - direct)


def _week_month(rows: list[TrainingRow], week_key: str) -> str | None:
    for row in rows:
        d = date.fromisoformat(row.local_date)
        if f"{d.isocalendar().year}-W{d.isocalendar().week:02d}" == week_key:
            return f"{d.year}-{d.month:02d}"
    return None


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
