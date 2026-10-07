# P0072 r2 first physical control test — blocked before SET

2026-10-07 09:35–09:39 UTC. Operator confirmed flash. Identity 888/72, revision tuple 2/1/3, initial control IDLE. One hardware attempt (1/3). No firmware modification or flash during this test.

Atomic FC16 offset300 words [49266,1,2,3800,0,90,1,2] accepted. State QUEUED then IDLE, error3, accepted1/applied0, snapshot-valid0, touched0, ack0, readbacks3, restores0. Last parsed configuration: power1, Zone1 mode2, flow target2850, DHW target5200, boost0. No CN105 SET was reached: code returns from the snapshot gate before apply_plan. AUTO was not sent because no saved session or changed fields existed.

Source path proves the failed gate is GET28 bytes4–10: GET26 and GET09 parsed successfully and GET28 boost0 was parsed, then snapshot failed. Reference maps these bytes to holiday, DHW/heating/cooling prohibits in zones1/2 and server control. Firmware rejects any nonzero byte; it does not retain/expose these raw bytes, so the particular flag and whether it is relevant to Zone1 heating cannot yet be identified. Do not assume an active heating safety fault or bypass the gate. Next firmware improvement should expose raw GET28/rejection byte and assess only documented operation-relevant preconditions without changing native prohibits.

Post-test readings: curve target28.5 C, flow30 C, return28 C, compressor0 Hz, brine13/13 C. FAST and A3 sample generations continue increasing; no protocol/UART errors observed in post-test identity blocks. Some multi-block samples correctly report null when generations change during acquisition, not communication failure.

Short control validation failed safely. Explicit AUTO restoration, lease-expiry restoration and the requested15-minute38 C experiment were NOT performed. No heating result or physical SET correctness is claimed. Original running state was not altered by the command path.

RPC method verified from https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/MbRtuClient/ : WriteHoldingRegisters is FC16 and uses id/sid/addr/values. Logs retain requests, replies and timestamped telemetry. The harness is archived as executed, with workstation-specific import path; not a portable unattended controller.
