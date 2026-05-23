# Codex Knowhow

Durable lessons about how Codex should work in this repository.

This file is for reusable lessons learned from packages, not raw package evidence.

## Current baseline

### Separate package evidence from global lessons

Codex should store package-specific review/debug output under:

```text
requirements/package-runs/<Pxxxx>/
```

Global lessons should be promoted into:

```text
memory/knowhow/
```

### Review output is evidence

Package consistency review output should be stored when it contains decisions, warnings, conflicts, assumptions or useful context for later ChatGPT/human review.

### Debug output is evidence

Live test/debug output should be stored when it explains a fix, a failed attempt, a runtime anomaly or a semantic side effect.

### Do not promote raw logs blindly

Raw logs may be large and noisy. Store concise excerpts or summaries unless the package explicitly requires full logs.

## Future promoted lessons

Promote improvements to prompt/package-writing style here when repeated package reviews show the same weakness.
