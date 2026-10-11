# Actuator coordination: partial graph

Confirmed local states below are numeric firmware states. Names such as “running” are not assigned solely from their number. Missing transitions remain explicit UNKNOWN.

`caller request -> AF400 selected step -> optional AF452 correction ->3A33 ->B1AF0 PWM ->B1B9C timer032A ->GET15 observation`.

AF400 request0/other gives step0; request2 gives3; request1 selects0770 only in phases9/10 with3D07!=2 and3A02!=2, otherwise07E6. After selection, **only request1 AND3AD2=2** invokesAF452. For49C7=2..7 it writes `max(2, selected_step-(49C7-2))`; other49C7 values leave the step unchanged. Its floor must not be applied when the pump is off. The49C7 producer and exact Water flow control menu correspondence remain UNKNOWN; a lower observed flow alone does not prove this branch was active.

P83's B1AF0 step1/2/3/4 yields PWM52/41/31/20; default0 includes step5. Off pathB1B8A gives100. These are command representations, not measuredRPM or a linear speed law. GET15 run3A34, commandedPWM3A38 and feedback3E9D should be compared separately.

| Initiating branch | FTC action | Observation / next stage | Stop/timeout qualification |
|---|---|---|---|
| AECA4 ordinary phases7/8/11/12/13 | Request1 before later overrides; clears local timers | Applies0977 routing to3A31/3A32,AF400,AEC0A,AF330 | Raw timer check<300 can suppress;3A02/3D07/3ED2 override; units UNKNOWN |
| AECA4 DHW9/10 | AF240 selects request | Same final routing; AF400 may select storedDHW step | DHW completion/valve settlement unresolved |
| AECA4 phase6 or heating with3A4A=4 and3F6D!=1 | AF12E and timer-dependent path | Pump may continue independently of compressor | Not proven universal overrun duration |
| AEE84 alternative pump path | AF1D8 if state condition fails, otherwise request1 | Same routing/AF400; alarms/special states override | Timer<300 and3ED2>2 can suppress; not blindly “300seconds” |
| A13A6/A13C4 compressor-related status | Assigns3A2C from peer05DB or timed/gated branch | A162A also constructs39C3 operation/inhibit request | No complete start/stop acknowledgment contract established |
| AC79A state0→1→2→0 | Clears/starts/resumes83BCA as cataloged | Caller output70 in2,100 otherwise | Not yet mapped to compressor thermostat |
| Brine pump | P83 forwarded service18/19 reports step/RPM | Other-controller boundary | No local independent speed-control law established |
| Three-way valve, zone/sanitary pumps, booster/immersion | Separate actuators, not aliases for3A33 | Native priority affects selected phase and target | Exact lead/lag, transitions and safety graph UNKNOWN |

A162A composes operation/inhibit39C3 from numerous guards (3D12/3D0D/3D24,3A4A,3D94/96/97/98/99,board and fault paths). Its value is not a rawHz. The excerpted B2700 threshold involves3A4A; until B4674's full ownership and subsequent requests are qualified, calling it the fixed-flow thermostat would overstate the evidence.

The executable model covers pump *selection/correction* and generic timer word transitions, not the entire above scheduler. No assumptions that brine follows water pump, both stop together, or valve travel completes immediately enter the model. OFF, pre-circulation, startup, minimum capacity, thermostat-off, overrun and restart remain proposed observation labels until bound to predicates.
