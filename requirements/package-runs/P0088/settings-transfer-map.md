# D extended settings transfer ranges

All33 records of807EA, stride8, bounded by8D6C8. Direction bit5 equals session direction4980. Direction1 writes a staged triple; direction0 reads it. Selector0 is a separate accepted end marker. Category/session context is required because different selectors alias the same storage. These are not external CN105 A3 numbers.

| Range | Selectors | Bank | Offset | Staging bytes |
|---|---|---|---|---|
| 0 | 1..1 | 0 | 0000 | 1940..1942 |
| 1 | 2..4 | 0 | 0006 | 1946..194E |
| 2 | 5..9 | 0 | 0012 | 1952..1960 |
| 3 | 51..53 | 0 | 0015 | 1955..195D |
| 4 | 54..56 | 0 | 0027 | 1967..196F |
| 5 | 101..135 | 0 | 0000 | 1940..19A8 |
| 6 | 151..178 | 0 | 0069 | 19A9..19FC |
| 7 | 201..235 | 1 | 0000 | 1B40..1BA8 |
| 8 | 251..278 | 1 | 0069 | 1BA9..1BFC |
| 9 | 301..363 | 2 | 0000 | 1D40..1DFC |
| 10 | 401..435 | 3 | 0000 | 1F40..1FA8 |
| 11 | 500..500 | 3 | 0069 | 1FA9..1FAB |
| 12 | 364..398 | 4 | 0000 | 2140..21A8 |
| 13 | 21..48 | 4 | 0069 | 21A9..21FC |
| 14 | 501..503 | 0 | 0000 | 1940..1948 |
| 15 | 511..514 | 0 | 0009 | 1949..1954 |
| 16 | 521..522 | 0 | 0015 | 1955..195A |
| 17 | 524..524 | 0 | 001B | 195B..195D |
| 18 | 551..558 | 0 | 0000 | 1940..1957 |
| 19 | 571..573 | 0 | 0018 | 1958..1960 |
| 20 | 581..590 | 0 | 0021 | 1961..197E |
| 21 | 601..602 | 0 | 00A5 | 19E5..19EA |
| 22 | 651..685 | 1 | 0000 | 1B40..1BA8 |
| 23 | 701..735 | 1 | 0069 | 1BA9..1C11 |
| 24 | 751..785 | 1 | 00D2 | 1C12..1C7A |
| 25 | 801..807 | 1 | 013B | 1C7B..1C8F |
| 26 | 10..16 | 1 | 019E | 1CDE..1CF2 |
| 27 | 811..873 | 0 | 0000 | 1940..19FC |
| 28 | 874..936 | 1 | 0000 | 1B40..1BFC |
| 29 | 937..999 | 2 | 0000 | 1D40..1DFC |
| 30 | 451..485 | 3 | 0000 | 1F40..1FA8 |
| 31 | 61..95 | 4 | 0000 | 2140..21A8 |
| 32 | 611..638 | 4 | 0069 | 21A9..21FC |

Selectors120 and589 both map to triple1979..197B. The DHW-pump import reads197B, but the meaning of an alias still depends on category. The heating-pump staged byte1CB0 is outside every range in this table; SET79 has a separate direct staging route. This proves a finite table gap, not global D-path absence.

See settings-d-events.md and settings-apply-order.md for state gates, application timing and remaining peer dependencies.
