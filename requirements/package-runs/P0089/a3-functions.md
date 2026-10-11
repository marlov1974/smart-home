# A3 — återstående funktioner följda

Alla koder här är decimala. Ingen kommunikation med pumparna har skett.
Den samlade listan finns i cn105-function-overview.md/json. Den omfattar 159 koder:
109 manualnamn och 50 native/korrelerade beskrivningar. **Det betyder inte att alla
159 fysiska funktioner är identifierade.** För 350–363 känner vi operationen i FTC,
men mottagarens betydelse saknas fortfarande.

## Läsfunktioner

| Kod | Namn | Belagd kedja och kvarstående gräns |
|---|---|---|
| 160 | FTC modellprofil-ID | 38BC normaliseras via tabell80FF8 i8F142 och väljer konfigurationspost88E95 i91948. Exakta modellnamn per ID återstår. |
| 161 | FTC DIP-vald hårdvaruvariant | 38BD kommer från3879 bits2–6.91948 väljer variantindex via81ADC; CE2A4 väljer även pumpens effektuppskattningstabell utifrån varianten. Det är inte en uppmätt effekt eller firmwareversion. |
| 536 | Trolig kondenserings-/mättnadstemperatur från FTC:s givarkanal | 8CC5B returnerar signed0692/100.8DDD0 räknar fram0692 från0ADC via80DF2. A59E4 skickar samma värde i GET0F bytes4–5, vilka den pinnade externa avkodaren namnger CondensingTemp. Fysisk givarbeteckning är inte oberoende verifierad. |

Rättelse: tidigare text kallade536 en temperatur från underkortsvägen.
Den påvisade producenten är FTC:s givarkonvertering. Vid0915!=1 skrivs ett
standardvärde4057; vid aktiv kanal men givarfel0A8C!=0 hoppar koden över
uppdateringen. Ett svar kan alltså vara standardvärde eller kvarhållet värde,
inte ett färskt mätvärde.536 ska inte användas som en ny brinegivare.

## Servicekommandon — inte läsningar

Alla350–363 sätter3A76=1.9D588 för över detta till sändningskön083C bit0
och kvitterar flaggan. Att dispatchergrenen svarar bevisar inte att mottagaren
har utfört kommandot. Ingen ON/OFF-betydelse antas för värden1 och2.

| Kod | FTC-operation | Återstående innebörd |
|---|---|---|
| 350 | Nolla39FE,39FF,3A00,3A01 | Nollade serviceval, inte bevisat fysiskt stopp |
| 351–357 | Sätt39FE till1–7, nolla tre övriga väljare | Sju servicelägen; exakt fysisk funktion okänd |
| 358/359 | Sätt39FF till1/2; nolla3A00/3A01 | Första hjälpfunktionen, okänd fysisk funktion |
| 360/361 | Sätt3A00 till1/2; nolla39FF/3A01 | Andra hjälpfunktionen, okänd fysisk funktion |
| 362/363 | Sätt3A01 till1/2; nolla39FF/3A00 | Tredje hjälpfunktionen, okänd fysisk funktion |

**358–363 behåller39FE.** Två serviceanrop kan därför kombineras och ska inte
antas vara fristående eller idempotenta mätfrågor.

Den indirekta tabellen82B34 har nu kopplats till väljarna.9C228 packar:

| Väljare | Logisk byte, nollbaserad | Bitar |
|---|---|---|
| 3A00 | 1 | 0–1 |
| 3A01 | 1 | 2–3 |
| 39FF | 1 | 4–5 |
| 39FE | 2 | 0–2 |

9B9A8 kan välja tabellen via intern direktväljare1E. Det är **inte A3-kod30**
eller CN105 GET1E. Den befintliga källtransporten packar/stagar via1318/084B;
port/personlighet och mottagarsidan är separata kvalificeringar.
A162A använder dessutom39FE=1..7 för flaggan39CD i den vanliga begäran;
läge1 påverkar även tidsfält39CB. Det bevisar särskild servicebehandling,
inte vilka fysiska utgångar som ska aktiveras.

## Vad som krävs för slutnamn

För350–363 behövs mottagarens avkodning av dessa servicefält, eller en
auktoritativ kommandotabell för just den mottagaren. FTC-koden slutar här vid
överföringen. Att följa fler generiska packarrutiner kan verifiera transporten
men ger inte de saknade betydelserna. Vi har inte tilldelat påhittade pump-,
ventil- eller kompressornamn.160/161 behöver en modell-/variantordlista.
536 har ett starkt korrelerat temperaturnamn men behöver givarkopplingen bekräftad.

Källor: privata native exporter8C0B4,8DDD0,8E3DE,A162A,A59E4,9D588;
nya exporter8F142,91948,8EFA2,CE2A4 iP0089/private/a3-names;
P0088/source-outgoing.md och source-tx-descriptors.json;
pinnad P0083 EcodanDecoder.cpp Process0x0F.
Binärhash och tabellbytes finns i a3-naming-evidence.json.
