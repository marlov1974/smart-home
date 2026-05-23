# Device Management Memory Index

Device management is the G2 model for making Shelly devices converge to desired configuration.

It covers:

- physical-to-logical device lookup
- device replacement
- installer responsibilities
- local installer state
- deploy file structure
- source/build/deploy layers
- Shelly component/config/script/KVS handling

## Files

```text
identity-and-registry.md       physical id -> logical device lookup
installer-model.md             installer responsibilities and flow
local-state.md                 one-component local verified-version model
shelly-deploy-structure.md     dep/s layout and file semantics
source-build-deploy-layers.md  src -> build -> dep/s three-layer model
mac-layer.md                   Mac tools/services as first-class G2 code
```

## Core decisions

- Stable identity is logical device name.
- Physical Shelly device id is replaceable.
- `dep/s/reg/d.json` maps physical device id to logical device and device target version.
- A Shelly device stores only a minimal verified device target version locally.
- KVS is not installer truth.
- Shelly source architecture and Shelly deploy chunk architecture are separate.
- Deploy chunks are generated numeric byte-size chunks.

## Package history

Created by `P0006-device-management-and-deploy-architecture`.
