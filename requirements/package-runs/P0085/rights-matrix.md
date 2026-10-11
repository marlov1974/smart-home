# P0085 rights matrix — PARTIAL

C=CONFIRMED; I=INFERRED; U=UNKNOWN; R=RESTRICTED. Expanded labels below. All code addresses refer to static20.01, physical observations explicitly P81/21.00. CN22 cells concern documented **screen UI capability**, not proven wire packets or password bypass. CN105 session cells describe additional access, with ordinary controls remaining independent. See [access gates](access-gates.md) and [P84 matrix](../P0084/screen-cn105-parity-matrix.md).

| Function | CN22 screen | Ordinary CN105 | CN105 settings session | CNRF | CNIT |
|---|---|---|---|---|---|
| Live telemetry |CONFIRMED S1 display |CONFIRMED GET/P81 21.00; A4F68 |UNKNOWN extra telemetry |UNKNOWN |UNKNOWN |
| Local running-info/A3 |CONFIRMED S1 menu; wireUNKNOWN |CONFIRMED CEBEE→8C0B4; P81 allowlist |UNKNOWN extra selectors |UNKNOWN |UNKNOWN |
| Forwarded brine/compressor service |CONFIRMED S1 menu |CONFIRMED CED82/0866/0868; P81 |UNKNOWN |UNKNOWN |UNKNOWN |
| Selector200 or>=700 via A3 |INFERRED D8B7E2 lacks same filter; D≠provedCN22 |RESTRICTED CEDD6 |UNKNOWN general equivalent; service1002 participates in session |UNKNOWN |UNKNOWN |
| Normal on/off, mode, targets |CONFIRMED S1 UI |CONFIRMED SET32/A468E/A46C4 field paths; P84 |UNKNOWN additional rights |UNKNOWN |UNKNOWN |
| Heating/DHW inhibit |CONFIRMED UI selection S1 |RESTRICTED SET34/server-control semantics; P84 |UNKNOWN broader permission |UNKNOWN |UNKNOWN |
| DHW normal/ECO |CONFIRMED S1 |CONFIRMED BC02C/A462A→3912 |UNKNOWN additional permission |UNKNOWN |UNKNOWN |
| Dedicated DHW priority tuning |UNKNOWN distinct parameter |UNKNOWN; normal/ECO or boost are not proof |UNKNOWN |UNKNOWN |UNKNOWN |
| Pump-level configured read |CONFIRMED S1 pp24/94 |RESTRICTED GET65/79→CFB18; P81 FF |CONFIRMED gated packers A7D48/A8BCC, physicalUNKNOWN |UNKNOWN |UNKNOWN |
| Pump-level setting |CONFIRMED S1 menu |RESTRICTED session-gated |INFERRED end-to-end; confirmed AACA5/ABA09→staging→BD401/BD811; full applyUNKNOWN |UNKNOWN |UNKNOWN |
| Other service configuration |CONFIRMED S1 menu, UI password |RESTRICTED selected settings require session |INFERRED A90F8/import family; not all fields mapped |UNKNOWN |UNKNOWN |
| Schedule editing |CONFIRMED S1 UI |UNKNOWN full edit; inhibit≠schedule |UNKNOWN exact fields |UNKNOWN |UNKNOWN |
| Curve-point editing |CONFIRMED S1 UI |UNKNOWN full edit; SET32 curve mode≠curve points |UNKNOWN exact fields |UNKNOWN |UNKNOWN |
| Energy-monitor settings read |CONFIRMED S1 pp26–27 |RESTRICTED GET71/72→CFB18 |CONFIRMED A8290/A830C selected fields; scalesPARTIAL |UNKNOWN |UNKNOWN |
| Energy-monitor settings write |CONFIRMED S1 UI |UNKNOWN complete transaction |INFERRED settings family; exact apply/scalesUNKNOWN |UNKNOWN |UNKNOWN |
| Energy measurements |CONFIRMED S1 UI |CONFIRMED GET07/A1/A2/P81; CDFxx banks |UNKNOWN additional access |UNKNOWN |UNKNOWN |
| Bus diagnostics / memory read |UNKNOWN UI-equivalent |UNKNOWN normal GET equivalent |UNKNOWN |UNKNOWN (UART1 path not assigned) |UNKNOWN (UART1 path not assigned) |
| Firmware/service maintenance |UNKNOWN port-specific updater |UNKNOWN |UNKNOWN |UNKNOWN |UNKNOWN; UART1 service loops are unassigned |
| Password/language/display-local data |CONFIRMED documented UI; transportUNKNOWN |UNKNOWN |UNKNOWN |UNKNOWN |UNKNOWN |

**Higher-rights hypotheses:** CNRF greater than CN105 = UNKNOWN; CNIT greater than CN105 = UNKNOWN. Every proposed capability above remains UNKNOWN on those connectors. Code-level alternate diagnostics are CONFIRMED, but the necessary physical attribution and version match are absent. No blanket “disproved” claim is made from missing mappings.
