# P0077 — Helgens borrhåls- och COP-test (VP1 + VP2)

## Status
Beställt separat paket. Codex får utveckla och testa mätning, analys och körplanslogik offline. Fysisk körning och fjärrstyrning kräver separat godkännande samt verifierade drift- och återställningsvillkor.

## Beroenden
P0076: unika verifierade Modbus-adresser på samma RS485-buss, självständig telemetri och säker EFFECT-styrning per värmepump. Båda delar samma borrhål/brinekälla. En enda RS485-master; ingen broadcast-styrning. Externa elmätare för VP1 och VP2 måste kontrolleras vad gäller krets, faser och mätgränser.

## Mål
Studera borrhålets temperaturrespons och återhämtning mot **faktisk avgiven värmeeffekt till golvvärmesystemet**, inte kompressorns eleffekt eller antaget uttag ur marken. Jämför COP per VP och sammanlagt när värme- och elmätningar har verifierade, förenliga systemgränser. Ingen dubbelräkning av värme från gemensamma hydrauliska slingor. MVP:s beräknade vatteneffekt är inte automatiskt samma sak som leverans till golvet vid DHW, blandning eller bypass.

## Studie A: effekttrappa
| Steg | Önskad total avgiven effekt | Tid |
|---|---:|---:|
| A1 | 3 kW | 4 h |
| A2 | 6 kW | 4 h |
| A3 | 9 kW | 4 h |
| A4 | 12 kW | 4 h |

Totalt 16 h exklusive övergångar. Total effekt avser VP1 + VP2, inte 12 kW från vardera. Logga individuell effektfördelning och verkligt uppnådd nivå. Ouppnåelig nivå markeras, inte framtvingas.

## Studie B: återhämtning
| Steg | Aktivitet | Tid |
|---|---|---:|
| B1 | 9 kW totalt | 4 h |
| B2 | Vila | 1 h |
| B3 | 9 kW totalt | 4 h |
| B4 | Vila | 2 h |
| B5 | 9 kW totalt | 4 h |
| B6 | Vila | 4 h |
| B7 | 9 kW totalt | 4 h |

Totalt 23 h, varav 7 h vila. Båda studierna omfattar minst **39 h** plus övergångar och eventuell slutåterhämtning. En verklig borrhålsvila kräver att båda VP har slutat ta ut väsentlig värme ur den gemensamma källan; logga faktiska kompressor- och driftlägen. Om uttag kvarstår ska perioden etiketteras partiell återhämtning. Skydd och husets värme-/varmvattenbehov får inte förbises.

## Datainsamling
TH32/TH34 för båda maskinerna ungefär en gång per minut med tidsstämpel, ålder, giltighet och känd grov temperaturskalning. Dessutom kompressor-Hz, primärflöde, fram/retur, uppmätt vattenvärme, begärd och uppnådd golvvärme, native mode, EFFECT-fas, driftspärrar och separata elektriska kW/kWh. Snabbare processdata får aggregeras till minutmedel/min/max utan att rådata kastas. Mac sparar rådata, CSV, sessions-ID och tidsstämplad steghistorik.

Beräkna COP över tidsynkroniserade giltiga intervall som levererad värmeenergi dividerad med uppmätt elenergi, med exakt angivna inkluderade pumpar/tillskott. Vid saknad eller felaktig mätgräns: COP_UNAVAILABLE. Analysera brinetemperaturfall efter 5/15/30/60/120/240 minuter, tidig/sen lutning, återhämtning efter 1/2/4 h, hysteres och eventuella knän; redovisa osäkerhet och ordningseffekter.

## Säkerhet och godkännande
MVP3 har högst 1800 sekunders lease och RAM-baserad snapshot. Fyra timmars hålltid kräver testad leaseförnyelse och säker återställning vid omstart, tappad kommunikation eller ogiltiga givardata. Utan verifierad återställning får testet inte köras obevakat. Ingen automatisk återstart av hög effekt efter reboot. Codex måste presentera testade stopplägen, nivågränser, vilobeteende, supervision och operatörens manuella avbrytning före separat fysisk GO. Native skydd förbikopplas aldrig.

## Avgränsning
Jämförelser med 18 kW totalt och eventuell 24–27 kW kontinuerlig tvåpumpsdrift är framtida mål, **inte** ingående steg i detta helgtest. 18 kW är inte ett enpumpsmål. Resultaten ska klassas efter faktisk effekt, inte beställd effekt.

## Leverans och acceptans
Codex gör package bootstrap, review/design/functions, offline helsekvens-simulering och tester för båda adresserna, bortfall, återstart, lease, dubbla elmätare och falsk återhämtningsklassning. Resultatet redovisas i requirements/package-runs/P0077/. Fysisk acceptans kräver att operatören godkänner körningen separat och att korrekt loggning, säker återställning och spårbar COP-beräkning demonstreras.
