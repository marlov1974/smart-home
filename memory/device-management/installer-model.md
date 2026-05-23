# Installer Model

The G2 Shelly installer converges a physical Shelly device to the desired state for its logical device.

The installer is not runtime control logic. It only owns setup, deployment, configuration and verification.

## Desired state source

Desired state is stored in GitHub deploy artifacts:

```text
dep/s/reg/d.json
dep/s/dev/<logical>/...
dep/s/rec/...
dep/s/ch/...
```

Shelly devices fetch deploy artifacts from `dep/s/` only.

## Installer flow

```text
1. Read own Shelly device id.
2. Fetch dep/s/reg/d.json.
3. Look up own id -> logical device + target version.
4. Read local installer text component.
5. If local verified version equals target version: stop/OK.
6. Fetch dep/s/dev/<logical>/i.json.
7. Verify registry logical/target match i.json logical/target.
8. Fetch requested part files.
9. Apply desired state idempotently.
10. Verify/read back where required.
11. Write local verified version as the final step.
12. Start runtime if allowed.
13. Stop installer.
```

## Missing registry entry

If the installer cannot find its physical Shelly id in the registry, it must stop without changing scripts, components, KVS, config or actuators.

This prevents unknown/new hardware from adopting a role by accident.

## Idempotent apply

Installer operations should be safe to repeat.

Examples:

- ensure component exists
- set component/config to desired value again if needed
- ensure script slot/name/config exists
- upload script when missing or wrong
- write KVS bootstrap if missing

## Local state is written last

The local installer text component must be updated only after all desired state parts for the device have been applied and verified.

If target version is 49 and local state is 48:

```text
Before install:  local = 48
During install:  local = 48
On failure:      local = 48
On success:      local = 49
```

Therefore a failed install never marks the device as updated.

## KVS policy

KVS is not installer truth.

KVS may be used for:

- runtime/cache state
- bootstrap keys
- diagnostics

Installer must tolerate missing KVS after reboot by recreating desired KVS keys or letting runtime recreate them.

## Components and config

Components and config may be applied idempotently.

For simple stable settings, installer may set them again rather than performing a complicated diff.

For risky settings, the relevant device part must explicitly allow the installer to change them.

Examples of risky settings:

- Wi-Fi/network
- cloud
- MQTT
- security/enhanced security
- authentication

## Runtime activation

Runtime activation is separate from installation.

Installer may start boot/master only if the device safety/config allows it.

Installer must not change actuators unless the package and device safety policy explicitly permit that.
