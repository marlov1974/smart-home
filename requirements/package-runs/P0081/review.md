# P0081 review — WARN

Origin synchronized by fast-forward to d8d2d95; existing authorized P0080 working changes retained without conflict. Baseline installed on both units: 7adaecf1. Active-thread delta bootstrap used.

GET zero-filled16-byte framing and A3 high/low service number are established in local pinned F1p source (WriteServiceCodeCMD) and P0071 physical evidence. OCH722A pages30–32 identify read-only display codes and hazardous200/340/342/343/344; these are excluded. Display identity is not proof of CN105 availability.

Installed firmware has no RAW API. Offline implementation and exact artifact qualification precede requesting the package-required physical activation step. No new heating control or firmware activation is inferred from read-only scan permission. Current scheduler state must be checked live before mapping.


Live follow-up confirmed the native Shelly RPC methods work with the new addressed API. Config transition required a reboot on the tested Shelly firmware (although current generic docs permit runtime application); always use returned restart_required. Ten baseline queries completed with correct IDs and checksums. Direct00 no response and DIRECT1E/1F zero data must remain separate outcomes.

Additional primary reference reviewed: https://github.com/gekkekoe/esphome-ecodan-hp/blob/main/protocol.md (2026-10-10). Its command list distinguishes42 GET from other message types and describes1E/1F as historically empty. This is corroborating external evidence, not a substitute for this device's repeated samples.
