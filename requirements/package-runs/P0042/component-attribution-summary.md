# P0042 component attribution summary

Status: PASS
1. UTC remains primary storage/join truth.
2. Fixed-CET model calendar fields were added.
3. AI-1 and AI-2 targets are built on fixed-CET model days by default.
4. Fixed-CET removed DST-caused skipped center dates: P0041 DST skips=56, P0042 skipped=6.
5. Summer holiday boundaries have a one civil-hour tradeoff versus Europe/Stockholm.
6. area_diff scale issues corrected with floor=0.105683.
7. Corrected dataset is ready for P0043 AI-2 training.
No AI training, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
