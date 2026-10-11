# P0086 — CN105 settings session

Analytical **PARTIAL**; executable physical read/close and apply **BLOCKED**, physical **NOT RUN**. Static 20.01 addresses; see verification.json/evidence.json. External21.00 transaction is not claimed complete. The missing internal acknowledgment is a specific blocker, not an invented default transition.

## Wire fields and response

CONFIRMED: SET C8 maps to internal34. CF758 reads direction payload1 into4980 (0=write branch,1=read branch); CF75C reads action payload2 (0..3); CF760 reads category mask payload3 into497F; CF7C8 chooses its first set bit as category1..7 into4981. Category6 corresponds to mask20h, not literal6. CF832 compares category with payload15 of settings commands. CF704 is the eligibility gate; accepted fields alone do not establish the internal service state. A8F74 calls CF9C4 and places its result in reply C8 payload1. Zero means this state/action is accepted;1 means busy;FF means mismatch/rejection, not an applied setting.

## State transition inventory

2372 is the session state. Each row is subordinate to global CF518/CEECE aborts and direction/category guards. SET/GET parsing also changes4982–4985; they are not immutable reads.

| State / function | Progress condition | Next |
|---|---|---|
|0 / CEF86|eligible C8 action0, save direction/mask/category|1|
|1 / CEFA8|internal service1002, low050D=0 with direction0|2|
|1 / CEFA8|internal service1002, low050D=2 with direction1|7|
|2 / CF04C|recognized settings command, category match; A90F8 stages data|3|
|3 / CF0E0|C8 action1, CF846 selects import phase|4|
|4 / CF118|CF978:4987=1 and3248=0|5|
|5 / CF1A4|C8 action2; matching restage instead returns3|6|
|6 / CF228|internal1002 low050D=1|12|
|7 / CF28A|GET callback sets4983=1|8|
|8 / CF306|CF978 internal acknowledgment|9|
|9 / CF31C|C8 action1|10|
|10 / CF3C8|GET sets4983=1 returns8; C8 action2|11|
|11 / CF43A|internal1002 low050D=3|12|
|12 / CF494|response callback4982=1|0|

CFB18 sets4985=1 and clears4983 before evaluation; category mismatch sets4983=FF and returnsFF. States7/8/10 return1 while setting4983=1; state9 returns0 and sets4983=1. All other states returnFF. Therefore an attempted GET can advance or abort a session. Level5 is only an operator comparison point; an FF reply followed by zeros is not level0.

CF9C4 reply table: state0 accepts action2/3; state1 busy; states2/3/4/7/8/9 accept action0; states5/10 accept0/1, with action1 setting4982=2; states6/11 accept0/1; state12 accepts0/1/2 and action2 sets4982=1. Other combinations return1 orFF according to guard. A bad direction returnsFF/4982=FF. No generic success→next-state shortcut is valid.

CF518 resets to0 for eligible action3, direction mismatch, link/control guard failure or expired descriptors840CE/840C2/840D4. CEECE adds link/global reset gates. Timers are firmware descriptor ticks; their wall-clock values are not qualified. Host tests use explicit finite simulated deadlines (not claimed firmware seconds). CF660 clears transient flags at the end of each task pass. 0414 is split by CEEA8 into3248/4987; 8BD02 moves service1002-related data through shared D state. A transport acknowledgment does not prove CF978, nor persistence. No wire-only method to observe all these internal states is qualified on21.00.

## Whole staged blocks

CONFIRMED A90F8 subbranches (payload index0 is selector):

| Setter | Payload→staging | Forced defaults |
|---|---|---|
|65 atAACA5|2→1973;4→1975;5→1976;7→1978;8→1979;10→197B|1974,1977,197A=0|
|79 atABA09|2→1CAB;3→1CAC;4→1CAD;5→1CAE;7→1CB0;8→1CB1;10→1CB3;11→1CB4;13→1CB6|1CAF,1CB2,1CB5=0|

BD166 phase6 calls broader imports, not just these bytes. BD296:1975 converts viaC514A to077D,1978→077F,197B directly→0770. BD780:1CAC/1CAD→07E5,1CB0→07E6,1CB3→07E7,1CB6→07E8; many other staged settings are imported in the same phase. Pump bytes have no local1..5 clamp. Defaults/validation for the whole import and persistence after restart are NOT fully qualified. Copying a16-byte GET response verbatim into SET would be unsafe: status/selector layout and fields are not guaranteed identical.

GET65 A7D48 payload10 reads0770, GET79 A8BCC payload7 reads07E6 behind CFB18. settings.py preserves full16-byte captures and produces only an offline single-byte diff. That diff is **not a valid SET packet**. apply() always raises with the missing block/rollback qualification.

## Two handoffs

B-read: snapshot native mode/targets and session baseline; open direction1/category6; establish internal1002 and CF978 progression; capture successful GET65/79 raw blocks; request close; independently verify state0 and unchanged prior control. No applying action or guessed ACK progression. Currently blocked at external choreography/internal-ack observation and verified close after link failure.

B-write: only after B-read and complete neighboring-field, persistence and recovery proof. One unit, one operating mode, snapshot all affected blocks;5→4; verify configured level, independent PWM and actual flow; restore5 and all neighbors; verify after closure and a separately approved restart if persistence is involved. No promised L/min, no zero-filled neighbors. Link-loss rollback remains UNKNOWN, so no live candidate is executable.

Tests exercise an **observer contract with explicit synthetic internal events**, not an emulator of the entire FTC state machine. Missing events, wrong state/category, bad reply or deadline prevent success; read/close synthetic success requires an explicit prior-state restoration observation.
