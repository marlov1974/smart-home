# P0040 short-term forecast design

Input: nearest known spot hours, weather forecast, special-day calendar and active shape components. Mechanism: generate hourly shape, apply weather/special-day deltas, then anchor level from known spot context. Output: 7-day hourly absolute forecast. P0040 does not build the API.
