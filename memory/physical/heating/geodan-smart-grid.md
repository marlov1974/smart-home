# Geodan Smart Grid Control

## Sources

Condensed from:

- uploaded Mitsubishi Electric Swedish Smart Grid manual `15371.pdf`, titled `Användarmanual SMART GRID - Styrning via externa enheter`
- uploaded Mitsubishi Electric Geodan service manual `ZEMES_SILTUMSUKNIS_GEODAN_SERVISA_INSTRUKCIJA.pdf`, model `EHGT17D-YM9ED`, service ref `EHGT17D-YM9ED.UK`

## Current project status

Heat-pump Smart Grid control is not ready for G2 live control.

Before any G2 package controls VP1/VP2 Smart Grid inputs, the operator must manually verify and set the heat-pump Smart Grid settings. Until that manual verification is possible, the heat pumps must remain in their current unmanaged/ostyrt operating mode so the house continues to function without G2 control.

A future VP-control package must start with an installed-settings verification gate and must not assume the intended `IN11`/`IN12` behavior is active just because the wiring exists.

## Model and terminal confirmation

The service manual confirms the relevant model track:

```text
Model: EHGT17D-YM9ED
Service ref: EHGT17D-YM9ED.UK
FTC terminal block: TBI.3
IN11: TBI.3 3-4
IN12: TBI.3 1-2
Function: Smart grid ready input
```

The wiring diagram shows TBI.3 with `IN8`, `IN9`, `IN11`, and `IN12`, and Table 1 names `IN12` as Smart grid ready input while referring `IN11`/`IN12` behavior to the installation manual / Smart Grid settings.

## Active control inputs

The Geodan/Ecodan Smart Grid function is controlled through two external inputs:

```text
IN11
IN12
```

The external controller must be able to close two contacts.

## Contact semantics

```text
IN11 OFF/open  + IN12 OFF/open  = Normal function
IN11 ON/closed + IN12 OFF/open  = Start recommendation
IN11 OFF/open  + IN12 ON/closed = Stop command
IN11 ON/closed + IN12 ON/closed = Start command
```

Interpretation:

- start recommendation means the machine may start if there is a need
- start command means the machine must start directly
- stop command blocks the Smart Grid selected function
- normal function means ordinary Geodan settings apply
- after a stop command, the machine may take up to about 20 minutes to stop to protect the compressor

## Manual price-control example

High electricity price:

```text
IN11 OFF/open
IN12 ON/closed
```

Low electricity price:

```text
IN11 ON/closed
IN12 ON/closed
```

Normal operation:

```text
IN11 OFF/open
IN12 OFF/open
```

## Smart Grid configuration scope

Smart Grid can be configured to affect:

```text
- domestic hot water
- heating
- cooling
- pump cycles
```

If more than one function is selected, Smart Grid controls them together; the Smart Grid manual states they cannot be controlled separately by the same IN11/IN12 signal combination.

The service manual menu tree places Smart grid ready under:

```text
Main menu -> Service -> Operation settings -> Smart grid ready
```

with settings for DHW, Heating, Pump cycles and target/interval behavior.

## Efficiency warning

The Smart Grid manual warns that high storage temperatures:

- reduce efficiency
- increase heat losses
- can reduce heat-pump lifetime

G2 planning consequence:

- avoid unnecessary high DHW/storage targets
- avoid high flow temperatures unless needed
- treat Smart Grid boost as a cost/need trade-off, not free storage

## House command bit order

Unless installation evidence proves otherwise:

```text
first bit  = IN11
second bit = IN12
0 = OFF/open
1 = ON/closed
```

Therefore:

```text
00 = normal function
10 = start recommendation
01 = stop command
11 = start command
```

The house-specific VP1/VP2 flow/DHW target mappings remain documented in `heat-pumps.md`.

## Diagnostics useful for future G2 work

Service menu running information includes request codes useful for non-invasive diagnostics:

```text
175 = FTC output signal information
176 = FTC input signal information
553 = FTC output signal information at time of error
554 = FTC input signal information at time of error
```

The service manual also states that if the heat pump is forced ON/OFF because Smart grid ready input `IN11` and `IN12` are used, and switch-on/off commands are input, this is normal operation and no action is necessary.

## Open installation checks

Before any live control package, verify:

- which Shelly/relay output drives IN11
- which Shelly/relay output drives IN12
- that the installed interface closes contacts as expected
- current Smart Grid settings for VP1
- current Smart Grid settings for VP2
- whether VP1 and VP2 use identical Smart Grid function selection
- that the operator has intentionally moved the heat pumps from unmanaged/ostyrt operation into the required Smart Grid-ready configuration
