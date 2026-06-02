# P0047 calendar signal attribution

{
  "bridge_day_strong": {
    "spread_near_zero": 17,
    "spread_positive": 20,
    "spread_small_nonzero": 11
  },
  "bridge_day_weak": {
    "spread_positive": 16,
    "spread_small_nonzero": 2,
    "spread_spike_positive": 6
  },
  "fixed_public_holiday": {
    "spread_near_zero": 67,
    "spread_positive": 52,
    "spread_small_nonzero": 25
  },
  "holiday_eve": {
    "spread_near_zero": 1,
    "spread_positive": 14,
    "spread_small_nonzero": 7,
    "spread_spike_positive": 2
  },
  "holiday_period_day": {
    "spread_near_zero": 52,
    "spread_positive": 29,
    "spread_small_nonzero": 15
  },
  "major_social_holiday": {
    "spread_near_zero": 39,
    "spread_positive": 47,
    "spread_small_nonzero": 10
  },
  "movable_public_holiday": {
    "spread_near_zero": 34,
    "spread_positive": 69,
    "spread_small_nonzero": 17
  },
  "normal_saturday": {
    "spread_near_zero": 372,
    "spread_positive": 544,
    "spread_small_nonzero": 187,
    "spread_spike_positive": 49
  },
  "normal_sunday": {
    "spread_near_zero": 391,
    "spread_positive": 500,
    "spread_small_nonzero": 206,
    "spread_spike_positive": 55
  },
  "normal_weekday": {
    "spread_near_zero": 1328,
    "spread_negative": 5,
    "spread_positive": 2851,
    "spread_small_nonzero": 863,
    "spread_spike_positive": 713
  },
  "post_holiday_recovery_day": {
    "spread_near_zero": 5,
    "spread_positive": 4,
    "spread_small_nonzero": 1,
    "spread_spike_positive": 14
  },
  "pre_holiday_transition_day": {
    "spread_near_zero": 4,
    "spread_positive": 31,
    "spread_small_nonzero": 7,
    "spread_spike_positive": 6
  },
  "special_weekend_day": {
    "spread_near_zero": 30,
    "spread_positive": 29,
    "spread_small_nonzero": 13
  }
}

Special-day categories are present, but P0047 treats calendar attribution as diagnostic because spread regimes are dominated by grid/weather/price context rather than calendar labels alone.
