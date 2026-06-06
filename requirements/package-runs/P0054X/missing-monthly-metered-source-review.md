# P0054X missing monthly/metered source review

Status: `MISSING`

The operator flagged that the loaded P0054W data likely covers only the 15m/60m or load-profile part and that monthly-read series must also be found.

P0054X confirms the problem:

- Public eSett `EXP18` gives per-MGA load profiles.
- Public eSett `EXP15` gives MBA-level `metered/profiled/total`.
- No inspected public eSett endpoint gives `metered` or total consumption per MGA.
- No local DB table or local file/export contains a separate monthly-read or measured per-MGA source.

Required next source step:

```text
Find or obtain a source/export that maps monthly-read or measured consumption to MGA.
```

Acceptable future paths:

- operator-provided eSett/NBS export with MGA and settlement class,
- another project-approved public source contract that exposes measured/monthly-read per MGA,
- authenticated/manual source review package if credentials/access are required and explicitly approved.

Until then, use P0054W data only as `profiled_load_profile`, not as total SE3 MGA consumption.
