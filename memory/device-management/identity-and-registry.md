# Device Identity and Registry

## Identity levels

G2 separates physical device identity from logical device identity and human/device-facing labels.

```text
Physical identity:
  Shelly device id, MAC, model, IP, NAT URL.

Logical identity:
  stable role/name in the G2 solution.

Shelly device name:
  device-local human-facing name configured on the Shelly.

Channel name:
  human-facing name for a Shelly output/input/channel.
```

Examples of logical devices:

```text
ftx-main
ftx-air
ftx-water
plant-main
floor-main
vvb-vvc
vp-io
```

## Stable identity

The stable key is the logical device name.

A physical Shelly device can be replaced. The logical device should survive replacement.

```text
Good:
  ftx-main

Replaceable:
  8813bfdaa0c0
  192.168.77.40
  hardware model, within compatibility limits
```

## Naming standard

G2 uses different names for different layers. Do not collapse them into one field.

Suggested standard:

```text
logical device name:
  kebab-case, stable G2 role, e.g. ftx-dampers

Shelly device name:
  human/local device label. Prefer a clear variant of the logical device name.
  Existing packages may test exact Shelly display names before the standard is finalized.

Shelly channel name:
  short human-facing channel label, e.g. dampers

physical Shelly id:
  lowercase hardware id, e.g. 8813bfd99f54

runtime endpoint:
  current Mac/operator access URL, not durable identity
```

For P0014, the deliberate test is:

```text
logical device / infrastructure role: ftx-dampers
physical Shelly id: 8813bfd99f54
stable LAN address: 192.168.77.30
Shelly device name to test: ftx_dampers
Shelly channel name to test: dampers
```

This P0014 underscore device name is a live device-management test, not a final naming standard for all G2 devices. If the test proves the API behavior, a later package should decide whether Shelly device names should use `ftx-dampers`, `ftx_dampers` or another consistent display convention.

P0014 verified the live dampers baseline on `shellypro1pm-8813bfd99f54`:

```text
Shelly device name: ftx_dampers
Shelly switch:0 channel name: dampers
Switch restore output after reboot setting: initial_state = restore_last
Virtual number component: number:200 / House Temp
House Temp config: min 10, max 30, default 21, persisted true, UI unit C, step 0.1
```

`House Temp` is a non-actuating G2 device-management proof and is not a production control input until a later package explicitly makes it one.

## Global registry

Every Shelly installer starts from:

```text
dep/s/reg/d.json
```

The registry maps physical Shelly id to logical device and device target version.

Compact format:

```json
{
  "v": 1,
  "d": {
    "8813bfdaa0c0": ["ftx-main", 49],
    "a1b2c3d4e5f6": ["ftx-air", 22],
    "51641545ab453": ["plant-main", 31]
  }
}
```

Fields:

```text
v          registry schema version
d          device map
key        physical Shelly id
value[0]   logical device name
value[1]   target version for that logical device
```

## Device replacement

To replace broken hardware for a logical device, update only the registry mapping to point the new physical Shelly id to the existing logical name and target version.

Before:

```json
{"8813bfdaa0c0":["ftx-main",49]}
```

After:

```json
{"newdeviceid":["ftx-main",49]}
```

The desired-state files remain under:

```text
dep/s/dev/ftx-main/
```

## Version meaning

Registry target version is per logical device, not global latest package.

If latest solution package is `P0049`, only affected devices should have target `49`.

Example:

```text
ftx-main    target 49
ftx-water   target 49
plant-main  target 42
floor-main  target 37
```

## Validation rules

Mac-side validation must check:

- physical ids are unique
- each active logical device appears at most once
- logical names use allowed characters
- `dep/s/dev/<logical>/i.json` exists
- registry target matches device index target

Shelly installer should remain simpler:

- if own id is missing from registry: stop without changes
- if registry and device index disagree: stop without changes

## Device name and note

The Shelly device name should normally store the logical device name or a deliberate, documented display-name variant.

Example:

```text
Device name: ftx-main
```

Device note may be used for human/G2 sanity metadata if it is locally stable on the target firmware.

Example:

```text
g2:ftx-main
```

Device note is limited and should not be primary installer state.
