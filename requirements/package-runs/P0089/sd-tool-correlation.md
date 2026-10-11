# P0089 — funktionsnamn via FTC6 SD Tool 1.01

## Källan och avgränsningen

Mitsubishis FTC6 SD Tool 1.01 basic (2020) hämtades från [Nukumis publicerade nedladdning](https://www.nukumi.cz/podklady). Exakt URL, SHA-256 för arkiv och EXE samt hash för sex läsmetoder finns i JSON. Windowsprogrammet har inte körts. Vendorbinärer, full IL och kalkylblad hålls i privat forskningskatalog.

Den avgörande kedjan är **CN105-packare → kategoribunden staging/aktiv variabel → SD-filens offset → RCFile-läsmetod → namngiven inställning**. Detta ger ett funktionellt namn utan att varje bit eller hela regleralgoritmen behöver avkodas. Strukturell korrelation klassas fortfarande som `trolig` där FTC:s peerimplementation saknas.

## Varför offsetmatchningen går att använda

- D-överföraren8D694 använder bas1940 + bank×512 + tabelloffset och tre bytes per fält. P88 har samtliga33 selektorintervall, inklusive kategoriöverlagringarna.
- SD-exportC9732 kopierar en512-byte bank till utgående data från offset0x46. CA488 skriver en triple på motsvarande dataoffset. Därför subtraheras0x46 från native exportörens argument innan jämförelse med SD-verktygets filoffset.
- Exempel: C9958 skriver07CB vid0x145. 0x145−0x46=255; SD_SV_Pos255 heter Sv_Flow_Sensor_maximum. A8378 packar samma07CB för73. Den oberoende CE554→CE422-kedjan visar dessutom att detta skalar primärflödet322E.
- Exempel: CA1D2 skriver07D9 vid0x199. 0x199−0x46=339, Sv_SG_Ready_Hw_SetTemp. A8AFE packar07D9 för77. Detta rättar det tidigare namnet rumsgivarval.
- För stagingfält används rätt kategori: HOL, INIT, schema eller service. Adressen1940 ensam ger inget namn. INIT-parsern läser språk vid byte2, temperaturenhet vid5, temperaturvisning vid8, kontakttelefon från9, tidsformat vid23, zontilldelning vid26 och givare vid29/32. Det matchar precis5C–5F:s triplar och zonval.
- SER2-parsern läser golvtorkning från315, sommarläge från414 och tyst drift från426. Bank1-staging1C7B−1B40=315 och1CDE−1B40=414. Detta är strukturbevis; aktiv körning i vår FTC är inte verifierad för dessa peerägda fält.
- ReadSER2 börjar med tre35-posters elprisscheman och använder PriceData. Det namnger74 och rättar tidigare kandidat tyst drift. ReadSER1:s165/168 avser säsongernas månader och namnger6E.

## Namn och belägg

| Kommando (41/42-par) | Funktion | SD-fält / offset | Bedömning |
|---|---|---|---|
| 57 | Årsperiod för veckoprogram 2 | SD_Sch_Pos: 105 | trolig |
| 59 | Semesterläge: aktivering samt start- och slutdatum | SD_Hol_Pos: 0, 3, 6 | trolig |
| 5C | Displayens språk, temperaturenhet och temperaturvisning | SD_Is_Pos: 0, 3, 6 | trolig |
| 5D | Kontakttelefon som visas på manöverpanelen | SD_Is_Pos: 9, 12, 15, 18 | trolig |
| 5E | Tidsformat, fjärrkontrollernas zontilldelning och rumsgivarval | SD_Is_Pos: 21, 24, 27, 30 | trolig |
| 5F | Tidsschema för val av rumsgivare per zon | SD_Is_Pos: 33, 36, 39, 42, 45, 48, 51, 54, 57, 60 | trolig |
| 6E | Säsongsperioder för elprisschemat | SD_SV_Pos: 165, 168 | trolig |
| 74 | Veckoschema för elpris i tre säsonger | SD_SV2_Pos: tre veckobanker i ReadSER2 | trolig |
| 75 | Golvtorkning: start-/sluttemperatur, maxtemperatur, hålltid och uppsteg | SD_SV2_Pos: 315, 318, 321, 324 | trolig |
| 76 | Golvtorkningens stegintervall/nedsteg och externa ingångar IN4/IN5 | SD_SV2_Pos: 327, 330, 333, 336 | namngiven del |
| 7D | Begränsning av eltillskott och sommarlägets temperatur-/tidsgränser | SD_SV2_Pos: 411, 414, 417, 420 | namngiven del |
| 7E | Sommarlägets tvångsstarttemperatur och schema/nivå för tyst drift | SD_SV2_Pos: 423, 426, 429, 432 | trolig |
| 73 | Flödessensorns maxvärde, varmvatten-tillskott och Normal/Fast-rumsreglering | SD_SV_Pos: 255, 258, 261 | identifierad |
| 77 | Smart-grid-temperaturbidrag, termo-ON-utgång och varmvattenåterladdning | SD_SV2_Pos: 339, 342, 345, 348 | identifierad |
| 78 | Variabelt vattenflöde och analogutgångens styrning, intervall och effekt | SD_SV2_Pos: 351, 354, 357, 360 | identifierad |
| 79 | Pump 4:s energibidrag, värmepumpens pumpnivå, analogprioritet och minflöde | SD_SV2_Pos: 363, 366, 369, 372 | identifierad |
| 7A | Maxflöde, hybridhysteres, buffertgivarkorrigering och smart-grid-värmeval | SD_SV2_Pos: 375, 378, 381, 384 | identifierad |
| 7B | Smart-grid-börvärden för rekommenderad/tvingad värme och kyla | SD_SV2_Pos: 387, 390, 393, 396 | identifierad |
| 7C | Periodisk cirkulation för värme/kyla, intervall och smart-grid-kylval | SD_SV2_Pos: 399, 402, 405, 408 | identifierad |
| 6C | Konfigurerad COP-tabell, punkter 1–6 | SD_SV_Pos: 129, 132, 135, 138, 141, 144 | namngiven del |
| 6D | Konfigurerad COP-tabell, punkter 7–12 | SD_SV_Pos: 147, 150, 153, 156, 159, 162 | namngiven del |
| 6F | Elpriser 1–6 för hybridens kostnadsjämförelse | SD_SV_Pos: 171, 177, 183, 189, 195, 201 | namngiven del |
| 70 | Elpriser 7–10 för hybridens kostnadsjämförelse | SD_SV_Pos: 207, 213, 219, 225 | namngiven del |

## Viktiga rättelser och gränser

- 6C/6D är en **konfigurerad COP-tabell**, inte live-COP.
- 74 är elprisschema; tyst drift ligger i7E.
- 77 är ett blandat paket med smart-grid-bidrag, termo-ON-utgång och varmvattenåterladdning. Det gamla namnet rumsgivarval var missvisande.
- 78 har variabelt vattenflöde samt analogutgångens styrning/intervall/effekt. Analogprioritet finns i79.
- 7D blandar eltillskottsbegränsning och sommarläge. 7E blandar sommarstyrning och tyst drift.
- SD-programmets ItemCode-värden är **inte** CN105-opkoder eller A3-servicekoder. Inga korsvisa nummerlikheter används som bevis.
- Programmet är en annan versionsartefakt än ftc6.mot. Kopplingar som enbart stöds av samma filformat hålls preliminära. Inga livekommandon eller flashningar har gjorts.
