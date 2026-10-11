# Controller ownership

| Owner / layer | Established contract | Unresolved |
|---|---|---|
| External Procon L2 | Commands flow target; measures water-sideW and Hz; its lease and filters are its own | Not a native thermal-kW command |
| FTC local L1 | Mode-specific selected temperature, calibrated water feedback, table-derived temperature representation, request/inhibit flags and pump PWM | Which outbound representation/profile is active on installed21.00; complete thermostat graph |
| Outbound request preparation | BA962 ->39EF/39F1;9A336/9A39E ->9AEDE10 ->08AA/08AB. A1ED8 ->39C7 ->997C6 ->9AEDE0E ->0890.39C3 ->088C/088D | Final physical peer/pin and on-wire timing for each personality; not provenHz demand |
| Other control path | P83 service17 targetHz,18 brine step,19 brineRPM,27/28 brine temperatures,52 frequency-control state are forwarded | Peer firmware absent: receiver law, Hz ramp/protections and brine controller unavailable |

No examined FTC formula converts a6kW target into a requestedHz. That is a bounded finding, not proof that no frequency-related code exists anywhere in the image. The strongest useful boundary is a temperature/operation interface with externally observed compressor behavior. P83's source-board forwarding and these serializers support investigating the other processor; they do not identify its complete firmware or prove one specific connector.

Do not treat a settingACK or cached compressorHz as acknowledgment of a particular demand byte. Future correlation needs target/error/operation request plus actualHz, targetHz and limit state, with separate timestamps. The current model returns UNKNOWN for actualHz, source limits and native stop/restart, even when the FTC-side lookup is known.
