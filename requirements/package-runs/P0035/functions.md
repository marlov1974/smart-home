# P0035 function design

## New calendar functions

`easter_sunday(year)`

- Computes Gregorian Easter Sunday.

`midsummer_eve(year)`

- Returns Friday between 19 and 25 June.

`all_saints_day(year)`

- Returns Saturday between 31 October and 6 November.

`classify_special_day(day)`

- Returns one deterministic calendar row with special-day, period, bridge and holiday metadata.

`generate_calendar(start_year, end_year)`

- Returns all date rows for the inclusive year interval.

`write_calendar_csv(rows, path)`

- Writes the committed CSV schema.

## Changed temperature-normalization functions

`initialize_schema(conn)`

- Adds P0035 tables and compatibility aliases.

`compute_m2_climate_normals(rows)`

- Changes method to broader cyclic smoothed robust normal.

`compute_m3a_statistical_temperature_delta(...)`

- M3A name for the old temperature-delta model.

`compute_m3b_special_day_delta(rows, m1_rows, m3a_rows, calendar_rows)`

- Computes conservative special-day deltas with sample counts and shrinkage.

`build_m3ab_normalized_training_series(...)`

- Builds M3A/M3B-normalized output rows.

`build_training_foundation(...)`

- Stores M3A, M3B, M3AB and compatibility outputs.

## Changed M4 functions

`load_p0035_training_series(feature_db)`

- Loads M3AB normalized targets and M3B addback columns when available.

`train_m4(...)`

- Trains residual targets against M1 baseline and writes staging/active artifacts.

`predict_rows(...)`

- Predicts residuals, normalized prices and addback evaluation prices.

`promote_active_model(staging_dir, active_dir)`

- Copies validated staging artifacts to active atomically enough for local file consumers.

`validate_m4_outputs(...)`

- Validates residual predictions, active artifacts, holdout evidence files and forbidden-feature exclusion.
