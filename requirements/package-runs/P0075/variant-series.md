# P0075: 16 varianter av 0x57

Adress 0x08008000, önskat antal16bytes, little-endian. Samtliga16 gav0RX inom3s. Discovery före, efter och mellan:17/17 giltiga identiska svar7a00700300ff000008002014. Ingen fysisk omstart under serien.

| Nr | Fält efter57 | Avslut | Exakt paket | RX |
|---|---|---|---|---|
| 1 | addr32-len32 | sum8 | `57 00 80 00 08 10 00 00 00 ef` | 0 |
| 2 | len16-addr32 | sum8 | `57 10 00 00 80 00 08 ef` | 0 |
| 3 | addr32-len16 | sum8 | `57 00 80 00 08 10 00 ef` | 0 |
| 4 | len32-addr32 | sum8 | `57 10 00 00 00 00 80 00 08 ef` | 0 |
| 5 | addr32-len32 | crc32-sum8 | `57 00 80 00 08 10 00 00 00 bd ce 45 18 d7` | 0 |
| 6 | len16-addr32 | crc32-sum8 | `57 10 00 00 80 00 08 6e 99 26 97 b3` | 0 |
| 7 | addr32-len16 | crc32-sum8 | `57 00 80 00 08 10 00 3c fb 29 8e dd` | 0 |
| 8 | len32-addr32 | crc32-sum8 | `57 10 00 00 00 00 80 00 08 88 9a 6f 63 e3` | 0 |
| 9 | addr32-len32 | none | `57 00 80 00 08 10 00 00 00` | 0 |
| 10 | len16-addr32 | none | `57 10 00 00 80 00 08` | 0 |
| 11 | addr32-len16 | none | `57 00 80 00 08 10 00` | 0 |
| 12 | len32-addr32 | none | `57 10 00 00 00 00 80 00 08` | 0 |
| 13 | addr32-len32 | crc32 | `57 00 80 00 08 10 00 00 00 bd ce 45 18` | 0 |
| 14 | len16-addr32 | crc32 | `57 10 00 00 80 00 08 6e 99 26 97` | 0 |
| 15 | addr32-len16 | crc32 | `57 00 80 00 08 10 00 3c fb 29 8e` | 0 |
| 16 | len32-addr32 | crc32 | `57 10 00 00 00 00 80 00 08 88 9a 6f 63` | 0 |

CRC32 beräknades över hela den föreslagna headern inklusive57 och skickadesLE32; sum8 över alla föregående paketbytes. No-trailer betyder att ingen kontrollsumma skickades. Dessa är hypoteser, inte bevisade läspaket.

Slutsats: bootloadern förblir kontaktbar men ingen av dessa16kombinationer identifierar läsprotokollet. Inget77/76ellerdata. Ej bevis för att57saknas; relativ adress, annan längd/enhet, annan CRC-täckning, handshake eller annan struktur återstår. Ingen läsning utanför applikationen identifierad, inget innehåll extraherat.

Testskript stoppat. Procon kvar i firmwareläge DIP00000000 och Shelly kvar i js_uart115200; normaldrift är inte återställd.

Drift: JS mem_used2016,peak4018,free23170, inga körfel under serien. Initial uppladdning hade unsupportedUnicode-escape i frame-literals; skriptstart nekades före UART-sändning. Korrigerat till hexescapes, full kod återläst och verifierad före körning.
