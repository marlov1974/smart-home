# P0085 next evidence

1. **Exact adapter model and placement:** a readable Mitsubishi adapter label and PCB connector labels/part number. This would document the likely installer error; existing reports do not establish successful CNRF communication. No need to contact MELCloud or collect private traffic.
2. **Port-to-peripheral map:** matching FTC schematic or unpowered continuity tracing through identified interface components. Record connector pin→component→MCU pin, ground and rails separately. This can decide CNIT/UART1 and D/CN22/CN3C hypotheses. Requires separately approved physical work.
3. **Version match:** vendor firmware matching physical21.00, or independently verified unchanged code blocks.20.01 absolute addresses must not be used to operate21.00.
4. **Passive protocol evidence:** only after voltage/isolation qualification, separately approve captures on an already correctly connected interface. Correlate timestamps with normal UI actions; do not send exploratory commands, move cables or alter switches under P85. Compare frame shape to UART0/1/2/D predictions.
5. **Static follow-up:** qualify9E938 far-address load semantics, UART clock sources and the UART0 indirect tables. Full main-display firmware would distinguish screen-local operations from FTC service calls. Finish session apply/ack/persistence/range checks before any CN105 pump-setting trial.

Not having a port map is not evidence that the port is absent, read-only, or more privileged. Current packet formats are research observations, not operational recipes.
