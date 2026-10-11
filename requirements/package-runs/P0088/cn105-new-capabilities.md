# CN105 delta against P81 and current Procon

P81 covered zero-parameter GET42 and104 allowed A3 selectors on21.00. It did not cover all frame families or complete settings transactions. Findings below are supplied20.01 unless explicitly historical.

| Benefit / finding | Exact route | Baseline and qualification |
|---|---|---|
|Explain the old1E/1F zero replies|GET42/1E→A5FF6 stores p1..14 fromA4CD2;1F→A6068 storesp1..12;A4CD2 returns0|New operand proof of explicit zero fields, not a brine sensor mapping; no universal21.00 claim|
|Read about/configurationC9|FC5B,C9→A5148→A8F8A; connected02/7A gate|Known public F1p family, missed by ordinary42/C9 scan. Procon normalGET cannot substitute type42|
|Additional frame families|5C/CC→A5172→A8FF8 (CC,FF);5D/CC→A519C→A900E (CC);02/00 and02/01 descriptors|New explicit enumeration. Their existence is not a useful control claim; final native effects and alternate frame schema remain open|
|Configured DHW/heating pump levels|GET65 p10 from0770;GET79 p7 from07E6 viaCFB18|P81FF now explained by category/session guards. These are configured levels, not instantaneous speed or flow|
|Pump and neighboring setting writes|SET65/79 through A90F8 to staging1973..197B/1CAB..1CB6;BD166 phase6 import|P84/P86 qualified stores reused. Full transaction/rollback/persistence still missing; no ready-to-send packet|
|Settings categories rather than blanket unsupported flags|SETC8 directionp1/actionp2/maskp3; matching categoryp15;47 recognized settings blocks50..7E|Complete bounded route inventory; categories1..7 must not be confused with literalmask values. P88 binds1002 andCF978 to D events; generator of that peer sequence remains unresolved (settings-d-events.md)|
|Service return formats beyond Procon numeric1/2|A3 selectorBE16, formatp3, valuep4/5|P81 had legitimate3/4 replies; format6 can mean busy/guard/timeout. Not all formats are implemented in production|
|Energy details and counter behavior|GET07 BE16 fields3/5/11; A3 520..531|Power units not calibrated; even A3 queries fold accounting with remainder loss;532 clears original counters. Not a generic read-only polling list|
|Actual versus requested compressor/brine feedback|A3 17/18/19/27/28/52 forwarded via class1|Already partly in Procon. Complete source-board frequency law is absent from this FTC-local dispatcher|

Public baseline pinned in P83: F1p Process0xC9 is selected by GET_ABOUT_RESPONSE, while ordinary GET_RESPONSE lists01..29/A1/A2/A3. Merely naming a GET in public code is weaker than interpreting all its bytes. The current Procon `cn105.c` uses fast codes04/0C/14/0B/09/15/26/28,41 controls32/34 and an exclusive A3 service owner; API600 extends zero-filledGET and an allowlist, not arbitrary sessions/frames. No baseline production code was changed.

The complete256-slot SET and256-slot GET lookups include defaults and rejected slots in command-atlas. This is exhaustive for those two lookup tables only. Nested settings field semantics, peer-owned actions and02-family effects prevent calling CN105's total feature set complete.

A3 continuation: the current ten-attempt budget includes legitimate format0 pending replies. Same forwarded selector normally polls the cached job. A future production change should separate pending polls from communication errors and qualify same-selector rearming. Details and native cancellation path: a3-job-lifecycle.md. Internal1005 announces settings requests to a peer, while D tag1/selector0 feeds CF978; neither closes the full external transaction.

Application-order qualification: accepted C8 action1 in write state3 schedules the category import within the same native loop, before the state4 end acknowledgment. Do not use a later error/timeout as evidence that settings were untouched. The D extended mapping is narrower than all CN105-staged fields; in particular it does not include1CB0 even though SET79 directly stages that heating-pump byte.
