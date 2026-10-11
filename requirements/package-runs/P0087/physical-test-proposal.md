# Proposed discrimination — NOT RUN

All tests below require a separate live authorization. P87 performs zero connections, GET/SET, captures, flashing or settings changes. Keep native safeties; first establish installed firmware and validated observables. Do not read the20.01 RAM addresses on21.00 by assumption.

| Unknown | Smallest useful later comparison | Required observables / result |
|---|---|---|
| Active outbound demand path | Passive simultaneous CN105 plus identified source-link capture first | Decoded selected target/error/request fields, phase, targetHz/actualHz/limit code; whether table or direct-temperature path is active |
| History vs direct response | Under stable heating, one approved+0.5C target step, then hold; repeat from a different prior deficit after recovery | Independent source timestamps, effective target, targetHz, actualHz, flow/return, flow, brine, otherVP status; compare identical error with matched conditions |
| Repeated-setpoint side effects | Compare same held target with no repeats against sparse identical repeats, within existing lease contract | ACK/readback, outbound request, native timers if qualified; distinguish refresh effects from sampling |
| Stop/restart threshold | Observe a naturally occurring approach to target and normal restart before proposing any intentional stop | Effective target minus measured flow, targetHz/actualHz, phase/permission, native timer state; bracket transitions by sample age |
| Water-flow correction | Observe stored step, commandedPWM, feedback and flow through a natural phase change | Does49C7-correlated correction occur? No pump-setting writes needed initially |
| DHW arbitration | Observe natural heating→DHW→heating | Valve feedback if available, separate pump states, permissions andHz; no inferred instantaneous valve motion |

Any later perturbation must be bounded to one pump with the other held unchanged, record prior mode/target/inhibits and restore those exact values. Stop changes on measured flow approaching the existing40C limit, invalid/aged critical feedback, a fault, unexpectedDHW priority or loss of acknowledgment; restore the prior command through the qualified controller path and verify readback. Do not override native minimum-off or protective stops. Hold/observation duration must be chosen after passive cadence measurement; no invented native ten-minute timer is a prerequisite or a bypass target.

Code-only next step: trace A162A's request39C3 and profile0900/0975 eligibility to the final peer serializer; independently trace timer tick scheduling and B4674/3A4A ownership. This is more discriminating than retuning EFFECT against an assumed PID.
