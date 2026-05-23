# Shelly Deploy Structure

Shelly deploy artifacts live under:

```text
dep/s/
```

Shelly devices fetch from `dep/s/` only.

## Structure

```text
dep/s/
  reg/
    d.json

  dev/
    <logical>/
      i.json
      scr.json
      cmp.json
      cfg.json
      kvs.json
      safe.json

  rec/
    <role>.json

  ch/
    <role>/
      01.js
      02.js
      03.js
```

## Registry

```text
dep/s/reg/d.json
```

Maps physical Shelly id to logical device and target version.

```json
{"v":1,"d":{"8813bfdaa0c0":["ftx-main",49]}}
```

## Device entrypoint

```text
dep/s/dev/<logical>/i.json
```

Example:

```json
{
  "v": 1,
  "l": "ftx-main",
  "p": 49,
  "m": "pro1pm",
  "parts": ["scr", "cmp", "cfg", "kvs", "safe"]
}
```

Fields:

```text
v      schema
l      logical device name
p      target version for this device
m      expected model/model-class
parts  part files installer should fetch/apply
```

## Scripts part

```text
dep/s/dev/<logical>/scr.json
```

Example:

```json
{
  "v": 1,
  "s": [
    {"id":1,"r":"installer","n":"installer_v49","rec":"installer","boot":false},
    {"id":2,"r":"boot","n":"boot_v49","rec":"boot","boot":true},
    {"id":3,"r":"master","n":"master_v49","rec":"master","boot":false},
    {"id":7,"r":"brain","n":"brain_v49","rec":"brain","boot":false}
  ]
}
```

Fields:

```text
id    fixed Shelly script id
r     role
n     script name, including version
rec   recipe name under dep/s/rec/
boot  script enable/autostart config
```

## Recipe

```text
dep/s/rec/<role>.json
```

Recipe contains only the chunk count.

Example:

```json
{"v":1,"n":3}
```

Installer derives chunk paths by convention:

```text
dep/s/ch/<role>/01.js
dep/s/ch/<role>/02.js
dep/s/ch/<role>/03.js
```

## Chunks

Deploy chunks are numeric size-based transport chunks.

They do not encode logical architecture.

```text
dep/s/ch/brain/01.js
dep/s/ch/brain/02.js
dep/s/ch/brain/03.js
```

Chunks are generated from the built complete script.

## Components part

```text
dep/s/dev/<logical>/cmp.json
```

Example:

```json
{
  "v": 1,
  "c": [
    {"t":"text","id":200,"n":"g2.i","p":true,"d":"1|0"},
    {"t":"number","id":201,"n":"g2.flow.sup","p":true,"d":0,"min":0,"max":300,"u":"l/s"},
    {"t":"boolean","id":200,"n":"g2.healthy","p":true,"d":false}
  ]
}
```

Fields:

```text
t    component type
id   component id
n    component name
p    persisted
d    default value
u    unit
```

## Config part

```text
dep/s/dev/<logical>/cfg.json
```

Example:

```json
{
  "v": 1,
  "name": "ftx-main",
  "note": "g2:ftx-main",
  "tz": "Europe/Stockholm",
  "allow": {
    "name": true,
    "note": true,
    "timezone": true,
    "cloud": false,
    "mqtt": false,
    "wifi": false
  }
}
```

`allow` defines what installer may change.

## KVS part

```text
dep/s/dev/<logical>/kvs.json
```

Example:

```json
{
  "v": 1,
  "keys": [
    {"k":"g2.mode","val":{"mode":"STD"}},
    {"k":"g2.runtime.flags","val":{"driver_inhibit":0}}
  ]
}
```

KVS is runtime/cache/bootstrap state, not installer truth.

## Safety part

```text
dep/s/dev/<logical>/safe.json
```

Example:

```json
{
  "v": 1,
  "installer_id": 1,
  "boot_id": 2,
  "master_id": 3,
  "state_text": 200,
  "stop_runtime_before_install": true,
  "start_after_install": true,
  "never_delete": [1],
  "max_script_size": 24000,
  "put_wait_ms": 120
}
```

Safety owns recovery and activation constraints for the installer.

## Key rules

- Paths under `dep/s/` should remain short.
- Registry is the first file every installer fetches.
- Device entrypoint is `dep/s/dev/<logical>/i.json`.
- Registry target and entrypoint target must match.
- Installer writes local version only after successful convergence.
- KVS loss must not break installer recovery.
