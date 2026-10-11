# A3: pending jobs versus communication retries

Offline finding, FTC6 20.01, 2026-10-11. No production code or device state changed.

## Finding

For forwarded (class 1) A3 requests, repeating the same selector is normally a poll of an existing job/result, not a restart of the downstream request. Therefore a request, a quiet wait, and a result fetch is a reasonable design. The required wait duration is not established by this static analysis. There is no demonstrated unsolicited CN105 completion delivery in the paths reviewed.

Evidence in the SHA-pinned image identified in provenance.md:

- `CEDFA`: class 1 compares current selector `3238` with previous selector `323E`; equality returns zero. Class 2 returns one independently of equality.
- `CEBEE`: changed class 1 (`8001`) calls `CED82` to submit the request, initializes the cached reply through `CED66`, and sets job state `0866=1`. Unchanged class 1 branches directly to exit at `CECBC`, without resubmitting or resetting the cache. The high-bit operation at `CEC25` must be interpreted with the signed-FB correction described in decoder-and-pin-corrections.md.
- `CED66`: caches selector at `3240`, format at `3244`, value at `3242/3243`. `A8F34` builds the CN105 A3 response from cache accessors.
- `CECBE`/`CEDC0`: an internal nonzero command other than `8F` can clear shared request flags `0402/0404` and reset `0400`. Thus a quiet wait must not be assumed equivalent to interleaving unrelated requests. This does not alone prove loss of the cached result.

The original `CECFA` function-body export was truncated at `CED07`. The hash-gated `P88A3Completion` CFG walk resolves all 24 instructions through `CED47` without relying on that stale function body. `CED0B` rotates the received word left three and masks seven, extracting bits13..15 as format. `CECFA` masks the selector to ten bits, reads bytes38A3/38A4, and calls classifier8C04E. For class1 it callsCED66 with that selector, format and raw bytes. Format7 additionally writes selector to0400. There is **no comparison against the outstanding selector in this function**. Procon must keep its response-selector check. This does not imply every arbitrary received packet bypasses earlier transport/profile gates.

`CECEC` calls this consumer when389A.bit1 is set, then callsCED4A to map native failure state0866=3 to cached format6. In9D0C2, received staging types0E/0F clear0866 when it was2. Job state and cached reply are therefore distinct. Repeating a completed selector must not be assumed to force a fresh measurement; cache freshness and job rearming need separate qualification.

The request-cancellation chain is now explicit: CECBE can clear0402;8BFD0 detects its1-to0 transition using previous386D and sets0868=1;9D29E clears service bit15 from pending083A, inflight083E and acknowledged0842, and clears0866/0867/0868. This is a conditional native cancellation path, not proof that every interleaved command always cancels a job in installed firmware.

Conversely,9D29E consumes0866=1 by setting pending083A.bit15, zeroing0867 and moving0866 to2.9D598 maintains its own counter on selected queue item10(hex): it increments while0867<3, otherwise marks0866=3 and0868=1. This counter is independent of the ten Procon polling attempts; no wall-clock deadline is derived from it here.

## Current Procon implementation

Reviewed `procon/modular/firmware/src/service.c`: `RETRY_MS=1000`, `MAX_ATTEMPTS=10`. Every transmitted request increments `attempts`. Reply format zero enters the same retry scheduling path used after a timeout; formats one/two complete the sample. Pending replies do not increment the communication-failure counter, but they consume the same attempt budget. On exhaustion the sample becomes invalid and the cycle advances.

Consequently many displayed retries can be successful pending-status polls. They do not establish repeated loss of communication or repeated downstream job execution. FTC's own downstream retry mechanism is another layer and must be distinguished from this counter.

## Proposed follow-up, not implemented here

1. Submit one selector and reserve the service-query window.
2. Wait using a latency estimate measured per selector, without unrelated CN105 requests during the reserved window.
3. Fetch the same selector. Treat format zero as pending, with a bounded job deadline and optional subsequent polls, not as a transport failure.
4. Track transport failures, pending polls, completed results and result age independently.
5. Qualify how a new acquisition of the same selector is armed, so a cached result is not labelled newly measured merely because it was just received.

Do not generalize this policy to every A3 code: local class 2 executes again on each request, and some local service/energy operations have side effects. A fixed delay alone cannot guarantee completion under variable downstream load or a missing peer.
