# Shelly Knowhow

Durable Shelly lessons learned from G2 packages, live tests and package reviews.

This file is for general reusable knowledge, not raw package logs.

## Current baseline

### Use bounded log capture

When streaming Shelly logs during live testing, use bounded capture so the process does not hang indefinitely.

Mac-compatible example:

```bash
perl -e 'alarm shift; exec @ARGV' 60 curl -N http://192.168.86.240:8040/debug/log
```

### Treat log streaming as read-only diagnostics

Opening `/debug/log` is diagnostic observation. It does not itself change device state.

Starting/stopping scripts, writing KVS, uploading scripts, changing components or changing actuators are live actions and require explicit package permission.

## Future promoted lessons

Promote repeated or important package observations here, for example:

- RPC sequencing issues
- timer/concurrency behavior
- heap/memory thresholds
- KVS size/shape limits
- script runtime duration concerns
- WebSocket/logging side effects
- installer/deploy edge cases
