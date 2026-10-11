# P0089 provenance

Repo base07a89d7; P88 reference4934a0e. Exact source and local public-reference hashes are in provenance.json. Public pins inherited from P83: F1p7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5 and gekkekoe829754a334df5050a1ffb58557b45d28fa2de231. Files already held locally; no moving-main comparison or new public labels assumed firmware proof.

FTC20.01 binary SHA256d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a, base80000,size80000hex. Isolated copies of P88 bits-fixed and bits-fixed-repeat; Ghidra12.1.4, repaired m16c:LE:16:p88-bits. No shared processor or P88 project edits.45 targeted assembly exports match; evidence.json pins them and four ROM tables. Same decoder in both projects is reproducibility, not independent ISA validation. EXITD and hidden-stack-argument limitations remain; critical branches were checked in assembly. A4601 includes a leadingNOP before dormantA4602; no caller was located, so it proves neither a usable setter nor global absence.

GET0B rounding follows A4D5E stack operands, A4CDC signed32 division and D4704 sign normalization / unsigned division / sign restore. For positive divisor50 this truncates toward zero; A4D00 then clamps0..255. Existing P88 helper exports support the intermediary and remain immutable.

OCH722A and prior P83/P88 manual findings are contextual only in this batch. No new installer-menu labels or operating ranges have been inferred from the manual without a field binding. Installed21.00 and historical P81 captures are not new physical verification. No hardware activity.
