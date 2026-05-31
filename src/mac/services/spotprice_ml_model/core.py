"""P0034 deterministic M4 normal spot model."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import json
import math
import sqlite3
from typing import Iterable


DEFAULT_FEATURE_DB = Path.home() / ".smart-home" / "data" / "spotprice_model_features.sqlite3"
DEFAULT_MODEL_DIR = Path.home() / ".smart-home" / "data" / "spotprice_ml_models" / "m4"
MODEL_DB_NAME = "m4_model.sqlite3"
PACKAGE_ID = "P0034"
MODEL_VERSION = "m4_sklearn_polynomial_ridge_v2"
RIDGE_LAMBDA = 1.0
RANDOM_SEED = 34

FEATURE_NAMES = (
    "intercept",
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
    "days_since_start_scaled",
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


def load_p0033_training_series(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[TrainingRow]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
              utc_hour_start,
              local_date,
              local_hour,
              temp_normalized_price_v1_se1 AS target_se1,
              temp_normalized_area_diff_v1 AS target_area_diff,
              temp_normalized_price_v1_se3 AS target_se3,
              normal_price_v1_se1 AS baseline_se1,
              normal_price_v1_area_diff AS baseline_area_diff,
              normal_price_v1_se1 + normal_price_v1_area_diff AS baseline_se3
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
        )
        for row in rows
    ]


def build_calendar_features(rows: list[TrainingRow]) -> dict[str, list[float]]:
    if not rows:
        return {}
    start = date.fromisoformat(rows[0].local_date)
    last = date.fromisoformat(rows[-1].local_date)
    span = max(1, (last - start).days)
    output: dict[str, list[float]] = {}
    for row in rows:
        d = date.fromisoformat(row.local_date)
        weekday = d.weekday()
        iso_week = d.isocalendar().week
        month = d.month
        doy = d.timetuple().tm_yday
        values = {
            "intercept": 1.0,
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
            "days_since_start_scaled": (d - start).days / span,
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
                    json.dumps(features[row.utc_hour_start], separators=(",", ":")),
                )
            )
        conn.executemany(
            """
            INSERT INTO m4_feature_matrix
            (utc_hour_start, local_date, local_hour, split, target_se1, target_area_diff, target_se3,
             baseline_se1, baseline_area_diff, baseline_se3, features_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    if not train_rows:
        raise ValueError("no training rows")
    models: dict[str, dict[str, object]] = {}
    for target, column in TARGETS.items():
        x = [row["features"] for row in train_rows]
        y = [float(row[column]) for row in train_rows]
        models[target] = train_m4_target_model(target=target, target_column=column, x=x, y=y, ridge_lambda=ridge_lambda)
    _write_model_artifacts(model_dir, models)
    predictions = predict_rows(rows, models)
    with connect_model_db(model_dir) as conn:
        initialize_schema(conn)
        run_id = _start_run(conn, "train-m4")
        _replace_predictions(conn, predictions)
        _replace_level_and_curve(conn, predictions)
        _replace_metrics(conn, predictions)
        _write_artifact_manifest(conn, model_dir, models)
        _finish_run(conn, run_id, "ok", "trained")
    return {"ok": True, "model_dir": str(Path(model_dir).expanduser()), "targets": sorted(models)}


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
        forbidden = [name for name in feature_names if any(token in name for token in ("temp", "weather", "wind", "solar", "cloud"))]
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
        Path("requirements/package-runs/P0034/holdout-results.md"),
        Path("requirements/package-runs/P0034/baseline-comparison.md"),
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
    x: list[list[float]],
    y: list[float],
    ridge_lambda: float = RIDGE_LAMBDA,
) -> dict[str, object]:
    try:
        from sklearn.linear_model import Ridge
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import PolynomialFeatures

        estimator = make_pipeline(
            PolynomialFeatures(degree=2, include_bias=False),
            Ridge(alpha=ridge_lambda, fit_intercept=True),
        )
        estimator.fit(x, y)
        return {
            "target": target,
            "target_column": target_column,
            "feature_names": list(FEATURE_NAMES),
            "algorithm": "sklearn_polynomial_features_ridge",
            "model_version": MODEL_VERSION,
            "random_seed": RANDOM_SEED,
            "parameters": {
                "polynomial_degree": 2,
                "polynomial_include_bias": False,
                "ridge_alpha": ridge_lambda,
                "ridge_fit_intercept": True,
            },
            "estimator": estimator,
        }
    except Exception as exc:
        coefficients = fit_ridge(x, y, ridge_lambda)
        return {
            "target": target,
            "target_column": target_column,
            "feature_names": list(FEATURE_NAMES),
            "coefficients": coefficients,
            "ridge_lambda": ridge_lambda,
            "algorithm": "pure_python_ridge_normal_equation",
            "fallback_reason": f"{type(exc).__name__}: {exc}",
            "model_version": "m4_ridge_calendar_v1",
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
        pred_se1 = predict_m4_target_model(models["system_proxy_se1"], row["features"])
        pred_area = predict_m4_target_model(models["area_diff_proxy_se3"], row["features"])
        output.append(
            {
                **row,
                "pred_se1": pred_se1,
                "pred_area_diff": pred_area,
                "pred_se3": pred_se1 + pred_area,
            }
        )
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


def write_model_artifact_manifest(model_dir: Path | str, models: dict[str, dict[str, object]]) -> dict[str, object]:
    _write_model_artifacts(model_dir, models)
    manifest = _artifact_manifest(model_dir, models)
    path = Path(model_dir).expanduser() / "m4_artifact_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def split_for_date(local_date: str) -> str:
    d = date.fromisoformat(local_date)
    if d <= date(2024, 12, 31):
        return "train"
    if d <= date(2025, 12, 31):
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
                row["target_se1"],
                row["pred_se1"],
                row["baseline_se1"],
                row["target_area_diff"],
                row["pred_area_diff"],
                row["baseline_area_diff"],
                row["target_se3"],
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
        ("system_proxy_se1", "target_se1", "pred_se1"),
        ("area_diff_proxy_se3", "target_area_diff", "pred_area_diff"),
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
            ("system_proxy_se1", "target_se1", "pred_se1", "baseline_se1"),
            ("area_diff_proxy_se3", "target_area_diff", "pred_area_diff", "baseline_area_diff"),
            ("recomposed_se3", "target_se3", "pred_se3", "baseline_se3"),
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
        ("system_proxy_se1", "target_se1", "baseline_se1"),
        ("area_diff_proxy_se3", "target_area_diff", "baseline_area_diff"),
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


def _week_month(rows: list[TrainingRow], week_key: str) -> str | None:
    for row in rows:
        d = date.fromisoformat(row.local_date)
        if f"{d.isocalendar().year}-W{d.isocalendar().week:02d}" == week_key:
            return f"{d.year}-{d.month:02d}"
    return None


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
