# P0084 conclusion

**Complete display parity over CN105: NOT ESTABLISHED. Research result: PARTIAL.**

There are real shared functions, including service dispatch and heating-mode assignment. CN105 additionally has session-gated installation-setting paths: SET65/79 stage the two water-pump levels. Their full safe transaction and physical21.00 behavior remain unverified.

The firmware also has real restrictions: directA3 filters selector200 and>=700, and pending D-path service activity takes precedence overA3. This disproves an unrestricted common-entry assumption, not every possible alternative command.

CN105 now traces to UART2; a separate GPIO/timer transport reaches the packed-command/service path. Its physical identity asCN22 still needs board/display evidence. The supplied image cannot yet establish the full screen command set, screen-local options or the observed10–15s timing.

See [capability matrix](screen-cn105-parity-matrix.md), [transport trace](screen-cn22-trace.md), [settings trace](settings-trace.md), [verification](verification.json), and [next evidence](open-questions.md). All work was offline. P83 andP84 have separate commits; original firmware and full disassembly are not published.
