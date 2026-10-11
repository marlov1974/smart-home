# P0089 — funktionerna följda till namngiven användning

47 av47 inställningsblock har nu ett namn på funktionen, identifierade delar eller en belagd tom plats. Detta omfattar uttryckliga arbetshypoteser från SD-formatet och betyder inte47 fullt bevisade implementationer. Alla142 CN105-vägar finns kvar i översikten.

## Viktigaste nya resultat

- 57: årsperiod för veckoprogram2.
- 59: semesteraktivering och datum.
- 5C–5F: språk/temperaturvisning, kontakttelefon, tidsformat, fjärrkontrollernas zoner och rumsgivarschema.
- 6E/74: elprissäsonger och veckoschema, inte tyst drift.
- 75/76: golvtorkningens profil och externa ingångar.
- 7D/7E: eltillskottsbegränsning, sommarläge och tyst drift.
- 6C/6D: konfigurerad COP-tabell. INTE live-COP.
- GET1B: status för tillåtet vattenflöde, bevisad genom en indirekt callbacktabell och dess min-/maxflödesövervakning.
- Ram02/00 avslutar en inställningssession och lämnar ett alternativt informationssvar.
- Tidigare felaktigt breda namn på77/78/79 har rättats med SD-exportör och namngivna läsmetoder.

## Vad som fortfarande inte är löst

SET33 samt ram02/01,5C,5D har konkreta protokollnamn för vad mottagare/svar gör. **Deras överordnade avsikt är fortfarande okänd.** De är inte färdigt identifierade fysiska funktioner bara för att kvittensen kan beskrivas. Blandade paket har kvar namnlösa detaljer och SD-korrelationerna måste skiljas från native och fysisk verifiering.

A3-listan har 109 manualnamn och 50 native/korrelerade beskrivningar. Alla 17 tidigare luckor har följts vidare.160/161 har nu namn för modellprofil och DIP-vald hårdvaruvariant;536 är trolig kondenserings-/mättnadstemperatur från FTC:s givarkonvertering. För350–363 finns exakta operationer och indirekta sändningsfält, men de 14 kodernas fysiska betydelser hos mottagaren är fortfarande okända. Se a3-functions.md. Att ersätta ”okänd” med ett operationsnamn är inte ett bevisat slutnamn för en fysisk funktion.

Nollställningar341/532 och räknarpåverkande energiläsningar är markerade. Inga liveanrop eller firmwareändringar har gjorts.

## Spårbarhet

- cn105-function-overview.md/json: hela användbara listan, namn och osäkerheter per väg.
- function-traces.md/json: alla23 tidigare luckor, native kedjor och explicita stopp.
- sd-tool-correlation.md/json:23 kommandon jämförda med tillverkarens SD-verktyg, symboler/offset och källhashar.
- fault1b-trace.md/json: indirekt flödesövervakning med pseudokod och ny dekompileringsproveniens.
- service_native_names.py:50 A3-beskrivningar med respektive gren/källkedja.

30 P89-tester passerar med privata fixtures. Publikt:29 passerar,1 privat test hoppas över. Tester skyddar inventering och reproducerbarhet; de gör inte hypoteser till bevis.


## Slutlig namnpassage

Se name-registry.md/json: alla142 katalogiserade CN105-vägar och159 A3-koder har nu namn. Alla1547 fältförekomster har referensnamn.996 av dem är positionsnamn för råbytes vars fysiska betydelse fortfarande är okänd. Tidigare formuleringar om saknade namn ersätts av denna namntäckning; de semantiska luckorna ovan kvarstår.33 tester passerar med privata fixtures.


## Syftesanalys — GET17/18/19

31 tidigare tekniskt namngivna fält har nu följts via indirekta fault descriptors till villkoren som övervakas.11 fält iGET17,12 iGET18 och8 iGET19. Nya syften omfattar primär-/tankövertemperatur, frysrisk, specifika givarfel, omvänd zondifferens, för lite flöde kontra fel på flödesgivaren, oförenlig källkonfiguration samt rumsmottagarens kommunikation och spärrar. Exakt radioorsak och fulla aktiverings-/tidsvillkor kvarstår.0 betyder inte generellt frisk givare: A4410:s kondensation beror på flagga.

Detta uppfyller inte hela användarens slutmål: ytterligare fält och kommandon återstår att följa till syfte. Tekniska positionsnamn räknas inte som semantisk täckning. A3/350–363:s mottagarbetydelse och de tidigare öppna protokollintentionerna är fortfarande öppna.

Se purpose-analysis.md/json.36 tester passerar med privata fixtures; diffkontroll ren. Inga liveåtgärder eller firmwareändringar. REPOSITORY_FILES.md uppdaterad för fem nya filer. Inga P86–88-filer ändrade.


## Fortsatt fältsyfte och indirekta tillstånd

Se [field-purpose-findings.md](field-purpose-findings.md) och [field-purpose-audit.md](field-purpose-audit.md). Av965 återstående råa byteförekomster har932 fått syfte eller protokollroll;33 är fortsatt öppna.334 grupper skiljer mätning, konfiguration och protokoll. Detta är inte932 nya funktioner och inte full semantisk täckning. Nya fynd: shuntutgångarnas betydelse, temperaturavvikelse utan Hz-respons, hybridens kostnad/CO2-faktorer, eltillskott/pannans eftergång och nollreturerna iGET1C–1F.

350/351 har nu modellkvalificerad primärmanualkoppling till återställning/pump-down på SUZ; inte verifierat på Geodan. Övriga serviceval och vissa protokollintentioner är fortfarande öppna.39 tester passerar med privata fixtures. Inga liveåtgärder, inga firmwareändringar och inga ändringar iP86–88.
