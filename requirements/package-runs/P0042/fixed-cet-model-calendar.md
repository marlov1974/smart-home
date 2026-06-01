# P0042 fixed-CET model calendar

UTC remains primary storage and join truth. `model_cet_timestamp = timestamp_utc + 1 hour` for every row, all year. AI-1 and AI-2 use `model_cet_date` as the model calendar. This removes Stockholm civil DST 23h/25h model-day artifacts while retaining Stockholm-local fields as diagnostics.

Tradeoff: summer civil-time holiday boundaries differ by one civil hour from Europe/Stockholm. Raw UTC data is unchanged, so later packages can compare Stockholm-local grouping if needed.
