# P0056O Implementation Design

## Package Interpretation

P0056O converts P0056K DayAhead delivery-day generation from fixed 24 local positions to canonical true local-day rows. The canonical representation is the source of truth for model/evaluation rows; any future fixed-position market-emulator adapter must be separate.

## Implementation Structure

1. Add a P0056K immutable target-row metadata type for canonical DayAhead delivery rows.
2. Replace fixed `range(24)` target generation with a UTC iterator bounded by Europe/Stockholm local midnight to next local midnight.
3. Emit required DST metadata in every P0056K `build_dayahead_rows` row.
4. Update P0056K origin scoring gate to expect the canonical row count for the delivery day instead of always 24.
5. Keep P0056N baseline evidence stable by adding an explicit legacy fixed-24 mapping helper there.
6. Add P0056O regression tests for spring-forward, fall-back and standard days.
7. Add a compact P0056O evidence generator for before/after row-generation verification and SE2 March alignment.

## Canonical Representation

For each delivery date, the canonical iterator:

- starts at local midnight in Europe/Stockholm
- ends at the next local midnight
- converts both boundaries to UTC
- iterates hourly UTC timestamps in `[start_utc, end_utc)`
- converts each UTC timestamp back to Stockholm local metadata

This naturally skips nonexistent spring-forward local 02:00 and includes two fall-back 02:00 rows with different UTC offsets.

## Intended Changes

- `src/mac/services/spotprice_model_diagnostics/p0056k.py`
  - add `DeliveryDayTarget`
  - add `delivery_day_target_rows`
  - make `delivery_day_target_utc_hours` delegate to canonical rows
  - add required schema fields in `build_dayahead_rows`
  - replace hard 24-row forecast gate with canonical expected count
- `src/mac/services/spotprice_model_diagnostics/p0056n.py`
  - keep pre-fix audit by introducing legacy fixed-24 target generation
- `src/mac/services/spotprice_model_diagnostics/p0056o.py`
  - generate compact P0056O evidence only; no model training
- `tests/mac/test_p0056o_dayahead_dst_fix.py`
  - cover required DST behavior and old-bug condition

## Test Strategy

- Unit tests for canonical row counts and metadata:
  - 2026-03-29: 23 rows, no local 02:00, unique UTC
  - 2025-10-26: 25 rows, local 02 twice with different offsets
  - 2026-10-25: same fall-back behavior
  - standard day: 24 rows
- Regression test proves legacy fixed-24 spring behavior duplicates UTC while new canonical behavior does not.
- Existing P0056K and P0056N tests remain meaningful.
- P0056O evidence generator verifies SE2 2026-03-25..31 row alignment without retraining.

## Risks and Uncertainties

- P0056K long-run model results will change if rerun across DST dates because canonical row counts change. P0056O intentionally does not rerun model optimization.
- Existing evidence from P0056K/P0056M remains historical and should not be rewritten.
- Future packages may need an adapter if a downstream consumer requires exactly 24 output positions for market-facing UI or emulator protocols.
