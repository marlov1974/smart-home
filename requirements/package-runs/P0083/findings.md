# P0083 results

**Completed offline research; A PARTIAL, B PARTIAL, C PARTIAL.** No live device traffic or firmware installation.

1. Service requests use a classifier before the local dispatcher. Common brine/compressor selectors follow a forwarded path, so absence from the local switch is not evidence of unsupported requests. Response format codes are not universal success/error flags.
2. Two independent water-pump setting candidates (DHW 0770, heating 07E6) feed selected step 3A33. Valid steps 1–5 map to PWM values 52/41/31/20/0; off maps to 100. GET15 exposes status and PWM. GET65/79 expose settings behind an access gate, explaining why FF captures cannot be interpreted as level zero.
3. Six running energy banks exist, with A3 selectors 520–531 returning split BCD fields. A1/A2 use a separate dated snapshot bank. Service **532 copies and clears** running banks. The accounting boundary and precise timing remain unresolved; do not label the running banks “today” yet.
4. The M16C module required direct-flow and immediate word-rotation repairs. Eleven decoding checks and twenty rotation emulation cases pass. Two exports of the qualified project are byte-identical across 366 files.

See [service](service-trace.md), [pump](pump-control-trace.md), [energy](energy-trace.md), [verification](verification.json), [reproduction](reproduce.md), and [remaining questions](open-questions.md). Every address is tied to the supplied image in [provenance](provenance.md), not installed FTC21.00.
