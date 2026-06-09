# P0056O DST Fix Design

The fix starts at local delivery-day midnight in Europe/Stockholm, ends at next local midnight, converts both boundaries to UTC, iterates hourly UTC timestamps and converts each target back to local metadata.

This avoids constructing nonexistent local timestamps on spring-forward days and naturally keeps both repeated local 02:00 rows on fall-back days with different UTC timestamps and offsets.

The canonical table is allowed to have 23, 24 or 25 rows. Any future fixed-24 consumer must use a separate adapter.
