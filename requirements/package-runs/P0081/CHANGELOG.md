# P0081 changelog

Status: complete — authorized VP1 installation and all 720 physical mapping observations verified.

Changed common CN105 arbiter and Modbus dispatcher, added bounded asynchronous RAW GET API600, mapper CLI, native/ARM/Python regressions and RAW_API documentation. P0072/300 control, P0080 BL2/layout/mode preserved. Exact artifact71b30837;2065 OTA cuts and full host/ARM verification pass.

Portable source commit7f7ca23285c5f5c4ca5c1a4d9cb84549f14dfc1d in procon-melcobems-mini-a1m. No site data exported. G2 retains preexisting authorized P0080 working changes; no unrelated commit/push. Read implementation-report.md, RAW_API.md and scan-plan.md for continuation. Do not treat mock code map as hardware support.

VP1 installed by OTA after explicit approval; VP2 retains its prior build. Shelly was changed to native Modbus client and rebooted as required by the configuration response. Ten of ten baseline reads passed. Both pumps remain in native curve operation; no heating-control writes in the mapping run.

Host follow-up preserves request intent and terminal data across a following health-check failure. Added complete 104-code manual metadata with display units, historical flags and unverified wire scaling; seven mapper tests pass. Firmware is unchanged by these host improvements; the physical runner uses the earlier host version and its records are enriched offline.

Repository file index updated for P0081 paths (787 paths at this stage). Created knowhow promotion `memory/knowhow/procon-async-mapping.md` for asynchronous acceptance versus completion, Shelly restart handling, evidence preservation and interpretation limits.

Final result: 512 direct and 208 A3 observations, two per code; zero communication errors and no status-classification differences between passes. Both pumps verified in native curve operation with idle control state. Full raw evidence remains private; sanitized map is in command-map.md.

Final standalone source/report commit: `76a4bd6a5c87b5cbc40cea521ac477c45b7a083b`. Expected-head update and source/report readback verified. Standalone file index now contains 189 paths.
