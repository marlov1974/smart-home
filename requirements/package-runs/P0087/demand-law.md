# Demand law: what is actually recovered

A162A callsA1EA4. A1EA4 callsA1EC4 andA1ED8, stores the former in38C4 and the latter in39E1/39C7. A1EC4 returns2800 except cooling phase11, where it returns1900. A1ED8's ordinary heating phase8 computes signed error `max(Tselected,2500)-Tfeedback` (or held3947 for profile0900=2). It selects the first threshold at or above error from ROM8355A, stride6. Both threshold columns are identical in this image:

| Error upper bound, C | Output, temperature-like C |
|---:|---:|
| -2.0 | 29.0 |
| -1.5 | 28.5 |
| -1.0 | 28.0 |
| -0.5 | 27.5 |
| 0 | 27.0 |
| 0.5 | 26.5 |
| 1.0 | 26.0 |
| 1.5 | 25.5 |
| 2.0 | 25.0 |
| 2.5 | 24.5 |
| otherwise | 24.0 |

Equality belongs to the displayed row. `4911=2` overrides the result with2700 **after** lookup. The table has no accumulator, derivative, elapsed-time term or rate state. Increasing heat deficit makes this output smaller, not larger; do not relabel it absoluteHz or kW. 997C6 selects39C7 for parameter10, clamps800..3950 and encodes `(x-800)/50`;9AEDE selector0E/17 stores its result in0890. A fixed reference plus varying synthetic feedback is consistent with an adapted temperature-demand interface (**STRONG HYPOTHESIS**), not proof of the receiver's algorithm.

A distinct packing branch9AEDE selector10 transmits target/feedback encoded from39EF/39F1. Profile selection and exact physical peer for each branch are not fully qualified. Therefore the table is not asserted to be the sole active Geodan law. Large positive error saturates this particular table above2.5C, but the separate target/feedback representation does not; **this does not prove that raising a target above +2.5C has no further effect on the installed machine**.

Mode9/10 uses a different1500/default/table path; cooling11 uses8359C with reversed error sign; room mode upstream usesBAE26 rather than fixed target copying. These are excluded from the executable heating branch rather than guessed. Profile2's held3947 is explicit input; its upstream sample/history semantics are unresolved.

The local equation is `v[k]=lookup(e[k])`, after branch selection and beforeoverride; no modeled local state evolves. This only answers same-error/different-history for that branch. External frequency control, start eligibility, limits, room adaptation and gates retain state elsewhere. An overall P/PI/PID/degree-minute label, anti-windup law, startup boost and stable minimum frequency are UNKNOWN.

Assembly qualification: A1FDB calls feedback; A1FE4 subtracts it; A2017 loads a signed threshold using farLDE; A201B..A2027 compare high signed / low unsigned halves; A2033 loads row+4. The implementation checks these operands and the actual ROM table, including both identical columns. It preserves16-bit wrap before sign extension. Synthetic tests exercise row edges and encoding saturation; these are transcription tests, not physical validation.
