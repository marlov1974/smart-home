# P0074 function design

New tests/test_platform_spec.py: independent CRC16 and additive checksum functions consume golden-vector JSON, validate response/no-response cases, platform invariants and Markdown local links. Output PASS or assertion failure; filesystem reads only, no firmware imports or network. Add invocation to existing Makefile test/host-test targets so CI covers the documentation contract. No firmware functions change. Document checker in the private function catalog.
