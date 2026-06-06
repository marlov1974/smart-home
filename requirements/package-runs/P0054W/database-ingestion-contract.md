# P0054W database ingestion contract

Native table: `esett_mga_consumption_native_v1`.

The native table preserves source system/name, country, MGA id/name, bidding zone, settlement class, resolution minutes, interval start/end, source value, unit, value kind, direction, quality status, ingest time and package id.

Uniqueness follows the P0054W required key including `version_or_publication_time_utc`, stored as an empty string when unavailable because SQLite treats nulls as distinct in unique keys.
