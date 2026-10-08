# P0078 — Geodan FTC systemidentifikation före EFFECT-reglering

## Status och paketordning
Beställt paket. Codex får genomföra dokumentanalys, offlineimplementation, simulering och tester. **Inga fysiska börvärdesändringar eller kompressorstarter auktoriseras av paketets skapande.** P0078 är en blockerande identifieringsgrind före slutlig aggressiv tuning av EFFECT i P0076; P0077:s långtidstest kräver sedan godkända säkerhetsgrindar.

## Syfte
Identifiera hur Mitsubishi Electric Geodan/FTC omsätter ändringar av fast framledningsbörvärde till kompressorfrekvens och värmeeffekt. Särskilj direkt temperaturfelsstyrning, intern integration/ackumulerat behov (gradminutsliknande), frekvensramp eller filter samt hybrid med separata start-/stopphystereser. Särskild fokus: bibehåll kompressordrift kring 6 kW utan att för långsam höjning av framledningsbörvärdet låter faktisk framledning passera interna stoppvillkor och ger ofrivillig återstartsväntan.

Dokumenterat i FTC/Geodan-serviceunderlag: reglerlägen, fast framledning och thermo-diff-/hysteresinställningar. **En fullständig intern FTC6-frekvensalgoritm eller verifierad gradminutsintegral har inte påvisats**. MHI-dokumentation för annan produktfamilj bevisar inte Mitsubishi Electric FTC-funktion. Ingen intern kompressormodell ska fastslås före mätning.

## Beroenden och systemmodell
- P0072 r3 ger FC04 framledning, retur, framledningsbörvärde, kompressor-Hz, primärflöde, beräknade vatten-watt, drift- och inhibit-diagnostik samt A3 TH32/TH34. Läs samma fysiska samples generation/freshness; fler Modbusförfrågningar ger inte automatiskt fler nya FTC-mätningar.
- P0076 EFFECT ska använda testets resultat; ingen implementation får anta att framledningsbörvärde är en direkt gaspedal för Hz.
- En värmepump åt gången i aktiva experiment. VP1 och VP2 delar borrhål; logga den andra pumpens aktivitet och undvik okontrollerade ändringar där.
- Bekräfta FTC fast framledningsläge och dokumentera befintlig hysteres, begränsningar och ursprungliga värden. Ändra inte serviceparametrar, termostatskydd, native spärrar eller kompressorsäkerhet inom paketet.

## Instrumentering och insamling
Samla vid varje nytt faktiskt accepterat CN105-sample, med önskat pollintervall omkring 5 s där möjligt:
- monotont tidsindex + UTC, aktuellt och historiskt framledningsbörvärde, uppmätt framledning/retur, temperaturfel `eT = target_flow - actual_flow` och tidsintegral av detta **beräknad endast för analys**, inte antagen intern FTC-variabel;
- kompressor-Hz, dess derivata/ramp, kompressorns kör-/stopptillstånd, aktuellt och filtrerat levererat vattenvärme-W (MVP3), primärflöde, gångtid och tid sedan sista start/stopp;
- rå native mode, GET28-spärrar, tillgängliga kontroll-/begränsningssignaler, A3 TH32/TH34 som minutbakgrund, EVENT vid varje börvärdes-SET och verifierad readback;
- källtidsstämplar, dataålder, uppdateringsgeneration, ogiltig/missad telemetri, kommandosekvens/lease, värmepumpens andra kretsaktivitet.

Servicekod 52 (kompressorbegränsningsstatus) och andra servicekoder får bedömas som separat read-only instrumenteringsförbättring endast efter protokoll/verifiering; inga godtyckliga CN105-förfrågningar eller osäkra SET.

## Testhypoteser
H1 direkt: samma temperaturfel ger liknande Hz-reaktion efter identifierad deadtime.
H2 ackumulerande: jämförbara aktuella fel men olika tidigare felhistorik ger olika respons även efter hänsyn till frekvensramp och termiskt tillstånd.
H3 ramp/filter: långsam Hz-ändring kan förklaras utan integral.
H4 hybrid: start/stopp bestäms av hysteres/andra villkor medan aktiv Hz-reglering följer annan dynamik.
H5 tidsbegränsningar: efter stopp finns skydds-/återstartsfördröjning, ej kringgåbar.

## TC-P0078-SYSID-01 — Deltest A: aktiv kompressor, litet steg
Förbered verifierat stabil kompressordrift och minst 10 minuters passiv baslinje. Under separat operatörsgodkännande: utför ett konservativt framledningsbörvärdessteg, preliminärt +2 °C inom verifierade tillåtna gränser; håll preliminärt 15–20 minuter eller avbryt vid uppnådda säkerhetsvillkor. Återställ tidigare börvärde med normal snapshot/readback/lease och observera återgång.

Mät latens till Hz-svar, Hz/min, effektrespons, eventuella mättnader, över- och undersvängning samt om Hz fortsätter driva vid ungefär oförändrat temperaturfel. Ingen extra SET skickas om tidigare ändring saknar verifierad readback.

## Deltest B: lika temperaturfel, olika historia
Sök två naturliga eller säkert uppnådda driftpunkter med ungefär samma aktuella eT men olika tidshistorik. Jämför Hz, dHz/dt, effekt, temperatur- och flödesvillkor. En långsam frekvensramp kan efterlikna en integral — jämför med separat rampmodell. Oklara data ger `INCONCLUSIVE`, inte automatiskt `INTEGRAL_CONFIRMED`.

## Deltest C: start/stopp och återstartshysteres
Fånga i första hand naturliga start-/stoppförlopp. Dokumentera börvärde, faktisk framledning, retur, eT, Hz och driftsvillkor precis före/efter stopp/start, samt tid mellan stopp och nästa möjliga start. Separera temperaturtröskel, hysteres, frekvensbegränsning och eventuell minsta stopptid. Provocera **inte** upprepade täta starter eller kringgå kompressorskydd.

## Deltest D: undvika oönskat stopp vid 6 kW
Undersök scenariot: effektbegäran 6 kW, effekt under målet, höjning av framledningsbörvärde riskerar att vara så långsam att faktisk framledning når eller passerar interna stoppskikt. Jämför offline och därefter högst i separat begränsat övervakat test:
- A: gradvis små fasta börvärdessteg;
- B: prediktiv temperaturmarginal med gräns för maximal temperatur, tid till svar och översvängning;
- C: separat begränsad START-fas följd av CAPTURE/HOLD.

Identifiera eventuella föregångare till stopp (minskande Hz, minskande eT, ackumulerat eT, markanta fördröjningar) och uppskatta robust marginal mot stopp. Målet är **inte** att köra förbi native stopptrösklar, utan att välja stabil drift när kontinuerligt 6 kW-behov är förenligt med maskinens säkra arbetsområde. Ett stopp som orsakas av naturlig styrning eller säkerhet får inte motverkas blint genom fortsatt börvärdeshöjning.

## Modellidentifiering, testsplit och evidens
Fit och jämför åtminstone direkt fördröjd P-modell, P med Hz-ramp/filter, PI/integral med ramp och hybrid med start/stopp-hysteres. Separera kalibrerings- och valideringsförlopp. Kvantifiera Hz-residual, prediktion av responslatens/start/stopp, falska positiva stoppprediktioner och känslighet för brine, flöde, hystereshistorik. Ingen påhittad numerisk starttröskel eller 10/60-minuters spärr tillåts utan observerad eller dokumenterad evidens.

## Säkerhet och livegrind
Offline och passiv mätning först. Innan aktivt steg ska Codex dokumentera P0076 kontrollkontrakt, säkerhetsgränser, normal snapshot/återställning, leaseförnyelse, operatörens avbrottsväg, felsäker hantering av ogiltiga processvärden, parallell VP-påverkan och fortsatt nativt skydd. Nuvarande r3 lagrar lease/snapshot endast i RAM; ingen påstådd återställning vid MCU-reset eller strömavbrott. En ändrad börvärdesstyrning får inte gå obevakad eller fortsätta vid stale feedback. Operatör godkänner en konkret, tidsbegränsad testsekvens före varje fysisk provrunda.

## Acceptance
1. Reproducerbart loggformat och korrekta validitets-/generationsgränser.
2. Skillnaden mellan direkt, integrerande och rampbegränsad respons bedömd eller uttryckligen oavgjord med stödd evidens.
3. Mätbara start-/stopphystereser/tidsfördröjningar identifierade eller avgränsade med osäkerhet.
4. Förklaring av när 6 kW kontinuerligt kan upprätthållas utan oönskade stopp, samt när det är fysiskt/native-begränsat.
5. Förslag till EFFECT-styrstruktur och initiala parametrar som validerats offline mot annan data än träningsdata.
6. Verifierad återgång till ursprungliga FTC-inställningar efter aktivt prov, med redovisning av eventuella blockers.
7. Inga nya hårdvaru-SET eller serviceändringar utan separat tillstånd.

## Codex process / outputs
Normal G2 bootstrap; läs `AGENTS.md`, P0072 r3, P0076, P0077, `procon/docs/MVP_API.md`, `CONTROL_API.md` och Geodan-servicemanual. Dokumentera `requirements/package-runs/P0078/review.md`, `design.md`, `functions.md` före kod. Implementera offline test/harness och synkroniserad analysloggning; verifiera med simulerade data och tydlig provenance. Leverera rådata lokalt, sanerade tidsserier/grafer, modelljämförelse, osäkerheter, fynd samt `CHANGELOG.md`, där fysisk validering markeras separat. Vid bristande readback eller säkerhetsgrind: STOP med konkret blocker, inte gissat beteende.
