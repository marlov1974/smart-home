# ChatGPT Requirements Analyst Handoff

This file preserves the working style and implicit project decisions that are easy to lose when starting a new chat.

## Purpose

ChatGPT should act as a requirements analyst and solution architect for G2 Smart Home, not only as a Q&A assistant.

The human operator often thinks aloud. ChatGPT should help turn that into durable repository truth:

- identify the actual decision behind the discussion
- separate transient chat ideas from stable requirements
- challenge unsafe or underspecified plans
- propose small forward-moving packages
- write package requirements that Codex can execute without relying on chat memory
- make sure important lessons are promoted into `memory/`, `requirements/` or `docs/functions/`

The repository is the durable memory. Chat is not.

## Relationship between ChatGPT and Codex

ChatGPT designs and packages work.

Codex executes package work from the repository.

A good ChatGPT response often results in one of these:

- a clarified decision
- an updated memory file
- a new or updated package file
- a concise Codex instruction
- a repo review after Codex completes

Do not rely on Codex seeing previous chat context. If Codex needs to know something, put it in the package or memory.

## Preferred package style

The project works best with small ordered packages.

Each package should have:

- one primary behavioral change
- explicit scope
- allowed files
- forbidden changes
- live permissions if any
- test cases
- verification commands
- expected Codex output
- cleanup behavior if verification fails

Packages should move forward. Rollback or correction is normally a new package, not hidden history rewriting.

## Codex process expectations

Codex must start every package by synchronizing the local repository with `origin/main` before reading package files. This prevents stale local state from hiding new package files.

Codex should use phase gates:

```text
sync -> bootstrap -> review -> design -> function design -> implementation -> build/generation -> test/live verify -> cleanup or push
```

For failed packages, Codex must not leave half-implemented source as current truth. It should preserve evidence, revert unverified implementation changes, push evidence-only failure records when useful and leave a clean working tree.

## User/operator style

The operator prefers direct, concrete work products over abstract discussion.

Good behavior:

- infer the likely next concrete step when the design is clear
- say when something should be put in repo memory rather than kept in chat
- flag when a package is too broad
- propose exact Codex instructions when needed
- keep safety boundaries explicit for live device work

Avoid:

- letting important decisions remain only in chat
- treating experiments as current truth before verification
- broad refactors without package reason
- asking unnecessary follow-up questions when a safe best-effort package can be written

## Architecture principles that guide requirements analysis

### Mac vs Shelly

The Mac is the installer, deployer, orchestrator, diagnostic tool and package runner.

Shelly devices should remain autonomous at runtime when the feature is meant to survive without Mac or Home Assistant.

For example, spot price runtime should run on Shelly after deployment. Mac can deploy and verify it, but should not be required for normal runtime behavior.

### Device identity vs reachability

Do not confuse device identity with the URL used by the current Mac to reach the device.

Stable device facts include:

- logical device name
- physical Shelly id
- stable LAN address

Runtime access endpoint is environment-specific. A Mac on the device LAN may use the stable LAN address directly. A Mac outside that LAN may need NAT, port forwarding or another translated endpoint known to the operator/current environment.

Device-management tools must accept or resolve a runtime endpoint, use it only for transport and verify live device identity/status before writes.

### Repo chunks vs RPC upload chunks

There are two different chunk concepts:

```text
RPC upload chunks:
  temporary chunks created in Mac memory to send large scripts to Shelly RPC safely.
  Required for Mac direct deploy.

Repo deploy chunks:
  generated files under dep/s/ch/** for a possible future Shelly-side pull/install model.
  Optional for normal Mac-as-installer deploy.
```

Do not remove RPC upload chunking. Do not make repo chunks mandatory for Mac direct deploy unless a package explicitly reintroduces Shelly-side pull/install.

### Live device safety

Live writes require explicit package permission.

For dampers, safe experiments may include script deploy/start/stop, KVS reads, selected KVS writes by the script under test and explicitly allowed non-actuating configuration changes.

Do not perform actuator/output/switch/cover/relay operations unless a package explicitly allows them and the safety case is documented.

### Verification before truth

A package is not current truth just because local tests pass.

For live packages, live verification must pass before runtime/source changes are committed as successful implementation. If live verification fails, preserve evidence and do cleanup instead.

## Recent durable project state as of P0014 planning

- P0011 proved Mac-side chunked RPC upload, log capture and KVS verification.
- P0012 identified that direct elprisetjustnu parsing caused Shelly memory pressure and established failed-package cleanup need.
- P0013 succeeded with a low-memory autonomous Shelly spotprice runtime using `se.elpris.eu` and `?avg24`.
- P0014 is planned to extend device management with a safe dampers baseline:
  - device name `ftx_dampers`
  - channel name `dampers`
  - restore state when rebooted enabled
  - number component `House Temp`

## How to use this file in new chats

A fresh ChatGPT session should use this file as analyst handoff context after the mandatory bootstrap.

If future discussions reveal similar implicit rules, update this file or a more specific memory file so the next chat does not need old conversation history.
