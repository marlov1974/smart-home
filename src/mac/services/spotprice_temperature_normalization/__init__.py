"""P0033 temperature-normalized spotprice training foundation."""

from .core import (
    build_training_foundation,
    compute_m1_calm_normal_price,
    compute_m2_climate_anomalies,
    compute_m2_climate_normals,
    compute_m3_statistical_temperature_delta,
    default_feature_db_path,
    dump_p0032_location_weights,
    initialize_schema,
    select_m2_target_weights,
    summarize_temperature_normalization,
    validate_training_foundation,
)

__all__ = [
    "build_training_foundation",
    "compute_m1_calm_normal_price",
    "compute_m2_climate_anomalies",
    "compute_m2_climate_normals",
    "compute_m3_statistical_temperature_delta",
    "default_feature_db_path",
    "dump_p0032_location_weights",
    "initialize_schema",
    "select_m2_target_weights",
    "summarize_temperature_normalization",
    "validate_training_foundation",
]
