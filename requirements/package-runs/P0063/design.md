# P0063 Implementation Design

## Package Interpretation

Deploy the current G2 FTX state runtime to the live dampers device so the existing source guard takes effect in Home Assistant.

## Implementation Structure

- Extend `src.mac.tools.shelly_live.core` with a narrow FTX state deploy path.
- Build the state script from the imported G1-style recipe by mapping recipe chunk paths from `rt/...` to `src/shelly/ftx/...`.
- Reuse existing Shelly RPC helpers for identity verification, script lookup, chunked upload, script start and debug log capture.
- Add verification helpers for `Number.GetStatus?id=202` and FTX state KVS keys.

## Intended Changes

- Add `state_v1_8_0` to allowed live-write script names.
- Add `deploy-ftx-state` CLI command.
- Add unit tests for recipe build mapping, guard presence and deploy RPC sequence.

## Test Strategy

- Focused unit tests for `tests.mac.tools.shelly_live.test_core`.
- Focused FTX state source test for `tests.mac.shelly_ftx.test_vvx_efficiency`.
- Live verification against dampers after upload/start.

## Risks

- `state_v1_8_0` writes FTX aggregate KVS and virtual numbers by design. This package explicitly allows those state writes.
- If live input telemetry has `vvx=1` at verification time, `Number 202` may correctly become non-zero. Current live precheck shows `vvx=0`, so verification is expected to prove zeroing.
