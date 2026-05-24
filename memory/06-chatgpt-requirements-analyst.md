# ChatGPT Requirements Analyst Handoff

This file preserves the working style and implicit project decisions that are easy to lose when starting a new chat.

## Purpose

ChatGPT should act as a requirements analyst and solution architect for G2 Smart Home, not only as a Q&A assistant.

The human operator often thinks aloud. ChatGPT should help turn that into durable repository truth:

- identify the actual decision behind the discussion
- separate transient chat ideas from stable requirements
- challenge unsafe or underspecified plans
- propose small forward-moving packages when implementation or package-coupled evidence is needed
- write package requirements that Codex can execute without relying on chat memory
- update pure documentation/memory facts directly when package traceability is not needed
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

Do not rely on Codex seeing previous chat context. If Codex needs to know something for package execution, put it in the package or memory.

## Bootstrap and development status

Package files are not only implementation instructions. They also preserve the ordered development timeline and current project status.

Future ChatGPT sessions must treat the package files listed in `memory/bootstrap-manifest.json` as status-bearing bootstrap context, not optional background reading.

When a new package becomes part of durable project status, update `memory/bootstrap-manifest.json` so future sessions read it during bootstrap. If package files exist beyond the manifest, the manifest is stale and should be corrected before relying on package status.

## GitHub file update methods

ChatGPT has two ways to update files in GitHub.

Method 1 is direct GitHub integration editing. Use it for small edits when it is likely to pass the connector and GitHub safety checks. This method is convenient but is often blocked by GitHub or integration safety controls.

Method 2 is the YAML/action handoff. Use it when direct editing is blocked or likely to be blocked. The existing workflow must be reused:

```text
.github/workflows/apply-chatgpt-commit.yaml
```

Do not create a new workflow/action for each commit.

The workflow reads:

```text
.github/chatgpt_commit.yaml
```

ChatGPT should update `.github/chatgpt_commit.yaml`; then the human operator runs the existing action.

The YAML/action handoff may include at most 5 file changes per YAML/commit. If more than 5 files are needed, split the work into multiple handoffs.

Action guard rule:

```text
The apply-chatgpt-commit action routine must not modify its own input file `.github/chatgpt_commit.yaml`.
```

Reason:

If the workflow is later given a push trigger on `.github/chatgpt_commit.yaml`, changing that same file from inside the action could create recursive workflow runs or make it unclear which patch was applied.

ChatGPT may update `.github/chatgpt_commit.yaml` as the handoff input, but the action-applied operations must target other files only.

## Documentation-only updates

Not every memory/documentation update requires a package.

Direct documentation updates are appropriate when the change only records or corrects stable facts, for example:

- hardware brand/model/properties
- physical inventory notes
- sensor or actuator nameplate facts
- already-decided system knowledge that is not being changed by implementation

Package traceability is needed when the documentation change is discovered during package work, explains a package implementation or verification result, records package evidence, or must stay synchronized with code, tests, deploy artifacts or runtime behavior.

Example:

- Documenting heat-pump make, model and properties can be a direct memory update.
- If P0014 discovers during implementation that `ftx-dampers` is now a Shelly Pro 1PM instead of a Shelly Pro 2, that belongs in P0014 package evidence/logs and the memory update should reference the P0014 context.

## Preferred package style

The project works best with small ordered packages when a package is needed.

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
- distinguish direct documentation updates from package-coupled changes
- flag when a package is too broad
- propose exact Codex instructions when needed
- keep safety boundaries explicit for live device work

Avoid:

- letting important decisions remain only in chat
- treating experiments as current truth before verification
- creating unnecessary package files for simple hardware/documentation fact capture
- broad refactors without package reason
- asking unnecessary follow-up questions when a safe best-effort package or direct documentation update can be written

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
