# Namnregister — CN105 och A3

Alla poster inom den katalogiserade omfattningen har nu ett namn. Namn, beskrivning och säkerhetsgrad är separata. Detta betyder inte att alla fysiska funktioner är identifierade.

Namn är referensetiketter. Tekniska positionsnamn löser inte okänd fysisk betydelse. Överlappande råbytes och sammansatta fält är inte oberoende funktioner.

Omfattning: 142 kommandovägar, 159 A3-koder och 1547 fältförekomster. Andra portar och ännu inte katalogiserade fält ingår inte.

## Kommandon

| Kod | Namn | Bedömning |
|---|---|---|
| uart2.41.32 | Ställ driftläge och temperaturmål | identifierad |
| uart2.41.33 | Kvittera SET33 | namngiven del |
| uart2.41.34 | Ställ driftspärrar och extern styrning | identifierad |
| uart2.41.35 | Ställ zonernas temperaturmål | identifierad |
| uart2.41.50 | Varmvattenmål, temperaturfall och maximal körtid | namngiven del |
| uart2.41.51 | Varmvattenläge, återhämtningspaus och legionellamål | trolig |
| uart2.41.52 | Legionellacykelns tidsinställningar | trolig |
| uart2.41.53 | Zonernas värme-/kylreglerläge | identifierad |
| uart2.41.54 | Zonernas temperaturbörvärden | identifierad |
| uart2.41.55 | Värmekurvans punkter per zon | trolig |
| uart2.41.56 | Veckoprogram för värme/kyla och varmvatten | trolig |
| uart2.41.57 | Årsperiod för veckoprogram 2 | trolig |
| uart2.41.58 | Reserverad inställningsplats 58 | platshållare |
| uart2.41.59 | Semesterläge: aktivering samt start- och slutdatum | trolig |
| uart2.41.5a | Semesterlägets temperaturmål | identifierad |
| uart2.41.5b | Reserverad inställningsplats 5B | platshållare |
| uart2.41.5c | Displayens språk, temperaturenhet och temperaturvisning | trolig |
| uart2.41.5d | Kontakttelefon som visas på manöverpanelen | trolig |
| uart2.41.5e | Tidsformat, fjärrkontrollernas zontilldelning och rumsgivarval | trolig |
| uart2.41.5f | Tidsschema för val av rumsgivare per zon | trolig |
| uart2.41.60 | Kalibrering av temperaturgivare, grupp 1 | identifierad |
| uart2.41.61 | Kalibrering av temperaturgivare, grupp 2 | identifierad |
| uart2.41.62 | Kalibrering av temperaturgivare, grupp 3 | identifierad |
| uart2.41.63 | Cirkulationspumpens ekonomi- och temperaturvillkor | trolig |
| uart2.41.64 | Eltillskottets tillåtelse och fördröjningar | trolig |
| uart2.41.65 | Shuntventilens gångtid/intervall och varmvattenpumpens nivå | namngiven del |
| uart2.41.66 | Val av värmekälla och samtidig värme/varmvatten | trolig |
| uart2.41.67 | Värmeregleringens temperaturgränser och tidsintervall | namngiven del |
| uart2.41.68 | Värmepumpens temperaturhysteres | trolig |
| uart2.41.69 | Värmekällornas kapaciteter för hybridberäkning | trolig |
| uart2.41.6a | Hybridens utetemperaturgräns, pannverkningsgrad, bränslepris och elens CO2-faktor | namngiven del |
| uart2.41.6b | Pannbränslets CO2-faktor för hybridval | namngiven del |
| uart2.41.6c | Konfigurerad COP-tabell, punkter 1–6 | namngiven del |
| uart2.41.6d | Konfigurerad COP-tabell, punkter 7–12 | namngiven del |
| uart2.41.6e | Säsongsperioder för elprisschemat | trolig |
| uart2.41.6f | Elpriser 1–6 för hybridens kostnadsjämförelse | namngiven del |
| uart2.41.70 | Elpriser 7–10 för hybridens kostnadsjämförelse | namngiven del |
| uart2.41.71 | Energiberäkning: tillskott och primärpump | namngiven del |
| uart2.41.72 | Energiberäkning: extra pumpar och energikorrigering | namngiven del |
| uart2.41.73 | Flödessensorns maxvärde, varmvatten-tillskott och Normal/Fast-rumsreglering | identifierad |
| uart2.41.74 | Veckoschema för elpris i tre säsonger | trolig |
| uart2.41.75 | Golvtorkning: start-/sluttemperatur, maxtemperatur, hålltid och uppsteg | trolig |
| uart2.41.76 | Golvtorkningens stegintervall/nedsteg och externa ingångar IN4/IN5 | namngiven del |
| uart2.41.77 | Smart-grid-temperaturbidrag, termo-ON-utgång och varmvattenåterladdning | identifierad |
| uart2.41.78 | Variabelt vattenflöde och analogutgångens styrning, intervall och effekt | identifierad |
| uart2.41.79 | Pump 4:s energibidrag, värmepumpens pumpnivå, analogprioritet och minflöde | identifierad |
| uart2.41.7a | Maxflöde, hybridhysteres, buffertgivarkorrigering och smart-grid-värmeval | identifierad |
| uart2.41.7b | Smart-grid-börvärden för rekommenderad/tvingad värme och kyla | identifierad |
| uart2.41.7c | Periodisk cirkulation för värme/kyla, intervall och smart-grid-kylval | identifierad |
| uart2.41.7d | Begränsning av eltillskott och sommarlägets temperatur-/tidsgränser | namngiven del |
| uart2.41.7e | Sommarlägets tvångsstarttemperatur och schema/nivå för tyst drift | trolig |
| uart2.41.c8 | Styr inställningsöverföring | identifierad |
| uart2.42.01 | Läs styrenhetens tid | trolig |
| uart2.42.02 | Läs avfrostnings- och termostatstatus | trolig |
| uart2.42.03 | Läs fel och zonstatus | trolig |
| uart2.42.04 | Läs kompressorfrekvens och enhetsstatus | identifierad |
| uart2.42.05 | Läs värmekälla och varmvattenstatus | trolig |
| uart2.42.06 | Hybridjämförelse: kostnad, CO2 och valt elpris | namngiven del |
| uart2.42.07 | Läs effekt och förbrukningsräknare | identifierad |
| uart2.42.09 | Läs temperaturmål och gränser | trolig |
| uart2.42.0b | Läs rumstemperaturer och valda givare | identifierad |
| uart2.42.0c | Läs primärkretsens och varmvattnets temperaturer | identifierad |
| uart2.42.0d | Läs zonernas framledning och retur | trolig |
| uart2.42.0e | Läs pannans framledning och retur | trolig |
| uart2.42.0f | Läs extra temperaturgivare | trolig |
| uart2.42.10 | Läs termostater, flödesvakter och externa ingångar | identifierad |
| uart2.42.11 | Läs DIP-konfiguration | trolig |
| uart2.42.13 | Läs kompressordrift och drifttid | trolig |
| uart2.42.14 | Läs ingångar, tillskott och vattenflöde | identifierad |
| uart2.42.15 | Läs pump- och ventilstatus | identifierad |
| uart2.42.16 | Läs extra pumpars status | trolig |
| uart2.42.17 | Läs givarfel, övertemperatur och frysrisk | namngiven del |
| uart2.42.18 | Läs temperaturrespons och cirkulationsfel | namngiven del |
| uart2.42.19 | Driftskydd, värmekällekonfiguration och flödesgivarfel | namngiven del |
| uart2.42.1a | Rapporterade tillståndskoder från sex anslutna enheter | namngiven del |
| uart2.42.1b | Status för övervakning av värmepumpens tillåtna vattenflöde | identifierad |
| uart2.42.1c | Läs nollfyllt svar 1C | platshållare |
| uart2.42.1d | Läs nollfyllt svar 1D | platshållare |
| uart2.42.1e | Läs nollfyllt svar 1E | platshållare |
| uart2.42.1f | Läs nollfyllt svar 1F | platshållare |
| uart2.42.20 | Tom reserverad datasvarsplats 20 | platshållare |
| uart2.42.26 | Läs driftlägen och temperaturmål | identifierad |
| uart2.42.27 | Läs nollfyllt svar 27 | platshållare |
| uart2.42.28 | Läs driftspärrar och extern styrstatus | identifierad |
| uart2.42.29 | Läs värme-/kylläge och zonmål | trolig |
| uart2.42.50 | Varmvattenmål, temperaturfall och maximal körtid | namngiven del |
| uart2.42.51 | Varmvattenläge, återhämtningspaus och legionellamål | trolig |
| uart2.42.52 | Legionellacykelns tidsinställningar | trolig |
| uart2.42.53 | Zonernas värme-/kylreglerläge | identifierad |
| uart2.42.54 | Zonernas temperaturbörvärden | identifierad |
| uart2.42.55 | Värmekurvans punkter per zon | trolig |
| uart2.42.56 | Veckoprogram för värme/kyla och varmvatten | trolig |
| uart2.42.57 | Årsperiod för veckoprogram 2 | trolig |
| uart2.42.58 | Reserverad inställningsplats 58 | platshållare |
| uart2.42.59 | Semesterläge: aktivering samt start- och slutdatum | trolig |
| uart2.42.5a | Semesterlägets temperaturmål | identifierad |
| uart2.42.5b | Reserverad inställningsplats 5B | platshållare |
| uart2.42.5c | Displayens språk, temperaturenhet och temperaturvisning | trolig |
| uart2.42.5d | Kontakttelefon som visas på manöverpanelen | trolig |
| uart2.42.5e | Tidsformat, fjärrkontrollernas zontilldelning och rumsgivarval | trolig |
| uart2.42.5f | Tidsschema för val av rumsgivare per zon | trolig |
| uart2.42.60 | Kalibrering av temperaturgivare, grupp 1 | identifierad |
| uart2.42.61 | Kalibrering av temperaturgivare, grupp 2 | identifierad |
| uart2.42.62 | Kalibrering av temperaturgivare, grupp 3 | identifierad |
| uart2.42.63 | Cirkulationspumpens ekonomi- och temperaturvillkor | trolig |
| uart2.42.64 | Eltillskottets tillåtelse och fördröjningar | trolig |
| uart2.42.65 | Shuntventilens gångtid/intervall och varmvattenpumpens nivå | namngiven del |
| uart2.42.66 | Val av värmekälla och samtidig värme/varmvatten | trolig |
| uart2.42.67 | Värmeregleringens temperaturgränser och tidsintervall | namngiven del |
| uart2.42.68 | Värmepumpens temperaturhysteres | trolig |
| uart2.42.69 | Värmekällornas kapaciteter för hybridberäkning | trolig |
| uart2.42.6a | Hybridens utetemperaturgräns, pannverkningsgrad, bränslepris och elens CO2-faktor | namngiven del |
| uart2.42.6b | Pannbränslets CO2-faktor för hybridval | namngiven del |
| uart2.42.6c | Konfigurerad COP-tabell, punkter 1–6 | namngiven del |
| uart2.42.6d | Konfigurerad COP-tabell, punkter 7–12 | namngiven del |
| uart2.42.6e | Säsongsperioder för elprisschemat | trolig |
| uart2.42.6f | Elpriser 1–6 för hybridens kostnadsjämförelse | namngiven del |
| uart2.42.70 | Elpriser 7–10 för hybridens kostnadsjämförelse | namngiven del |
| uart2.42.71 | Energiberäkning: tillskott och primärpump | namngiven del |
| uart2.42.72 | Energiberäkning: extra pumpar och energikorrigering | namngiven del |
| uart2.42.73 | Flödessensorns maxvärde, varmvatten-tillskott och Normal/Fast-rumsreglering | identifierad |
| uart2.42.74 | Veckoschema för elpris i tre säsonger | trolig |
| uart2.42.75 | Golvtorkning: start-/sluttemperatur, maxtemperatur, hålltid och uppsteg | trolig |
| uart2.42.76 | Golvtorkningens stegintervall/nedsteg och externa ingångar IN4/IN5 | namngiven del |
| uart2.42.77 | Smart-grid-temperaturbidrag, termo-ON-utgång och varmvattenåterladdning | identifierad |
| uart2.42.78 | Variabelt vattenflöde och analogutgångens styrning, intervall och effekt | identifierad |
| uart2.42.79 | Pump 4:s energibidrag, värmepumpens pumpnivå, analogprioritet och minflöde | identifierad |
| uart2.42.7a | Maxflöde, hybridhysteres, buffertgivarkorrigering och smart-grid-värmeval | identifierad |
| uart2.42.7b | Smart-grid-börvärden för rekommenderad/tvingad värme och kyla | identifierad |
| uart2.42.7c | Periodisk cirkulation för värme/kyla, intervall och smart-grid-kylval | identifierad |
| uart2.42.7d | Begränsning av eltillskott och sommarlägets temperatur-/tidsgränser | namngiven del |
| uart2.42.7e | Sommarlägets tvångsstarttemperatur och schema/nivå för tyst drift | trolig |
| uart2.42.a1 | Läs förbrukad energi | trolig |
| uart2.42.a2 | Läs producerad energi | trolig |
| uart2.42.a3 | Beställ och läs serviceresultat | identifierad |
| uart2.42.c8 | Läs inställningssessionens status | identifierad |
| uart2.frame.02.00 | Avsluta session och svara med information | namngiven del |
| uart2.frame.02.01 | Kvittera alternativ ram 02 | namngiven del |
| uart2.frame.5a | Anslutning till CN105 | identifierad |
| uart2.frame.5b | Läs styrenhetsinformation | identifierad |
| uart2.frame.5c | Besvara ansluten CC-fråga | namngiven del |
| uart2.frame.5d | Kvittera ansluten CC-ram | namngiven del |

## A3-koder (decimal)

| Kod | Namn | Bedömning |
|---|---|---|
| 0 | Drifttillstånd | manualnamn |
| 1 | Kompressorström | manualnamn |
| 2 | Kompressorns sammanlagda drifttid | manualnamn |
| 3 | Kompressorns antal starter | manualnamn |
| 4 | Hetgastemperatur TH4 | manualnamn |
| 5 | Vätskeledningens temperatur TH3 | manualnamn |
| 9 | Utetemperatur TH7 | manualnamn |
| 10 | Kylflänstemperatur TH8 | manualnamn |
| 12 | Överhettning | manualnamn |
| 13 | Underkylning | manualnamn |
| 14 | Kondenseringstemperatur | manualnamn |
| 16 | Kompressorns faktiska frekvens | manualnamn |
| 17 | Kompressorns målfrekvens | manualnamn |
| 18 | Brinepumpens styrsteg | manualnamn |
| 19 | Brinepumpens varvtal | manualnamn |
| 22 | Expansionsventil A: öppning | manualnamn |
| 25 | Primärström | manualnamn |
| 26 | DC-mellankretsspänning | manualnamn |
| 27 | Brine in TH32 | manualnamn |
| 28 | Brine ut TH34 | manualnamn |
| 48 | Drifttid med aktiv termostat | manualnamn |
| 51 | Underkortets reglerstatus | manualnamn |
| 52 | Kompressorns frekvensreglerstatus | manualnamn |
| 53 | Fläktreglerstatus enligt manualen | manualnamn |
| 54 | Aktuatorernas utgångsstatus | manualnamn |
| 55 | Detaljer för fel U9 | manualnamn |
| 70 | Underkortets inställda kapacitet | manualnamn |
| 71 | Underkortets konfiguration | manualnamn |
| 90 | Underkortets firmwareversion | manualnamn |
| 91 | Underkortets versionssuffix | manualnamn |
| 100 | Senaste fördröjda fel på underkortet | manualnamn |
| 101 | Näst senaste fördröjda fel på underkortet | manualnamn |
| 102 | Tredje senaste fördröjda fel på underkortet | manualnamn |
| 103 | Senaste fel | manualnamn |
| 104 | Näst senaste fel | manualnamn |
| 105 | Tredje senaste fel | manualnamn |
| 106 | Felaktig givare TH3/TH7/TH8 | manualnamn |
| 107 | Drifttillstånd vid fel | manualnamn |
| 108 | Kompressorström vid fel | manualnamn |
| 109 | Kompressorns drifttid vid fel | manualnamn |
| 110 | Kompressorns antal starter vid fel | manualnamn |
| 111 | Hetgastemperatur vid fel | manualnamn |
| 112 | TH3 vid fel | manualnamn |
| 113 | Brine ut TH34 vid fel | manualnamn |
| 115 | Brine in TH32 vid fel | manualnamn |
| 116 | Utetemperatur vid fel | manualnamn |
| 117 | Kylflänstemperatur vid fel | manualnamn |
| 118 | Överhettning vid fel | manualnamn |
| 119 | Underkylning vid fel | manualnamn |
| 120 | Kompressorfrekvens vid fel | manualnamn |
| 121 | Brinepumpens styrsteg vid fel | manualnamn |
| 122 | Fläkt 1-varvtal vid fel enligt manualen | manualnamn |
| 125 | Expansionsventil A vid fel | manualnamn |
| 129 | Kondenseringstemperatur vid fel | manualnamn |
| 130 | Termostatens drifttid fram till fel | manualnamn |
| 154 | Vattenpump 1: drifttid sedan nollställning | manualnamn |
| 155 | Kompressorns ackumulerade drifttidsräknare (grov del) | namngiven del |
| 156 | Vattenpump 2: drifttid sedan nollställning | manualnamn |
| 157 | Vattenpump 3: drifttid sedan nollställning | manualnamn |
| 158 | Vattenpump 4: drifttid sedan nollställning | manualnamn |
| 160 | Läs modellprofil | namngiven del |
| 161 | Läs hårdvaruvariant | namngiven del |
| 162 | FTC DIP-bank 1 | manualnamn |
| 163 | FTC DIP-bank 2 | manualnamn |
| 164 | FTC DIP-bank 3 | manualnamn |
| 165 | FTC DIP-bank 4 | manualnamn |
| 166 | FTC DIP-bank 5 | manualnamn |
| 175 | FTC utgångssignaler | manualnamn |
| 176 | FTC ingångssignaler | manualnamn |
| 177 | Shuntventilens öppningssteg | manualnamn |
| 178 | Primärpumpens återrapporterade signal | identifierad |
| 179 | Termo-ON-utgångens status | identifierad |
| 185 | Förbrukningsberäkningens aktuella värde | namngiven del |
| 186 | Värmeproduktionsberäkningens aktuella värde | namngiven del |
| 190 | FTC firmwareversion, första delen | manualnamn |
| 191 | FTC firmwareversion, andra delen | manualnamn |
| 200 | Återställ funktionsinställningar till fabriksinställning | manualnamn |
| 340 | Nollställ vattenpump 1:s drifttid | manualnamn |
| 341 | Nollställ kompressorns grova drifttidsräknare | identifierad |
| 342 | Nollställ vattenpump 2:s drifttid | manualnamn |
| 343 | Nollställ vattenpump 3:s drifttid | manualnamn |
| 344 | Nollställ vattenpump 4:s drifttid | manualnamn |
| 350 | Återställ källsidans serviceläge | namngiven del |
| 351 | Pump-down-val (SUZ; Geodan obekräftat) | namngiven del |
| 352 | Välj serviceläge 2 | namngiven del |
| 353 | Välj serviceläge 3 | namngiven del |
| 354 | Välj serviceläge 4 | namngiven del |
| 355 | Välj serviceläge 5 | namngiven del |
| 356 | Välj serviceläge 6 | namngiven del |
| 357 | Välj serviceläge 7 | namngiven del |
| 358 | Sätt serviceval 39FF till 1 | namngiven del |
| 359 | Sätt serviceval 39FF till 2 | namngiven del |
| 360 | Sätt serviceval 3A00 till 1 | namngiven del |
| 361 | Sätt serviceval 3A00 till 2 | namngiven del |
| 362 | Sätt serviceval 3A01 till 1 | namngiven del |
| 363 | Sätt serviceval 3A01 till 2 | namngiven del |
| 500 | Rumsbörvärde värme, zon 1 | identifierad |
| 501 | Framledningsbörvärde värme, zon 1 | identifierad |
| 502 | Rumsbörvärde kyla, zon 1 | identifierad |
| 503 | Framledningsbörvärde kyla, zon 1 | identifierad |
| 504 | Rumstemperatur zon 1 TH1A | manualnamn |
| 505 | Köldmediets vätsketemperatur TH2 | manualnamn |
| 506 | Primär retur THW2 | manualnamn |
| 507 | Rumstemperatur zon 2 TH1B | manualnamn |
| 508 | Varmvatten nedre givare THW5B | manualnamn |
| 509 | Framledning zon 1 THW6 | manualnamn |
| 510 | Utetemperatur TH7 | manualnamn |
| 511 | Primär framledning THW1 | manualnamn |
| 512 | Retur zon 1 THW7 | manualnamn |
| 513 | Framledning zon 2 THW8 | manualnamn |
| 514 | Retur zon 2 THW9 | manualnamn |
| 515 | Extern pannas framledning THWB1 | manualnamn |
| 516 | Extern pannas returtemperatur | namngiven del |
| 517 | Rumsbörvärde värme, zon 2 | identifierad |
| 518 | Framledningsbörvärde värme, zon 2 | identifierad |
| 519 | Rumsbörvärde kyla, zon 2 | identifierad |
| 520 | Energiräknare förbrukning varmvatten, högre siffror | trolig |
| 521 | Energiräknare förbrukning varmvatten, lägre siffror | trolig |
| 522 | Energiräknare förbrukning värme, högre siffror | trolig |
| 523 | Energiräknare förbrukning värme, lägre siffror | trolig |
| 524 | Energiräknare förbrukning kyla, högre siffror | trolig |
| 525 | Energiräknare förbrukning kyla, lägre siffror | trolig |
| 526 | Energiräknare produktion varmvatten, högre siffror | trolig |
| 527 | Energiräknare produktion varmvatten, lägre siffror | trolig |
| 528 | Energiräknare produktion värme, högre siffror | trolig |
| 529 | Energiräknare produktion värme, lägre siffror | trolig |
| 530 | Energiräknare produktion kyla, högre siffror | trolig |
| 531 | Energiräknare produktion kyla, lägre siffror | trolig |
| 532 | Spara och nollställ energiräknarbanken | identifierad |
| 533 | Framledningsbörvärde kyla, zon 2 | identifierad |
| 534 | Varmvatten övre givare THW5A | manualnamn |
| 535 | Blandningstankens temperatur THW10 | manualnamn |
| 536 | Kondenserings-/mättnadstemperatur från FTC:s givarkanal | trolig |
| 540 | Primärkretsens vattenflöde | manualnamn |
| 550 | FTC senaste fördröjda fel | manualnamn |
| 551 | Vald värmekälla vid fel | manualnamn |
| 552 | FTC driftläge vid fel | manualnamn |
| 553 | FTC utgångssignaler vid fel | manualnamn |
| 554 | FTC ingångssignaler vid fel | manualnamn |
| 555 | Rumstemperatur zon 1 vid fel | manualnamn |
| 556 | Rumstemperatur zon 2 vid fel | manualnamn |
| 557 | TH2 vid fel | manualnamn |
| 558 | Primär framledning vid fel | manualnamn |
| 559 | Primär retur vid fel | manualnamn |
| 560 | Varmvatten THW5B vid fel | manualnamn |
| 561 | Framledning zon 1 vid fel | manualnamn |
| 562 | Retur zon 1 vid fel | manualnamn |
| 563 | Framledning zon 2 vid fel | manualnamn |
| 564 | Retur zon 2 vid fel | manualnamn |
| 565 | Extern pannas framledning vid fel | manualnamn |
| 566 | Extern pannas returtemperatur vid fel | namngiven del |
| 567 | FTC identifiering av felaktig temperaturgivare | manualnamn |
| 568 | Shuntventilens öppningssteg vid fel | manualnamn |
| 569 | Vilken flödesvakt som löste ut | manualnamn |
| 570 | Primärpumpens återrapporterade signal vid fel | identifierad |
| 571 | Primärflöde vid fel | manualnamn |
| 572 | Varmvattentemperatur vid fel | identifierad |
| 573 | Termo-ON-utgångens status vid fel | identifierad |
| 574 | Bufferttankstemperatur vid fel | namngiven del |

## Läs- och skrivfält

RX/TX är relativt FTC. ID behåller originalpost, riktning och fältindex. Flera katalogposter kan beskriva samma byte; de har inte slagits ihop eller fått gissade givarnamn.

| Fält-ID | Namn | Syfte | Namngrund |
|---|---|---|---|
| uart2.41.00/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.01/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.02/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.03/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.04/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.05/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.06/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.07/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.08/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.09/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.0a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.0b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.0c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.0d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.0e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.0f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.10/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.11/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.12/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.13/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.14/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.15/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.16/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.17/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.18/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.19/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.1a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.1b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.1c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.1d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.1e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.1f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.20/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.21/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.22/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.23/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.24/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.25/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.26/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.27/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.28/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.29/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.2a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.2b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.2c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.2d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.2e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.2f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.30/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.31/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.32/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.33/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.34/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.35/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.36/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.37/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.38/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.39/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.3a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.3b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.3c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.3d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.3e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.3f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.40/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.41/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.42/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.43/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.44/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.45/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.46/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.47/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.48/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.49/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.4a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.4b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.4c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.4d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.4e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.4f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.50/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.51/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.52/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.53/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.54/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.55/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.56/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.57/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.58/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.59/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.5a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.5b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.5c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.5d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.5e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.5f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.60/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.61/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.62/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.63/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.64/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.65/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.66/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.67/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.68/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.69/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.6a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.6b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.6c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.6d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.6e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.6f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.70/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.71/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.72/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.73/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.74/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.75/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.76/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.77/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.78/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.79/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.7a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.7b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.7c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.7d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.7e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.7f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.80/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.81/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.82/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.83/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.84/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.85/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.86/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.87/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.88/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.89/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.8a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.8b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.8c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.8d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.8e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.8f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.90/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.91/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.92/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.93/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.94/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.95/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.96/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.97/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.98/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.99/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.9a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.9b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.9c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.9d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.9e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.9f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.a9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.aa/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ab/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ac/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ad/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ae/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.af/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.b9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ba/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.bb/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.bc/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.bd/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.be/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.bf/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.c8/rx_fields/0 | Överföringsriktning | Inte fördjupat här | befintlig fältroll |
| uart2.41.c8/rx_fields/1 | Sessionsåtgärd | Inte fördjupat här | befintlig fältroll |
| uart2.41.c8/rx_fields/2 | Kategorimask | Inte fördjupat här | befintlig fältroll |
| uart2.41.c8/rx_fields/3 | Kategori för nästa inställningsblock | Inte fördjupat här | befintlig fältroll |
| uart2.41.c9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ca/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.cb/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.cc/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.cd/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ce/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.cf/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.d9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.da/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.db/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.dc/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.dd/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.de/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.df/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.e9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ea/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.eb/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ec/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ed/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ee/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ef/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.f9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.fa/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.fb/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.fc/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.fd/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.fe/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.41.ff/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.00/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.01/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.02/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.03/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.04/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.05/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.06/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.07/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.07/tx_fields/0 | Förbrukad effekt | Följa effekt; upplösning och samtidighet begränsar live-COP. | syfte med källkorrelation |
| uart2.42.07/tx_fields/1 | Producerad effekt | Följa effekt; upplösning och samtidighet begränsar live-COP. | syfte med källkorrelation |
| uart2.42.07/tx_fields/2 | Ackumulerad förbrukningsräknare | Följa förbrukning över tid; hantera omslag och period separat. | syfte med källkorrelation |
| uart2.42.08/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.09/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.0a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.0b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.0c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.0d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.0e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.0f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.10/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.11/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.12/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.13/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.14/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.15/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.16/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.17/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.18/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.19/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.1a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.1b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.1c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.1d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.1e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.1e/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/1 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/2 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/3 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/4 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/5 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/6 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/7 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/8 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/9 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/10 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/11 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/12 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1e/tx_fields/13 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.1f/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/1 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/2 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/3 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/4 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/5 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/6 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/7 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/8 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/9 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/10 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.1f/tx_fields/11 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.42.20/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.21/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.22/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.23/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.24/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.25/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.26/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.27/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.28/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.29/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.2a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.2b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.2c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.2d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.2e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.2f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.30/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.31/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.32/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.33/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.34/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.35/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.36/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.37/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.38/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.39/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.3a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.3b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.3c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.3d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.3e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.3f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.40/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.41/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.42/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.43/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.44/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.45/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.46/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.47/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.48/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.49/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.4a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.4b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.4c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.4d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.4e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.4f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.50/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.51/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.52/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.53/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.54/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.55/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.56/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.57/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.58/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.59/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.5a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.5b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.5c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.5d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.5e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.5f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.60/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.61/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.62/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.63/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.64/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.65/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.65/tx_fields/0 | Konfigurerad nivå för primärpump | Läsa konfigurationen för konfigurerad nivå för primärpump. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.42.66/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.67/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.68/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.69/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.6a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.6b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.6c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.6d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.6e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.6f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.70/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.71/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.72/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.73/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.74/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.75/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.76/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.77/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.78/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.79/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.79/tx_fields/0 | Värmepumpskretsens pumpnivå | Läsa konfigurationen för värmepumpskretsens pumpnivå. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.42.7a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.7b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.7c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.7d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.7e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.7f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.80/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.81/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.82/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.83/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.84/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.85/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.86/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.87/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.88/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.89/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.8a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.8b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.8c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.8d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.8e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.8f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.90/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.91/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.92/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.93/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.94/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.95/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.96/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.97/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.98/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.99/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.9a/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.9b/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.9c/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.9d/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.9e/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.9f/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a3/rx_fields/0 | Servicekod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a3/tx_fields/0 | Servicekod för svaret | Koppla svaret till beställd A3-fråga. | protokollroll belagd |
| uart2.42.a3/tx_fields/1 | Servicevärdets format/status | Avgöra hur svaret ska tolkas och om ett resultat finns. | protokollroll belagd |
| uart2.42.a3/tx_fields/2 | Servicefrågans resultat | Läsa värdet enligt den specifika A3-kodens betydelse. | protokollroll belagd |
| uart2.42.a4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.a9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.aa/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ab/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ac/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ad/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ae/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.af/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.b9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ba/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.bb/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.bc/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.bd/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.be/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.bf/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.c9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ca/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.cb/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.cc/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.cd/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ce/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.cf/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.d9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.da/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.db/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.dc/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.dd/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.de/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.df/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.e9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ea/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.eb/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ec/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ed/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ee/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ef/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f0/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f1/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f2/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f3/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f4/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f5/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f6/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f7/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f8/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.f9/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.fa/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.fb/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.fc/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.fd/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.fe/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.42.ff/rx_fields/0 | Kommandokod | Inte fördjupat här | befintlig fältroll |
| uart2.tx.005.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.006.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.007.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.008.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.009.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.010.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.011.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.012.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.013.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.014.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.015.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.016.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.017.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.018.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.019.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.020.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.021.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.022.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.023.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.024.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.025.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.026.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.027.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.028.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.029.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.030.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.031.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.032.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.033.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.034.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.035.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.036.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.037.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.038.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.039.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.040.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.041.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.042.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.043.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.044.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.045.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.046.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.047.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.048.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.049.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.050.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.051.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.052.p00/tx_fields/0 | Kvittens för inställningsskrivning | Bekräfta protokollsvaret; inte bevis på fysisk tillämpning. | protokollroll belagd |
| uart2.tx.053.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.053.p01/tx_fields/0 | Styrenhetens datum | Datera drift och scheman. | syfte med källkorrelation |
| uart2.tx.053.p02/tx_fields/0 | Styrenhetens datum | Datera drift och scheman. | syfte med källkorrelation |
| uart2.tx.053.p03/tx_fields/0 | Styrenhetens datum | Datera drift och scheman. | syfte med källkorrelation |
| uart2.tx.053.p04/tx_fields/0 | Styrenhetens klockslag | Tidsätta drift och scheman. | syfte med källkorrelation |
| uart2.tx.053.p05/tx_fields/0 | Styrenhetens klockslag | Tidsätta drift och scheman. | syfte med källkorrelation |
| uart2.tx.053.p06/tx_fields/0 | Styrenhetens klockslag | Tidsätta drift och scheman. | syfte med källkorrelation |
| uart2.tx.053.p07/tx_fields/0 | FTC-programmets identitetsbytes | Identifiera programversion; alla fyra delars presentationsformat är inte fastställt. | syfte med källkorrelation |
| uart2.tx.053.p08/tx_fields/0 | FTC-programmets identitetsbytes | Identifiera programversion; alla fyra delars presentationsformat är inte fastställt. | syfte med källkorrelation |
| uart2.tx.053.p09/tx_fields/0 | FTC-programmets identitetsbytes | Identifiera programversion; alla fyra delars presentationsformat är inte fastställt. | syfte med källkorrelation |
| uart2.tx.053.p10/tx_fields/0 | FTC-programmets identitetsbytes | Identifiera programversion; alla fyra delars presentationsformat är inte fastställt. | syfte med källkorrelation |
| uart2.tx.053.p11/tx_fields/0 | Svar 53 – databyte 11 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.053.p12/tx_fields/0 | Svar 53 – databyte 12 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.053.p13/tx_fields/0 | Svar 53 – databyte 13 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.054.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.054.p01/tx_fields/0 | Rumsgivarval per zon | Visa vilka rumskanaler zonerna använder. | syfte med källkorrelation |
| uart2.tx.054.p02/tx_fields/0 | Rumsgivarval per zon | Visa vilka rumskanaler zonerna använder. | syfte med källkorrelation |
| uart2.tx.054.p03/tx_fields/0 | Avfrostningsstatus | Visa källenhetens avfrostningsläge. | syfte med källkorrelation |
| uart2.tx.054.p04/tx_fields/0 | Eltillskottets drift och eftergång | Visa om eltillskott är aktivt eller nyligen har varit aktivt; skiljer direkt drift från eftergång. | syfte följt i kod |
| uart2.tx.054.p05/tx_fields/0 | Svar 54 – databyte 5 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.054.p06/tx_fields/0 | Extern pannas drift och eftergång | Visa om pannutgångarna är aktiva eller befinner sig i eftergång. | syfte följt i kod |
| uart2.tx.054.p07/tx_fields/0 | Svar 54 – databyte 7 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.055.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.055.p01/tx_fields/0 | Köldmedie-/källfelklass | Skilja felklass från den detaljerade felkoden. | syfte med källkorrelation |
| uart2.tx.055.p02/tx_fields/0 | Rapporterad felkod | Visa systemets felkod. | syfte med källkorrelation |
| uart2.tx.055.p03/tx_fields/0 | Rapporterad felkod | Visa systemets felkod. | syfte med källkorrelation |
| uart2.tx.055.p04/tx_fields/0 | Formaterad felkod | Överföra felkodens andra representation. | syfte med källkorrelation |
| uart2.tx.055.p05/tx_fields/0 | Formaterad felkod | Överföra felkodens andra representation. | syfte med källkorrelation |
| uart2.tx.055.p06/tx_fields/0 | Svar 55 – databyte 6 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.055.p07/tx_fields/0 | Svar 55 – databyte 7 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.055.p08/tx_fields/0 | Aktiva värmezoner | Visa om båda zonerna eller bara en deltar. | syfte med källkorrelation |
| uart2.tx.055.p09/tx_fields/0 | Cykel-/temperaturhysteresens tillstånd zon 1 | Följa zonens särskilda reglergren vid återkommande värmestarter. | syfte följt i kod |
| uart2.tx.055.p10/tx_fields/0 | Cykel-/temperaturhysteresens tillstånd zon 2 | Följa samma reglergren för den andra zonen. | syfte följt i kod |
| uart2.tx.055.p11/tx_fields/0 | Tillgängliga källenheter | Ange vilka enheter som ingår i systemet. | syfte med källkorrelation |
| uart2.tx.055.p12/tx_fields/0 | Valda källenheter för drift | Visa vilka av upp till sex källenheter som har valts för att täcka behovet. | syfte följt i kod |
| uart2.tx.056.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.056.p01/tx_fields/0 | Kompressorfrekvens | Följa kompressorns arbetsnivå. | syfte med källkorrelation |
| uart2.tx.056.p02/tx_fields/0 | Kompressorfrekvens enhet 1 | Följa respektive källenhets kompressor. | syfte med källkorrelation |
| uart2.tx.056.p03/tx_fields/0 | Kompressorfrekvens enhet 2 | Följa respektive källenhets kompressor. | syfte med källkorrelation |
| uart2.tx.056.p04/tx_fields/0 | Kompressorfrekvens enhet 3 | Följa respektive källenhets kompressor. | syfte med källkorrelation |
| uart2.tx.056.p05/tx_fields/0 | Kompressorfrekvens enhet 4 | Följa respektive källenhets kompressor. | syfte med källkorrelation |
| uart2.tx.056.p06/tx_fields/0 | Kompressorfrekvens enhet 5 | Följa respektive källenhets kompressor. | syfte med källkorrelation |
| uart2.tx.056.p07/tx_fields/0 | Kompressorfrekvens enhet 6 | Följa respektive källenhets kompressor. | syfte med källkorrelation |
| uart2.tx.056.p08/tx_fields/0 | Bestående temperaturavvikelse utan frekvensändring | Skilja kvarstående positiv eller negativ temperaturavvikelse när kompressorns Hz ligger still. Hjälp för analys av reglerrespons, inte bevis på maximal effekt. | syfte följt i kod |
| uart2.tx.056.p09/tx_fields/0 | Svar 56 – databyte 9 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.056.p10/tx_fields/0 | Svar 56 – databyte 10 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.057.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.057.p01/tx_fields/0 | Svar 57 – databyte 1 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.057.p02/tx_fields/0 | Svar 57 – databyte 2 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.057.p03/tx_fields/0 | Svar 57 – databyte 3 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.057.p04/tx_fields/0 | Svar 57 – databyte 4 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.057.p05/tx_fields/0 | Effektbegränsningens rapporterade nivå | Visa den mest begränsande effektgränsen, inte producerad kW. | syfte följt i kod |
| uart2.tx.057.p06/tx_fields/0 | Använd värmekälla | Visa vilket slags värmekälla som används. | syfte med källkorrelation |
| uart2.tx.057.p07/tx_fields/0 | Varmvattenproduktionens värmekällfas | Skilja normalfas, värmepump och elektrisk eftervärmning. | syfte med källkorrelation |
| uart2.tx.057.p08/tx_fields/0 | Svar 57 – databyte 8 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.057.p09/tx_fields/0 | Svar 57 – databyte 9 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.057.p10/tx_fields/0 | Hybridens valprioritet | Visa prioriteringsvalet för jämförelse mellan värmekällor. | syfte med källkorrelation |
| uart2.tx.057.p11/tx_fields/0 | Beräknad värmekostnad för panna | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.057.p12/tx_fields/0 | Beräknad värmekostnad för panna | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.057.p13/tx_fields/0 | Beräknad värmekostnad för panna | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.058.p01/tx_fields/0 | Beräknad värmekostnad för värmepump | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p02/tx_fields/0 | Beräknad värmekostnad för värmepump | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p03/tx_fields/0 | Beräknad värmekostnad för värmepump | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p04/tx_fields/0 | Beräknat CO2-bidrag för panna | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p05/tx_fields/0 | Beräknat CO2-bidrag för panna | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p06/tx_fields/0 | Beräknat CO2-bidrag för panna | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p07/tx_fields/0 | Beräknat CO2-bidrag för värmepump | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p08/tx_fields/0 | Beräknat CO2-bidrag för värmepump | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p09/tx_fields/0 | Beräknat CO2-bidrag för värmepump | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p10/tx_fields/0 | Aktivt elpris för hybridberäkning | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p11/tx_fields/0 | Aktivt elpris för hybridberäkning | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.058.p12/tx_fields/0 | Aktivt elpris för hybridberäkning | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | syfte med SD-korrelation |
| uart2.tx.059.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.059.p01/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.059.p02/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.059.p03/tx_fields/0 | Förbrukad effekt | Följa effekt; upplösning och samtidighet begränsar live-COP. | syfte med källkorrelation |
| uart2.tx.059.p04/tx_fields/0 | Förbrukad effekt | Följa effekt; upplösning och samtidighet begränsar live-COP. | syfte med källkorrelation |
| uart2.tx.059.p05/tx_fields/0 | Producerad effekt | Följa effekt; upplösning och samtidighet begränsar live-COP. | syfte med källkorrelation |
| uart2.tx.059.p06/tx_fields/0 | Producerad effekt | Följa effekt; upplösning och samtidighet begränsar live-COP. | syfte med källkorrelation |
| uart2.tx.059.p07/tx_fields/0 | Förbrukningsberäkning tillgänglig | Bedöma om effekt- och energifälten kan användas; inte ny energimätning. | syfte med källkorrelation |
| uart2.tx.059.p08/tx_fields/0 | Produktionsberäkning tillgänglig | Bedöma om effekt- och energifälten kan användas; inte ny energimätning. | syfte med källkorrelation |
| uart2.tx.059.p09/tx_fields/0 | Värmefunktion tillgänglig | Bedöma om effekt- och energifälten kan användas; inte ny energimätning. | syfte med källkorrelation |
| uart2.tx.059.p10/tx_fields/0 | Energiberäkningens status | Bedöma om effekt- och energifälten kan användas; inte ny energimätning. | syfte med källkorrelation |
| uart2.tx.059.p11/tx_fields/0 | Ackumulerad förbrukningsräknare | Följa förbrukning över tid; hantera omslag och period separat. | syfte med källkorrelation |
| uart2.tx.059.p12/tx_fields/0 | Ackumulerad förbrukningsräknare | Följa förbrukning över tid; hantera omslag och period separat. | syfte med källkorrelation |
| uart2.tx.060.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.061.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.061.p01/tx_fields/0 | Valt rumsmål zon 1 | Visa aktivt rumsmål med hänsyn till drift- och semesterläge. | syfte med källkorrelation |
| uart2.tx.061.p02/tx_fields/0 | Valt rumsmål zon 1 | Visa aktivt rumsmål med hänsyn till drift- och semesterläge. | syfte med källkorrelation |
| uart2.tx.061.p03/tx_fields/0 | Valt rumsmål zon 2 | Visa aktivt rumsmål med hänsyn till drift- och semesterläge. | syfte med källkorrelation |
| uart2.tx.061.p04/tx_fields/0 | Valt rumsmål zon 2 | Visa aktivt rumsmål med hänsyn till drift- och semesterläge. | syfte med källkorrelation |
| uart2.tx.061.p05/tx_fields/0 | Aktivt temperaturmål zon 1 | Visa målet som valts för zonens värme-/kylreglering. Kan vara rums- eller framledningsmål beroende på reglerläge. | syfte med källkorrelation |
| uart2.tx.061.p06/tx_fields/0 | Aktivt temperaturmål zon 1 | Visa målet som valts för zonens värme-/kylreglering. Kan vara rums- eller framledningsmål beroende på reglerläge. | syfte med källkorrelation |
| uart2.tx.061.p07/tx_fields/0 | Aktivt temperaturmål zon 2 | Visa zonens aktuella målkanal beroende på reglerläge. | syfte följt i kod |
| uart2.tx.061.p08/tx_fields/0 | Aktivt temperaturmål zon 2 | Visa zonens aktuella målkanal beroende på reglerläge. | syfte följt i kod |
| uart2.tx.061.p09/tx_fields/0 | Legionellacykelns temperaturmål | Visa den särskilda temperaturreferensen för legionellakörning. | syfte med källkorrelation |
| uart2.tx.061.p10/tx_fields/0 | Legionellacykelns temperaturmål | Visa den särskilda temperaturreferensen för legionellakörning. | syfte med källkorrelation |
| uart2.tx.061.p11/tx_fields/0 | Temperaturfall för varmvattenåterladdning | Visa inställd temperaturgräns som används av regleringen. | syfte med källkorrelation |
| uart2.tx.061.p12/tx_fields/0 | Högsta tillåtna framledningsmål | Visa inställd temperaturgräns som används av regleringen. | syfte med källkorrelation |
| uart2.tx.061.p13/tx_fields/0 | Lägsta tillåtna framledningsmål | Visa inställd temperaturgräns som används av regleringen. | syfte med källkorrelation |
| uart2.tx.062.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.063.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.063.p01/tx_fields/0 | Rumstemperatur zon 1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.063.p02/tx_fields/0 | Rumstemperatur zon 1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.063.p03/tx_fields/0 | Rumstemperatur zon 2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.063.p04/tx_fields/0 | Rumstemperatur zon 2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.063.p05/tx_fields/0 | Svar 63 – databyte 5 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.063.p06/tx_fields/0 | Svar 63 – databyte 6 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.063.p07/tx_fields/0 | Svar 63 – databyte 7 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.063.p08/tx_fields/0 | Köldmediets vätsketemperatur TH2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.063.p09/tx_fields/0 | Köldmediets vätsketemperatur TH2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.063.p10/tx_fields/0 | Kompakt givarkanal för köldmediet | Alternativ representation för TH2-kanalen. | syfte med källkorrelation |
| uart2.tx.063.p11/tx_fields/0 | Utetemperatur TH7 | Visa temperatur utomhus. | syfte med källkorrelation |
| uart2.tx.064.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.064.p01/tx_fields/0 | Primär framledning THW1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.064.p02/tx_fields/0 | Primär framledning THW1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.064.p03/tx_fields/0 | Kompakt givarkanal: Primär framledning THW1 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.064.p04/tx_fields/0 | Primär retur THW2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.064.p05/tx_fields/0 | Primär retur THW2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.064.p06/tx_fields/0 | Kompakt givarkanal: Primär retur THW2 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.064.p07/tx_fields/0 | Varmvattentemperatur THW5B | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.064.p08/tx_fields/0 | Varmvattentemperatur THW5B | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.064.p09/tx_fields/0 | Kompakt givarkanal: Varmvattentemperatur THW5B | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.064.p10/tx_fields/0 | Varmvattentemperatur THW5A | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.064.p11/tx_fields/0 | Varmvattentemperatur THW5A | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.064.p12/tx_fields/0 | Kompakt givarkanal: Varmvattentemperatur THW5A | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.065.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.065.p01/tx_fields/0 | Framledning zon 1 THW6 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.065.p02/tx_fields/0 | Framledning zon 1 THW6 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.065.p03/tx_fields/0 | Kompakt givarkanal: Framledning zon 1 THW6 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.065.p04/tx_fields/0 | Retur zon 1 THW7 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.065.p05/tx_fields/0 | Retur zon 1 THW7 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.065.p06/tx_fields/0 | Kompakt givarkanal: Retur zon 1 THW7 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.065.p07/tx_fields/0 | Framledning zon 2 THW8 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.065.p08/tx_fields/0 | Framledning zon 2 THW8 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.065.p09/tx_fields/0 | Kompakt givarkanal: Framledning zon 2 THW8 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.065.p10/tx_fields/0 | Retur zon 2 THW9 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.065.p11/tx_fields/0 | Retur zon 2 THW9 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.065.p12/tx_fields/0 | Kompakt givarkanal: Retur zon 2 THW9 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.066.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.066.p01/tx_fields/0 | Extern pannas framledning THWB1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.066.p02/tx_fields/0 | Extern pannas framledning THWB1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.066.p03/tx_fields/0 | Kompakt givarkanal: Extern pannas framledning THWB1 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.066.p04/tx_fields/0 | Extern pannas retur THWB2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.066.p05/tx_fields/0 | Extern pannas retur THWB2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.066.p06/tx_fields/0 | Kompakt givarkanal: Extern pannas retur THWB2 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.067.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.067.p01/tx_fields/0 | Bufferttankens temperatur THW10 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.067.p02/tx_fields/0 | Bufferttankens temperatur THW10 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.067.p03/tx_fields/0 | Kompakt givarkanal: Bufferttankens temperatur THW10 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.067.p04/tx_fields/0 | Kondenserings-/mättnadstemperatur | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.067.p05/tx_fields/0 | Kondenserings-/mättnadstemperatur | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | syfte med källkorrelation |
| uart2.tx.067.p06/tx_fields/0 | Kompakt givarkanal: Kondenserings-/mättnadstemperatur | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | syfte med källkorrelation |
| uart2.tx.068.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.068.p01/tx_fields/0 | Termostatingång zon 1 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | syfte med källkorrelation |
| uart2.tx.068.p02/tx_fields/0 | Termostatingång zon 2 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | syfte med källkorrelation |
| uart2.tx.068.p03/tx_fields/0 | Flödesvakt 1 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | syfte med källkorrelation |
| uart2.tx.068.p04/tx_fields/0 | Flödesvakt 2 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | syfte med källkorrelation |
| uart2.tx.068.p05/tx_fields/0 | Flödesvakt 3 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | syfte med källkorrelation |
| uart2.tx.068.p06/tx_fields/0 | Extern ingång IN4 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | syfte med källkorrelation |
| uart2.tx.068.p07/tx_fields/0 | Extern ingång IN5 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | syfte med källkorrelation |
| uart2.tx.069.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.069.p01/tx_fields/0 | FTC DIP-bank SW1 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p02/tx_fields/0 | FTC DIP-bank SW1 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p03/tx_fields/0 | FTC DIP-bank SW2 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p04/tx_fields/0 | FTC DIP-bank SW2 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p05/tx_fields/0 | FTC DIP-bank SW3 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p06/tx_fields/0 | FTC DIP-bank SW3 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p07/tx_fields/0 | FTC DIP-bank SW4 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p08/tx_fields/0 | FTC DIP-bank SW4 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p09/tx_fields/0 | FTC DIP-bank SW5 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p10/tx_fields/0 | FTC DIP-bank SW5 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p11/tx_fields/0 | FTC DIP-bank SW6 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.069.p12/tx_fields/0 | FTC DIP-bank SW6 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | syfte med källkorrelation |
| uart2.tx.070.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.071.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.071.p01/tx_fields/0 | Kompressor i drift | Skilja kompressordrift från stopp. | syfte med källkorrelation |
| uart2.tx.071.p02/tx_fields/0 | Kompressordrift per källenhet | Visa driftmask för sex enheter. | syfte med källkorrelation |
| uart2.tx.071.p03/tx_fields/0 | Samlad kompressordrifttid | Följa drifttid; delarna bildar en gemensam räknare. | syfte med källkorrelation |
| uart2.tx.071.p04/tx_fields/0 | Samlad kompressordrifttid | Följa drifttid; delarna bildar en gemensam räknare. | syfte med källkorrelation |
| uart2.tx.071.p05/tx_fields/0 | Samlad kompressordrifttid | Följa drifttid; delarna bildar en gemensam räknare. | syfte med källkorrelation |
| uart2.tx.071.p06/tx_fields/0 | Drifttid källenhet 1 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.071.p07/tx_fields/0 | Drifttid källenhet 1 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.071.p08/tx_fields/0 | Drifttid källenhet 2 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.071.p09/tx_fields/0 | Drifttid källenhet 2 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.071.p10/tx_fields/0 | Drifttid källenhet 3 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.071.p11/tx_fields/0 | Drifttid källenhet 3 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.072.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.072.p01/tx_fields/0 | Extern panna aktiverad | Visa pannstyrningens utgångstillstånd efter drift- och skyddsvillkor. | syfte följt i kod |
| uart2.tx.072.p02/tx_fields/0 | Eltillskott steg 1 | Visa aktivering av tillskott; inte direkt uppmätt eleffekt. | syfte med källkorrelation |
| uart2.tx.072.p03/tx_fields/0 | Eltillskott steg 2 | Visa aktivering av tillskott; inte direkt uppmätt eleffekt. | syfte med källkorrelation |
| uart2.tx.072.p04/tx_fields/0 | Eltillskott extra steg | Visa aktivering av tillskott; inte direkt uppmätt eleffekt. | syfte med källkorrelation |
| uart2.tx.072.p05/tx_fields/0 | Varmvattentankens elpatron | Visa aktivering av tillskott; inte direkt uppmätt eleffekt. | syfte med källkorrelation |
| uart2.tx.072.p06/tx_fields/0 | Drifttid källenhet 4 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.072.p07/tx_fields/0 | Drifttid källenhet 4 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.072.p08/tx_fields/0 | Drifttid källenhet 5 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.072.p09/tx_fields/0 | Drifttid källenhet 5 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.072.p10/tx_fields/0 | Drifttid källenhet 6 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.072.p11/tx_fields/0 | Drifttid källenhet 6 | Jämföra drifttid mellan anslutna enheter. | syfte med källkorrelation |
| uart2.tx.072.p12/tx_fields/0 | Primärt vattenflöde | Följa cirkulationen genom värmepumpen. | syfte med källkorrelation |
| uart2.tx.072.p13/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.073.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.073.p01/tx_fields/0 | Primär cirkulationspump i drift | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p02/tx_fields/0 | Primärpumpens styrsignal | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p03/tx_fields/0 | Primärpumpens återkoppling | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p04/tx_fields/0 | Cirkulationspump 2 | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p05/tx_fields/0 | Zonpump på OUT3 | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p06/tx_fields/0 | Trevägsventil 1 | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p07/tx_fields/0 | Trevägsventil 2 | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p08/tx_fields/0 | Shuntmotor: aktiveringsutgång OUT5A | Tillsammans med OUT5B: 00/01 stopp,10 öppna,11 stäng. Rapporterar utgång, inte mekanisk position. | syfte följt i kod |
| uart2.tx.073.p09/tx_fields/0 | Shuntmotor: riktningsutgång OUT5B | Tillsammans med OUT5A: 00/01 stopp,10 öppna,11 stäng. Rapporterar utgång, inte mekanisk position. | syfte följt i kod |
| uart2.tx.073.p10/tx_fields/0 | Shuntventilens steg | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p11/tx_fields/0 | Shuntventilens rörelsestatus | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | syfte med källkorrelation |
| uart2.tx.073.p12/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.073.p13/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.074.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.074.p01/tx_fields/0 | Varmvattenpump 4 | Visa pumpens utgångsstatus. Fysisk cirkulation kräver separat verifiering. | syfte med källkorrelation |
| uart2.tx.074.p02/tx_fields/0 | Zonpump på OUT13 | Visa pumpens utgångsstatus. Fysisk cirkulation kräver separat verifiering. | syfte med källkorrelation |
| uart2.tx.074.p03/tx_fields/0 | Ytterligare zonpumpsutgång | Visa pumpens utgångsstatus. Fysisk cirkulation kräver separat verifiering. | syfte med källkorrelation |
| uart2.tx.075.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.075.p01/tx_fields/0 | Övertemperatur i primärkretsen | Upptäcka att framledning eller retur blir för varm. | syfte följt i kod |
| uart2.tx.075.p02/tx_fields/0 | Övertemperatur i varmvattentanken | Upptäcka för hög temperatur i varmvattnet. | syfte följt i kod |
| uart2.tx.075.p03/tx_fields/0 | Fel på primär framledningsgivare | Visa när framledningstemperaturen inte kan användas som tillförlitligt mätvärde. | syfte följt i kod |
| uart2.tx.075.p04/tx_fields/0 | Fel på primär returgivare | Visa när returtemperaturen inte kan användas som tillförlitligt mätvärde. | syfte följt i kod |
| uart2.tx.075.p05/tx_fields/0 | Fel på varmvattengivare THW5B | Upptäcka bortfall eller fel i den nedre varmvattengivarens kanal. | syfte följt i kod |
| uart2.tx.075.p06/tx_fields/0 | Fel på framledningsgivare zon 1 | Kontrollera att zon 1 har ett användbart framledningsvärde. | syfte följt i kod |
| uart2.tx.075.p07/tx_fields/0 | Fel på returgivare zon 1 | Kontrollera att zon 1 har ett användbart returvärde. | syfte följt i kod |
| uart2.tx.075.p08/tx_fields/0 | Fel på framledningsgivare zon 2 | Kontrollera att zon 2 har ett användbart framledningsvärde. | syfte följt i kod |
| uart2.tx.075.p09/tx_fields/0 | Fel på returgivare zon 2 | Kontrollera att zon 2 har ett användbart returvärde. | syfte följt i kod |
| uart2.tx.075.p10/tx_fields/0 | Frysrisk i primärkretsen | Upptäcka farligt låg vattentemperatur i framledning eller retur. | syfte följt i kod |
| uart2.tx.075.p13/tx_fields/0 | Fel på varmvattengivare THW5A | Övervaka den övre varmvattengivaren; felet används också när temperaturkälla väljs. | syfte följt i kod |
| uart2.tx.076.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.076.p01/tx_fields/0 | Orimlig temperaturrespons i primärkretsen | Upptäcka utebliven temperaturökning under värmeproduktion tillsammans med orimligt förhållande mellan framledning och retur. | syfte följt i kod |
| uart2.tx.076.p02/tx_fields/0 | Omvänt temperaturförhållande i zon 1 | Upptäcka att zonens retur är mer än 5 grader varmare än framledningen under övervakad drift. | syfte följt i kod |
| uart2.tx.076.p03/tx_fields/0 | Omvänt temperaturförhållande i zon 2 | Upptäcka att zonens retur är mer än 5 grader varmare än framledningen under övervakad drift. | syfte följt i kod |
| uart2.tx.076.p04/tx_fields/0 | Otillräckligt primärflöde | Upptäcka för liten vattencirkulation via flödesvakt eller flödesmätare. | syfte följt i kod |
| uart2.tx.076.p05/tx_fields/0 | Utlöst flödesvakt 2 | Upptäcka utebliven cirkulation på kretsen som övervakas av flödesvakt 2. | syfte följt i kod |
| uart2.tx.076.p06/tx_fields/0 | Utlöst flödesvakt 3 | Upptäcka utebliven cirkulation på kretsen som övervakas av flödesvakt 3. | syfte följt i kod |
| uart2.tx.076.p07/tx_fields/0 | Fel på någon av zonernas rumsgivare | Visa om rumstemperaturen för zon 1 eller zon 2 inte går att lita på. | syfte följt i kod |
| uart2.tx.076.p08/tx_fields/0 | Fel på köldmediets vätsketemperaturgivare | Kontrollera att köldmediets temperaturkanal ger ett användbart värde. | syfte följt i kod |
| uart2.tx.076.p09/tx_fields/0 | För kallt under övervakad drift eller avfrostning | Upptäcka låga köldmedie-/vattentemperaturer i särskilda driftlägen. | syfte följt i kod |
| uart2.tx.076.p10/tx_fields/0 | Övertemperatur vid extern panna | Upptäcka för hög temperatur på pannans framledning. | syfte följt i kod |
| uart2.tx.076.p11/tx_fields/0 | Fel på pannans framledningsgivare | Kontrollera att den externa pannans framledningstemperatur är användbar. | syfte följt i kod |
| uart2.tx.076.p12/tx_fields/0 | Fel på delad panna-/buffertgivarkanal | Visa fel i givarkanalen som konfigurationen använder för pannretur eller bufferttank. | syfte följt i kod |
| uart2.tx.077.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.077.p01/tx_fields/0 | För låg framledning i zon 1 under särskild drift | Upptäcka att zon 1 förblir under 25 grader när det övervakade driftläget kräver uppvärmning. | syfte följt i kod |
| uart2.tx.077.p02/tx_fields/0 | Frysrisk vid extern panna | Upptäcka mycket låg temperatur på pannans framledning efter startvillkor och väntetider. | syfte följt i kod |
| uart2.tx.077.p03/tx_fields/0 | Oförenlig värmekällekonfiguration | Upptäcka kombinationer av värmekälla, tillgängliga enheter och systemval som inte stöds. | syfte följt i kod |
| uart2.tx.077.p04/tx_fields/0 | Kommunikationsövervakning av rumsgivarmottagaren | Upptäcka att giltig kommunikation från rumsgivarmottagaren uteblir under för lång tid. | syfte följt i kod |
| uart2.tx.077.p05/tx_fields/0 | Spärrad rumsreglering per rumskanal | Visa vilka av de åtta rumskanalerna som rapporterar status som hindrar rumsreglering. | syfte följt i kod |
| uart2.tx.077.p06/tx_fields/0 | Samlad avvikelse från anslutna källenheter | Visa om någon vald källenhet har den avvikelse som rapporteras i enheternas sammanfattande statusmask. | syfte följt i kod |
| uart2.tx.077.p07/tx_fields/0 | Misslyckad varmvatten-/växlingssekvens | Upptäcka utebliven tankuppvärmning eller för hög primärtemperatur under särskilda varmvattensekvenser. | syfte följt i kod |
| uart2.tx.077.p08/tx_fields/0 | Fel på vattenflödesmätarens givarkanal | Skilja ett fel på själva flödesgivaren från ett giltigt men för lågt vattenflöde. | syfte följt i kod |
| uart2.tx.078.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.078.p01/tx_fields/0 | Felkod från källenhet 1 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p02/tx_fields/0 | Felkod från källenhet 1 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p03/tx_fields/0 | Felkod från källenhet 2 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p04/tx_fields/0 | Felkod från källenhet 2 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p05/tx_fields/0 | Felkod från källenhet 3 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p06/tx_fields/0 | Felkod från källenhet 3 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p07/tx_fields/0 | Felkod från källenhet 4 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p08/tx_fields/0 | Felkod från källenhet 4 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p09/tx_fields/0 | Felkod från källenhet 5 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p10/tx_fields/0 | Felkod från källenhet 5 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p11/tx_fields/0 | Felkod från källenhet 6 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.078.p12/tx_fields/0 | Felkod från källenhet 6 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | syfte följt i kod |
| uart2.tx.079.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.079.p01/tx_fields/0 | Vattenflöde utanför tillåtet område | Visa resultatet av min-/maxflödesövervakningen. | syfte med källkorrelation |
| uart2.tx.080.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.080.p01/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p02/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p03/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p04/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p05/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p06/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p07/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p08/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p09/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p10/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p11/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p12/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p13/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.080.p14/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.081.p01/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p02/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p03/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p04/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p05/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p06/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p07/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p08/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p09/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p10/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p11/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p12/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.081.p13/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.082.p01/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p02/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p03/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p04/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p05/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p06/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p07/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p08/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p09/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p10/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p11/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p12/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p13/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.082.p14/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.083.p01/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p02/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p03/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p04/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p05/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p06/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p07/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p08/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p09/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p10/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p11/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.083.p12/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.084.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.085.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.086.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.087.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.088.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.089.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.090.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.090.p01/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.090.p02/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.090.p03/tx_fields/0 | Systemets på/av-läge | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | syfte med källkorrelation |
| uart2.tx.090.p04/tx_fields/0 | Aktivt driftläge | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | syfte med källkorrelation |
| uart2.tx.090.p05/tx_fields/0 | Varmvattenläge | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | syfte med källkorrelation |
| uart2.tx.090.p06/tx_fields/0 | Reglerläge zon 1 | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | syfte med källkorrelation |
| uart2.tx.090.p07/tx_fields/0 | Reglerläge zon 2 | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | syfte med källkorrelation |
| uart2.tx.090.p08/tx_fields/0 | Varmvattenbörvärde | Visa temperaturmålet som styr värmeproduktionen. | syfte med källkorrelation |
| uart2.tx.090.p09/tx_fields/0 | Varmvattenbörvärde | Visa temperaturmålet som styr värmeproduktionen. | syfte med källkorrelation |
| uart2.tx.090.p10/tx_fields/0 | Framledningsmål zon 1 | Visa temperaturmålet som styr värmeproduktionen. | syfte med källkorrelation |
| uart2.tx.090.p11/tx_fields/0 | Framledningsmål zon 1 | Visa temperaturmålet som styr värmeproduktionen. | syfte med källkorrelation |
| uart2.tx.090.p12/tx_fields/0 | Framledningsmål zon 2 | Visa temperaturmålet som styr värmeproduktionen. | syfte med källkorrelation |
| uart2.tx.090.p13/tx_fields/0 | Framledningsmål zon 2 | Visa temperaturmålet som styr värmeproduktionen. | syfte med källkorrelation |
| uart2.tx.090.p14/tx_fields/0 | Svar 90 – databyte 14 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.091.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.091.p01/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.091.p02/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.091.p03/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.091.p04/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.091.p05/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.091.p06/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.091.p07/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.091.p08/tx_fields/0 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | protokollroll belagd |
| uart2.tx.092.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.092.p01/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.092.p02/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.092.p03/tx_fields/0 | Tvingad varmvattenladdning | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p04/tx_fields/0 | Semesterläge | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p05/tx_fields/0 | Spärr för varmvatten | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p06/tx_fields/0 | Spärr för värme zon 1 | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p07/tx_fields/0 | Spärr för kyla zon 1 | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p08/tx_fields/0 | Spärr för värme zon 2 | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p09/tx_fields/0 | Spärr för kyla zon 2 | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p10/tx_fields/0 | Extern styrnings ägarskap | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p11/tx_fields/0 | Extern styrnings kompletterande status | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | syfte med källkorrelation |
| uart2.tx.092.p12/tx_fields/0 | Svar 92 – databyte 12 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.093.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.093.p01/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.093.p02/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.093.p03/tx_fields/0 | Värme-/kylval | Skilja vald temperaturfunktion. | syfte med källkorrelation |
| uart2.tx.093.p04/tx_fields/0 | Kompletterande temperaturmål zon 1 | Visa den andra målkanalen; exakt relation till valt reglerläge behöver konsumentvillkoren. | syfte följt i kod |
| uart2.tx.093.p05/tx_fields/0 | Kompletterande temperaturmål zon 1 | Visa den andra målkanalen; exakt relation till valt reglerläge behöver konsumentvillkoren. | syfte följt i kod |
| uart2.tx.093.p06/tx_fields/0 | Kompletterande temperaturmål zon 2 | Visa den andra målkanalen; exakt relation till valt reglerläge behöver konsumentvillkoren. | syfte följt i kod |
| uart2.tx.093.p07/tx_fields/0 | Kompletterande temperaturmål zon 2 | Visa den andra målkanalen; exakt relation till valt reglerläge behöver konsumentvillkoren. | syfte följt i kod |
| uart2.tx.094.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.094.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.094.p02/tx_fields/0 | Legionellakörning tillåten | Läsa konfigurationen för legionellakörning tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p04/tx_fields/0 | Legionellakörning tillåten | Läsa konfigurationen för legionellakörning tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p05/tx_fields/0 | Varmvattenmål | Läsa konfigurationen för varmvattenmål. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p07/tx_fields/0 | Varmvattenmål | Läsa konfigurationen för varmvattenmål. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p08/tx_fields/0 | Temperaturfall före varmvattenstart | Läsa konfigurationen för temperaturfall före varmvattenstart. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p09/tx_fields/0 | Temperaturfall före varmvattenstart | Läsa konfigurationen för temperaturfall före varmvattenstart. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p10/tx_fields/0 | Temperaturfall före varmvattenstart | Läsa konfigurationen för temperaturfall före varmvattenstart. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p11/tx_fields/0 | Maximal varmvattenkörtid | Läsa konfigurationen för maximal varmvattenkörtid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p12/tx_fields/0 | Maximal varmvattenkörtid | Läsa konfigurationen för maximal varmvattenkörtid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p13/tx_fields/0 | Maximal varmvattenkörtid | Läsa konfigurationen för maximal varmvattenkörtid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.094.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.095.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.095.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.095.p02/tx_fields/0 | Paus mellan varmvattenkörningar | Läsa konfigurationen för paus mellan varmvattenkörningar. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p03/tx_fields/0 | Paus mellan varmvattenkörningar | Läsa konfigurationen för paus mellan varmvattenkörningar. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p04/tx_fields/0 | Paus mellan varmvattenkörningar | Läsa konfigurationen för paus mellan varmvattenkörningar. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p05/tx_fields/0 | Normal/eco-varmvatten | Läsa konfigurationen för normal/eco-varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p07/tx_fields/0 | Normal/eco-varmvatten | Läsa konfigurationen för normal/eco-varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p08/tx_fields/0 | Legionellatemperatur | Läsa konfigurationen för legionellatemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p09/tx_fields/0 | Legionellatemperatur | Läsa konfigurationen för legionellatemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p10/tx_fields/0 | Legionellatemperatur | Läsa konfigurationen för legionellatemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p11/tx_fields/0 | Intervall mellan legionellakörningar | Läsa konfigurationen för intervall mellan legionellakörningar. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p12/tx_fields/0 | Intervall mellan legionellakörningar | Läsa konfigurationen för intervall mellan legionellakörningar. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p13/tx_fields/0 | Intervall mellan legionellakörningar | Läsa konfigurationen för intervall mellan legionellakörningar. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.095.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.096.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.096.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.096.p02/tx_fields/0 | Starttid för legionellakörning | Läsa konfigurationen för starttid för legionellakörning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p03/tx_fields/0 | Starttid för legionellakörning | Läsa konfigurationen för starttid för legionellakörning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p04/tx_fields/0 | Starttid för legionellakörning | Läsa konfigurationen för starttid för legionellakörning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p05/tx_fields/0 | Maximal legionellakörtid | Läsa konfigurationen för maximal legionellakörtid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p06/tx_fields/0 | Maximal legionellakörtid | Läsa konfigurationen för maximal legionellakörtid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p07/tx_fields/0 | Maximal legionellakörtid | Läsa konfigurationen för maximal legionellakörtid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p08/tx_fields/0 | Temperaturhålltid vid legionellakörning | Läsa konfigurationen för temperaturhålltid vid legionellakörning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p09/tx_fields/0 | Temperaturhålltid vid legionellakörning | Läsa konfigurationen för temperaturhålltid vid legionellakörning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p10/tx_fields/0 | Temperaturhålltid vid legionellakörning | Läsa konfigurationen för temperaturhålltid vid legionellakörning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.096.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.097.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.097.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.097.p02/tx_fields/0 | Reglerläge zon 1 | Läsa konfigurationen för reglerläge zon 1. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.097.p04/tx_fields/0 | Reglerläge zon 1 | Läsa konfigurationen för reglerläge zon 1. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.097.p05/tx_fields/0 | Reglerläge zon 2 | Läsa konfigurationen för reglerläge zon 2. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.097.p07/tx_fields/0 | Reglerläge zon 2 | Läsa konfigurationen för reglerläge zon 2. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.097.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.098.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.098.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.098.p02/tx_fields/0 | Format för zoninställningen | Tolka efterföljande inställningsvärden. | protokollroll belagd |
| uart2.tx.098.p03/tx_fields/0 | Vald zon | Ange vilken zon inställningssvaret gäller. | protokollroll belagd |
| uart2.tx.098.p05/tx_fields/0 | Rumsbörvärde värme | Visa börvärdet för den valda zonen och reglerformen. | syfte med källkorrelation |
| uart2.tx.098.p07/tx_fields/0 | Fast framledningsmål värme | Visa börvärdet för den valda zonen och reglerformen. | syfte med källkorrelation |
| uart2.tx.098.p09/tx_fields/0 | Värmekurvans temperaturmål | Visa börvärdet för den valda zonen och reglerformen. | syfte med källkorrelation |
| uart2.tx.098.p11/tx_fields/0 | Rumsbörvärde kyla | Visa börvärdet för den valda zonen och reglerformen. | syfte med källkorrelation |
| uart2.tx.098.p13/tx_fields/0 | Fast framledningsmål kyla | Visa börvärdet för den valda zonen och reglerformen. | syfte med källkorrelation |
| uart2.tx.098.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.099.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.099.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.099.p02/tx_fields/0 | Format för zoninställningen | Tolka efterföljande inställningsvärden. | protokollroll belagd |
| uart2.tx.099.p03/tx_fields/0 | Vald zon | Ange vilken zon inställningssvaret gäller. | protokollroll belagd |
| uart2.tx.099.p04/tx_fields/0 | Värmekurvans tre punkter för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.099.p05/tx_fields/0 | Värmekurvans tre punkter för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.099.p06/tx_fields/0 | Värmekurvans tre punkter för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.099.p07/tx_fields/0 | Värmekurvans tre punkter för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.099.p08/tx_fields/0 | Värmekurvans tre punkter för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.099.p09/tx_fields/0 | Värmekurvans tre punkter för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.099.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.100.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.100.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.100.p03/tx_fields/0 | Val av veckoprogram | Ange programbanken som svarsdatan hör till. | protokollroll belagd |
| uart2.tx.100.p04/tx_fields/0 | Val av dag/tidsblock | Välja del av veckoprogrammet tillsammans med första väljaren. | protokollroll belagd |
| uart2.tx.100.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.101.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.101.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.101.p02/tx_fields/0 | Årsperiod för veckoprogram 2 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.101.p03/tx_fields/0 | Årsperiod för veckoprogram 2 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.101.p04/tx_fields/0 | Årsperiod för veckoprogram 2 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.101.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.102.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.102.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.102.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.103.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.103.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.103.p02/tx_fields/0 | Semesterfunktioner | Läsa konfigurationen för semesterfunktioner. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p03/tx_fields/0 | Semesterfunktioner | Läsa konfigurationen för semesterfunktioner. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p04/tx_fields/0 | Semesterfunktioner | Läsa konfigurationen för semesterfunktioner. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p05/tx_fields/0 | Semesterns startdatum | Läsa konfigurationen för semesterns startdatum. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p06/tx_fields/0 | Semesterns startdatum | Läsa konfigurationen för semesterns startdatum. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p07/tx_fields/0 | Semesterns startdatum | Läsa konfigurationen för semesterns startdatum. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p08/tx_fields/0 | Semesterns slutdatum | Läsa konfigurationen för semesterns slutdatum. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p09/tx_fields/0 | Semesterns slutdatum | Läsa konfigurationen för semesterns slutdatum. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p10/tx_fields/0 | Semesterns slutdatum | Läsa konfigurationen för semesterns slutdatum. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.103.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.104.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.104.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.104.p02/tx_fields/0 | Format för zoninställningen | Tolka efterföljande inställningsvärden. | protokollroll belagd |
| uart2.tx.104.p03/tx_fields/0 | Vald zon | Ange vilken zon inställningssvaret gäller. | protokollroll belagd |
| uart2.tx.104.p04/tx_fields/0 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.104.p05/tx_fields/0 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.104.p06/tx_fields/0 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.104.p07/tx_fields/0 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.104.p08/tx_fields/0 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.104.p09/tx_fields/0 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.104.p10/tx_fields/0 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.104.p11/tx_fields/0 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.104.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.105.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.105.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.105.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.106.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.106.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.106.p02/tx_fields/0 | Displayspråk | Läsa konfigurationen för displayspråk. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.106.p04/tx_fields/0 | Displayspråk | Läsa konfigurationen för displayspråk. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.106.p05/tx_fields/0 | Temperaturenhet | Läsa konfigurationen för temperaturenhet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.106.p07/tx_fields/0 | Temperaturenhet | Läsa konfigurationen för temperaturenhet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.106.p08/tx_fields/0 | Temperaturvisning | Läsa konfigurationen för temperaturvisning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.106.p10/tx_fields/0 | Temperaturvisning | Läsa konfigurationen för temperaturvisning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.106.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.107.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.107.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.107.p02/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p03/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p04/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p05/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p06/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p07/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p08/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p09/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p10/tx_fields/0 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.107.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.108.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.108.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.108.p02/tx_fields/0 | Tidsformat | Läsa konfigurationen för tidsformat. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.108.p04/tx_fields/0 | Tidsformat | Läsa konfigurationen för tidsformat. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.108.p05/tx_fields/0 | Fjärrkontrollens zon | Läsa konfigurationen för fjärrkontrollens zon. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.108.p07/tx_fields/0 | Fjärrkontrollens zon | Läsa konfigurationen för fjärrkontrollens zon. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.108.p08/tx_fields/0 | Rumsgivare zon 1 | Läsa konfigurationen för rumsgivare zon 1. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.108.p10/tx_fields/0 | Rumsgivare zon 1 | Läsa konfigurationen för rumsgivare zon 1. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.108.p11/tx_fields/0 | Rumsgivare zon 2 | Läsa konfigurationen för rumsgivare zon 2. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.108.p13/tx_fields/0 | Rumsgivare zon 2 | Läsa konfigurationen för rumsgivare zon 2. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.108.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.109.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.109.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.109.p02/tx_fields/0 | Format för zoninställningen | Tolka efterföljande inställningsvärden. | protokollroll belagd |
| uart2.tx.109.p03/tx_fields/0 | Vald zon | Ange vilken zon inställningssvaret gäller. | protokollroll belagd |
| uart2.tx.109.p04/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p05/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p06/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p07/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p08/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p09/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p10/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p11/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p12/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p13/tx_fields/0 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.109.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.110.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.110.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.110.p02/tx_fields/0 | Kalibrering THW1 framledning | Läsa konfigurationen för kalibrering thw1 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.110.p04/tx_fields/0 | Kalibrering THW1 framledning | Läsa konfigurationen för kalibrering thw1 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.110.p05/tx_fields/0 | Kalibrering THW2 retur | Läsa konfigurationen för kalibrering thw2 retur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.110.p07/tx_fields/0 | Kalibrering THW2 retur | Läsa konfigurationen för kalibrering thw2 retur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.110.p08/tx_fields/0 | Kalibrering THW5 varmvatten | Läsa konfigurationen för kalibrering thw5 varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.110.p10/tx_fields/0 | Kalibrering THW5 varmvatten | Läsa konfigurationen för kalibrering thw5 varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.110.p11/tx_fields/0 | Kalibrering THW6 zon 1 framledning | Läsa konfigurationen för kalibrering thw6 zon 1 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.110.p13/tx_fields/0 | Kalibrering THW6 zon 1 framledning | Läsa konfigurationen för kalibrering thw6 zon 1 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.110.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.111.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.111.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.111.p02/tx_fields/0 | Kalibrering THW7 zon 1 retur | Läsa konfigurationen för kalibrering thw7 zon 1 retur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.111.p04/tx_fields/0 | Kalibrering THW7 zon 1 retur | Läsa konfigurationen för kalibrering thw7 zon 1 retur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.111.p05/tx_fields/0 | Kalibrering THW8 zon 2 framledning | Läsa konfigurationen för kalibrering thw8 zon 2 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.111.p07/tx_fields/0 | Kalibrering THW8 zon 2 framledning | Läsa konfigurationen för kalibrering thw8 zon 2 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.111.p08/tx_fields/0 | Kalibrering THW9 zon 2 retur | Läsa konfigurationen för kalibrering thw9 zon 2 retur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.111.p10/tx_fields/0 | Kalibrering THW9 zon 2 retur | Läsa konfigurationen för kalibrering thw9 zon 2 retur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.111.p11/tx_fields/0 | Kalibrering THWB1 pannframledning | Läsa konfigurationen för kalibrering thwb1 pannframledning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.111.p13/tx_fields/0 | Kalibrering THWB1 pannframledning | Läsa konfigurationen för kalibrering thwb1 pannframledning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.111.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.112.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.112.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.112.p02/tx_fields/0 | Kalibrering THWB2 pannretur | Korrigera givarens temperaturbidrag. | syfte med SD-korrelation |
| uart2.tx.112.p04/tx_fields/0 | Kalibrering THWB2 pannretur | Korrigera givarens temperaturbidrag. | syfte med SD-korrelation |
| uart2.tx.112.p11/tx_fields/0 | Kalibrering THW5A övre varmvatten | Korrigera givarens temperaturbidrag. | syfte med SD-korrelation |
| uart2.tx.112.p13/tx_fields/0 | Kalibrering THW5A övre varmvatten | Korrigera givarens temperaturbidrag. | syfte med SD-korrelation |
| uart2.tx.112.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.113.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.113.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.113.p02/tx_fields/0 | Tillåt ekonomistopp av pump 1 | Läsa konfigurationen för tillåt ekonomistopp av pump 1. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.113.p04/tx_fields/0 | Tillåt ekonomistopp av pump 1 | Läsa konfigurationen för tillåt ekonomistopp av pump 1. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.113.p05/tx_fields/0 | Villkor för pumpstopp | Läsa konfigurationen för villkor för pumpstopp. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.113.p07/tx_fields/0 | Villkor för pumpstopp | Läsa konfigurationen för villkor för pumpstopp. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.113.p08/tx_fields/0 | Frysskyddets framledningsmål | Läsa konfigurationen för frysskyddets framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.113.p10/tx_fields/0 | Frysskyddets framledningsmål | Läsa konfigurationen för frysskyddets framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.113.p11/tx_fields/0 | Frysskyddets utetemperaturgräns | Läsa konfigurationen för frysskyddets utetemperaturgräns. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.113.p13/tx_fields/0 | Frysskyddets utetemperaturgräns | Läsa konfigurationen för frysskyddets utetemperaturgräns. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.113.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.114.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.114.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.114.p02/tx_fields/0 | Eltillskott för värme tillåtet | Läsa konfigurationen för eltillskott för värme tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.114.p04/tx_fields/0 | Eltillskott för värme tillåtet | Läsa konfigurationen för eltillskott för värme tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.114.p05/tx_fields/0 | Fördröjning före eltillskott värme | Läsa konfigurationen för fördröjning före eltillskott värme. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.114.p07/tx_fields/0 | Fördröjning före eltillskott värme | Läsa konfigurationen för fördröjning före eltillskott värme. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.114.p08/tx_fields/0 | Eltillskott för varmvatten tillåtet | Läsa konfigurationen för eltillskott för varmvatten tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.114.p10/tx_fields/0 | Eltillskott för varmvatten tillåtet | Läsa konfigurationen för eltillskott för varmvatten tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.114.p11/tx_fields/0 | Fördröjning före eltillskott varmvatten | Läsa konfigurationen för fördröjning före eltillskott varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.114.p13/tx_fields/0 | Fördröjning före eltillskott varmvatten | Läsa konfigurationen för fördröjning före eltillskott varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.114.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.115.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.115.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.115.p02/tx_fields/0 | Shuntens fulla gångtid | Läsa konfigurationen för shuntens fulla gångtid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.115.p04/tx_fields/0 | Shuntens fulla gångtid | Läsa konfigurationen för shuntens fulla gångtid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.115.p05/tx_fields/0 | Intervall mellan shuntkorrigeringar | Läsa konfigurationen för intervall mellan shuntkorrigeringar. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.115.p07/tx_fields/0 | Intervall mellan shuntkorrigeringar | Läsa konfigurationen för intervall mellan shuntkorrigeringar. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.115.p08/tx_fields/0 | Konfigurerad nivå för primärpump | Läsa konfigurationen för konfigurerad nivå för primärpump. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.115.p10/tx_fields/0 | Konfigurerad nivå för primärpump | Läsa konfigurationen för konfigurerad nivå för primärpump. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.115.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.116.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.116.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.116.p02/tx_fields/0 | Val av värmekälla | Läsa konfigurationen för val av värmekälla. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.116.p04/tx_fields/0 | Val av värmekälla | Läsa konfigurationen för val av värmekälla. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.116.p05/tx_fields/0 | Samtidig värme och varmvatten | Läsa konfigurationen för samtidig värme och varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.116.p07/tx_fields/0 | Samtidig värme och varmvatten | Läsa konfigurationen för samtidig värme och varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.116.p08/tx_fields/0 | Utetemperatur för samtidig drift | Läsa konfigurationen för utetemperatur för samtidig drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.116.p10/tx_fields/0 | Utetemperatur för samtidig drift | Läsa konfigurationen för utetemperatur för samtidig drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.116.p11/tx_fields/0 | Lågtemperaturväxling tillåten | Läsa konfigurationen för lågtemperaturväxling tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.116.p13/tx_fields/0 | Lågtemperaturväxling tillåten | Läsa konfigurationen för lågtemperaturväxling tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.116.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.117.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.117.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.117.p02/tx_fields/0 | Utetemperatur för lågtemperaturväxling | Läsa konfigurationen för utetemperatur för lågtemperaturväxling. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.117.p04/tx_fields/0 | Utetemperatur för lågtemperaturväxling | Läsa konfigurationen för utetemperatur för lågtemperaturväxling. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.117.p05/tx_fields/0 | Rumsregleringens tidsintervall | Läsa konfigurationen för rumsregleringens tidsintervall. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.117.p07/tx_fields/0 | Rumsregleringens tidsintervall | Läsa konfigurationen för rumsregleringens tidsintervall. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.117.p08/tx_fields/0 | Lägsta framledningsmål | Läsa konfigurationen för lägsta framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.117.p10/tx_fields/0 | Lägsta framledningsmål | Läsa konfigurationen för lägsta framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.117.p11/tx_fields/0 | Högsta framledningsmål | Läsa konfigurationen för högsta framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.117.p13/tx_fields/0 | Högsta framledningsmål | Läsa konfigurationen för högsta framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.117.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.118.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.118.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.118.p02/tx_fields/0 | Temperaturhysteres aktiverad | Läsa konfigurationen för temperaturhysteres aktiverad. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.118.p04/tx_fields/0 | Temperaturhysteres aktiverad | Läsa konfigurationen för temperaturhysteres aktiverad. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.118.p05/tx_fields/0 | Nedre temperaturhysteres | Läsa konfigurationen för nedre temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.118.p07/tx_fields/0 | Nedre temperaturhysteres | Läsa konfigurationen för nedre temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.118.p08/tx_fields/0 | Övre temperaturhysteres | Läsa konfigurationen för övre temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.118.p10/tx_fields/0 | Övre temperaturhysteres | Läsa konfigurationen för övre temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.118.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.119.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.119.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.119.p02/tx_fields/0 | Värmepumpens beräkningskapacitet | Läsa konfigurationen för värmepumpens beräkningskapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p03/tx_fields/0 | Värmepumpens beräkningskapacitet | Läsa konfigurationen för värmepumpens beräkningskapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p04/tx_fields/0 | Värmepumpens beräkningskapacitet | Läsa konfigurationen för värmepumpens beräkningskapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p05/tx_fields/0 | Eltillskott 1 kapacitet | Läsa konfigurationen för eltillskott 1 kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p07/tx_fields/0 | Eltillskott 1 kapacitet | Läsa konfigurationen för eltillskott 1 kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p08/tx_fields/0 | Eltillskott 2 kapacitet | Läsa konfigurationen för eltillskott 2 kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p10/tx_fields/0 | Eltillskott 2 kapacitet | Läsa konfigurationen för eltillskott 2 kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p11/tx_fields/0 | Hybridens prioritering | Läsa konfigurationen för hybridens prioritering. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p13/tx_fields/0 | Hybridens prioritering | Läsa konfigurationen för hybridens prioritering. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.119.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.120.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.120.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.120.p02/tx_fields/0 | Hybridens utetemperaturgräns | Läsa konfigurationen för hybridens utetemperaturgräns. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p04/tx_fields/0 | Hybridens utetemperaturgräns | Läsa konfigurationen för hybridens utetemperaturgräns. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p05/tx_fields/0 | Pannans verkningsgrad | Läsa konfigurationen för pannans verkningsgrad. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p07/tx_fields/0 | Pannans verkningsgrad | Läsa konfigurationen för pannans verkningsgrad. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p08/tx_fields/0 | Pannbränslets pris | Läsa konfigurationen för pannbränslets pris. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p09/tx_fields/0 | Pannbränslets pris | Läsa konfigurationen för pannbränslets pris. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p10/tx_fields/0 | Pannbränslets pris | Läsa konfigurationen för pannbränslets pris. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p11/tx_fields/0 | Elens CO2-faktor | Läsa konfigurationen för elens co2-faktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p12/tx_fields/0 | Elens CO2-faktor | Läsa konfigurationen för elens co2-faktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p13/tx_fields/0 | Elens CO2-faktor | Läsa konfigurationen för elens co2-faktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.120.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.121.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.121.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.121.p02/tx_fields/0 | Pannbränslets CO2-faktor | Läsa konfigurationen för pannbränslets co2-faktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.121.p03/tx_fields/0 | Pannbränslets CO2-faktor | Läsa konfigurationen för pannbränslets co2-faktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.121.p04/tx_fields/0 | Pannbränslets CO2-faktor | Läsa konfigurationen för pannbränslets co2-faktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.121.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.122.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.122.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.122.p02/tx_fields/0 | Format för tabellvärden | Tolka de efterföljande värdena med samma format. | protokollroll belagd |
| uart2.tx.122.p03/tx_fields/0 | Konfigurerad COP-punkt 1 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p04/tx_fields/0 | Konfigurerad COP-punkt 1 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p05/tx_fields/0 | Konfigurerad COP-punkt 2 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p06/tx_fields/0 | Konfigurerad COP-punkt 2 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p07/tx_fields/0 | Konfigurerad COP-punkt 3 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p08/tx_fields/0 | Konfigurerad COP-punkt 3 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p09/tx_fields/0 | Konfigurerad COP-punkt 4 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p10/tx_fields/0 | Konfigurerad COP-punkt 4 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p11/tx_fields/0 | Konfigurerad COP-punkt 5 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p12/tx_fields/0 | Konfigurerad COP-punkt 5 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p13/tx_fields/0 | Konfigurerad COP-punkt 6 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p14/tx_fields/0 | Konfigurerad COP-punkt 6 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.122.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.123.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.123.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.123.p02/tx_fields/0 | Format för tabellvärden | Tolka de efterföljande värdena med samma format. | protokollroll belagd |
| uart2.tx.123.p03/tx_fields/0 | Konfigurerad COP-punkt 7 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p04/tx_fields/0 | Konfigurerad COP-punkt 7 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p05/tx_fields/0 | Konfigurerad COP-punkt 8 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p06/tx_fields/0 | Konfigurerad COP-punkt 8 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p07/tx_fields/0 | Konfigurerad COP-punkt 9 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p08/tx_fields/0 | Konfigurerad COP-punkt 9 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p09/tx_fields/0 | Konfigurerad COP-punkt 10 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p10/tx_fields/0 | Konfigurerad COP-punkt 10 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p11/tx_fields/0 | Konfigurerad COP-punkt 11 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p12/tx_fields/0 | Konfigurerad COP-punkt 11 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p13/tx_fields/0 | Konfigurerad COP-punkt 12 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p14/tx_fields/0 | Konfigurerad COP-punkt 12 | Underlag för val av värmekälla; inte uppmätt live-COP. | syfte med SD-korrelation |
| uart2.tx.123.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.124.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.124.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.124.p02/tx_fields/0 | Period för elprissäsong 2 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.124.p03/tx_fields/0 | Period för elprissäsong 2 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.124.p04/tx_fields/0 | Period för elprissäsong 2 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.124.p05/tx_fields/0 | Period för elprissäsong 3 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.124.p06/tx_fields/0 | Period för elprissäsong 3 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.124.p07/tx_fields/0 | Period för elprissäsong 3 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | syfte med källkorrelation |
| uart2.tx.124.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.125.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.125.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.125.p02/tx_fields/0 | Format för tabellvärden | Tolka de efterföljande värdena med samma format. | protokollroll belagd |
| uart2.tx.125.p03/tx_fields/0 | Elpris 1 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p04/tx_fields/0 | Elpris 1 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p05/tx_fields/0 | Elpris 2 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p06/tx_fields/0 | Elpris 2 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p07/tx_fields/0 | Elpris 3 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p08/tx_fields/0 | Elpris 3 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p09/tx_fields/0 | Elpris 4 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p10/tx_fields/0 | Elpris 4 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p11/tx_fields/0 | Elpris 5 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p12/tx_fields/0 | Elpris 5 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p13/tx_fields/0 | Elpris 6 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p14/tx_fields/0 | Elpris 6 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.125.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.126.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.126.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.126.p02/tx_fields/0 | Format för tabellvärden | Tolka de efterföljande värdena med samma format. | protokollroll belagd |
| uart2.tx.126.p03/tx_fields/0 | Elpris 7 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.126.p04/tx_fields/0 | Elpris 7 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.126.p05/tx_fields/0 | Elpris 8 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.126.p06/tx_fields/0 | Elpris 8 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.126.p07/tx_fields/0 | Elpris 9 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.126.p08/tx_fields/0 | Elpris 9 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.126.p09/tx_fields/0 | Elpris 10 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.126.p10/tx_fields/0 | Elpris 10 | Underlag för hybridens kostnadsjämförelse. | syfte med SD-korrelation |
| uart2.tx.126.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.127.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.127.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.127.p02/tx_fields/0 | Varmvattenpatronens beräkningskapacitet | Läsa konfigurationen för varmvattenpatronens beräkningskapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p04/tx_fields/0 | Varmvattenpatronens beräkningskapacitet | Läsa konfigurationen för varmvattenpatronens beräkningskapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p05/tx_fields/0 | Elmätarens pulsfaktor | Läsa konfigurationen för elmätarens pulsfaktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p06/tx_fields/0 | Elmätarens pulsfaktor | Läsa konfigurationen för elmätarens pulsfaktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p07/tx_fields/0 | Elmätarens pulsfaktor | Läsa konfigurationen för elmätarens pulsfaktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p08/tx_fields/0 | Värmemätarens pulsfaktor | Läsa konfigurationen för värmemätarens pulsfaktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p09/tx_fields/0 | Värmemätarens pulsfaktor | Läsa konfigurationen för värmemätarens pulsfaktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p10/tx_fields/0 | Värmemätarens pulsfaktor | Läsa konfigurationen för värmemätarens pulsfaktor. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p11/tx_fields/0 | Pump 1 beräkningsbidrag | Läsa konfigurationen för pump 1 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p12/tx_fields/0 | Pump 1 beräkningsbidrag | Läsa konfigurationen för pump 1 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p13/tx_fields/0 | Pump 1 beräkningsbidrag | Läsa konfigurationen för pump 1 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.127.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.128.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.128.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.128.p02/tx_fields/0 | Pump 2 beräkningsbidrag | Läsa konfigurationen för pump 2 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p03/tx_fields/0 | Pump 2 beräkningsbidrag | Läsa konfigurationen för pump 2 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p04/tx_fields/0 | Pump 2 beräkningsbidrag | Läsa konfigurationen för pump 2 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p05/tx_fields/0 | Pump 3 beräkningsbidrag | Läsa konfigurationen för pump 3 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p06/tx_fields/0 | Pump 3 beräkningsbidrag | Läsa konfigurationen för pump 3 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p07/tx_fields/0 | Pump 3 beräkningsbidrag | Läsa konfigurationen för pump 3 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p08/tx_fields/0 | Korrigering av producerad energi | Läsa konfigurationen för korrigering av producerad energi. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p10/tx_fields/0 | Korrigering av producerad energi | Läsa konfigurationen för korrigering av producerad energi. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p11/tx_fields/0 | Flödesgivarens nedre skalpunkt | Läsa konfigurationen för flödesgivarens nedre skalpunkt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p13/tx_fields/0 | Flödesgivarens nedre skalpunkt | Läsa konfigurationen för flödesgivarens nedre skalpunkt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.128.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.129.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.129.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.129.p02/tx_fields/0 | Flödesgivarens övre skalpunkt | Läsa konfigurationen för flödesgivarens övre skalpunkt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.129.p04/tx_fields/0 | Flödesgivarens övre skalpunkt | Läsa konfigurationen för flödesgivarens övre skalpunkt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.129.p05/tx_fields/0 | Varmvattentillskott | Läsa konfigurationen för varmvattentillskott. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.129.p07/tx_fields/0 | Varmvattentillskott | Läsa konfigurationen för varmvattentillskott. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.129.p08/tx_fields/0 | Normal/snabb rumsreglering | Läsa konfigurationen för normal/snabb rumsreglering. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.129.p10/tx_fields/0 | Normal/snabb rumsreglering | Läsa konfigurationen för normal/snabb rumsreglering. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.129.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.130.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.130.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.130.p03/tx_fields/0 | Val av elprissäsong och veckodag | Ange vilket schemablock som efterfrågas. | protokollroll belagd |
| uart2.tx.130.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.131.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.131.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.131.p02/tx_fields/0 | Golvtorkning start-/sluttemperatur | Läsa konfigurationen för golvtorkning start-/sluttemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p03/tx_fields/0 | Golvtorkning start-/sluttemperatur | Läsa konfigurationen för golvtorkning start-/sluttemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p04/tx_fields/0 | Golvtorkning start-/sluttemperatur | Läsa konfigurationen för golvtorkning start-/sluttemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p05/tx_fields/0 | Golvtorkning maxtemperatur | Läsa konfigurationen för golvtorkning maxtemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p06/tx_fields/0 | Golvtorkning maxtemperatur | Läsa konfigurationen för golvtorkning maxtemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p07/tx_fields/0 | Golvtorkning maxtemperatur | Läsa konfigurationen för golvtorkning maxtemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p08/tx_fields/0 | Golvtorkning hålltid | Läsa konfigurationen för golvtorkning hålltid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p09/tx_fields/0 | Golvtorkning hålltid | Läsa konfigurationen för golvtorkning hålltid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p10/tx_fields/0 | Golvtorkning hålltid | Läsa konfigurationen för golvtorkning hålltid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p11/tx_fields/0 | Golvtorkning uppsteg | Läsa konfigurationen för golvtorkning uppsteg. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p12/tx_fields/0 | Golvtorkning uppsteg | Läsa konfigurationen för golvtorkning uppsteg. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p13/tx_fields/0 | Golvtorkning uppsteg | Läsa konfigurationen för golvtorkning uppsteg. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.131.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.132.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.132.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.132.p02/tx_fields/0 | Golvtorkning hålltid uppåt | Läsa konfigurationen för golvtorkning hålltid uppåt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p03/tx_fields/0 | Golvtorkning hålltid uppåt | Läsa konfigurationen för golvtorkning hålltid uppåt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p04/tx_fields/0 | Golvtorkning hålltid uppåt | Läsa konfigurationen för golvtorkning hålltid uppåt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p05/tx_fields/0 | Golvtorkning nedsteg | Läsa konfigurationen för golvtorkning nedsteg. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p06/tx_fields/0 | Golvtorkning nedsteg | Läsa konfigurationen för golvtorkning nedsteg. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p07/tx_fields/0 | Golvtorkning nedsteg | Läsa konfigurationen för golvtorkning nedsteg. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p08/tx_fields/0 | Golvtorkning hålltid nedåt | Läsa konfigurationen för golvtorkning hålltid nedåt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p09/tx_fields/0 | Golvtorkning hålltid nedåt | Läsa konfigurationen för golvtorkning hålltid nedåt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p10/tx_fields/0 | Golvtorkning hålltid nedåt | Läsa konfigurationen för golvtorkning hålltid nedåt. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p11/tx_fields/0 | Funktionsval för IN4 och IN5 | Läsa konfigurationen för funktionsval för in4 och in5. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p12/tx_fields/0 | Funktionsval för IN4 och IN5 | Läsa konfigurationen för funktionsval för in4 och in5. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p13/tx_fields/0 | Funktionsval för IN4 och IN5 | Läsa konfigurationen för funktionsval för in4 och in5. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.132.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.133.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.133.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.133.p02/tx_fields/0 | Smart-grid temperaturbidrag varmvatten | Läsa konfigurationen för smart-grid temperaturbidrag varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.133.p04/tx_fields/0 | Smart-grid temperaturbidrag varmvatten | Läsa konfigurationen för smart-grid temperaturbidrag varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.133.p05/tx_fields/0 | Smart-grid temperaturbidrag värme | Läsa konfigurationen för smart-grid temperaturbidrag värme. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.133.p07/tx_fields/0 | Smart-grid temperaturbidrag värme | Läsa konfigurationen för smart-grid temperaturbidrag värme. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.133.p08/tx_fields/0 | Termo-ON-utgångens val | Läsa konfigurationen för termo-on-utgångens val. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.133.p10/tx_fields/0 | Termo-ON-utgångens val | Läsa konfigurationen för termo-on-utgångens val. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.133.p11/tx_fields/0 | Startgivare för varmvattenåterladdning | Läsa konfigurationen för startgivare för varmvattenåterladdning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.133.p13/tx_fields/0 | Startgivare för varmvattenåterladdning | Läsa konfigurationen för startgivare för varmvattenåterladdning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.133.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.134.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.134.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.134.p02/tx_fields/0 | Variabel flödesstyrning | Läsa konfigurationen för variabel flödesstyrning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.134.p04/tx_fields/0 | Variabel flödesstyrning | Läsa konfigurationen för variabel flödesstyrning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.134.p05/tx_fields/0 | Analog 0–10 V-styrning | Läsa konfigurationen för analog 0–10 v-styrning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.134.p07/tx_fields/0 | Analog 0–10 V-styrning | Läsa konfigurationen för analog 0–10 v-styrning. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.134.p08/tx_fields/0 | Analogstyrningens intervall | Läsa konfigurationen för analogstyrningens intervall. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.134.p10/tx_fields/0 | Analogstyrningens intervall | Läsa konfigurationen för analogstyrningens intervall. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.134.p11/tx_fields/0 | Analogstyrningens effektparameter | Läsa konfigurationen för analogstyrningens effektparameter. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.134.p13/tx_fields/0 | Analogstyrningens effektparameter | Läsa konfigurationen för analogstyrningens effektparameter. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.134.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.135.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.135.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.135.p02/tx_fields/0 | Pump 4 beräkningsbidrag | Läsa konfigurationen för pump 4 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p03/tx_fields/0 | Pump 4 beräkningsbidrag | Läsa konfigurationen för pump 4 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p04/tx_fields/0 | Pump 4 beräkningsbidrag | Läsa konfigurationen för pump 4 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p05/tx_fields/0 | Värmepumpskretsens pumpnivå | Läsa konfigurationen för värmepumpskretsens pumpnivå. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p07/tx_fields/0 | Värmepumpskretsens pumpnivå | Läsa konfigurationen för värmepumpskretsens pumpnivå. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p08/tx_fields/0 | Analogstyrningens prioritet | Läsa konfigurationen för analogstyrningens prioritet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p10/tx_fields/0 | Analogstyrningens prioritet | Läsa konfigurationen för analogstyrningens prioritet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p11/tx_fields/0 | Värmepumpens minflöde | Läsa konfigurationen för värmepumpens minflöde. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p13/tx_fields/0 | Värmepumpens minflöde | Läsa konfigurationen för värmepumpens minflöde. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.135.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.136.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.136.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.136.p02/tx_fields/0 | Värmepumpens maxflöde | Läsa konfigurationen för värmepumpens maxflöde. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.136.p04/tx_fields/0 | Värmepumpens maxflöde | Läsa konfigurationen för värmepumpens maxflöde. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.136.p05/tx_fields/0 | Hybridens temperaturhysteres | Läsa konfigurationen för hybridens temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.136.p07/tx_fields/0 | Hybridens temperaturhysteres | Läsa konfigurationen för hybridens temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.136.p08/tx_fields/0 | Buffertgivarens kalibrering | Läsa konfigurationen för buffertgivarens kalibrering. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.136.p10/tx_fields/0 | Buffertgivarens kalibrering | Läsa konfigurationen för buffertgivarens kalibrering. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.136.p11/tx_fields/0 | Smart-grid-reglering för värme | Läsa konfigurationen för smart-grid-reglering för värme. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.136.p13/tx_fields/0 | Smart-grid-reglering för värme | Läsa konfigurationen för smart-grid-reglering för värme. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.136.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.137.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.137.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.137.p02/tx_fields/0 | Värmemål vid rekommenderad smart-grid-drift | Läsa konfigurationen för värmemål vid rekommenderad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.137.p04/tx_fields/0 | Värmemål vid rekommenderad smart-grid-drift | Läsa konfigurationen för värmemål vid rekommenderad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.137.p05/tx_fields/0 | Värmemål vid tvingad smart-grid-drift | Läsa konfigurationen för värmemål vid tvingad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.137.p07/tx_fields/0 | Värmemål vid tvingad smart-grid-drift | Läsa konfigurationen för värmemål vid tvingad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.137.p08/tx_fields/0 | Kylmål vid rekommenderad smart-grid-drift | Läsa konfigurationen för kylmål vid rekommenderad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.137.p10/tx_fields/0 | Kylmål vid rekommenderad smart-grid-drift | Läsa konfigurationen för kylmål vid rekommenderad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.137.p11/tx_fields/0 | Kylmål vid tvingad smart-grid-drift | Läsa konfigurationen för kylmål vid tvingad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.137.p13/tx_fields/0 | Kylmål vid tvingad smart-grid-drift | Läsa konfigurationen för kylmål vid tvingad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.137.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.138.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.138.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.138.p02/tx_fields/0 | Periodisk pumpdrift under värme | Läsa konfigurationen för periodisk pumpdrift under värme. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.138.p04/tx_fields/0 | Periodisk pumpdrift under värme | Läsa konfigurationen för periodisk pumpdrift under värme. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.138.p05/tx_fields/0 | Periodisk pumpdrift under kyla | Läsa konfigurationen för periodisk pumpdrift under kyla. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.138.p07/tx_fields/0 | Periodisk pumpdrift under kyla | Läsa konfigurationen för periodisk pumpdrift under kyla. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.138.p08/tx_fields/0 | Pumpcykelns intervall | Läsa konfigurationen för pumpcykelns intervall. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.138.p10/tx_fields/0 | Pumpcykelns intervall | Läsa konfigurationen för pumpcykelns intervall. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.138.p11/tx_fields/0 | Smart-grid-reglering för kyla | Läsa konfigurationen för smart-grid-reglering för kyla. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.138.p13/tx_fields/0 | Smart-grid-reglering för kyla | Läsa konfigurationen för smart-grid-reglering för kyla. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.138.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.139.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.139.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.139.p02/tx_fields/0 | Begränsning av eltillskottets kapacitet | Läsa konfigurationen för begränsning av eltillskottets kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p04/tx_fields/0 | Begränsning av eltillskottets kapacitet | Läsa konfigurationen för begränsning av eltillskottets kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p05/tx_fields/0 | Sommarläge tillåtet | Läsa konfigurationen för sommarläge tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p07/tx_fields/0 | Sommarläge tillåtet | Läsa konfigurationen för sommarläge tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p08/tx_fields/0 | Sommarlägets temperaturgränser | Läsa konfigurationen för sommarlägets temperaturgränser. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p09/tx_fields/0 | Sommarlägets temperaturgränser | Läsa konfigurationen för sommarlägets temperaturgränser. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p10/tx_fields/0 | Sommarlägets temperaturgränser | Läsa konfigurationen för sommarlägets temperaturgränser. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p11/tx_fields/0 | Sommarlägets tidsgränser | Läsa konfigurationen för sommarlägets tidsgränser. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p12/tx_fields/0 | Sommarlägets tidsgränser | Läsa konfigurationen för sommarlägets tidsgränser. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p13/tx_fields/0 | Sommarlägets tidsgränser | Läsa konfigurationen för sommarlägets tidsgränser. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.139.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.140.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.140.p01/tx_fields/0 | Inställningssessionens status | Visa om inställningsblocket får lämnas ut; CFB18. | protokollroll belagd |
| uart2.tx.140.p02/tx_fields/0 | Sommarlägets tvångsstarttemperatur | Läsa konfigurationen för sommarlägets tvångsstarttemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p04/tx_fields/0 | Sommarlägets tvångsstarttemperatur | Läsa konfigurationen för sommarlägets tvångsstarttemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p05/tx_fields/0 | Tyst drift tillåten | Läsa konfigurationen för tyst drift tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p07/tx_fields/0 | Tyst drift tillåten | Läsa konfigurationen för tyst drift tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p08/tx_fields/0 | Tyst drift start-/sluttid | Läsa konfigurationen för tyst drift start-/sluttid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p09/tx_fields/0 | Tyst drift start-/sluttid | Läsa konfigurationen för tyst drift start-/sluttid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p10/tx_fields/0 | Tyst drift start-/sluttid | Läsa konfigurationen för tyst drift start-/sluttid. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p11/tx_fields/0 | Tyst drift nivå | Läsa konfigurationen för tyst drift nivå. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p13/tx_fields/0 | Tyst drift nivå | Läsa konfigurationen för tyst drift nivå. Formatbyte och värde hör ihop; inte tre mätningar. | syfte med SD-korrelation |
| uart2.tx.140.p15/tx_fields/0 | Inställningskategori | Koppla blocket till rätt inställningssession; källa2357. | protokollroll belagd |
| uart2.tx.141.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.141.p01/tx_fields/0 | Energipostens datum | Koppla energier till samma period innan de jämförs. | syfte med källkorrelation |
| uart2.tx.141.p02/tx_fields/0 | Energipostens datum | Koppla energier till samma period innan de jämförs. | syfte med källkorrelation |
| uart2.tx.141.p03/tx_fields/0 | Energipostens datum | Koppla energier till samma period innan de jämförs. | syfte med källkorrelation |
| uart2.tx.141.p04/tx_fields/0 | Förbrukad energi för värme | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.141.p05/tx_fields/0 | Förbrukad energi för värme | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.141.p06/tx_fields/0 | Förbrukad energi för värme | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.141.p07/tx_fields/0 | Förbrukad energi för kyla | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.141.p08/tx_fields/0 | Förbrukad energi för kyla | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.141.p09/tx_fields/0 | Förbrukad energi för kyla | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.141.p10/tx_fields/0 | Förbrukad energi för varmvatten | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.141.p11/tx_fields/0 | Förbrukad energi för varmvatten | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.141.p12/tx_fields/0 | Förbrukad energi för varmvatten | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.142.p01/tx_fields/0 | Energipostens datum | Koppla energier till samma period innan de jämförs. | syfte med källkorrelation |
| uart2.tx.142.p02/tx_fields/0 | Energipostens datum | Koppla energier till samma period innan de jämförs. | syfte med källkorrelation |
| uart2.tx.142.p03/tx_fields/0 | Energipostens datum | Koppla energier till samma period innan de jämförs. | syfte med källkorrelation |
| uart2.tx.142.p04/tx_fields/0 | Producerad energi för värme | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p05/tx_fields/0 | Producerad energi för värme | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p06/tx_fields/0 | Producerad energi för värme | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p07/tx_fields/0 | Producerad energi för kyla | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p08/tx_fields/0 | Producerad energi för kyla | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p09/tx_fields/0 | Producerad energi för kyla | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p10/tx_fields/0 | Producerad energi för varmvatten | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p11/tx_fields/0 | Producerad energi för varmvatten | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.142.p12/tx_fields/0 | Producerad energi för varmvatten | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | syfte med källkorrelation |
| uart2.tx.143.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.143.p01/tx_fields/0 | Servicekod för svaret | Koppla svaret till beställd A3-fråga. | protokollroll belagd |
| uart2.tx.143.p02/tx_fields/0 | Servicekod för svaret | Koppla svaret till beställd A3-fråga. | protokollroll belagd |
| uart2.tx.143.p03/tx_fields/0 | Servicevärdets format/status | Avgöra hur svaret ska tolkas och om ett resultat finns. | protokollroll belagd |
| uart2.tx.143.p04/tx_fields/0 | Servicefrågans resultat | Läsa värdet enligt den specifika A3-kodens betydelse. | protokollroll belagd |
| uart2.tx.143.p05/tx_fields/0 | Servicefrågans resultat | Läsa värdet enligt den specifika A3-kodens betydelse. | protokollroll belagd |
| uart2.tx.144.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.144.p01/tx_fields/0 | Godkännande av inställningssession | Rapportera om överföringssessionen accepteras. | protokollroll belagd |
| uart2.tx.145.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.146.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.146.p01/tx_fields/0 | Svar 146 – databyte 1 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.146.p02/tx_fields/0 | Svar 146 – databyte 2 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.146.p03/tx_fields/0 | Svar 146 – databyte 3 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.146.p04/tx_fields/0 | Svar 146 – databyte 4 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.146.p05/tx_fields/0 | Svar 146 – databyte 5 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.146.p06/tx_fields/0 | FTC-generationens identifierare | Används av klienten för att välja kompatibel funktionalitet. | syfte med källkorrelation |
| uart2.tx.146.p07/tx_fields/0 | Svar 146 – databyte 7 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.146.p08/tx_fields/0 | Förbrukningsberäkning konfigurerad | Visa att förbrukningsberäkningens lägesval inte är noll; skilj från GET07:s striktare värden1/2. | syfte följt i kod |
| uart2.tx.146.p09/tx_fields/0 | Svar 146 – databyte 9 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.147.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.147.p01/tx_fields/0 | Fast FF-svar på CC-frågan | Avsluta CC-svaret; överordnad protokollavsikt är fortfarande okänd. | protokollroll belagd |
| uart2.tx.148.p00/tx_fields/0 | Svarskod | Koppla svaret till rätt fråga; ingen fysisk mätstorhet. | protokollroll belagd |
| uart2.tx.149.p00/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.149.p01/tx_fields/0 | Svar 149 – databyte 1 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.149.p02/tx_fields/0 | Svar 149 – databyte 2 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.149.p03/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.149.p04/tx_fields/0 | Svar 149 – databyte 4 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.149.p05/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.149.p06/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.149.p07/tx_fields/0 | Svar 149 – databyte 7 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.149.p08/tx_fields/0 | Svar 149 – databyte 8 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.149.p09/tx_fields/0 | Svar 149 – databyte 9 | Inte fördjupat här | tekniskt positionsnamn |
| uart2.tx.149.p10/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.149.p11/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.150.p00/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.tx.150.p01/tx_fields/0 | Konstant nollfält | Platshållare i denna firmware; betyder inte uppmätt noll. | protokollroll belagd |
| uart2.frame.5c/tx_fields/0 | CC-markör | Inte fördjupat här | befintlig fältroll |
| uart2.frame.5c/tx_fields/1 | Konstant FF-värde | Inte fördjupat här | befintlig fältroll |
