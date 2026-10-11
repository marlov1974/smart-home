# Kommandokatalog – FTC6

FTC20.01; inte verifierat mot installerad21.00.

Alla poster i nuvarande portmatris, alla gemensamma serviceposter samt alla råkodöversättningar. Inte bevisat komplett för hela firmwaren.

**Läsnyckel:** hex anges med0x eller enligt uttrycklig kolumnnotering. Serviceval anges i decimal. ROM-adresser är spårnings-ID, inte kommandon. En gemensam svarsrutin bevisar inte att flera koder gör samma sak. Okända funktioner behålls i listan.

## Portar och gränssnitt

|Gränssnitt|Port|Säkerhet i kopplingen|Poster|
|---|---|---|---|
|uart2|CN105|protocol/P81 corroborated|141|
|source-software|CN3C candidate|software path proven; connector inferred|38|
|d|CN22 candidate|connector inferred; peer implementation absent|35|
|uart6|CNRF candidate|room protocol proven; connector inferred|6|
|uart0|CN108/storage candidate|file protocol proven; connector inferred|38|
|uart1|CNIT candidate|diagnostic protocol; connector unbound|11|

269 rutter/mallar/intervall är inte269 oberoende funktioner. Serviceval och interna översättningar redovisas separat. Procons Modbus-register och bootloader tillhör ett annat firmwarelager; inga likheter i nummer används som bevis för koppling.

## Samma funktion eller kedja över flera gränssnitt

|Funktion|Kod/koder|Vad sambandet betyder|Källa|
|---|---|---|---|
|Varmvattenboost|CN105 SET34 p3, enable p1.bit0 ↔ UART6 typ4A p9 (svar6A)|Gemensam setter B95E0 /3919; olika validering, inte identiska paket|[uart6-room-path.md](uart6-room-path.md)|
|Semesterläge|CN105 SET34 p4, enable p1.bit1 ↔ UART6 typ4B p9 (svar6B)|Gemensam setter C0AD0 /391B|[uart6-room-path.md](uart6-room-path.md)|
|Framledningsbörvärde|CN105 SET32 → källänk familj05, variant1|Styrkedja via urval/överstyrning; vidareförmedlat effektivt värde, inte kodalias|[source-outgoing.md](source-outgoing.md)|
|Servicefråga / Running information|CN105 GET A3 + serviceval → källänk1C → svar1D → A3-resultat|Villkorad vidarebefordran; lokala serviceval går inte alla till underkortet|[a3-job-lifecycle.md](a3-job-lifecycle.md)|
|Inställningssession|CN105 SET C8 → D intern service1005 (decimal) → överföring / slutmarkör|Sessionskedja;1005 är inte ett externt A3-val eller fristående wire-opcode|[settings-d-events.md](settings-d-events.md)|
|Återläsning av hjälptillstånd|SET34 p11/p12 → GET28 p11/p12|Delade tillstånd39EC/39A4; skrivning och läsning, inte samma operation|[cn105-control-fields.md](cn105-control-fields.md)|

## uart2 – CN105

Alla kända poster på denna väg. Okänd funktion betyder att rutten är identifierad men ännu inte semantiskt kartlagd.

|Kod / underkod|Funktion|Vad den gör / känd effekt|Spårnings-ID|
|---|---|---|---|
|FC / typ0x41 / kod0x32|Operating controls including zone1 fixed-flow target|A459C maps 0/1; invalid or disabled -> FF. 90368 copies valid value to38BF and clears082E.bit7; additional side effects remain; DHW mode through A462A ->3912; FF ignored; Zone1 mode through A468E ->BBE92; also unconditional mode context for target branch; Zone2 mode through A468E ->BBE92; also unconditional mode context for target branch; BE16 DHW target viaA46C4; FFFF ignored ->3906; BE16 zone1 target viaA46FA ->B9BFE with decoded p6; mode2/5 skipped at caller; FFFF ignored downstream; BE16 zone2 target viaA46FA ->B9BFE with decoded p7; mode2/5 skipped at caller; FFFF ignored downstream; low3bits ->082A.bits11..13;2342.bit2 clears these afterward|uart2.41.32|
|FC / typ0x41 / kod0x33|SET 33|Funktion/effekt ännu okänd|uart2.41.33|
|FC / typ0x41 / kod0x34|SET 34|0/1 viaA472C ->B95E0 ->3919 boost; FF ignored; 0/1 viaA4760 ->C0AD0 ->391B holiday; FF ignored; 0/1 accepted, other/disabled FF preserves prior39A6.bit0; 0/1 accepted, other/disabled FF preserves prior39A6.bit1; 0/1 accepted, other/disabled FF preserves prior39A6.bit2; 0/1 accepted, other/disabled FF preserves prior39A6.bit3; 0/1 accepted, other/disabled FF preserves prior39A6.bit4; 0 sets4977=1;1 sets4976=1;invalid/disabled unchanged. Event flags, not direct assignment of both; 1 increments byte33EA and sets39EC=1;0 clears both;invalid/disabled unchanged. Counter>=10 contributes39ED=1; 0/1 ->39A4;invalid/disabled ignored; 8929D lookup times10 ->3E06 ->3933; values>10 select index0; ABE04==1 overrides3933=100|uart2.41.34|
|FC / typ0x41 / kod0x35|SET 35|Funktion/effekt ännu okänd|uart2.41.35|
|FC / typ0x41 / kod0x50|SET 50|Funktion/effekt ännu okänd|uart2.41.50|
|FC / typ0x41 / kod0x51|SET 51|Funktion/effekt ännu okänd|uart2.41.51|
|FC / typ0x41 / kod0x52|SET 52|Funktion/effekt ännu okänd|uart2.41.52|
|FC / typ0x41 / kod0x53|SET 53|Funktion/effekt ännu okänd|uart2.41.53|
|FC / typ0x41 / kod0x54|SET 54|Funktion/effekt ännu okänd|uart2.41.54|
|FC / typ0x41 / kod0x55|SET 55|Funktion/effekt ännu okänd|uart2.41.55|
|FC / typ0x41 / kod0x56|SET 56|Funktion/effekt ännu okänd|uart2.41.56|
|FC / typ0x41 / kod0x57|SET 57|Funktion/effekt ännu okänd|uart2.41.57|
|FC / typ0x41 / kod0x58|SET 58|Funktion/effekt ännu okänd|uart2.41.58|
|FC / typ0x41 / kod0x59|SET 59|Funktion/effekt ännu okänd|uart2.41.59|
|FC / typ0x41 / kod0x5A|SET 5a|Funktion/effekt ännu okänd|uart2.41.5a|
|FC / typ0x41 / kod0x5B|SET 5b|Funktion/effekt ännu okänd|uart2.41.5b|
|FC / typ0x41 / kod0x5C|SET 5c|Funktion/effekt ännu okänd|uart2.41.5c|
|FC / typ0x41 / kod0x5D|SET 5d|Funktion/effekt ännu okänd|uart2.41.5d|
|FC / typ0x41 / kod0x5E|SET 5e|Funktion/effekt ännu okänd|uart2.41.5e|
|FC / typ0x41 / kod0x5F|SET 5f|Funktion/effekt ännu okänd|uart2.41.5f|
|FC / typ0x41 / kod0x60|SET 60|Funktion/effekt ännu okänd|uart2.41.60|
|FC / typ0x41 / kod0x61|SET 61|Funktion/effekt ännu okänd|uart2.41.61|
|FC / typ0x41 / kod0x62|SET 62|Funktion/effekt ännu okänd|uart2.41.62|
|FC / typ0x41 / kod0x63|SET 63|Funktion/effekt ännu okänd|uart2.41.63|
|FC / typ0x41 / kod0x64|SET 64|Funktion/effekt ännu okänd|uart2.41.64|
|FC / typ0x41 / kod0x65|Stage DHW settings block including pump level|changes neighboring settings; no local1..5 clamp; cannot use zero-filled payload|uart2.41.65|
|FC / typ0x41 / kod0x66|SET 66|Funktion/effekt ännu okänd|uart2.41.66|
|FC / typ0x41 / kod0x67|SET 67|Funktion/effekt ännu okänd|uart2.41.67|
|FC / typ0x41 / kod0x68|SET 68|Funktion/effekt ännu okänd|uart2.41.68|
|FC / typ0x41 / kod0x69|SET 69|Funktion/effekt ännu okänd|uart2.41.69|
|FC / typ0x41 / kod0x6A|SET 6a|Funktion/effekt ännu okänd|uart2.41.6a|
|FC / typ0x41 / kod0x6B|SET 6b|Funktion/effekt ännu okänd|uart2.41.6b|
|FC / typ0x41 / kod0x6C|SET 6c|Funktion/effekt ännu okänd|uart2.41.6c|
|FC / typ0x41 / kod0x6D|SET 6d|Funktion/effekt ännu okänd|uart2.41.6d|
|FC / typ0x41 / kod0x6E|SET 6e|Funktion/effekt ännu okänd|uart2.41.6e|
|FC / typ0x41 / kod0x6F|SET 6f|Funktion/effekt ännu okänd|uart2.41.6f|
|FC / typ0x41 / kod0x70|SET 70|Funktion/effekt ännu okänd|uart2.41.70|
|FC / typ0x41 / kod0x71|SET 71|Funktion/effekt ännu okänd|uart2.41.71|
|FC / typ0x41 / kod0x72|SET 72|Funktion/effekt ännu okänd|uart2.41.72|
|FC / typ0x41 / kod0x73|SET 73|Funktion/effekt ännu okänd|uart2.41.73|
|FC / typ0x41 / kod0x74|SET 74|Funktion/effekt ännu okänd|uart2.41.74|
|FC / typ0x41 / kod0x75|SET 75|Funktion/effekt ännu okänd|uart2.41.75|
|FC / typ0x41 / kod0x76|SET 76|Funktion/effekt ännu okänd|uart2.41.76|
|FC / typ0x41 / kod0x77|SET 77|Funktion/effekt ännu okänd|uart2.41.77|
|FC / typ0x41 / kod0x78|SET 78|Funktion/effekt ännu okänd|uart2.41.78|
|FC / typ0x41 / kod0x79|Stage heating settings including pump level|Stages1CB0; category6 import BD780 writes07E6; physical actuator consumption is separate|uart2.41.79|
|FC / typ0x41 / kod0x7A|SET 7a|Funktion/effekt ännu okänd|uart2.41.7a|
|FC / typ0x41 / kod0x7B|SET 7b|Funktion/effekt ännu okänd|uart2.41.7b|
|FC / typ0x41 / kod0x7C|SET 7c|Funktion/effekt ännu okänd|uart2.41.7c|
|FC / typ0x41 / kod0x7D|SET 7d|Funktion/effekt ännu okänd|uart2.41.7d|
|FC / typ0x41 / kod0x7E|SET 7e|Funktion/effekt ännu okänd|uart2.41.7e|
|FC / typ0x41 / kod0xC8|Settings category session action|Write action1 schedules category import before end acknowledgment; timeout/reset is not rollback|uart2.41.c8|
|FC / typ0x42 / kod0x01|GET 01|Funktion/effekt ännu okänd|uart2.42.01|
|FC / typ0x42 / kod0x02|GET 02|Funktion/effekt ännu okänd|uart2.42.02|
|FC / typ0x42 / kod0x03|GET 03|Funktion/effekt ännu okänd|uart2.42.03|
|FC / typ0x42 / kod0x04|Native and multi-unit status fields (raw sources)|Funktion/effekt ännu okänd|uart2.42.04|
|FC / typ0x42 / kod0x05|GET 05|Funktion/effekt ännu okänd|uart2.42.05|
|FC / typ0x42 / kod0x06|GET 06|Funktion/effekt ännu okänd|uart2.42.06|
|FC / typ0x42 / kod0x07|Consumed/produced power and increasing consumed counter|no counter clearing proven in GET07; do not equate with A3 energy fold|uart2.42.07|
|FC / typ0x42 / kod0x09|GET 09|Funktion/effekt ännu okänd|uart2.42.09|
|FC / typ0x42 / kod0x0B|Room/selected temperature sources|Funktion/effekt ännu okänd|uart2.42.0b|
|FC / typ0x42 / kod0x0C|Primary flow/return/DHW temperatures and sampled companions|Funktion/effekt ännu okänd|uart2.42.0c|
|FC / typ0x42 / kod0x0D|GET 0d|Funktion/effekt ännu okänd|uart2.42.0d|
|FC / typ0x42 / kod0x0E|GET 0e|Funktion/effekt ännu okänd|uart2.42.0e|
|FC / typ0x42 / kod0x0F|GET 0f|Funktion/effekt ännu okänd|uart2.42.0f|
|FC / typ0x42 / kod0x10|GET 10|Funktion/effekt ännu okänd|uart2.42.10|
|FC / typ0x42 / kod0x11|GET 11|Funktion/effekt ännu okänd|uart2.42.11|
|FC / typ0x42 / kod0x13|GET 13|Funktion/effekt ännu okänd|uart2.42.13|
|FC / typ0x42 / kod0x14|Input flags, multi-unit words and quantized primary flow|Funktion/effekt ännu okänd|uart2.42.14|
|FC / typ0x42 / kod0x15|Actuator/native-state report|Funktion/effekt ännu okänd|uart2.42.15|
|FC / typ0x42 / kod0x16|GET 16|Funktion/effekt ännu okänd|uart2.42.16|
|FC / typ0x42 / kod0x17|GET 17|Funktion/effekt ännu okänd|uart2.42.17|
|FC / typ0x42 / kod0x18|GET 18|Funktion/effekt ännu okänd|uart2.42.18|
|FC / typ0x42 / kod0x19|GET 19|Funktion/effekt ännu okänd|uart2.42.19|
|FC / typ0x42 / kod0x1A|GET 1a|Funktion/effekt ännu okänd|uart2.42.1a|
|FC / typ0x42 / kod0x1B|GET 1b|Funktion/effekt ännu okänd|uart2.42.1b|
|FC / typ0x42 / kod0x1C|GET 1c|Funktion/effekt ännu okänd|uart2.42.1c|
|FC / typ0x42 / kod0x1D|GET 1d|Funktion/effekt ännu okänd|uart2.42.1d|
|FC / typ0x42 / kod0x1E|Explicit zero data response 1e|none in A4CD2|uart2.42.1e|
|FC / typ0x42 / kod0x1F|Explicit zero data response 1f|none in A4CD2|uart2.42.1f|
|FC / typ0x42 / kod0x20|GET 20|Funktion/effekt ännu okänd|uart2.42.20|
|FC / typ0x42 / kod0x26|Reported modes and requested target words|Funktion/effekt ännu okänd|uart2.42.26|
|FC / typ0x42 / kod0x27|GET 27|Funktion/effekt ännu okänd|uart2.42.27|
|FC / typ0x42 / kod0x28|Boost, holiday and flag report|Funktion/effekt ännu okänd|uart2.42.28|
|FC / typ0x42 / kod0x29|GET 29|Funktion/effekt ännu okänd|uart2.42.29|
|FC / typ0x42 / kod0x50|GET 50|Funktion/effekt ännu okänd|uart2.42.50|
|FC / typ0x42 / kod0x51|GET 51|Funktion/effekt ännu okänd|uart2.42.51|
|FC / typ0x42 / kod0x52|GET 52|Funktion/effekt ännu okänd|uart2.42.52|
|FC / typ0x42 / kod0x53|GET 53|Funktion/effekt ännu okänd|uart2.42.53|
|FC / typ0x42 / kod0x54|GET 54|Funktion/effekt ännu okänd|uart2.42.54|
|FC / typ0x42 / kod0x55|GET 55|Funktion/effekt ännu okänd|uart2.42.55|
|FC / typ0x42 / kod0x56|GET 56|Funktion/effekt ännu okänd|uart2.42.56|
|FC / typ0x42 / kod0x57|GET 57|Funktion/effekt ännu okänd|uart2.42.57|
|FC / typ0x42 / kod0x58|GET 58|Funktion/effekt ännu okänd|uart2.42.58|
|FC / typ0x42 / kod0x59|GET 59|Funktion/effekt ännu okänd|uart2.42.59|
|FC / typ0x42 / kod0x5A|GET 5a|Funktion/effekt ännu okänd|uart2.42.5a|
|FC / typ0x42 / kod0x5B|GET 5b|Funktion/effekt ännu okänd|uart2.42.5b|
|FC / typ0x42 / kod0x5C|GET 5c|Funktion/effekt ännu okänd|uart2.42.5c|
|FC / typ0x42 / kod0x5D|GET 5d|Funktion/effekt ännu okänd|uart2.42.5d|
|FC / typ0x42 / kod0x5E|GET 5e|Funktion/effekt ännu okänd|uart2.42.5e|
|FC / typ0x42 / kod0x5F|GET 5f|Funktion/effekt ännu okänd|uart2.42.5f|
|FC / typ0x42 / kod0x60|GET 60|Funktion/effekt ännu okänd|uart2.42.60|
|FC / typ0x42 / kod0x61|GET 61|Funktion/effekt ännu okänd|uart2.42.61|
|FC / typ0x42 / kod0x62|GET 62|Funktion/effekt ännu okänd|uart2.42.62|
|FC / typ0x42 / kod0x63|GET 63|Funktion/effekt ännu okänd|uart2.42.63|
|FC / typ0x42 / kod0x64|GET 64|Funktion/effekt ännu okänd|uart2.42.64|
|FC / typ0x42 / kod0x65|DHW pump configured level, within settings block|CFB18 changes session flags; FF is not level zero|uart2.42.65|
|FC / typ0x42 / kod0x66|GET 66|Funktion/effekt ännu okänd|uart2.42.66|
|FC / typ0x42 / kod0x67|GET 67|Funktion/effekt ännu okänd|uart2.42.67|
|FC / typ0x42 / kod0x68|GET 68|Funktion/effekt ännu okänd|uart2.42.68|
|FC / typ0x42 / kod0x69|GET 69|Funktion/effekt ännu okänd|uart2.42.69|
|FC / typ0x42 / kod0x6A|GET 6a|Funktion/effekt ännu okänd|uart2.42.6a|
|FC / typ0x42 / kod0x6B|GET 6b|Funktion/effekt ännu okänd|uart2.42.6b|
|FC / typ0x42 / kod0x6C|GET 6c|Funktion/effekt ännu okänd|uart2.42.6c|
|FC / typ0x42 / kod0x6D|GET 6d|Funktion/effekt ännu okänd|uart2.42.6d|
|FC / typ0x42 / kod0x6E|GET 6e|Funktion/effekt ännu okänd|uart2.42.6e|
|FC / typ0x42 / kod0x6F|GET 6f|Funktion/effekt ännu okänd|uart2.42.6f|
|FC / typ0x42 / kod0x70|GET 70|Funktion/effekt ännu okänd|uart2.42.70|
|FC / typ0x42 / kod0x71|GET 71|Funktion/effekt ännu okänd|uart2.42.71|
|FC / typ0x42 / kod0x72|GET 72|Funktion/effekt ännu okänd|uart2.42.72|
|FC / typ0x42 / kod0x73|GET 73|Funktion/effekt ännu okänd|uart2.42.73|
|FC / typ0x42 / kod0x74|GET 74|Funktion/effekt ännu okänd|uart2.42.74|
|FC / typ0x42 / kod0x75|GET 75|Funktion/effekt ännu okänd|uart2.42.75|
|FC / typ0x42 / kod0x76|GET 76|Funktion/effekt ännu okänd|uart2.42.76|
|FC / typ0x42 / kod0x77|GET 77|Funktion/effekt ännu okänd|uart2.42.77|
|FC / typ0x42 / kod0x78|GET 78|Funktion/effekt ännu okänd|uart2.42.78|
|FC / typ0x42 / kod0x79|Heating pump configured level, within settings block|CFB18 changes session flags; FF is not level zero|uart2.42.79|
|FC / typ0x42 / kod0x7A|GET 7a|Funktion/effekt ännu okänd|uart2.42.7a|
|FC / typ0x42 / kod0x7B|GET 7b|Funktion/effekt ännu okänd|uart2.42.7b|
|FC / typ0x42 / kod0x7C|GET 7c|Funktion/effekt ännu okänd|uart2.42.7c|
|FC / typ0x42 / kod0x7D|GET 7d|Funktion/effekt ännu okänd|uart2.42.7d|
|FC / typ0x42 / kod0x7E|GET 7e|Funktion/effekt ännu okänd|uart2.42.7e|
|FC / typ0x42 / kod0xA1|GET a1|Funktion/effekt ännu okänd|uart2.42.a1|
|FC / typ0x42 / kod0xA2|GET a2|Funktion/effekt ännu okänd|uart2.42.a2|
|FC / typ0x42 / kod0xA3|Service selector/result gateway|Classified local or forwarded job; same-selector polling can read pending/cache; some energy selectors mutate counters|uart2.42.a3|
|FC / typ0x42 / kod0xC8|GET c8|Funktion/effekt ännu okänd|uart2.42.c8|
|FC / typ0x5B / kod0xC9|About/configuration C9 through alternate frame type|downstream effects unqualified|uart2.frame.5b|
|FC / typ0x5C / kod0xCC|CC frame family5C|Funktion/effekt ännu okänd|uart2.frame.5c|
|FC / typ0x5D / kod0xCC|CC frame family5D|Funktion/effekt ännu okänd|uart2.frame.5d|
|frame="02" (hex); type_position=3 (decimal); type="00" (hex)|Alternate02 frame subfamily00|Funktion/effekt ännu okänd|uart2.frame.02.00|
|frame="02" (hex); type_position=3 (decimal); type="01" (hex)|Alternate02 frame subfamily01|Funktion/effekt ännu okänd|uart2.frame.02.01|

Port- och protokollunderlag: [cn105-new-capabilities.md](cn105-new-capabilities.md). Fält, villkor och återstående luckor finns i JSON-katalogen och kommandomatrisen.

## source-software – CN3C candidate

Alla kända poster på denna väg. Okänd funktion betyder att rutten är identifierad men ännu inte semantiskt kartlagd.

|Kod / underkod|Funktion|Vad den gör / känd effekt|Spårnings-ID|
|---|---|---|---|
|direction="RX"; type_low_five_bits="1D" (hex); length=6 (decimal)|Forwarded service-result envelope|Funktion/effekt ännu okänd|source.service-result.1d|
|b3.bits5..5=0x0; b4.bits6..6=0x0|Source packet template 82a7a|Funktion/effekt ännu okänd|source.packet.82a7a|
|b3.bits5..5=0x0; b4.bits6..6=0x1|Source packet template 82af2|Funktion/effekt ännu okänd|source.packet.82af2|
|b3.bits5..5=0x1; b4.bits6..6=0x0|Source packet template 82b34|Funktion/effekt ännu okänd|source.packet.82b34|
|b3.bits5..5=0x1; b4.bits6..6=0x1|Source packet template 82b70|Funktion/effekt ännu okänd|source.packet.82b70|
|b0.bits0..4=0x5; b2.bits6..7=0x0|Native demand packet, family05 variant0|Funktion/effekt ännu okänd|source.packet.82b94|
|b0.bits0..4=0x5; b2.bits6..7=0x2|Source packet template 82be2|Funktion/effekt ännu okänd|source.packet.82be2|
|b0.bits0..4=0x5; b2.bits6..7=0x1|Target/return/feedback/flow packet, family05 variant1|Encodes selected temperatures and nonlinear primary-flow value; not direct compressor-Hz control|source.packet.82c2a|
|b0.bits0..4=0x5; b2.bits6..7=0x3|Source packet template 82c60|Funktion/effekt ännu okänd|source.packet.82c60|
|b0.bits0..4=0x19; b1.bits4..4=0x1|Source packet template 82c7e|Funktion/effekt ännu okänd|source.packet.82c7e|
|b0.bits0..4=0x19; b1.bits4..4=0x0|Source packet template 82cb4|Funktion/effekt ännu okänd|source.packet.82cb4|
|Ingen fast kod identifierad; se fältlayout|Source packet template 82cea|Funktion/effekt ännu okänd|source.packet.82cea|
|b0.bits0..4=0xD|Source packet template 82d0e|Funktion/effekt ännu okänd|source.packet.82d0e|
|b0.bits0..4=0x11; b1.bits4..5=0x1; b1.bits6..7=0x0|Source packet template 82d32|Funktion/effekt ännu okänd|source.packet.82d32|
|b0.bits0..4=0x11; b1.bits6..7=0x2; b4.bits0..7=0x2|Source packet template 82d6e|Funktion/effekt ännu okänd|source.packet.82d6e|
|b0.bits0..4=0x11; b1.bits6..7=0x2; b4.bits0..7=0x2|Source packet template 82daa|Funktion/effekt ännu okänd|source.packet.82daa|
|b0.bits0..4=0x11; b1.bits6..7=0x1; b3.bits6..6=0x1; b3.bits7..7=0x1|Source packet template 82de0|Funktion/effekt ännu okänd|source.packet.82de0|
|b0.bits0..4=0x11; b1.bits6..7=0x3|Source packet template 82e28|Funktion/effekt ännu okänd|source.packet.82e28|
|b0.bits0..4=0x10|Source packet template 82e76|Funktion/effekt ännu okänd|source.packet.82e76|
|Ingen fast kod identifierad; se fältlayout|Source packet template 82e94|Funktion/effekt ännu okänd|source.packet.82e94|
|b0.bits0..4=0x14|Source packet template 82ed0|Funktion/effekt ännu okänd|source.packet.82ed0|
|b0.bits0..4=0x1C|Queued source service request template|Funktion/effekt ännu okänd|source.packet.82eee|
|Ingen fast kod identifierad; se fältlayout|Source packet template 82f24|Funktion/effekt ännu okänd|source.packet.82f24|
|b0.bits0..4=0x15; b0.bits5..7=0x1|Source packet template 82f3c|Funktion/effekt ännu okänd|source.packet.82f3c|
|b0.bits0..4=0x15; b0.bits5..7=0x1|Source packet template 82f6c|Funktion/effekt ännu okänd|source.packet.82f6c|
|b0.bits0..4=0x15; b0.bits5..7=0x1|Source packet template 82f9c|Funktion/effekt ännu okänd|source.packet.82f9c|
|b0.bits0..4=0x15; b0.bits5..7=0x1|Source packet template 82fcc|Funktion/effekt ännu okänd|source.packet.82fcc|
|b0.bits0..4=0x15; b0.bits5..7=0x2|Source packet template 82ffc|Funktion/effekt ännu okänd|source.packet.82ffc|
|b0.bits0..4=0x15; b0.bits5..7=0x2|Source packet template 8302c|Funktion/effekt ännu okänd|source.packet.8302c|
|b0.bits0..4=0x15; b0.bits5..7=0x2|Source packet template 8305c|Funktion/effekt ännu okänd|source.packet.8305c|
|b0.bits0..4=0x15; b0.bits5..7=0x4|Source packet template 8308c|Funktion/effekt ännu okänd|source.packet.8308c|
|b0.bits0..4=0x15; b0.bits5..7=0x4|Source packet template 830bc|Funktion/effekt ännu okänd|source.packet.830bc|
|b0.bits0..4=0x15; b0.bits5..7=0x3|Source packet template 830ec|Funktion/effekt ännu okänd|source.packet.830ec|
|b0.bits0..4=0x15; b0.bits5..7=0x3|Source packet template 8311c|Funktion/effekt ännu okänd|source.packet.8311c|
|b0.bits0..4=0x15; b0.bits5..7=0x5|Source packet template 8314c|Funktion/effekt ännu okänd|source.packet.8314c|
|b0.bits0..4=0x15; b0.bits5..7=0x5|Source packet template 8317c|Funktion/effekt ännu okänd|source.packet.8317c|
|b0.bits0..4=0x15; b0.bits5..7=0x0|Source packet template 831ac|Funktion/effekt ännu okänd|source.packet.831ac|
|b0.bits0..4=0x15; b0.bits5..7=0x0|Source packet template 831dc|Funktion/effekt ännu okänd|source.packet.831dc|

Port- och protokollunderlag: [source-link.md](source-link.md). Fält, villkor och återstående luckor finns i JSON-katalogen och kommandomatrisen.

## d – CN22 candidate

Alla kända poster på denna väg. Okänd funktion betyder att rutten är identifierad men ännu inte semantiskt kartlagd.

|Kod / underkod|Funktion|Vad den gör / känd effekt|Spårnings-ID|
|---|---|---|---|
|utökad väljare 1..1 (decimal); extended.bit0=1|Extended settings selectors 1..1|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.00|
|utökad väljare 2..4 (decimal); extended.bit0=1|Extended settings selectors 2..4|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.01|
|utökad väljare 5..9 (decimal); extended.bit0=1|Extended settings selectors 5..9|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.02|
|utökad väljare 51..53 (decimal); extended.bit0=1|Extended settings selectors 51..53|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.03|
|utökad väljare 54..56 (decimal); extended.bit0=1|Extended settings selectors 54..56|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.04|
|utökad väljare 101..135 (decimal); extended.bit0=1|Extended settings selectors 101..135|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.05|
|utökad väljare 151..178 (decimal); extended.bit0=1|Extended settings selectors 151..178|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.06|
|utökad väljare 201..235 (decimal); extended.bit0=1|Extended settings selectors 201..235|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.07|
|utökad väljare 251..278 (decimal); extended.bit0=1|Extended settings selectors 251..278|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.08|
|utökad väljare 301..363 (decimal); extended.bit0=1|Extended settings selectors 301..363|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.09|
|utökad väljare 401..435 (decimal); extended.bit0=1|Extended settings selectors 401..435|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.10|
|utökad väljare 500..500 (decimal); extended.bit0=1|Extended settings selectors 500..500|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.11|
|utökad väljare 364..398 (decimal); extended.bit0=1|Extended settings selectors 364..398|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.12|
|utökad väljare 21..48 (decimal); extended.bit0=1|Extended settings selectors 21..48|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.13|
|utökad väljare 501..503 (decimal); extended.bit0=1|Extended settings selectors 501..503|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.14|
|utökad väljare 511..514 (decimal); extended.bit0=1|Extended settings selectors 511..514|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.15|
|utökad väljare 521..522 (decimal); extended.bit0=1|Extended settings selectors 521..522|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.16|
|utökad väljare 524..524 (decimal); extended.bit0=1|Extended settings selectors 524..524|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.17|
|utökad väljare 551..558 (decimal); extended.bit0=1|Extended settings selectors 551..558|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.18|
|utökad väljare 571..573 (decimal); extended.bit0=1|Extended settings selectors 571..573|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.19|
|utökad väljare 581..590 (decimal); extended.bit0=1|Extended settings selectors 581..590|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.20|
|utökad väljare 601..602 (decimal); extended.bit0=1|Extended settings selectors 601..602|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.21|
|utökad väljare 651..685 (decimal); extended.bit0=1|Extended settings selectors 651..685|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.22|
|utökad väljare 701..735 (decimal); extended.bit0=1|Extended settings selectors 701..735|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.23|
|utökad väljare 751..785 (decimal); extended.bit0=1|Extended settings selectors 751..785|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.24|
|utökad väljare 801..807 (decimal); extended.bit0=1|Extended settings selectors 801..807|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.25|
|utökad väljare 10..16 (decimal); extended.bit0=1|Extended settings selectors 10..16|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.26|
|utökad väljare 811..873 (decimal); extended.bit0=1|Extended settings selectors 811..873|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.27|
|utökad väljare 874..936 (decimal); extended.bit0=1|Extended settings selectors 874..936|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.28|
|utökad väljare 937..999 (decimal); extended.bit0=1|Extended settings selectors 937..999|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.29|
|utökad väljare 451..485 (decimal); extended.bit0=1|Extended settings selectors 451..485|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.30|
|utökad väljare 61..95 (decimal); extended.bit0=1|Extended settings selectors 61..95|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.31|
|utökad väljare 611..638 (decimal); extended.bit0=1|Extended settings selectors 611..638|Direction1 mutates staged data; handler sets0868 to cancel native service request|d.transfer.range.32|
|intern service 1005 (decimal), wirekod ej fristående fastställd|Internal settings-session pending-request advertisement|No persistent write established in this helper|d.settings.advertisement1005|
|utökad väljare0; intern markör0x4000|Extended settings event selector zero supplies end marker|Funktion/effekt ännu okänd|d.settings.extended-end|

Port- och protokollunderlag: [settings-d-events.md](settings-d-events.md). Fält, villkor och återstående luckor finns i JSON-katalogen och kommandomatrisen.

## uart6 – CNRF candidate

Alla kända poster på denna väg. Okänd funktion betyder att rutten är identifierad men ännu inte semantiskt kartlagd.

|Kod / underkod|Funktion|Vad den gör / känd effekt|Spårnings-ID|
|---|---|---|---|
|frame="FC" (hex); type="48" (hex); reply_type="68" (hex); header="04 03" (hex); direction="peer→FTC"|room reports|updates reports and selected requested state|uart6.command.48|
|frame="FC" (hex); type="49" (hex); reply_type="69" (hex); header="04 03" (hex); direction="peer→FTC"|room reports and target selection|updates reports and selected requested state|uart6.command.49|
|frame="FC" (hex); type="4a" (hex); reply_type="6a" (hex); header="04 03" (hex); direction="peer→FTC"|room reports and DHW boost|updates reports and selected requested state|uart6.command.4a|
|frame="FC" (hex); type="4b" (hex); reply_type="6b" (hex); header="04 03" (hex); direction="peer→FTC"|room reports and holiday|updates reports and selected requested state|uart6.command.4b|
|frame="FC" (hex); type="4c" (hex); reply_type="6c" (hex); header="04 03" (hex); direction="peer→FTC"|receiver status masks|updates reports and selected requested state|uart6.command.4c|
|type="5a" (hex); reply="7a"; payload0="ca"; header="04 03" (hex)|accessory connect|updates 3F28.bit0|uart6.connect|

Port- och protokollunderlag: [uart6-room-path.md](uart6-room-path.md). Fält, villkor och återstående luckor finns i JSON-katalogen och kommandomatrisen.

## uart0 – CN108/storage candidate

Alla kända poster på denna väg. Okänd funktion betyder att rutten är identifierad men ännu inte semantiskt kartlagd.

|Kod / underkod|Funktion|Vad den gör / känd effekt|Spårnings-ID|
|---|---|---|---|
|operation0x00; lokalt mall-ID 0 (decimal); Z:\DUMMY\DUMMY.DAT|default Z:\DUMMY\DUMMY.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.00|
|operation0x52; lokalt mall-ID 1 (decimal); Z:\DUMMY\DUMMY.DAT|read file Z:\DUMMY\DUMMY.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.01|
|operation0x57; lokalt mall-ID 2 (decimal); Z:\DUMMY\DUMMY.DAT|write file Z:\DUMMY\DUMMY.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.02|
|operation0x53; lokalt mall-ID 3 (decimal); Z:\DUMMY\DUMMY.DAT|status/control Z:\DUMMY\DUMMY.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.03|
|operation0x46; lokalt mall-ID 4 (decimal); Z:\DUMMY\DUMMY.DAT|status/control Z:\DUMMY\DUMMY.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.04|
|operation0x57; lokalt mall-ID 5 (decimal); A:\LOG\YYYY\MM\DD\HHMMSS.LOG|write file A:\LOG\YYYY\MM\DD\HHMMSS.LOG|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.05|
|operation0x52; lokalt mall-ID 6 (decimal); A:\SETTING\6_HW.DAT|read file A:\SETTING\6_HW.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.06|
|operation0x52; lokalt mall-ID 7 (decimal); A:\SETTING\6_AC.DAT|read file A:\SETTING\6_AC.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.07|
|operation0x52; lokalt mall-ID 8 (decimal); A:\SETTING\6_S1_1.DAT|read file A:\SETTING\6_S1_1.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.08|
|operation0x52; lokalt mall-ID 9 (decimal); A:\SETTING\6_S1_2.DAT|read file A:\SETTING\6_S1_2.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.09|
|operation0x52; lokalt mall-ID 10 (decimal); A:\SETTING\6_S1_3.DAT|read file A:\SETTING\6_S1_3.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.10|
|operation0x52; lokalt mall-ID 11 (decimal); A:\SETTING\6_S1_4.DAT|read file A:\SETTING\6_S1_4.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.11|
|operation0x52; lokalt mall-ID 12 (decimal); A:\SETTING\6_S1_5.DAT|read file A:\SETTING\6_S1_5.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.12|
|operation0x52; lokalt mall-ID 13 (decimal); A:\SETTING\6_HOL.DAT|read file A:\SETTING\6_HOL.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.13|
|operation0x52; lokalt mall-ID 14 (decimal); A:\SETTING\6_INI.DAT|read file A:\SETTING\6_INI.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.14|
|operation0x52; lokalt mall-ID 15 (decimal); A:\SETTING\6_SER1.DAT|read file A:\SETTING\6_SER1.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.15|
|operation0x52; lokalt mall-ID 16 (decimal); A:\SETTING\6_SER2.DAT|read file A:\SETTING\6_SER2.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.16|
|operation0x52; lokalt mall-ID 17 (decimal); A:\SETTING\6_S2_1.DAT|read file A:\SETTING\6_S2_1.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.17|
|operation0x52; lokalt mall-ID 18 (decimal); A:\SETTING\6_S2_2.DAT|read file A:\SETTING\6_S2_2.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.18|
|operation0x52; lokalt mall-ID 19 (decimal); A:\SETTING\6_S2_3.DAT|read file A:\SETTING\6_S2_3.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.19|
|operation0x52; lokalt mall-ID 20 (decimal); A:\SETTING\6_S2_4.DAT|read file A:\SETTING\6_S2_4.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.20|
|operation0x52; lokalt mall-ID 21 (decimal); A:\SETTING\6_S2_5.DAT|read file A:\SETTING\6_S2_5.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.21|
|operation0x57; lokalt mall-ID 22 (decimal); A:\SETTING\6_HW.DAT|write file A:\SETTING\6_HW.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.22|
|operation0x57; lokalt mall-ID 23 (decimal); A:\SETTING\6_AC.DAT|write file A:\SETTING\6_AC.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.23|
|operation0x57; lokalt mall-ID 24 (decimal); A:\SETTING\6_S1_1.DAT|write file A:\SETTING\6_S1_1.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.24|
|operation0x57; lokalt mall-ID 25 (decimal); A:\SETTING\6_S1_2.DAT|write file A:\SETTING\6_S1_2.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.25|
|operation0x57; lokalt mall-ID 26 (decimal); A:\SETTING\6_S1_3.DAT|write file A:\SETTING\6_S1_3.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.26|
|operation0x57; lokalt mall-ID 27 (decimal); A:\SETTING\6_S1_4.DAT|write file A:\SETTING\6_S1_4.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.27|
|operation0x57; lokalt mall-ID 28 (decimal); A:\SETTING\6_S1_5.DAT|write file A:\SETTING\6_S1_5.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.28|
|operation0x57; lokalt mall-ID 29 (decimal); A:\SETTING\6_HOL.DAT|write file A:\SETTING\6_HOL.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.29|
|operation0x57; lokalt mall-ID 30 (decimal); A:\SETTING\6_INI.DAT|write file A:\SETTING\6_INI.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.30|
|operation0x57; lokalt mall-ID 31 (decimal); A:\SETTING\6_SER1.DAT|write file A:\SETTING\6_SER1.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.31|
|operation0x57; lokalt mall-ID 32 (decimal); A:\SETTING\6_SER2.DAT|write file A:\SETTING\6_SER2.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.32|
|operation0x57; lokalt mall-ID 33 (decimal); A:\SETTING\6_S2_1.DAT|write file A:\SETTING\6_S2_1.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.33|
|operation0x57; lokalt mall-ID 34 (decimal); A:\SETTING\6_S2_2.DAT|write file A:\SETTING\6_S2_2.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.34|
|operation0x57; lokalt mall-ID 35 (decimal); A:\SETTING\6_S2_3.DAT|write file A:\SETTING\6_S2_3.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.35|
|operation0x57; lokalt mall-ID 36 (decimal); A:\SETTING\6_S2_4.DAT|write file A:\SETTING\6_S2_4.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.36|
|operation0x57; lokalt mall-ID 37 (decimal); A:\SETTING\6_S2_5.DAT|write file A:\SETTING\6_S2_5.DAT|read can import staged settings; write sends file/log; not a pure heat-control protocol|uart0.transaction.37|

Port- och protokollunderlag: [uart0-storage-path.md](uart0-storage-path.md). Fält, villkor och återstående luckor finns i JSON-katalogen och kommandomatrisen.

## uart1 – CNIT candidate

Alla kända poster på denna väg. Okänd funktion betyder att rutten är identifierad men ännu inte semantiskt kartlagd.

|Kod / underkod|Funktion|Vad den gör / känd effekt|Spårnings-ID|
|---|---|---|---|
|low_nibble=0 (decimal); length=5 (decimal); checksum="sum0"|Diagnostic session open|sets3D4C session|uart1.diag.open|
|low_nibble=1 (decimal); address="bytes1..3 little endian"; length="high nibble lookup832BE:1,2,4,8,16,32,64,then1"|Near16 memory read despite wide request|reading MMIO could have effects; not a flash dump|uart1.diag.read|
|low_nibble=2 (decimal); subcommand="f0" (hex)|Drain diagnostic log|drains8 usable12-byte records; overflow drops; checksum absent from captured22-byteCN105|uart1.diag.log|
|low_nibble_range=[3, 15]|Diagnostic close/default low nibble|resets diagnostic session|uart1.diag.close|
|command="52"; address="packed14 bits"|Normal personality memory/translation read|Funktion/effekt ännu okänd|uart1.normal.52|
|command="45"|Blocking service loop E|sustained service loop changes scheduler behavior|uart1.normal.45|
|command="46"|Blocking service loop F|sustained service loop changes scheduler behavior|uart1.normal.46|
|byte0="12"; subcommand_byte1="00"; response_type="12"; response_length=100 (decimal)|Plant status and sensor snapshot|not fully qualified; instruction audit required for packed bit fields|uart1.diag.12.00|
|byte0="12"; subcommand_byte1="01"; response_type="12"; response_length=66 (decimal)|Controller states and primary flow snapshot|not fully qualified; instruction audit required for packed bit fields|uart1.diag.12.01|
|byte0="12"; subcommand_byte1="02"; response_type="12"; response_length=62 (decimal)|Actuator and native request snapshot|not fully qualified; instruction audit required for packed bit fields|uart1.diag.12.02|
|byte0="12"; subcommand_byte1="10"; response_type="12"; response_length=13 (decimal)|Packed operation flags|not fully qualified; instruction audit required for packed bit fields|uart1.diag.12.10|

Port- och protokollunderlag: [uart1-snapshots.md](uart1-snapshots.md). Fält, villkor och återstående luckor finns i JSON-katalogen och kommandomatrisen.

## Serviceval och interna serviceklasser

Dessa är underkoder/klassificeringsintervall, inte nya fysiska portar. CN105 A3 använder den gemensamma tjänsten; vissa val är lokala, andra vidarebefordras. Interna val är inte automatiskt tillgängliga via A3. Klassintervall överlappar enskilda val och ska inte dubbelräknas.

|Kod (decimal om numerisk)|Funktion|Effekt|Nåbarhet / villkor|ID|
|---|---|---|---|---|
|{"selector_range": [0, 149]}|Service class 1 interval 0–149|Okänd|internal classifier; UNKNOWN|service.class.00|
|{"selector_range": [150, 199]}|Service class 2 interval 150–199|Okänd|internal classifier; UNKNOWN|service.class.01|
|{"selector_range": [200, 299]}|Service class 1 interval 200–299|Okänd|internal classifier; UNKNOWN|service.class.02|
|{"selector_range": [300, 399]}|Service class 2 interval 300–399|Okänd|internal classifier; UNKNOWN|service.class.03|
|{"selector_range": [400, 499]}|Service class 1 interval 400–499|Okänd|internal classifier; UNKNOWN|service.class.04|
|{"selector_range": [500, 599]}|Service class 2 interval 500–599|Okänd|internal classifier; UNKNOWN|service.class.05|
|{"selector_range": [600, 763]}|Service class 1 interval 600–763|Okänd|internal classifier; UNKNOWN|service.class.06|
|{"selector_range": [764, 764]}|Service class 4 interval 764–764|Okänd|internal classifier; UNKNOWN|service.class.07|
|{"selector_range": [765, 766]}|Service class 3 interval 765–766|Okänd|internal classifier; UNKNOWN|service.class.08|
|{"selector_range": [767, 767]}|Service class 5 interval 767–767|Okänd|internal classifier; UNKNOWN|service.class.09|
|{"selector_range": [768, 949]}|Service class 0 interval 768–949|Okänd|internal classifier; UNKNOWN|service.class.10|
|{"selector_range": [950, 950]}|Service class 7 interval 950–950|Okänd|internal classifier; UNKNOWN|service.class.11|
|{"selector_range": [951, 951]}|Service class 9 interval 951–951|Okänd|internal classifier; UNKNOWN|service.class.12|
|{"selector_range": [952, 999]}|Service class 0 interval 952–999|Okänd|internal classifier; UNKNOWN|service.class.13|
|{"selector_range": [1000, 1001]}|Service class 2 interval 1000–1001|Okänd|internal classifier; UNKNOWN|service.class.14|
|{"selector_range": [1002, 1002]}|Service class 11 interval 1002–1002|Okänd|internal classifier; UNKNOWN|service.class.15|
|{"selector_range": [1003, 1005]}|Service class 12 interval 1003–1005|Okänd|internal classifier; UNKNOWN|service.class.16|
|{"selector_range": [1006, 1009]}|Service class 1 interval 1006–1009|Okänd|internal classifier; UNKNOWN|service.class.17|
|{"selector_range": [1010, 1011]}|Service class 2 interval 1010–1011|Okänd|internal classifier; UNKNOWN|service.class.18|
|{"selector_range": [1012, 1016]}|Service class 1 interval 1012–1016|Okänd|internal classifier; UNKNOWN|service.class.19|
|{"selector_range": [1017, 1017]}|Service class 10 interval 1017–1017|Okänd|internal classifier; UNKNOWN|service.class.20|
|{"selector_range": [1018, 1020]}|Service class 8 interval 1018–1020|Okänd|internal classifier; UNKNOWN|service.class.21|
|{"selector_range": [1021, 1021]}|Service class 4 interval 1021–1021|Okänd|internal classifier; UNKNOWN|service.class.22|
|{"selector_range": [1022, 1022]}|Service class 5 interval 1022–1022|Okänd|internal classifier; UNKNOWN|service.class.23|
|{"selector_range": [1023, 1023]}|Service class 6 interval 1023–1023|Okänd|internal classifier; UNKNOWN|service.class.24|
|{"selector_range": [1024, 65535]}|Service class 0 interval 1024–65535|Okänd|internal classifier; UNKNOWN|service.class.25|
|{"selector": 154, "class": 2}|Local service 154|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.154|
|{"selector": 155, "class": 2}|Local service 155|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.155|
|{"selector": 156, "class": 2}|Local service 156|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.156|
|{"selector": 157, "class": 2}|Local service 157|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.157|
|{"selector": 158, "class": 2}|Local service 158|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.158|
|{"selector": 160, "class": 2}|Local service 160|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.160|
|{"selector": 161, "class": 2}|Local service 161|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.161|
|{"selector": 162, "class": 2}|Local service 162|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.162|
|{"selector": 163, "class": 2}|Local service 163|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.163|
|{"selector": 164, "class": 2}|Local service 164|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.164|
|{"selector": 165, "class": 2}|Local service 165|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.165|
|{"selector": 166, "class": 2}|Local service 166|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.166|
|{"selector": 175, "class": 2}|Local service 175|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.175|
|{"selector": 176, "class": 2}|Local service 176|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.176|
|{"selector": 177, "class": 2}|Local service 177|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.177|
|{"selector": 178, "class": 2}|Local service 178|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.178|
|{"selector": 179, "class": 2}|Local service 179|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.179|
|{"selector": 185, "class": 2}|Local service 185|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.185|
|{"selector": 186, "class": 2}|Local service 186|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.186|
|{"selector": 190, "class": 2}|Local service 190|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.190|
|{"selector": 191, "class": 2}|Local service 191|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.191|
|{"selector": 340, "class": 2}|Local service 340|Sets manual/state flag in 3ADC..3AE0|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.340|
|{"selector": 341, "class": 2}|Local service 341|Sets manual/state flag in 3ADC..3AE0|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.341|
|{"selector": 342, "class": 2}|Local service 342|Sets manual/state flag in 3ADC..3AE0|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.342|
|{"selector": 343, "class": 2}|Local service 343|Sets manual/state flag in 3ADC..3AE0|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.343|
|{"selector": 344, "class": 2}|Local service 344|Sets manual/state flag in 3ADC..3AE0|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.344|
|{"selector": 350, "class": 2}|Local service 350|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.350|
|{"selector": 351, "class": 2}|Local service 351|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.351|
|{"selector": 352, "class": 2}|Local service 352|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.352|
|{"selector": 353, "class": 2}|Local service 353|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.353|
|{"selector": 354, "class": 2}|Local service 354|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.354|
|{"selector": 355, "class": 2}|Local service 355|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.355|
|{"selector": 356, "class": 2}|Local service 356|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.356|
|{"selector": 357, "class": 2}|Local service 357|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.357|
|{"selector": 358, "class": 2}|Local service 358|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.358|
|{"selector": 359, "class": 2}|Local service 359|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.359|
|{"selector": 360, "class": 2}|Local service 360|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.360|
|{"selector": 361, "class": 2}|Local service 361|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.361|
|{"selector": 362, "class": 2}|Local service 362|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.362|
|{"selector": 363, "class": 2}|Local service 363|Manual output action, changes 3A76 and output request fields|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.363|
|{"selector": 500, "class": 2}|Local service 500|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.500|
|{"selector": 501, "class": 2}|Local service 501|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.501|
|{"selector": 502, "class": 2}|Local service 502|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.502|
|{"selector": 503, "class": 2}|Local service 503|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.503|
|{"selector": 504, "class": 2}|Local service 504|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.504|
|{"selector": 505, "class": 2}|Local service 505|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.505|
|{"selector": 506, "class": 2}|Local service 506|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.506|
|{"selector": 507, "class": 2}|Local service 507|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.507|
|{"selector": 508, "class": 2}|Local service 508|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.508|
|{"selector": 509, "class": 2}|Local service 509|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.509|
|{"selector": 510, "class": 2}|Local service 510|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.510|
|{"selector": 511, "class": 2}|Local service 511|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.511|
|{"selector": 512, "class": 2}|Local service 512|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.512|
|{"selector": 513, "class": 2}|Local service 513|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.513|
|{"selector": 514, "class": 2}|Local service 514|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.514|
|{"selector": 515, "class": 2}|Local service 515|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.515|
|{"selector": 516, "class": 2}|Local service 516|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.516|
|{"selector": 517, "class": 2}|Local service 517|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.517|
|{"selector": 518, "class": 2}|Local service 518|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.518|
|{"selector": 519, "class": 2}|Local service 519|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.519|
|{"selector": 520, "class": 2}|Local service 520|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.520|
|{"selector": 521, "class": 2}|Local service 521|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.521|
|{"selector": 522, "class": 2}|Local service 522|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.522|
|{"selector": 523, "class": 2}|Local service 523|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.523|
|{"selector": 524, "class": 2}|Local service 524|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.524|
|{"selector": 525, "class": 2}|Local service 525|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.525|
|{"selector": 526, "class": 2}|Local service 526|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.526|
|{"selector": 527, "class": 2}|Local service 527|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.527|
|{"selector": 528, "class": 2}|Local service 528|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.528|
|{"selector": 529, "class": 2}|Local service 529|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.529|
|{"selector": 530, "class": 2}|Local service 530|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.530|
|{"selector": 531, "class": 2}|Local service 531|Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.531|
|{"selector": 532, "class": 2}|Local service 532|Copies energy bank then clears original counters and saves date|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.532|
|{"selector": 533, "class": 2}|Local service 533|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.533|
|{"selector": 534, "class": 2}|Local service 534|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.534|
|{"selector": 535, "class": 2}|Local service 535|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.535|
|{"selector": 536, "class": 2}|Local service 536|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.536|
|{"selector": 540, "class": 2}|Local service 540|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.540|
|{"selector": 550, "class": 2}|Local service 550|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.550|
|{"selector": 551, "class": 2}|Local service 551|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.551|
|{"selector": 552, "class": 2}|Local service 552|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.552|
|{"selector": 553, "class": 2}|Local service 553|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.553|
|{"selector": 554, "class": 2}|Local service 554|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.554|
|{"selector": 555, "class": 2}|Local service 555|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.555|
|{"selector": 556, "class": 2}|Local service 556|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.556|
|{"selector": 557, "class": 2}|Local service 557|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.557|
|{"selector": 558, "class": 2}|Local service 558|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.558|
|{"selector": 559, "class": 2}|Local service 559|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.559|
|{"selector": 560, "class": 2}|Local service 560|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.560|
|{"selector": 561, "class": 2}|Local service 561|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.561|
|{"selector": 562, "class": 2}|Local service 562|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.562|
|{"selector": 563, "class": 2}|Local service 563|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.563|
|{"selector": 564, "class": 2}|Local service 564|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.564|
|{"selector": 565, "class": 2}|Local service 565|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.565|
|{"selector": 566, "class": 2}|Local service 566|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.566|
|{"selector": 567, "class": 2}|Local service 567|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.567|
|{"selector": 568, "class": 2}|Local service 568|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.568|
|{"selector": 569, "class": 2}|Local service 569|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.569|
|{"selector": 570, "class": 2}|Local service 570|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.570|
|{"selector": 571, "class": 2}|Local service 571|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.571|
|{"selector": 572, "class": 2}|Local service 572|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.572|
|{"selector": 573, "class": 2}|Local service 573|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.573|
|{"selector": 574, "class": 2}|Local service 574|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.574|
|{"selector": 1000, "class": 2}|Local service 1000|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.1000|
|{"selector": 1001, "class": 2}|Local service 1001|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.1001|
|{"selector": 1003, "class": 12}|Local service 1003|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.1003|
|{"selector": 1004, "class": 12}|Local service 1004|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.1004|
|{"selector": 1005, "class": 12}|Local service 1005|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.1005|
|{"selector": 1010, "class": 2}|Local service 1010|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.1010|
|{"selector": 1011, "class": 2}|Local service 1011|Unresolved beyond local handler|local branch proven; external eligibility separate; CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105|service.local.1011|

## Råkoder till interna händelser

Råkoder är hex; normaliserade händelser är decimal. Historik kan undertrycka eller ändra resultatet. D TX är lokala sändningsnotifieringar, inte inkommande kommandon. Dessa rader kan överlappa paketfamiljer ovan.

|Väg / portkandidat|Råkod|Intern händelse|Kandidat / funktion|
|---|---|---|---|
|source_rx / CN3C|0x00|1|source.dispatch.00; funktion ej fullständigt fastställd; 9ce33|
|source_rx / CN3C|0x01|6|source.dispatch.05; funktion ej fullständigt fastställd; 9ce07|
|source_rx / CN3C|0x02|11|source.dispatch.10; funktion ej fullständigt fastställd; 9ce07|
|source_rx / CN3C|0x03|15|source.dispatch.14; funktion ej fullständigt fastställd; 9cd8c|
|source_rx / CN3C|0x04|2|source.dispatch.01; funktion ej fullständigt fastställd; 9ce1a|
|source_rx / CN3C|0x05|7|source.dispatch.06; funktion ej fullständigt fastställd; 9cda5|
|source_rx / CN3C|0x06|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x07|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x08|3|source.dispatch.02; funktion ej fullständigt fastställd; 9cee3|
|source_rx / CN3C|0x09|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x0a|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x0b|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x0c|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x0d|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x0e|12|source.dispatch.11; funktion ej fullständigt fastställd; 9cec7|
|source_rx / CN3C|0x0f|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x10|4|source.dispatch.03; funktion ej fullständigt fastställd; 9ceaf|
|source_rx / CN3C|0x11|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x12|13|source.dispatch.12; funktion ej fullständigt fastställd; 9ce97|
|source_rx / CN3C|0x13|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x14|5|source.dispatch.04; funktion ej fullständigt fastställd; 9ce7e|
|source_rx / CN3C|0x15|8|source.dispatch.07; funktion ej fullständigt fastställd; 9ce4c|
|source_rx / CN3C|0x16|14|source.dispatch.13; funktion ej fullständigt fastställd; 9ce65|
|source_rx / CN3C|0x17|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x18|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x19|9|source.dispatch.08; funktion ej fullständigt fastställd; 9cdd6|
|source_rx / CN3C|0x1a|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x1b|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x1c|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x1d|10|source.dispatch.09; funktion ej fullständigt fastställd; 9cefb|
|source_rx / CN3C|0x1e|0|Ingen normaliserad händelse|
|source_rx / CN3C|0x1f|0|Ingen normaliserad händelse|
|d_tx_event / CN22|0x00|18|d.dispatch.17; funktion ej fullständigt fastställd; 9f60e|
|d_tx_event / CN22|0x01|0|Ingen normaliserad händelse|
|d_tx_event / CN22|0x02|17|d.dispatch.16; funktion ej fullständigt fastställd; 9f61e|
|d_tx_event / CN22|0x03|0|Ingen normaliserad händelse|
|d_tx_event / CN22|0x04|23|d.dispatch.22; funktion ej fullständigt fastställd; 9f60e|
|d_tx_event / CN22|0x05|0|Ingen normaliserad händelse|
|d_tx_event / CN22|0x06|16|d.dispatch.15; funktion ej fullständigt fastställd; 9f61e|
|d_tx_event / CN22|0x07|0|Ingen normaliserad händelse|
|d_tx_event / CN22|0x08|20|d.dispatch.19; funktion ej fullständigt fastställd; 9f60e|
|d_tx_event / CN22|0x09|0|Ingen normaliserad händelse|
|d_tx_event / CN22|0x0a|24|d.dispatch.23; funktion ej fullständigt fastställd; 9f60e|
|d_tx_event / CN22|0x0b|0|Ingen normaliserad händelse|
|d_tx_event / CN22|0x0c|22|d.dispatch.21; funktion ej fullständigt fastställd; 9f60e|
|d_tx_event / CN22|0x0d|0|Ingen normaliserad händelse|
|d_tx_event / CN22|0x0e|21|d.dispatch.20; funktion ej fullständigt fastställd; 9f60e|
|d_tx_event / CN22|0x0f|0|Ingen normaliserad händelse|
|d_rx / CN22|0x00|5|d.dispatch.04; funktion ej fullständigt fastställd; 9f446|
|d_rx / CN22|0x01|1|d.dispatch.00; funktion ej fullständigt fastställd; 9f34c|
|d_rx / CN22|0x02|4|d.dispatch.03; funktion ej fullständigt fastställd; 9f405|
|d_rx / CN22|0x03|0|Ingen normaliserad händelse|
|d_rx / CN22|0x04|13|d.dispatch.12; funktion ej fullständigt fastställd; 9f5ae|
|d_rx / CN22|0x05|12|d.dispatch.11; funktion ej fullständigt fastställd; 9f587|
|d_rx / CN22|0x06|3|d.dispatch.02; funktion ej fullständigt fastställd; 9f3cf|
|d_rx / CN22|0x07|2|d.dispatch.01; funktion ej fullständigt fastställd; 9f393|
|d_rx / CN22|0x08|7|d.dispatch.06; funktion ej fullständigt fastställd; 9f4c9|
|d_rx / CN22|0x09|0|Ingen normaliserad händelse|
|d_rx / CN22|0x0a|15|d.dispatch.14; funktion ej fullständigt fastställd; 9f5f0|
|d_rx / CN22|0x0b|14|d.dispatch.13; funktion ej fullständigt fastställd; 9f5cc|
|d_rx / CN22|0x0c|11|d.dispatch.10; funktion ej fullständigt fastställd; 9f565|
|d_rx / CN22|0x0d|10|d.dispatch.09; funktion ej fullständigt fastställd; 9f53d|
|d_rx / CN22|0x0e|9|d.dispatch.08; funktion ej fullständigt fastställd; 9f51b|
|d_rx / CN22|0x0f|8|d.dispatch.07; funktion ej fullständigt fastställd; 9f4f5|

## Ej kommandon och återstående täckning

376 CN105 default/avvisade uppslag listas i JSON, men räknas inte som kommandon.
Interna grenar utan styrkt extern kod behålls som strukturella luckor i JSON och command-atlas.json. Ingen port eller funktion har hittats på för att fylla en tom ruta.

Källor: [portmatris](command-port-matrix.md), [maskinläsbar katalog](command-catalog.json), [rå atlas](command-atlas.json).
