# P0083 provenance and scope

All hexadecimal flash/RAM addresses in this package describe **only** the supplied image below. They are not addresses on installed FTC21.00. This convention applies to every trace/table. Confidence labels refer to static evidence, not a physical validation. The image's 20.01 identification is a header/service-190 interpretation; exact PCB/part attribution remains unproven.

| Input/tool | Exact identity |
|---|---|
| ftc6.mot SHA256 | `e94f9d9369b5efb9d2af66209fb431fde6ed0a1690b9ce0960adbf5cdb53b0c3` |
| ftc6.id SHA256 | `f488249ce1e39e098e5862458773133155eb135dd7f2a7fbf64b38fdf70924c2` |
| FF-filled binary SHA256; base 80000 | `d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a` |
| Sparse address+byte SHA256 | `2beabad902a617333229b35abf0236813f55e7db754bee4d16c2c50d5cfe63e5` |
| Ghidra | 12.1.4 PUBLIC, macOS arm64; P0082 built native components |
| Java | Temurin 21.0.12.1+1 |
| esaulenka/ghidra_m16c | `2833a30bf0ba5b9ac9b2e472966b4bc04d4f71cc` |
| silverchris/m16c comparison | `a67013a617ddd82d4f04ebf31c2752f82f99e2d0`; identical language data |
| Language | `m16c:LE:16:default:default` |
| Original slaspec SHA256 | `1c1f46945fc47a6bb5f6c755578708a4709aca47cd1aac9721256cc0eec243b8` |
| P83 patched slaspec SHA256 | `087e6afb29a7625e789b30467a12cad4ab2c2731e08a98c914969a308df3f46f` |

Sources reviewed: P0082 findings/disassembly/selector JSON/open questions/verification, P0081 command map and implementation report, [Renesas M16C/60 software manual](https://www.renesas.com/en/document/mah/m16c60-m16c20-m16ctiny-series-software-manual), Mitsubishi OCH722A pp26–32 and commissioning settings (local PDF downloaded from [manual mirror](https://ecoinnovation.lv/wp-content/uploads/2023/02/ZEMES_SILTUMSU%CC%84KNIS_GEODAN_SERVISA_INSTRUKCIJA.pdf)), [F1p decoder](https://github.com/F1p/Home-Assistant-Mitsubishi-CN105-to-MQTT/blob/7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5/EcodanDecoder.cpp), and [gekkekoe protocol](https://github.com/gekkekoe/esphome-ecodan-hp/blob/829754a334df5050a1ffb58557b45d28fa2de231/protocol.md)/[response code](https://github.com/gekkekoe/esphome-ecodan-hp/blob/829754a334df5050a1ffb58557b45d28fa2de231/components/ecodan/response.cpp). These public protocol implementations corroborate interpretation; they do not establish firmware-version identity.

Local evidence: workspace `P0083/private/final/` and `final-repeat/` contain function assembly, decompilation, incoming references and full instruction/reference indexes. `P0083/private/final.log` records replay from a clean copy of the P82 project. Raw firmware, ID, manuals, third-party module, full disassembly and customer frames are not published. Selected historical field observations are in `physical-crosscheck.json` without device identifiers/full frames. No live device connection, state change, firmware build/deploy or flash occurred in P83.
