# P0081 function design

cn_command: route isolated diagnostic magic into submit validation; preserve existing controls and exclude concurrent diagnostic ownership. cn_read: expose sticky diagnostic result. cn_init/feed/tick/begin/disconnect/bad_frame: maintain bounded diagnostics, correlate raw responses, exclusive retries and terminal errors. modbus_reply: accept only exact new envelope at600 and new read range. Existing ABI exports preserved.

Private diagnostic helpers: allowlist(code), pending(), finish(status,error), submit(words), read(address), retry(now), accept(frame): bounded state, no arbitrary frame parameters or SET.

Python CLI functions: build envelope and plan, Shelly RPC/read/submit, identity and health gates, coherent snapshot, bounded poll, resumable scan, JSONL/CSV/Markdown reporting. Tests inject mocked transport/time.

Host logging follow-up: `scan` now journals the exact bounded submission intent before RPC and persists a terminal result even when its following health check fails. The failure is then raised, preventing subsequent submissions. Added regression `test_health_error_retains_reply`; all six mapper tests pass. This does not modify firmware or the already-running physical scan process. Private report helpers summarize existing evidence and generate a value-free public code map; they perform no device access.

Manual metadata completion: load a portable service-code catalog covering the exact 104-code allowlist, with concise display-label hypotheses, manual display units, page provenance and historical-versus-live distinction. Keep CN105 scaling unverified. Future JSONL/CSV reports include this metadata; the existing physical run is enriched offline without modifying captured raw observations. Verify exact catalog/allowlist equality and continued exclusion of reset codes. No firmware, allowed query or scan scheduling change.
