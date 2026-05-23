# Device Identity and Registry

## Identity levels

G2 separates physical device identity from logical device identity.

```text
Physical identity:
  Shelly device id, MAC, model, IP, NAT URL.

Logical identity:
  stable role/name in the G2 solution.
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

The Shelly device name should normally store the logical device name.

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
