"""P0038 solar/wind normalization diagnostics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json
import math
import sqlite3
import time
from statistics import median

from src.mac.services.spotprice_model_diagnostics.p0037 import (
    TARGET_FIELDS,
    build_features,
    count_splits,
    fit_m1_surface,
    fit_strict_components,
    load_diagnostic_rows,
    predict_m1,
)
from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_PRICE_DB_PATH, DEFAULT_WEATHER_DB_PATH


EVIDENCE_DIR = Path("requirements/package-runs/P0038")
WEATHER_DB = DEFAULT_WEATHER_DB_PATH
SHRINKAGE_K = 72.0
M3C_CAP = 0.30
M3D_CAP = 0.50

P0038_WIND_LOCATIONS = {
    "Malmo": (55.6050, 13.0038, "south_wind_proxy", 0.55),
    "Kalmar": (56.6634, 16.3568, "south_wind_proxy", 0.45),
    "Kristinehamn": (59.3098, 14.1081, "central_wind_proxy", 1.00),
    "Pitea": (65.3172, 21.4794, "north_wind_proxy", 0.35),
    "Ange": (62.5246, 15.6590, "north_wind_proxy", 0.35),
    "Harnosand": (62.6323, 17.9379, "north_wind_proxy", 0.30),
}

WIND_PROXY_MAP = {
    "south": "p0038_south_wind_proxy",
    "central": "p0038_central_wind_proxy",
    "north": "p0038_north_wind_proxy",
}

SOLAR_PROXY_MAP = {
    "south": "p0038_south_solar_proxy",
    "se3": "p0038_se3_load_solar_proxy",
    "north": "p0038_north_solar_proxy",
}


@dataclass(frozen=True)
class P0038Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0038_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    price_db: Path | str = DEFAULT_PRICE_DB_PATH,
    weather_db: Path | str = WEATHER_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0038Result:
    rows = load_diagnostic_rows(feature_db=feature_db, price_db=price_db, weather_db=weather_db)
    fit_strict_components(rows)
    enrich_p0038_weather(rows, weather_db)
    apply_solar_wind_features(rows)
    fit_apply_m3c_m3d(rows)
    fit_apply_m4_area_only(rows)
    matrix = build_p0038_matrix(rows)
    persist_feature_db_outputs(rows, feature_db)
    evidence = write_p0038_evidence(Path(evidence_dir), rows, matrix, weather_db)
    status = "PASS" if _mae(matrix, "M1+M3A+M3B+M3C+M3D+M4_area_diff_only", "recomposed_se3") < _mae(matrix, "M1+M3A+M3B", "recomposed_se3") else "WARN"
    return P0038Result(status=status, row_counts=count_splits(rows), evidence=evidence)


def enrich_p0038_weather(rows: list[dict[str, object]], weather_db: Path | str) -> None:
    needed = set(WIND_PROXY_MAP.values()) | set(SOLAR_PROXY_MAP.values())
    with sqlite3.connect(Path(weather_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        records = conn.execute(
            f"""
            SELECT area_proxy, utc_hour_start, weighted_shortwave_radiation, weighted_cloud_cover,
                   weighted_wind_speed_100m, source_coverage_count, source_coverage_weight
            FROM weather_area_hourly
            WHERE area_proxy IN ({",".join("?" for _ in needed)})
            """,
            tuple(sorted(needed)),
        ).fetchall()
    by_key = {(row["area_proxy"], row["utc_hour_start"]): row for row in records}
    for row in rows:
        utc = row["utc_hour_start"]
        for name, area_proxy in WIND_PROXY_MAP.items():
            item = by_key.get((area_proxy, utc))
            row[f"p0038_wind_{name}_100m"] = None if item is None else float(item["weighted_wind_speed_100m"])
        for name, area_proxy in SOLAR_PROXY_MAP.items():
            item = by_key.get((area_proxy, utc))
            row[f"p0038_solar_{name}_shortwave"] = None if item is None else float(item["weighted_shortwave_radiation"])
            row[f"p0038_solar_{name}_cloud"] = None if item is None else float(item["weighted_cloud_cover"])


def apply_solar_wind_features(rows: list[dict[str, object]]) -> None:
    for row in rows:
        south_solar = solar_generation_proxy(row["p0038_solar_south_shortwave"], row["p0038_solar_south_cloud"])
        se3_solar = solar_generation_proxy(row["p0038_solar_se3_shortwave"], row["p0038_solar_se3_cloud"])
        north_solar = solar_generation_proxy(row["p0038_solar_north_shortwave"], row["p0038_solar_north_cloud"])
        row["m3c_solar_proxy_se1"] = 0.50 * north_solar + 0.25 * se3_solar + 0.25 * south_solar
        row["m3c_solar_proxy_area"] = 0.60 * south_solar + 0.25 * se3_solar + 0.15 * north_solar
        south_wind = wind_power_proxy(row["p0038_wind_south_100m"])
        central_wind = wind_power_proxy(row["p0038_wind_central_100m"])
        north_wind = wind_power_proxy(row["p0038_wind_north_100m"])
        row["m3d_wind_proxy_se1"] = 0.50 * north_wind + 0.25 * central_wind + 0.25 * south_wind
        row["m3d_wind_proxy_area"] = 0.60 * south_wind + 0.25 * central_wind + 0.15 * north_wind
        row["m3d_south_minus_north"] = south_wind - north_wind
        row["m3d_central_minus_north"] = central_wind - north_wind
        row["m3d_south_minus_central"] = south_wind - central_wind


def solar_generation_proxy(shortwave: object, cloud_cover: object) -> float:
    radiation = max(0.0, float(shortwave or 0.0))
    cloud = min(100.0, max(0.0, float(cloud_cover or 0.0)))
    return radiation * (1.0 - 0.35 * cloud / 100.0)


def wind_power_proxy(speed_100m: object) -> float:
    speed = max(0.0, float(speed_100m or 0.0))
    if speed < 3.0:
        return 0.0
    if speed >= 15.0:
        return 1.0
    return ((speed - 3.0) / 12.0) ** 3


def fit_apply_m3c_m3d(rows: list[dict[str, object]]) -> None:
    for component, proxy_prefix, cap in (("m3c", "solar", M3C_CAP), ("m3d", "wind", M3D_CAP)):
        for short in ("se1", "area"):
            field = f"{component}_{proxy_prefix}_proxy_{short}"
            normals = fit_normal_surface([row for row in rows if row["split"] == "train"], field)
            for row in rows:
                normal = predict_normal_surface(normals, row)
                row[f"{component}_normal_{short}"] = normal
                row[f"{component}_anomaly_{short}"] = float(row[field]) - normal
            thresholds = anomaly_thresholds([row[f"{component}_anomaly_{short}"] for row in rows if row["split"] == "train"])
            for row in rows:
                row[f"{component}_bucket_{short}"] = bucket_value(float(row[f"{component}_anomaly_{short}"]), thresholds, "solar" if component == "m3c" else "wind")
        fit_component_deltas(rows, component, cap)


def fit_component_deltas(rows: list[dict[str, object]], component: str, cap: float) -> None:
    train = [row for row in rows if row["split"] == "train"]
    for short, actual_col in (("se1", "actual_se1"), ("area", "actual_area_diff")):
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in train:
            base = float(row[f"m1_structural_{short}"])
            residual = float(row[actual_col]) - base - float(row[f"m3a_{short}"]) - float(row[f"m3b_{short}"])
            if component == "m3d":
                residual -= float(row[f"m3c_{short}"])
            grouped[str(row[f"{component}_bucket_{short}"])].append(residual)
        normal_median = median(grouped.get("normal_solar" if component == "m3c" else "normal_wind", [0.0]))
        deltas: dict[str, float] = {}
        counts: dict[str, int] = {}
        for bucket, values in grouped.items():
            raw = median(values) - normal_median
            shrink = len(values) / (len(values) + SHRINKAGE_K)
            deltas[bucket] = max(-cap, min(cap, raw * shrink))
            counts[bucket] = len(values)
        for row in rows:
            bucket = str(row[f"{component}_bucket_{short}"])
            near_zero_solar = component == "m3c" and float(row[f"m3c_solar_proxy_{short}"]) < 5.0 and float(row[f"{component}_normal_{short}"]) < 5.0
            row[f"{component}_{short}"] = 0.0 if near_zero_solar else deltas.get(bucket, 0.0)
            row[f"{component}_sample_count_{short}"] = counts.get(bucket, 0)


def fit_apply_m4_area_only(rows: list[dict[str, object]]) -> None:
    train = [row for row in rows if row["split"] == "train"]
    validate = [row for row in rows if row["split"] == "validate"]
    for row in rows:
        row["m3abcd_normalized_se1"] = float(row["actual_se1"]) - row["m3a_se1"] - row["m3b_se1"] - row["m3c_se1"] - row["m3d_se1"]
        row["m3abcd_normalized_area"] = float(row["actual_area_diff"]) - row["m3a_area"] - row["m3b_area"] - row["m3c_area"] - row["m3d_area"]
        row["m3abcd_normalized_se3"] = row["m3abcd_normalized_se1"] + row["m3abcd_normalized_area"]
    area_surface = fit_m1_surface(train, "m3abcd_normalized_area")
    se1_surface = fit_m1_surface(train, "m3abcd_normalized_se1")
    for row in rows:
        row["m1_abcd_area"] = predict_m1(area_surface, row)
        row["m1_abcd_se1"] = predict_m1(se1_surface, row)
        row["m4_area_target"] = row["m3abcd_normalized_area"] - row["m1_abcd_area"]
    features = build_features(rows)
    from sklearn.ensemble import HistGradientBoostingRegressor

    best: tuple[float, object] | None = None
    for params in (
        {"max_iter": 50, "learning_rate": 0.03, "max_leaf_nodes": 7, "min_samples_leaf": 100, "l2_regularization": 0.1, "early_stopping": True, "random_state": 38},
        {"max_iter": 100, "learning_rate": 0.03, "max_leaf_nodes": 7, "min_samples_leaf": 100, "l2_regularization": 0.1, "early_stopping": True, "random_state": 38},
    ):
        start = time.monotonic()
        model = HistGradientBoostingRegressor(**params)
        model.fit([features[r["utc_hour_start"]] for r in train], [r["m4_area_target"] for r in train])
        pred = [float(v) for v in model.predict([features[r["utc_hour_start"]] for r in validate])]
        score = mae([r["m4_area_target"] for r in validate], pred)
        if best is None or score < best[0]:
            best = (score, model)
        _ = time.monotonic() - start
    model = best[1] if best else None
    for row in rows:
        row["m4_se1_disabled"] = 0.0
        row["m4_area"] = float(model.predict([features[row["utc_hour_start"]]])[0]) if model else 0.0


def build_p0038_matrix(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    holdout = [row for row in rows if row["split"] == "holdout"]
    variants = (
        "M1+M3A+M3B",
        "M1+M3A+M3B+M3C",
        "M1+M3A+M3B+M3C+M3D",
        "M1+M3A+M3B+M3C+M3D+M4_area_diff_only",
        "M1+M3A+M3B+M3C+M3D+M4_SE1_and_area_diff_diagnostic",
    )
    output: list[dict[str, object]] = []
    baseline: dict[str, float] = {}
    previous: dict[str, float] = {}
    for variant in variants:
        for target in ("system_proxy_se1", "area_diff_proxy_se3", "recomposed_se3"):
            actual, pred = series(holdout, variant, target)
            value = mae(actual, pred)
            key = target
            if variant == variants[0]:
                baseline[key] = value
            output.append(
                {
                    "variant": variant,
                    "target": target,
                    "MAE": value,
                    "RMSE": rmse(actual, pred),
                    "signed_error": sum(p - a for a, p in zip(actual, pred)) / len(actual),
                    "MAE_delta_vs_m3ab": value - baseline.get(key, value),
                    "MAE_delta_vs_previous": value - previous.get(key, value),
                }
            )
            previous[key] = value
    return output


def series(rows: list[dict[str, object]], variant: str, target: str) -> tuple[list[float], list[float]]:
    if target == "recomposed_se3":
        a1, p1 = series(rows, variant, "system_proxy_se1")
        a2, p2 = series(rows, variant, "area_diff_proxy_se3")
        return [a + b for a, b in zip(a1, a2)], [a + b for a, b in zip(p1, p2)]
    short = "se1" if target == "system_proxy_se1" else "area"
    actual_col = "actual_se1" if short == "se1" else "actual_area_diff"
    pred = [float(row[f"m1_abcd_{short}"]) + row[f"m3a_{short}"] + row[f"m3b_{short}"] for row in rows]
    if "M3C" in variant:
        pred = [p + row[f"m3c_{short}"] for p, row in zip(pred, rows)]
    if "M3D" in variant:
        pred = [p + row[f"m3d_{short}"] for p, row in zip(pred, rows)]
    if "M4_area_diff_only" in variant and short == "area":
        pred = [p + row["m4_area"] for p, row in zip(pred, rows)]
    if "M4_SE1_and_area_diff" in variant:
        pred = [p + (row["m4_area"] if short == "area" else row["m4_se1_disabled"]) for p, row in zip(pred, rows)]
    return [float(row[actual_col]) for row in rows], pred


def persist_feature_db_outputs(rows: list[dict[str, object]], feature_db: Path | str) -> None:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS m3abcd_normalized_prices (
              utc_hour_start TEXT PRIMARY KEY,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              m3c_solar_delta_se1 REAL NOT NULL,
              m3c_solar_delta_area_diff REAL NOT NULL,
              m3d_wind_delta_se1 REAL NOT NULL,
              m3d_wind_delta_area_diff REAL NOT NULL,
              m3abcd_normalized_price_se1 REAL NOT NULL,
              m3abcd_normalized_area_diff REAL NOT NULL,
              m3abcd_normalized_se3 REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS m3c_solar_delta (
              target TEXT NOT NULL,
              utc_hour_start TEXT NOT NULL,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              anomaly_value REAL NOT NULL,
              bucket TEXT NOT NULL,
              solar_delta REAL NOT NULL,
              sample_count INTEGER NOT NULL,
              PRIMARY KEY (target, utc_hour_start)
            );
            CREATE TABLE IF NOT EXISTS m3d_wind_delta (
              target TEXT NOT NULL,
              utc_hour_start TEXT NOT NULL,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              anomaly_value REAL NOT NULL,
              bucket TEXT NOT NULL,
              wind_delta REAL NOT NULL,
              sample_count INTEGER NOT NULL,
              PRIMARY KEY (target, utc_hour_start)
            );
            """
        )
        conn.execute("DELETE FROM m3abcd_normalized_prices")
        conn.execute("DELETE FROM m3c_solar_delta")
        conn.execute("DELETE FROM m3d_wind_delta")
        conn.executemany(
            "INSERT INTO m3abcd_normalized_prices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    row["utc_hour_start"],
                    row["local_date"],
                    row["local_hour"],
                    row["m3c_se1"],
                    row["m3c_area"],
                    row["m3d_se1"],
                    row["m3d_area"],
                    row["m3abcd_normalized_se1"],
                    row["m3abcd_normalized_area"],
                    row["m3abcd_normalized_se3"],
                )
                for row in rows
                if row["split"] in {"train", "validate", "holdout"}
            ],
        )
        for table, component, delta_name in (("m3c_solar_delta", "m3c", "solar_delta"), ("m3d_wind_delta", "m3d", "wind_delta")):
            conn.executemany(
                f"INSERT INTO {table} VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        target,
                        row["utc_hour_start"],
                        row["local_date"],
                        row["local_hour"],
                        row[f"{component}_anomaly_{short}"],
                        row[f"{component}_bucket_{short}"],
                        row[f"{component}_{short}"],
                        row[f"{component}_sample_count_{short}"],
                    )
                    for row in rows
                    if row["split"] in {"train", "validate", "holdout"}
                    for target, short in (("system_proxy_se1", "se1"), ("area_diff_proxy_se3", "area"))
                ],
            )


def write_p0038_evidence(evidence_dir: Path, rows: list[dict[str, object]], matrix: list[dict[str, object]], weather_db: Path | str) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    holdout = [r for r in rows if r["split"] == "holdout"]
    paths: dict[str, str] = {}
    paths["weather"] = write(evidence_dir / "weather-signal-availability.md", weather_report(weather_db))
    paths["solar"] = write(evidence_dir / "solar-proxy-summary.md", proxy_report("solar"))
    paths["wind"] = write(evidence_dir / "wind-proxy-summary.md", proxy_report("wind"))
    paths["m3c"] = write(evidence_dir / "m3c-solar-attribution.md", subset_report(rows, "solar"))
    paths["m3d"] = write(evidence_dir / "m3d-wind-attribution.md", subset_report(rows, "wind"))
    paths["normalized"] = write(evidence_dir / "m3abcd-normalized-summary.md", f"# P0038 M3ABCD normalized summary\n\nrows = {len([r for r in rows if r['split'] in {'train','validate','holdout'}])}\nholdout_rows = {len(holdout)}\n")
    paths["policy"] = write(evidence_dir / "m4-area-only-policy.md", "# P0038 M4 area-only policy\n\nM4_SE1 remains disabled by default. M4_area_diff remains enabled only for area_diff recomposition when holdout improves.\n")
    paths["holdout"] = write(evidence_dir / "full-year-holdout-results.md", matrix_markdown(matrix))
    paths["summary"] = write(evidence_dir / "component-attribution-summary.md", summary(matrix))
    paths["CHANGELOG"] = write(evidence_dir / "CHANGELOG.md", "# P0038 changelog\n\n- Added P0038 wind/solar proxy locations and M3C/M3D diagnostics.\n- Backfilled local weather for P0038 proxy locations.\n- Wrote M3ABCD normalized local feature table and evidence.\n")
    (evidence_dir / "component-attribution-matrix.json").write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")
    paths["matrix_json"] = str(evidence_dir / "component-attribution-matrix.json")
    return paths


def weather_report(weather_db: Path | str) -> str:
    with sqlite3.connect(Path(weather_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT area_proxy, COUNT(*) AS rows,
                   SUM(weighted_wind_speed_100m IS NULL) AS null_wind100,
                   SUM(weighted_shortwave_radiation IS NULL) AS null_shortwave,
                   SUM(weighted_cloud_cover IS NULL) AS null_cloud
            FROM weather_area_hourly
            WHERE area_proxy LIKE 'p0038_%'
            GROUP BY area_proxy ORDER BY area_proxy
            """
        ).fetchall()
    lines = ["# P0038 weather signal availability", "", "| area_proxy | rows | null_wind100 | null_shortwave | null_cloud |", "|---|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['area_proxy']} | {row['rows']} | {row['null_wind100']} | {row['null_shortwave']} | {row['null_cloud']} |")
    lines.extend(["", "Available variables include `wind_speed_100m`, `wind_speed_10m`, `wind_gusts_10m`, `shortwave_radiation` and `cloud_cover`. Direct/diffuse radiation and explicit solar elevation are not currently stored.", ""])
    return "\n".join(lines)


def proxy_report(kind: str) -> str:
    if kind == "wind":
        return "# P0038 wind proxy summary\n\nMandatory locations: Malmo, Kalmar, Kristinehamn, Pitea, Ange, Harnosand. Wind proxy uses capped nonlinear `wind_speed_100m` transform.\n"
    return "# P0038 solar proxy summary\n\nSolar proxy uses `shortwave_radiation * (1 - 0.35 * cloud_cover/100)`. Night/near-zero solar potential deltas are zero-gated.\n"


def subset_report(rows: list[dict[str, object]], kind: str) -> str:
    holdout = [r for r in rows if r["split"] == "holdout"]
    if kind == "solar":
        subsets = {"daylight_hours": [r for r in holdout if r["m3c_solar_proxy_area"] >= 5], "night_hours": [r for r in holdout if r["m3c_solar_proxy_area"] < 5], "solar_high_anomaly": [r for r in holdout if r["m3c_bucket_area"].endswith("high_solar")], "solar_low_anomaly": [r for r in holdout if r["m3c_bucket_area"].endswith("low_solar")]}
        before, after = "M1+M3A+M3B", "M1+M3A+M3B+M3C"
        title = "# P0038 M3C solar attribution"
    else:
        subsets = {"wind_high_anomaly": [r for r in holdout if r["m3d_bucket_area"].endswith("high_wind")], "wind_low_anomaly": [r for r in holdout if r["m3d_bucket_area"].endswith("low_wind")], "all_hours": holdout}
        before, after = "M1+M3A+M3B+M3C", "M1+M3A+M3B+M3C+M3D"
        title = "# P0038 M3D wind attribution"
    lines = [title, "", "| subset | rows | before_MAE | after_MAE | delta |", "|---|---:|---:|---:|---:|"]
    for name, subset in subsets.items():
        if not subset:
            lines.append(f"| {name} | 0 |  |  |  |")
            continue
        actual, pred_before = series(subset, before, "recomposed_se3")
        _actual, pred_after = series(subset, after, "recomposed_se3")
        b = mae(actual, pred_before)
        a = mae(actual, pred_after)
        lines.append(f"| {name} | {len(subset)} | {fmt(b)} | {fmt(a)} | {fmt(a-b)} |")
    return "\n".join(lines) + "\n"


def matrix_markdown(matrix: list[dict[str, object]]) -> str:
    lines = ["# P0038 full-year holdout results", "", "| variant | target | MAE | RMSE | signed_error | MAE_delta_vs_m3ab | MAE_delta_vs_previous |", "|---|---|---:|---:|---:|---:|---:|"]
    for row in matrix:
        lines.append(f"| {row['variant']} | {row['target']} | {fmt(row['MAE'])} | {fmt(row['RMSE'])} | {fmt(row['signed_error'])} | {fmt(row['MAE_delta_vs_m3ab'])} | {fmt(row['MAE_delta_vs_previous'])} |")
    return "\n".join(lines) + "\n"


def summary(matrix: list[dict[str, object]]) -> str:
    def v(name: str, target: str = "recomposed_se3") -> float:
        return _mae(matrix, name, target)
    m3ab = v("M1+M3A+M3B")
    m3c = v("M1+M3A+M3B+M3C")
    m3d = v("M1+M3A+M3B+M3C+M3D")
    area = v("M1+M3A+M3B+M3C+M3D+M4_area_diff_only")
    lines = [
        "# P0038 component attribution summary",
        "",
        f"M3C recomposed SE3 MAE delta: {fmt(m3c-m3ab)}.",
        f"M3D recomposed SE3 MAE delta after M3C: {fmt(m3d-m3c)}.",
        f"M4 area-only recomposed SE3 MAE delta after M3C/M3D: {fmt(area-m3d)}.",
        "M4_SE1 remains disabled by default.",
        "",
        "No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
        "",
    ]
    return "\n".join(lines)


def fit_normal_surface(rows: list[dict[str, object]], field: str) -> dict[tuple[int, int], float]:
    grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["day_of_year"]), int(row["local_hour"]))].append(float(row[field]))
    return {key: float(median(values)) for key, values in grouped.items()}


def predict_normal_surface(surface: dict[tuple[int, int], float], row: dict[str, object]) -> float:
    key = (int(row["day_of_year"]), int(row["local_hour"]))
    if key in surface:
        return surface[key]
    values = [value for (doy, hour), value in surface.items() if hour == int(row["local_hour"]) and abs(doy - int(row["day_of_year"])) <= 14]
    return float(median(values)) if values else 0.0


def anomaly_thresholds(values: list[float]) -> tuple[float, float, float, float]:
    ordered = sorted(values)
    return tuple(ordered[int((len(ordered) - 1) * q)] for q in (0.1, 0.3, 0.7, 0.9))


def bucket_value(value: float, thresholds: tuple[float, float, float, float], kind: str) -> str:
    names = ("very_low", "low", "normal", "high", "very_high")
    suffix = "solar" if kind == "solar" else "wind"
    if value <= thresholds[0]:
        return f"{names[0]}_{suffix}"
    if value <= thresholds[1]:
        return f"{names[1]}_{suffix}"
    if value < thresholds[2]:
        return f"{names[2]}_{suffix}"
    if value < thresholds[3]:
        return f"{names[3]}_{suffix}"
    return f"{names[4]}_{suffix}"


def _mae(matrix: list[dict[str, object]], variant: str, target: str) -> float:
    return float(next(row["MAE"] for row in matrix if row["variant"] == variant and row["target"] == target))


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


def write(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return str(path)


def main() -> int:
    result = run_p0038_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
