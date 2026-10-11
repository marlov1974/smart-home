# Vad den fortsatta kartläggningen faktiskt löste

Alla katalogiserade råa TX-fält har gått igenom samma klassificering: meningsfullt mät-/styrsyfte, belagd protokollroll, konfigurationskorrelation eller uttryckligen kvarstående lucka. Inventeringen är fortfarande begränsad till de kända142 CN105-vägarna och159 A3-koderna. Det är inte ett bevis på att inga fler kommandon eller bytes finns.

Av de965 råa byteförekomster som återstod efter GET17–19 har932 fått syfte eller protokollroll.33 återstår utan tillräckligt specifikt användarsyfte. Detta är förekomster, inte932 nya funktioner: kvittenser upprepas, och flera bytes hör till samma värde.334 grupper sammanför de nya fältbeskrivningarna. SD-korrelationer är särskilt märkta och räknas inte som säker native identifiering.

Se [fältkatalogen](field-purpose-audit.md), [maskinläsbara spår](field-purpose-audit.json) och [samlat namnregister](name-registry.md). Varje grupp har kommando, svarspackare, payloadpositioner, syfte och evidensgrad. Gamla atlasposter och deras underlag bevaras.

## Signaler som hjälper våra praktiska frågor

- **GET04 byte8:** bestående temperaturavvikelse medan frekvensen ligger still. Detta är en reglerresponsindikator, inte bevis på full effekt eller exakt inverterbegränsning.
- **GET05 byte5:** kodad nivå från den mest begränsande effektgränsen. Den kommer från minsta värdet av flera gränser; den är inte producerad kW.
- **GET05/06:** hybridens kostnads-/CO2-jämförelser och valt elpris. Värdena bygger på konfiguration och beräknad prestanda.
- **GET14 byte1:** extern pannutgång efter drift- och skyddsvillkor. Byte2–5 är elektriska tillskott, och byte12 är vattenflöde.
- **GET15 byte8/9:** shuntens OUT5A/OUT5B. Bitparen00 och01 betyder stopp,10 öppna och11 stäng. Detta är elektriska utgångar, inte återrapporterad mekanisk ventilposition. Kopplingen bevisas av att samma funktioner fyller bit4/5 i servicekod175, vars utgångar namnges i OCH722A.
- **GET02 byte4/6:** eltillskottets respektive pannans drift/eftergång. Tillstånden har timerlogik och ska inte reduceras till en allmän boolesk kompressorflagga.
- **GET03 byte12:** vilka källenheter som valts för drift utifrån tillgänglighet, ordningslista och antal som behövs.
- **GET1C–1F:** de skrivna datafälten anropar konstantreturenA4CD2. De representerar inga brinegivare i referensfirmwaren. Samma slutsats får inte automatiskt överföras till andra firmwareversioner.

## Pseudokod: utebliven frekvensrespons

```text
positivt_villkor = temperaturavvikelse3947 >= 200
                   AND aktuell_Hz == föregående_Hz
                   AND avfrostningstillstånd != 2
negativt_villkor = temperaturavvikelse3947 <= -100
                   AND aktuell_Hz == föregående_Hz
                   AND avfrostningstillstånd != 2

kör separata timers medan respektive villkor består
när positiv timer är klar: välj tillstånd2
när negativ timer är klar: välj tillstånd1
lämna respektive tillstånd när dess tidsvillkor inte längre är uppfyllt
nollställ vid vissa drift-/enhets-/värmekällsbyten
GET04.p8 = tillståndets sammanfattning0/1/2
```

Native kedja: descriptor819A2 → callbacktabell87298 → C8388 → C83F6/C8478 → C84FA →4925 → A3CBC/A3CF4. Timerns faktiska varaktighet har inte fastställts här.3947 har både normal reglerkedja och en mottagen/behållen kanal i profil2; se P0087 flow-target-trace. Därför går det inte att ersätta den med valfri momentan temperaturdifferens i vår regulator.

## Vad som fortfarande saknas

De33 positionerna är öppet listade sist i fältkatalogen. De hör främst till modell-/protokollinformation, några källsidestatusar, kompletterande givarvärden och särskilda styrflaggor. För dessa finns adresser och kodkedjor, men inte tillräckligt belagd fysisk eller operativ betydelse. Några kan sannolikt lösas med vidare producent-/konsumentspårning i FTC; andra kräver modellens mottagarprotokoll. De ska inte beskrivas som alla externa blockeringar.

A3/350–363 har en separat begränsning: FTC skriver och överför serviceväljare, men källsidans tillämpning finns på mottagaren. Den nya manualkopplingen för350/351 gäller SUZ, inte bevisad Geodan-funktion; se [manualuppföljningen](service-manual-followup.md).352–363 saknar fortfarande tillförlitliga fysiska namn. SET33 och de alternativa02-/CC-ramarnas överordnade avsikt är också öppna trots identifierad kvittens-/sessionsfunktion.

**Hela användarmålet är alltså inte uppnått.** Rapporten redovisar faktiska framsteg utan att göra tekniska etiketter till förstådda funktioner.

## Reproduktion

Kör `overview.py`, `field_audit.py --private ../../P0089/private`, `name_registry.py` från repot. Kör därefter testerna i `tools/ftc6/p89` med P89_PRIVATE och P89_IMAGE satta. Auditverktyget kräver rätt SHA256 på referensfirmwaren, binder grupper till skrivna payloadpositioner och sparar hash för native packare, getters och nya funktionsspår. Två stora schemapackares indirekta switchkroppar kompletteras med C-export och är uttryckligen bara strukturell korrelation.

Inga register skrevs, inga pumpar kontaktades och ingen firmware installerades. P86–88 är oförändrade.

## Kontroll mot SD-verktygets driftsymboler

SD_Pos innehåller209 namngivna loggpositioner, även för flera kvarstående kandidater (bland annat referensadress, reservdrift och min-/maxindikering per enhet). De är användbara sökledtrådar, men har inte lagts in som säkra fältnamn enbart på grund av liknande ordning. Den exporterade9DAF0-rutinen bygger en UART1-diagnosbild med ett annat fältformat än SD_Pos. Exempelvis ligger38BD vid dess relativa byte9, medan SD-verktygets position9 heterOC_RefAdd. En direkt offsetöversättning vore därför fel. Den verkliga loggserialiseraren eller en verifierad formatöversättning behöver bindas till samma datakällor först. Ope_Log_Chg och LoadFile har extraherats statiskt ur tillverkarverktyget för fortsatt jämförelse; verktyget har inte körts.
