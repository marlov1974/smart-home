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

## GitHub push from Codex/local Mac

P0009 exposed that normal `git push` can fail even when Codex can create GitHub commits through the connector/API.

Durable setup for `dev/smart-home`:

```text
origin git@github.com:marlov1974/smart-home.git
SSH key ~/.ssh/id_ed25519_github
```

`~/.ssh/config` should route `github.com` through that key:

```sshconfig
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
```

The public key may be added either as an account SSH authentication key or as a repository deploy key with write access. If using a deploy key, `Allow write access` is required for pushes.

The public key must be pasted as one valid OpenSSH public-key line beginning with `ssh-ed25519`.

Verification commands:

```bash
ssh -T git@github.com
git -C dev/smart-home remote -v
git -C dev/smart-home fetch origin
git -C dev/smart-home push origin main
```

Expected healthy state:

```text
Hi marlov1974! You've successfully authenticated, but GitHub does not provide shell access.
origin git@github.com:marlov1974/smart-home.git
Everything up-to-date
## main...origin/main
```

If Codex publishes through the GitHub connector/API because normal push credentials are missing, the remote commit may have the same file content but different local history. Before resetting local history, compare content:

```bash
git fetch origin
git diff --stat HEAD origin/main
git diff --name-status HEAD origin/main
```

Only if both diffs are empty, synchronize local history with:

```bash
git reset --hard origin/main
```

If either diff is non-empty, do not reset; report the differing files and wait for a decision.

## Future promoted lessons

Promote improvements to prompt/package-writing style here when repeated package reviews show the same weakness.

## Baseline import changes source-of-truth

P0057 promoted a reusable workflow lesson: when a package imports a mature runtime baseline from another repository and explicitly changes source-of-truth, future follow-up work must inspect the imported G2 tree first rather than continuing to read the old repository by habit.

For FTX after P0057:

```text
primary inspection path: src/shelly/ftx/
old G1 repo: historical provenance or explicit comparison target
```

Keep import, deploy and production activation separate. A source baseline import does not imply live deployment or production activation.

## Escalated Python interpreter drift

P0055B2 exposed that an escalated `/bin/zsh -lc "python3 ..."` command may resolve a different `python3` than a normal sandboxed shell. In this case, normal `python3` was `/usr/bin/python3` with user-site `numpy 2.0.2` and `scikit-learn 1.6.1`, while escalated `zsh` resolved Homebrew Python 3.12 and could not import the Python 3.9 user-site packages.

For LABB model packages that need the existing user-installed ML stack, prefer an explicit interpreter in escalated commands:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/<package>-pycache /usr/bin/python3 -m <module>
```

If imports fail only under escalation, verify both `which python3` and `python3 -c "import site, sys; ..."` in the same execution mode before installing or changing dependencies.
