# CN105 — vad kommandona gör

Bredd först enligt användarens prioritering. Funktionen ska få ett begripligt namn före fortsatt fält-, timing- och regulatoranalys.

Detta är en första funktionsöversikt, inte en färdig kartläggning. 141 befintliga vägar plus anslutningsramen 5A. Läsning och skrivning räknas separat; A3-underkoder räknas inte som nya ramkommandon.

**Identifierad** avser övergripande roll, inte att alla fält är förstådda. **Trolig** är en arbetshypotes från externa referenser eller en kombination av native dataflöde, standardvärden och manual. **Namngiven del** betyder ett blandat paket där bara vissa funktioner har namn. **Familj känd** betyder att inställningsöverföringen är känd men innehållet saknar funktionsnamn. **Platshållare** gäller bara referensfirmwarens skrivna datafält.

Räkning: identifierad: 44; namngiven del: 36; platshållare: 10; trolig: 52.

Alla rader gäller CN105/UART2. FC41 = skrivbegäran, FC42 = läsbegäran. Exempelvis FC42/5A och ramtyp FC5A är olika saker. Inga fysiska tester har gjorts i denna genomgång.

| Kod/väg | Namn | Beskrivning | Bedömning |
|---|---|---|---|
| 41.32 | Ställ driftläge och temperaturmål | Begär driftläge och temperaturbörvärden, inklusive fast framledning. | identifierad |
| 41.33 | Kvittera SET33 | Generisk SET-kvittens för 33; tillämpning ej identifierad. Protokollrollen är namngiven. Vilken eventuell inställning anroparen avser och om en indirekt tillämpning finns är fortfarande okänt. | namngiven del |
| 41.34 | Ställ driftspärrar och extern styrning | Begär boost, semester, driftspärrar och extern styrning; innehåller även begränsningssignal. | identifierad |
| 41.35 | Ställ zonernas temperaturmål | Begär zonernas separata temperaturmål för värme/kyla; inte samma väg som fast framledning. | identifierad |
| 41.50 | Varmvattenmål, temperaturfall och maximal körtid | Tar emot varmvattenmål, temperaturfall och maximal körtid. Temperaturfall är kopplat till samma källa som GET09; körtidsnamnet stöds av minutomvandling och manualen. Övriga fält återstår. | namngiven del |
| 41.51 | Varmvattenläge, återhämtningspaus och legionellamål | Tar emot varmvattenläge, återhämtningspaus och legionellamål. Läge är direkt identifierat. Paus och legionellamål är funktionshypoteser från import, standardvärden och manual; inte full konsumentkedja. | trolig |
| 41.52 | Legionellacykelns tidsinställningar | Tar emot legionellacykelns tidsinställningar. Tidsenheterna och standardvärdena passar maximal cykeltid och temperaturhålltid. Alla fält är inte namngivna. | trolig |
| 41.53 | Zonernas värme-/kylreglerläge | Tar emot zonernas värme-/kylreglerläge. Inställningssessionens väg; skilj begärt läge från valt läge. | identifierad |
| 41.54 | Zonernas temperaturbörvärden | Tar emot zonernas temperaturbörvärden. Blocket omfattar flera temperaturmål per zon, inte ett enda framledningsmål. | identifierad |
| 41.55 | Värmekurvans punkter per zon | Tar emot värmekurvans punkter per zon. Zonval och punktstruktur stöder namnet. Exakt kurvtolkning är en hypotes och inte härledd enbart från ordningsföljden. | trolig |
| 41.56 | Veckoprogram för värme/kyla och varmvatten | Tar emot veckoprogram för värme/kyla och varmvatten. Sjudagarsindex och schemabanker stöder familjen. Exakt betydelse av samtliga programväljare är ännu inte fastställd. | trolig |
| 41.57 | Årsperiod för veckoprogram 2 | Tar emot årsperiod för veckoprogram 2. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.58 | Reserverad inställningsplats 58 | Tar emot reserverad inställningsplats 58. Läsaren lämnar inget inställningsinnehåll och skrivgrenen går direkt till gemensamt slut i denna image. | platshållare |
| 41.59 | Semesterläge: aktivering samt start- och slutdatum | Tar emot semesterläge: aktivering samt start- och slutdatum. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.5a | Semesterlägets temperaturmål | Tar emot semesterlägets temperaturmål. Flera mål och zonval; inte själva semesteraktiveringen. | identifierad |
| 41.5b | Reserverad inställningsplats 5B | Tar emot reserverad inställningsplats 5B. Läsaren lämnar inget inställningsinnehåll och skrivgrenen går direkt till gemensamt slut i denna image. | platshållare |
| 41.5c | Displayens språk, temperaturenhet och temperaturvisning | Tar emot displayens språk, temperaturenhet och temperaturvisning. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.5d | Kontakttelefon som visas på manöverpanelen | Tar emot kontakttelefon som visas på manöverpanelen. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.5e | Tidsformat, fjärrkontrollernas zontilldelning och rumsgivarval | Tar emot tidsformat, fjärrkontrollernas zontilldelning och rumsgivarval. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.5f | Tidsschema för val av rumsgivare per zon | Tar emot tidsschema för val av rumsgivare per zon. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.60 | Kalibrering av temperaturgivare, grupp 1 | Tar emot kalibrering av temperaturgivare, grupp 1. Framledning och retur är belagda. Alla givarnamn i gruppen återstår. | identifierad |
| 41.61 | Kalibrering av temperaturgivare, grupp 2 | Tar emot kalibrering av temperaturgivare, grupp 2. Kalibreringsfamilj identifierad; tilldelning till varje fysisk givare återstår. | identifierad |
| 41.62 | Kalibrering av temperaturgivare, grupp 3 | Tar emot kalibrering av temperaturgivare, grupp 3. Två ytterligare kalibreringsvärden; fysisk givartilldelning inte fullständigt belagd. | identifierad |
| 41.63 | Cirkulationspumpens ekonomi- och temperaturvillkor | Tar emot cirkulationspumpens ekonomi- och temperaturvillkor. Pumpvillkor och fördröjning har native konsumenter. Gruppens fullständiga fältnamn återstår. | trolig |
| 41.64 | Eltillskottets tillåtelse och fördröjningar | Tar emot eltillskottets tillåtelse och fördröjningar. Standardvärden och tillståndsvillkor stöder namnet; inte ett bevis för varje tillskottssteg. | trolig |
| 41.65 | Shuntventilens gångtid/intervall och varmvattenpumpens nivå | Tar emot shuntventilens gångtid/intervall och varmvattenpumpens nivå. Rättar tidigare alltför snävt namn DHW settings. Shuntnamnet är korrelerat via tider, utgångar och manual; pumpnivån är tidigare belagd. | namngiven del |
| 41.66 | Val av värmekälla och samtidig värme/varmvatten | Tar emot val av värmekälla och samtidig värme/varmvatten. BF750 kombinerar utetemperaturvillkor med zonspärrar. Namnet är en arbetshypotes för blandat block. | trolig |
| 41.67 | Värmeregleringens temperaturgränser och tidsintervall | Tar emot värmeregleringens temperaturgränser och tidsintervall. Framledningens min/max har läskoppling. Övriga villkor och intervall ska inte likställas med dessa gränser. | namngiven del |
| 41.68 | Värmepumpens temperaturhysteres | Tar emot värmepumpens temperaturhysteres. Standardvärden +5/-5 och användning i regleringen stöder familjen; aktiveringens fulla semantik återstår. | trolig |
| 41.69 | Värmekällornas kapaciteter för hybridberäkning | Tar emot värmekällornas kapaciteter för hybridberäkning. Matchar värmepumpskapacitet och två tillskott. Sista fältet är inte slutligt namngivet. | trolig |
| 41.6a | Hybridens utetemperaturgräns, pannverkningsgrad, bränslepris och elens CO2-faktor | Tar emot hybridens utetemperaturgräns, pannverkningsgrad, bränslepris och elens CO2-faktor. Faktornamnen stöds av kategorikvalificerad SD-import. Skala och fysisk tillämpning är separata frågor. | namngiven del |
| 41.6b | Pannbränslets CO2-faktor för hybridval | Tar emot pannbränslets CO2-faktor för hybridval. Konfigurerad jämförelsefaktor, inte uppmätt utsläpp eller effekt. | namngiven del |
| 41.6c | Konfigurerad COP-tabell, punkter 1–6 | Tar emot konfigurerad COP-tabell, punkter 1–6. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. Detta är INTE live-COP. | namngiven del |
| 41.6d | Konfigurerad COP-tabell, punkter 7–12 | Tar emot konfigurerad COP-tabell, punkter 7–12. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. Detta är INTE live-COP. | namngiven del |
| 41.6e | Säsongsperioder för elprisschemat | Tar emot säsongsperioder för elprisschemat. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.6f | Elpriser 1–6 för hybridens kostnadsjämförelse | Tar emot elpriser 1–6 för hybridens kostnadsjämförelse. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | namngiven del |
| 41.70 | Elpriser 7–10 för hybridens kostnadsjämförelse | Tar emot elpriser 7–10 för hybridens kostnadsjämförelse. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | namngiven del |
| 41.71 | Energiberäkning: tillskott och primärpump | Tar emot energiberäkning: tillskott och primärpump. Blocket innehåller energiberäkningens konfiguration; varje kapacitetsfält är inte slutligt namngivet. | namngiven del |
| 41.72 | Energiberäkning: extra pumpar och energikorrigering | Tar emot energiberäkning: extra pumpar och energikorrigering. Pump2/3 och korrigeringen tidigare belagda; återstående byte öppet. | namngiven del |
| 41.73 | Flödessensorns maxvärde, varmvatten-tillskott och Normal/Fast-rumsreglering | Tar emot flödessensorns maxvärde, varmvatten-tillskott och Normal/Fast-rumsreglering. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 41.74 | Veckoschema för elpris i tre säsonger | Tar emot veckoschema för elpris i tre säsonger. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. Tre säsonger × sju dagar stöds av ReadSER2:s prisparser; tidigare kandidat tyst drift var fel. | trolig |
| 41.75 | Golvtorkning: start-/sluttemperatur, maxtemperatur, hålltid och uppsteg | Tar emot golvtorkning: start-/sluttemperatur, maxtemperatur, hålltid och uppsteg. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.76 | Golvtorkningens stegintervall/nedsteg och externa ingångar IN4/IN5 | Tar emot golvtorkningens stegintervall/nedsteg och externa ingångar IN4/IN5. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | namngiven del |
| 41.77 | Smart-grid-temperaturbidrag, termo-ON-utgång och varmvattenåterladdning | Tar emot smart-grid-temperaturbidrag, termo-ON-utgång och varmvattenåterladdning. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. Ersätter det tidigare alltför breda och missvisande namnet rumsgivarval. | identifierad |
| 41.78 | Variabelt vattenflöde och analogutgångens styrning, intervall och effekt | Tar emot variabelt vattenflöde och analogutgångens styrning, intervall och effekt. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 41.79 | Pump 4:s energibidrag, värmepumpens pumpnivå, analogprioritet och minflöde | Tar emot pump 4:s energibidrag, värmepumpens pumpnivå, analogprioritet och minflöde. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 41.7a | Maxflöde, hybridhysteres, buffertgivarkorrigering och smart-grid-värmeval | Tar emot maxflöde, hybridhysteres, buffertgivarkorrigering och smart-grid-värmeval. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 41.7b | Smart-grid-börvärden för rekommenderad/tvingad värme och kyla | Tar emot smart-grid-börvärden för rekommenderad/tvingad värme och kyla. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 41.7c | Periodisk cirkulation för värme/kyla, intervall och smart-grid-kylval | Tar emot periodisk cirkulation för värme/kyla, intervall och smart-grid-kylval. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 41.7d | Begränsning av eltillskott och sommarlägets temperatur-/tidsgränser | Tar emot begränsning av eltillskott och sommarlägets temperatur-/tidsgränser. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | namngiven del |
| 41.7e | Sommarlägets tvångsstarttemperatur och schema/nivå för tyst drift | Tar emot sommarlägets tvångsstarttemperatur och schema/nivå för tyst drift. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 41.c8 | Styr inställningsöverföring | Styr en kategoribaserad session för överföring och tillämpning av inställningar. | identifierad |
| 42.01 | Läs styrenhetens tid | Läser styrenhetens tid. | trolig |
| 42.02 | Läs avfrostnings- och termostatstatus | Rapporterar avfrostning och termostatstatus. | trolig |
| 42.03 | Läs fel och zonstatus | Rapporterar felkoder och zonernas arbetsstatus. | trolig |
| 42.04 | Läs kompressorfrekvens och enhetsstatus | Rapporterar kompressorfrekvens och ytterligare driftstatus, inklusive flera enheter. | identifierad |
| 42.05 | Läs värmekälla och varmvattenstatus | Rapporterar värmekälla och varmvattenproduktionens status. | trolig |
| 42.06 | Hybridjämförelse: kostnad, CO2 och valt elpris | Hybridjämförelse: kostnad, CO2 och valt elpris. Beräknade jämförelsevärden baserade på pris-, verkningsgrads- och COP-konfiguration. Inte uppmätt effekt eller live-COP; absoluta skalenheter återstår. | namngiven del |
| 42.07 | Läs effekt och förbrukningsräknare | Rapporterar förbrukad/producerad effekt och en ökande förbrukningsräknare. | identifierad |
| 42.09 | Läs temperaturmål och gränser | Läser temperaturbörvärden och temperaturgränser för zoner och varmvatten. | trolig |
| 42.0b | Läs rumstemperaturer och valda givare | Rapporterar rumstemperaturer och andra valda temperaturkällor. | identifierad |
| 42.0c | Läs primärkretsens och varmvattnets temperaturer | Rapporterar primär framledning, retur och varmvatten samt ytterligare temperaturfält. | identifierad |
| 42.0d | Läs zonernas framledning och retur | Läser framledning och retur separat för zon 1 och zon 2. | trolig |
| 42.0e | Läs pannans framledning och retur | Läser extern pannas framledning och retur. | trolig |
| 42.0f | Läs extra temperaturgivare | Läser ytterligare temperaturgivare; givarnas identitet är modellberoende. | trolig |
| 42.10 | Läs termostater, flödesvakter och externa ingångar | Termostatingångar, flödesvakter och externa styringångar. Visar sju separata ingångar. Tidigare samlingsnamn termostaternas värmebehov var för snävt; externa ingångarnas funktion beror på konfiguration. | identifierad |
| 42.11 | Läs DIP-konfiguration | Rapporterar DIP-konfiguration och därmed möjliga systemegenskaper. | trolig |
| 42.13 | Läs kompressordrift och drifttid | Rapporterar kompressordrift och drifttid. | trolig |
| 42.14 | Läs ingångar, tillskott och vattenflöde | Rapporterar ingångs-/tillskottsstatus och primärt vattenflöde. | identifierad |
| 42.15 | Läs pump- och ventilstatus | Rapporterar pumpar, ventiler och andra aktuatorers driftstatus. | identifierad |
| 42.16 | Läs extra pumpars status | Rapporterar ytterligare vattenpumpars status. | trolig |
| 42.17 | Läs givarfel, övertemperatur och frysrisk | Givarfel, övertemperatur och frysrisk. Visar om temperaturvärden och temperaturgränser är användbara för säker drift. Alla11 skrivna statusfält har nu följts. Tids-/aktiveringsvillkor gäller; statuskod0 betyder inte generellt frisk givare. | namngiven del |
| 42.18 | Läs temperaturrespons och cirkulationsfel | Temperaturrespons, cirkulation och givarfel. Upptäcker utebliven uppvärmning, omvänd temperaturskillnad i zonerna, flödesvaktsfel och flera givarfel. Alla12 skrivna statusfält har nu följts; dessa signaler bevisar inte en viss fysisk felorsak. | namngiven del |
| 42.19 | Driftskydd, värmekällekonfiguration och flödesgivarfel | Driftskydd, värmekällekonfiguration och flödesgivarfel. Skiljer bland annat låg temperatur, oförenlig systemkonfiguration och fel på flödesgivaren. Alla åtta fält har syftesbeskrivning, inklusive kommunikation med rumsgivarmottagaren och spärrar per rumskanal. Exakt radioorsak bakom spärrar återstår. | namngiven del |
| 42.1a | Rapporterade tillståndskoder från sex anslutna enheter | Rapporterade tillståndskoder från sex anslutna enheter. En kod per enhet. Kodernas fulla betydelse och fysisk tilldelning är inte slutligt fastställda. | namngiven del |
| 42.1b | Status för övervakning av värmepumpens tillåtna vattenflöde | Status för övervakning av värmepumpens tillåtna vattenflöde. Rapporterar övervakning av min-/maxflöde, inte flödet i l/min. Indirekt producent bevisar varför direktreferenssökningen inte räckte. | identifierad |
| 42.1c | Läs nollfyllt svar 1C | Packar uttryckliga nollvärden i sina datafält i referensfirmwaren; ingen användbar mätfunktion där. | platshållare |
| 42.1d | Läs nollfyllt svar 1D | Packar uttryckliga nollvärden i sina datafält i referensfirmwaren; ingen användbar mätfunktion där. | platshållare |
| 42.1e | Läs nollfyllt svar 1E | Packar uttryckliga nollvärden i sina datafält i referensfirmwaren; ingen användbar mätfunktion där. | platshållare |
| 42.1f | Läs nollfyllt svar 1F | Packar uttryckliga nollvärden i sina datafält i referensfirmwaren; ingen användbar mätfunktion där. | platshållare |
| 42.20 | Tom reserverad datasvarsplats 20 | Tom reserverad datasvarsplats 20. Datafältet lämnas tomt i denna referensfirmware. Avsedd funktion i andra versioner är okänd. | platshållare |
| 42.26 | Läs driftlägen och temperaturmål | Rapporterar valda driftlägen och temperaturmål. | identifierad |
| 42.27 | Läs nollfyllt svar 27 | Packar uttryckliga nollvärden i sina datafält i referensfirmwaren; ingen användbar mätfunktion där. | platshållare |
| 42.28 | Läs driftspärrar och extern styrstatus | Rapporterar boost, semester, driftspärrar och extern styrstatus. | identifierad |
| 42.29 | Läs värme-/kylläge och zonmål | Rapporterar värme/kyla och zonernas temperaturbörvärden. | trolig |
| 42.50 | Varmvattenmål, temperaturfall och maximal körtid | Lämnar ut varmvattenmål, temperaturfall och maximal körtid. Temperaturfall är kopplat till samma källa som GET09; körtidsnamnet stöds av minutomvandling och manualen. Övriga fält återstår. | namngiven del |
| 42.51 | Varmvattenläge, återhämtningspaus och legionellamål | Lämnar ut varmvattenläge, återhämtningspaus och legionellamål. Läge är direkt identifierat. Paus och legionellamål är funktionshypoteser från import, standardvärden och manual; inte full konsumentkedja. | trolig |
| 42.52 | Legionellacykelns tidsinställningar | Lämnar ut legionellacykelns tidsinställningar. Tidsenheterna och standardvärdena passar maximal cykeltid och temperaturhålltid. Alla fält är inte namngivna. | trolig |
| 42.53 | Zonernas värme-/kylreglerläge | Lämnar ut zonernas värme-/kylreglerläge. Inställningssessionens väg; skilj begärt läge från valt läge. | identifierad |
| 42.54 | Zonernas temperaturbörvärden | Lämnar ut zonernas temperaturbörvärden. Blocket omfattar flera temperaturmål per zon, inte ett enda framledningsmål. | identifierad |
| 42.55 | Värmekurvans punkter per zon | Lämnar ut värmekurvans punkter per zon. Zonval och punktstruktur stöder namnet. Exakt kurvtolkning är en hypotes och inte härledd enbart från ordningsföljden. | trolig |
| 42.56 | Veckoprogram för värme/kyla och varmvatten | Lämnar ut veckoprogram för värme/kyla och varmvatten. Sjudagarsindex och schemabanker stöder familjen. Exakt betydelse av samtliga programväljare är ännu inte fastställd. | trolig |
| 42.57 | Årsperiod för veckoprogram 2 | Lämnar ut årsperiod för veckoprogram 2. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.58 | Reserverad inställningsplats 58 | Lämnar ut reserverad inställningsplats 58. Läsaren lämnar inget inställningsinnehåll och skrivgrenen går direkt till gemensamt slut i denna image. | platshållare |
| 42.59 | Semesterläge: aktivering samt start- och slutdatum | Lämnar ut semesterläge: aktivering samt start- och slutdatum. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.5a | Semesterlägets temperaturmål | Lämnar ut semesterlägets temperaturmål. Flera mål och zonval; inte själva semesteraktiveringen. | identifierad |
| 42.5b | Reserverad inställningsplats 5B | Lämnar ut reserverad inställningsplats 5B. Läsaren lämnar inget inställningsinnehåll och skrivgrenen går direkt till gemensamt slut i denna image. | platshållare |
| 42.5c | Displayens språk, temperaturenhet och temperaturvisning | Lämnar ut displayens språk, temperaturenhet och temperaturvisning. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.5d | Kontakttelefon som visas på manöverpanelen | Lämnar ut kontakttelefon som visas på manöverpanelen. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.5e | Tidsformat, fjärrkontrollernas zontilldelning och rumsgivarval | Lämnar ut tidsformat, fjärrkontrollernas zontilldelning och rumsgivarval. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.5f | Tidsschema för val av rumsgivare per zon | Lämnar ut tidsschema för val av rumsgivare per zon. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.60 | Kalibrering av temperaturgivare, grupp 1 | Lämnar ut kalibrering av temperaturgivare, grupp 1. Framledning och retur är belagda. Alla givarnamn i gruppen återstår. | identifierad |
| 42.61 | Kalibrering av temperaturgivare, grupp 2 | Lämnar ut kalibrering av temperaturgivare, grupp 2. Kalibreringsfamilj identifierad; tilldelning till varje fysisk givare återstår. | identifierad |
| 42.62 | Kalibrering av temperaturgivare, grupp 3 | Lämnar ut kalibrering av temperaturgivare, grupp 3. Två ytterligare kalibreringsvärden; fysisk givartilldelning inte fullständigt belagd. | identifierad |
| 42.63 | Cirkulationspumpens ekonomi- och temperaturvillkor | Lämnar ut cirkulationspumpens ekonomi- och temperaturvillkor. Pumpvillkor och fördröjning har native konsumenter. Gruppens fullständiga fältnamn återstår. | trolig |
| 42.64 | Eltillskottets tillåtelse och fördröjningar | Lämnar ut eltillskottets tillåtelse och fördröjningar. Standardvärden och tillståndsvillkor stöder namnet; inte ett bevis för varje tillskottssteg. | trolig |
| 42.65 | Shuntventilens gångtid/intervall och varmvattenpumpens nivå | Lämnar ut shuntventilens gångtid/intervall och varmvattenpumpens nivå. Rättar tidigare alltför snävt namn DHW settings. Shuntnamnet är korrelerat via tider, utgångar och manual; pumpnivån är tidigare belagd. | namngiven del |
| 42.66 | Val av värmekälla och samtidig värme/varmvatten | Lämnar ut val av värmekälla och samtidig värme/varmvatten. BF750 kombinerar utetemperaturvillkor med zonspärrar. Namnet är en arbetshypotes för blandat block. | trolig |
| 42.67 | Värmeregleringens temperaturgränser och tidsintervall | Lämnar ut värmeregleringens temperaturgränser och tidsintervall. Framledningens min/max har läskoppling. Övriga villkor och intervall ska inte likställas med dessa gränser. | namngiven del |
| 42.68 | Värmepumpens temperaturhysteres | Lämnar ut värmepumpens temperaturhysteres. Standardvärden +5/-5 och användning i regleringen stöder familjen; aktiveringens fulla semantik återstår. | trolig |
| 42.69 | Värmekällornas kapaciteter för hybridberäkning | Lämnar ut värmekällornas kapaciteter för hybridberäkning. Matchar värmepumpskapacitet och två tillskott. Sista fältet är inte slutligt namngivet. | trolig |
| 42.6a | Hybridens utetemperaturgräns, pannverkningsgrad, bränslepris och elens CO2-faktor | Lämnar ut hybridens utetemperaturgräns, pannverkningsgrad, bränslepris och elens CO2-faktor. Faktornamnen stöds av kategorikvalificerad SD-import. Skala och fysisk tillämpning är separata frågor. | namngiven del |
| 42.6b | Pannbränslets CO2-faktor för hybridval | Lämnar ut pannbränslets CO2-faktor för hybridval. Konfigurerad jämförelsefaktor, inte uppmätt utsläpp eller effekt. | namngiven del |
| 42.6c | Konfigurerad COP-tabell, punkter 1–6 | Lämnar ut konfigurerad COP-tabell, punkter 1–6. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. Detta är INTE live-COP. | namngiven del |
| 42.6d | Konfigurerad COP-tabell, punkter 7–12 | Lämnar ut konfigurerad COP-tabell, punkter 7–12. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. Detta är INTE live-COP. | namngiven del |
| 42.6e | Säsongsperioder för elprisschemat | Lämnar ut säsongsperioder för elprisschemat. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.6f | Elpriser 1–6 för hybridens kostnadsjämförelse | Lämnar ut elpriser 1–6 för hybridens kostnadsjämförelse. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | namngiven del |
| 42.70 | Elpriser 7–10 för hybridens kostnadsjämförelse | Lämnar ut elpriser 7–10 för hybridens kostnadsjämförelse. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | namngiven del |
| 42.71 | Energiberäkning: tillskott och primärpump | Lämnar ut energiberäkning: tillskott och primärpump. Blocket innehåller energiberäkningens konfiguration; varje kapacitetsfält är inte slutligt namngivet. | namngiven del |
| 42.72 | Energiberäkning: extra pumpar och energikorrigering | Lämnar ut energiberäkning: extra pumpar och energikorrigering. Pump2/3 och korrigeringen tidigare belagda; återstående byte öppet. | namngiven del |
| 42.73 | Flödessensorns maxvärde, varmvatten-tillskott och Normal/Fast-rumsreglering | Lämnar ut flödessensorns maxvärde, varmvatten-tillskott och Normal/Fast-rumsreglering. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 42.74 | Veckoschema för elpris i tre säsonger | Lämnar ut veckoschema för elpris i tre säsonger. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. Tre säsonger × sju dagar stöds av ReadSER2:s prisparser; tidigare kandidat tyst drift var fel. | trolig |
| 42.75 | Golvtorkning: start-/sluttemperatur, maxtemperatur, hålltid och uppsteg | Lämnar ut golvtorkning: start-/sluttemperatur, maxtemperatur, hålltid och uppsteg. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.76 | Golvtorkningens stegintervall/nedsteg och externa ingångar IN4/IN5 | Lämnar ut golvtorkningens stegintervall/nedsteg och externa ingångar IN4/IN5. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | namngiven del |
| 42.77 | Smart-grid-temperaturbidrag, termo-ON-utgång och varmvattenåterladdning | Lämnar ut smart-grid-temperaturbidrag, termo-ON-utgång och varmvattenåterladdning. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. Ersätter det tidigare alltför breda och missvisande namnet rumsgivarval. | identifierad |
| 42.78 | Variabelt vattenflöde och analogutgångens styrning, intervall och effekt | Lämnar ut variabelt vattenflöde och analogutgångens styrning, intervall och effekt. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 42.79 | Pump 4:s energibidrag, värmepumpens pumpnivå, analogprioritet och minflöde | Lämnar ut pump 4:s energibidrag, värmepumpens pumpnivå, analogprioritet och minflöde. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 42.7a | Maxflöde, hybridhysteres, buffertgivarkorrigering och smart-grid-värmeval | Lämnar ut maxflöde, hybridhysteres, buffertgivarkorrigering och smart-grid-värmeval. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 42.7b | Smart-grid-börvärden för rekommenderad/tvingad värme och kyla | Lämnar ut smart-grid-börvärden för rekommenderad/tvingad värme och kyla. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 42.7c | Periodisk cirkulation för värme/kyla, intervall och smart-grid-kylval | Lämnar ut periodisk cirkulation för värme/kyla, intervall och smart-grid-kylval. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | identifierad |
| 42.7d | Begränsning av eltillskott och sommarlägets temperatur-/tidsgränser | Lämnar ut begränsning av eltillskott och sommarlägets temperatur-/tidsgränser. Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad. | namngiven del |
| 42.7e | Sommarlägets tvångsstarttemperatur och schema/nivå för tyst drift | Lämnar ut sommarlägets tvångsstarttemperatur och schema/nivå för tyst drift. Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade. | trolig |
| 42.a1 | Läs förbrukad energi | Läser förbrukad energi uppdelad på värme, kyla och varmvatten. | trolig |
| 42.a2 | Läs producerad energi | Läser producerad energi uppdelad på värme, kyla och varmvatten. | trolig |
| 42.a3 | Beställ och läs serviceresultat | Förmedlar servicefrågor och deras typade resultat; en gateway med många underkoder. | identifierad |
| 42.c8 | Läs inställningssessionens status | Rapporterar inställningssessionens acceptans, upptagenstatus eller avvisning; inget tillämpningskvitto. | identifierad |
| frame.02.00 | Avsluta session och svara med information | Avsluta inställningssession och lämna alternativt informationssvar. Detta beskriver belagd funktion i FTC. Syftet med de konstanta informationsbytena är ännu inte namngivet; kommandot är inte effektfri läsning. | namngiven del |
| frame.02.01 | Kvittera alternativ ram 02 | Nollkvittens i det alternativa 02-protokollet. Belagd transportfunktion. Överordnad avsikt och eventuell indirekt sidoeffekt är inte identifierade. | namngiven del |
| frame.5a | Anslutning till CN105 | Etablerar protokollanslutning; separat ramtyp, inte GET/SET-underkommando 5A. | identifierad |
| frame.5b | Läs styrenhetsinformation | Läser information om styrenhet/konfiguration genom C9 i ramtyp 5B. | identifierad |
| frame.5c | Besvara ansluten CC-fråga | Anslutningsbunden CC-fråga med CC/FF-svar. Funktionsnamnet beskriver observerbar protokollfunktion. Det är inte belägg för en fysisk styrfunktion eller fullständig effektfrihet. | namngiven del |
| frame.5d | Kvittera ansluten CC-ram | Anslutningsbunden CC-kvittens. Funktionsnamnet beskriver observerbar protokollfunktion. Överordnad avsikt och indirekta sidoeffekter är fortfarande öppna. | namngiven del |

## Nästa varv — fortfarande bredd

1. Bekräfta preliminära SD-formatkopplingar och namnge återstående delar i blandade block. Behandla läs- och skrivparet tillsammans; börja inte kvalificera varje byte.
2. Precisera överordnad avsikt för SET33 och ramfamiljerna 5C/5D/02; GET1B är nu flödesövervakning.
3. Bekräfta de externa funktionsnamnen mot rätt firmware/modell. Särskilt 0F får inte likställas med Geodans brinegivare utan belägg.
4. Ge A3-underkoderna en separat funktionslista med status per kod, utan att åter blanda ihop kodantal och antal ramkommandon.
5. Först därefter fördjupa de funktioner som behövs för effektstyrning.

Maskinläsbara källhänvisningar och packaradresser finns i cn105-function-overview.json. Tidigare djupanalys är bevarad men styr inte längre arbetsordningen.

## A3-underkoder — vad funktionen heter

Koderna nedan är decimala. Manualnamn betyder dokumenterad funktion i Geodan-manualen, inte verifierat svar över vår CN105-väg. Underkort och FTC skiljs i beskrivningen. Kod200 avvisas av CN105; interna klasser och intervall räknas inte som funktioner.

| Kod | Funktionsnamn | Grund |
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

A3-namn och fysiskt tillgängliga värden är separata saker. Ruttvillkor och kända sidoeffekter finns i JSON-listan. Manualens fläktnamn53/122 är bevarade uttryckligen och har inte gissats om till brinefunktioner.
