# Package P0016 Debug Attempts

## Package

`P0016`

## Attempt limit

Default/package limit: 3

## Attempt 1

### Change summary

- Added `src/shelly/supply_uni/supply_uni_pub.js`.
- Added `src/shelly/supply_uni/supply_uni_refresh.js`.
- Added `src/shelly/supply_uni/manifest.json`.
- Extended Mac live tooling for P0016 deployment and verification.
- Added unit tests and durable function catalog docs.
- Generated build/deploy artifacts.

### Tests run

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/supply_uni/manifest.json --build-root build/shelly/supply_uni --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/supply_uni --dep-root dep/s --role supply_uni_pub
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/supply_uni --dep-root dep/s --role supply_uni_refresh
git diff --check
python3 -m src.mac.tools.shelly_live deploy-supply-uni --supply-base-url http://192.168.86.240:8020/ --dampers-base-url http://192.168.86.240:8030/ --publisher-script build/shelly/supply_uni/supply_uni_pub.js --refresher-script build/shelly/supply_uni/supply_uni_refresh.js --log-timeout 30 --kvs-timeout 30 --http-timeout 5
```

### Output/state result

PASS.

- Unit tests passed: 58 tests.
- Build generated both scripts.
- Build validation passed for both roles.
- Final live supply identity: `shellyplusuni-e08cfe8c1d18`.
- Final live dampers identity: `shellypro1pm-8813bfd99f54`.
- `supply_uni_pub` upload chunk count: 3.
- `supply_uni_refresh` upload chunk count: 2.
- `tele.supply_uni` readback passed contract validation.
- Final scripts: `supply_uni_pub` running, `supply_uni_refresh` stopped.

### Log/runtime observations

See `logs/live-supply-uni.md`.

No `out_of_memory`, actuator/output, device-config or forbidden operation evidence observed.

### Result

PASS.

### Next action

Finalize evidence, update memory for verified supply UNI id, commit and push.

## Final status

Done.

## Remaining uncertainty

- P0016 does not implement hourly scheduling for `supply_uni_refresh`; that remains future production scheduling work.
- `supply_uni_pub` is left running as a pre-production proof artifact, not production activation.
