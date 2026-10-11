# P0082 function design

- parse_srec: validate lengths/checksums/types/overlaps and return address-byte map; reject malformed input.
- inspect_image: derive sparse regions, gaps, hashes, vector candidates and setting string addresses without assigning semantics.
- headless audit: validate synthetic instruction vectors, seed verified candidate reset targets and export local instruction/function/reference evidence.
- tests: malformed checksum/count/overlap, S2 addresses and synthetic M16C opcode vectors.

- extract_service_map: derives address-only comparisons from local listing; constrained to the identified function and exact instruction patterns.
- run-analysis.sh: hash-gated invocation; outputs outside the public repo.
- Graph completion uses documented direct opcode edges and a verified descriptor-table layout; no third-party SLEIGH changes retained.
