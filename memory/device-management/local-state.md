# Local Installer State

G2 uses one local persistent Text component per Shelly device for installer state.

The component stores only the last verified device target version.

It does not store errors, logs, desired state, full hashes, runtime telemetry or history.

## Component

Default component:

```text
text:200
name: g2.i
```

## Value meaning

The value means:

```text
This device has successfully applied and verified its desired state up to version N.
```

Suggested compact format:

```text
1|49
```

Fields:

```text
1   local-state schema version
49  verified target version for this logical device
```

## Version scope

The local version is per logical device.

It is not necessarily the latest solution package.

Example:

```text
Latest package: P0049

Device target versions:
  ftx-main    49
  ftx-water   49
  plant-main  42
  floor-main  37
```

A device with local state `1|37` is fully updated if its registry target is also `37`.

## Write rule

The installer writes local state only after all requested parts have been applied and verified.

Failure leaves the previous verified version in place.

## Missing local state

If the component is missing, malformed or lower than target, installer should run the full desired-state convergence for that device.

If local state equals target, installer may stop quickly or perform a small sanity check.

## Why no error field

Errors belong in:

```text
requirements/package-runs/<Pxxxx>/
logs/debug output
Shelly log stream
```

The local component is intentionally not an error log.

## Why no script versions

Script versions are represented in script names and device manifests.

Example:

```text
brain_v49
driver_v49
```

Installer can verify scripts by listing script ids/names/config and by reading code when deeper verification is needed.

## Why no KVS state

KVS is not installer truth. It may disappear or be rebuilt.

The installer should recreate KVS bootstrap/runtime keys when needed and should not mark the device verified until required convergence is complete.
