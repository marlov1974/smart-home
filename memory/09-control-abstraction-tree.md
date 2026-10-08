# Control abstraction tree

L4 is the trunk of the home's control tree. L3 is the large branches, L2 the smaller branches, L1 the physical leaves.

Higher layers specify what and when. Lower layers determine how and maintain local safety. Commands flow down; actual telemetry, capability and limitations flow up.

Heat-pump mapping:
- L1 Mitsubishi FTC/inverter: protect machinery and regulate compressor frequency, pumps and native safety.
- L2 Procon: local EFFECT regulation such as holding 9 kW for a bounded 15-minute request.
- L3 Shelly: follow the run plan and coordinate VP1 and VP2.
- L4 Mac/Home Assistant: construct and optimize run plans using demand, electricity prices, forecasts and COP.

A layer must remain safe when its parent disappears; plans and control requests have bounded validity. The native L1 protections remain authoritative. P0072's RAM-only control snapshot means power-loss restoration is not yet guaranteed.

Floor-room mapping from P0068:
- L1 deterministic autonomous local room heating/valve control.
- L2 adaptive room learner/predictor, initially shadow-only.
The tree is a functional abstraction rather than a fixed physical-device hierarchy; branches can have different depth.

P0076 concerns VP L2, P0077 L3 test-plan execution and L4 analysis, P0078 identifies L1 control behavior before tuning L2. L0-L5 operating levels for heating are a separate naming system.
