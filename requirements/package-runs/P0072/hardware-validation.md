# P0072 hardware validation — pending

Operator alone flashes P0072-mvp-r1. Verify marker888/72/revision1 and LED; capture with read_mvp.py. Require repeated service27/28 completion, increasing GET04 count, no UART/parser regressions and plausible raw+decoded FAST values compared to physical display. Check flow/return and primary flow before treating derived W as useful. Input10/11 product brine-pump fields remain unavailable by design. No controls in r1, so no live command/fallback tests are permitted by this artifact. Current device is not changed by this build.
