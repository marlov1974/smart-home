# Vad avläsningarna används till

Denna fortsättning följer 31 fält i GET17, GET18 och GET19 till övervakningens faktiska villkor. Detta är ny syftesanalys, inte bara nya namn. Inga pumpar har kontaktats.

**Inte klart för hela protokollet.** GET17:s11 och GET18:s12 skrivna statusfält är följda; GET19:s8 är följda. Tidigare namn på hela paketen var för snäva.

| Kommando / databyte | Begripligt namn | Syfte |
|---|---|---|
| GET17 / 1 | Övertemperatur i primärkretsen | Upptäcka att framledning eller retur blir för varm. |
| GET17 / 2 | Övertemperatur i varmvattentanken | Upptäcka för hög temperatur i varmvattnet. |
| GET17 / 3 | Fel på primär framledningsgivare | Visa när framledningstemperaturen inte kan användas som tillförlitligt mätvärde. |
| GET17 / 4 | Fel på primär returgivare | Visa när returtemperaturen inte kan användas som tillförlitligt mätvärde. |
| GET17 / 5 | Fel på varmvattengivare THW5B | Upptäcka bortfall eller fel i den nedre varmvattengivarens kanal. |
| GET17 / 6 | Fel på framledningsgivare zon 1 | Kontrollera att zon 1 har ett användbart framledningsvärde. |
| GET17 / 7 | Fel på returgivare zon 1 | Kontrollera att zon 1 har ett användbart returvärde. |
| GET17 / 8 | Fel på framledningsgivare zon 2 | Kontrollera att zon 2 har ett användbart framledningsvärde. |
| GET17 / 9 | Fel på returgivare zon 2 | Kontrollera att zon 2 har ett användbart returvärde. |
| GET17 / 10 | Frysrisk i primärkretsen | Upptäcka farligt låg vattentemperatur i framledning eller retur. |
| GET17 / 13 | Fel på varmvattengivare THW5A | Övervaka den övre varmvattengivaren; felet används också när temperaturkälla väljs. |
| GET18 / 1 | Orimlig temperaturrespons i primärkretsen | Upptäcka utebliven temperaturökning under värmeproduktion tillsammans med orimligt förhållande mellan framledning och retur. |
| GET18 / 2 | Omvänt temperaturförhållande i zon 1 | Upptäcka att zonens retur är mer än 5 grader varmare än framledningen under övervakad drift. |
| GET18 / 3 | Omvänt temperaturförhållande i zon 2 | Upptäcka att zonens retur är mer än 5 grader varmare än framledningen under övervakad drift. |
| GET18 / 4 | Otillräckligt primärflöde | Upptäcka för liten vattencirkulation via flödesvakt eller flödesmätare. |
| GET18 / 8 | Fel på köldmediets vätsketemperaturgivare | Kontrollera att köldmediets temperaturkanal ger ett användbart värde. |
| GET18 / 9 | För kallt under övervakad drift eller avfrostning | Upptäcka låga köldmedie-/vattentemperaturer i särskilda driftlägen. |
| GET18 / 10 | Övertemperatur vid extern panna | Upptäcka för hög temperatur på pannans framledning. |
| GET18 / 11 | Fel på pannans framledningsgivare | Kontrollera att den externa pannans framledningstemperatur är användbar. |
| GET18 / 12 | Fel på delad panna-/buffertgivarkanal | Visa fel i givarkanalen som konfigurationen använder för pannretur eller bufferttank. |
| GET19 / 1 | För låg framledning i zon 1 under särskild drift | Upptäcka att zon 1 förblir under 25 grader när det övervakade driftläget kräver uppvärmning. |
| GET19 / 2 | Frysrisk vid extern panna | Upptäcka mycket låg temperatur på pannans framledning efter startvillkor och väntetider. |
| GET19 / 3 | Oförenlig värmekällekonfiguration | Upptäcka kombinationer av värmekälla, tillgängliga enheter och systemval som inte stöds. |
| GET19 / 6 | Samlad avvikelse från anslutna källenheter | Visa om någon vald källenhet har den avvikelse som rapporteras i enheternas sammanfattande statusmask. |
| GET19 / 7 | Misslyckad varmvatten-/växlingssekvens | Upptäcka utebliven tankuppvärmning eller för hög primärtemperatur under särskilda varmvattensekvenser. |
| GET18 / 5 | Utlöst flödesvakt 2 | Upptäcka utebliven cirkulation på kretsen som övervakas av flödesvakt 2. |
| GET18 / 6 | Utlöst flödesvakt 3 | Upptäcka utebliven cirkulation på kretsen som övervakas av flödesvakt 3. |
| GET18 / 7 | Fel på någon av zonernas rumsgivare | Visa om rumstemperaturen för zon 1 eller zon 2 inte går att lita på. |
| GET19 / 8 | Fel på vattenflödesmätarens givarkanal | Skilja ett fel på själva flödesgivaren från ett giltigt men för lågt vattenflöde. |
| GET19 / 4 | Kommunikationsövervakning av rumsgivarmottagaren | Upptäcka att giltig kommunikation från rumsgivarmottagaren uteblir under för lång tid. |
| GET19 / 5 | Spärrad rumsreglering per rumskanal | Visa vilka av de åtta rumskanalerna som rapporterar status som hindrar rumsreglering. |

## Vad fynden innebär

- Fel på flödesgivaren och för lågt vattenflöde är olika signaler. Ett transportmässigt läsbart flöde behöver därför inte vara användbart.
- Zonernas omvända temperaturförhållande övervakas med giltiga givare och mer än5 graders skillnad, efter drift- och tidsvillkor. Signalen kan hjälpa felsökning men bevisar inte rundgång.
- Övertemperaturövervakningen använder bland annat80 grader i primärkretsen och75 grader i tanken. Detta är referensfirmwarens utlösningsvillkor, inte rekommenderade börvärden eller våra styrgränser.
- Läsningarna rapporterar status från skyddslogik; de är inte kommandon för att aktivera eller avaktivera skydd.
- Trösklar är inte omedelbara larmgränser. Timer, driftläge, konfiguration och givargiltighet ingår. Exakta tider har inte kvalificerats här.

## Statuskodernas betydelse

A4410 maps source0→0;1/2→1;3/4/5→(flag?2:0). Other states fall back0. Do not label the wire byte a universal boolean fault flag.

En nolla är alltså inte generellt ett friskintyg. Den kan även uppstå när ett tillstånd inte exponeras av just den fältvarianten. Ursprungstillstånd och flagga måste beaktas.

## Kvarstående gränser

GET19 receiver mask has unknown radio-level cause; A3 service modes350..363 still need peer semantics; other commands/fields remain outside this purpose pass.

GET19:s låga zontemperatur och sekvensfel har användbara syften men ännu inte fullständiga menynamn/orsaksdiagnoser. Fältet för källenheter har en mask med tidsvillkor; exakt peer-felklass återstår.

## Reproduktion och källor

purpose-analysis.json sparar descriptorbytes, tillhörande callbacktabeller och hash för nya native exporter. Kedjan är svarspackare → tillstånd → indirekt descriptor → utlösningsvillkor. ManualOCH722A:s A3/504–515 och567/569 används för fysisk givartilldelning. C-dekompilering kontrolleras mot native instruktioner; privata exporter ingår inte i public repo.
