# P0054Y what we learned

P0054Y exposed a naming/semantics conflict:

```text
P0054W available public per-MGA rows are 15m/60m resolution,
but their measurement/settlement class is profiled/load-profile,
not measured/non_profiled.
```

Future packages must not use time resolution as a proxy for settlement class.

Correct package wording should name both dimensions:

```text
native resolution: 15m/60m
measurement or settlement class: profiled/load_profile vs metered/non_profiled
```
