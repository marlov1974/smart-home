# P0083 unresolved questions

- **A — PARTIAL:** protocol parsing, selector classification and response packing traced; exact physical UART ownership (CN105 versus CN22/internal bridge) remains NOT ESTABLISHED. Follow 9D8FE selector 46 to its peripheral and board connector. Complete forwarded class-1 reply path; selectors 17/18/19/27/28/52/54 cannot be declared absent from the local switch.
- **B — PARTIAL:** separate 0770/07E6 settings, selection and PWM mapping found. Confirm heating/DHW labels on matching hardware, trace the CFB18 access gate and complete SET 65/79 input validation/persistence. The valid-level-5 mapping and invalid-level fallback both produce zero PWM; zero alone cannot validate a configured level. CNPWM pin attribution remains a hypothesis.
- **C — PARTIAL:** running banks and A3 split-BCD exposure found; dated snapshot banks are distinct. Find automatic accounting boundary/midnight trigger, qualify timer tick and calibration, and establish atomic paired reads. Service 532 is a mutating accounting action, not an observation.
- Exact image hardware attribution is unproven. Obtain the matching FTC21.00 image or separately authorized captures to transfer semantic conclusions; never transfer absolute RAM addresses.
- Decoder qualification is limited to tested instructions. Validate further opcodes when required by a new trace, particularly indirect flow and far-pointer calling conventions.

Smallest next offline work: resolve CFB18/CF67E settings state machine and the outgoing queue-to-UART mapping. No firmware replacement is necessary to continue this research.
