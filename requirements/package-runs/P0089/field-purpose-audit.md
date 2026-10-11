# Återstående läsfält — syfteskartläggning

Counts are overlapping field occurrences, not functions. SD-format correlation is not native proof or hardware validation. Protocol labels do not resolve unknown peer semantics.

{'new_classified_occurrences': 932, 'remaining_raw_occurrences': 33, 'semantic_groups': 334, 'bindings': 905}

| Kommando / packare / payloadbytes | Funktion | Syfte | Evidensnivå |
|---|---|---|---|
| uart2.42.01 / a5480 / 1,2,3 | Styrenhetens datum | Datera drift och scheman. | kodkedja och källkorrelation |
| uart2.42.01 / a5480 / 4,5,6 | Styrenhetens klockslag | Tidsätta drift och scheman. | kodkedja och källkorrelation |
| uart2.42.01 / a5480 / 7,8,9,10 | FTC-programmets identitetsbytes | Identifiera programversion; alla fyra delars presentationsformat är inte fastställt. | kodkedja och källkorrelation |
| uart2.42.02 / a54f8 / 1,2 | Rumsgivarval per zon | Visa vilka rumskanaler zonerna använder. | kodkedja och källkorrelation |
| uart2.42.02 / a54f8 / 3 | Avfrostningsstatus | Visa källenhetens avfrostningsläge. | kodkedja och källkorrelation |
| uart2.42.03 / a5540 / 1 | Köldmedie-/källfelklass | Skilja felklass från den detaljerade felkoden. | kodkedja och källkorrelation |
| uart2.42.03 / a5540 / 2,3 | Rapporterad felkod | Visa systemets felkod. | kodkedja och källkorrelation |
| uart2.42.03 / a5540 / 4,5 | Formaterad felkod | Överföra felkodens andra representation. | kodkedja och källkorrelation |
| uart2.42.03 / a5540 / 8 | Aktiva värmezoner | Visa om båda zonerna eller bara en deltar. | kodkedja och källkorrelation |
| uart2.42.03 / a5540 / 11 | Tillgängliga källenheter | Ange vilka enheter som ingår i systemet. | kodkedja och källkorrelation |
| uart2.42.04 / a55c2 / 1 | Kompressorfrekvens | Följa kompressorns arbetsnivå. | kodkedja och källkorrelation |
| uart2.42.04 / a55c2 / 2 | Kompressorfrekvens enhet 1 | Följa respektive källenhets kompressor. | kodkedja och källkorrelation |
| uart2.42.04 / a55c2 / 3 | Kompressorfrekvens enhet 2 | Följa respektive källenhets kompressor. | kodkedja och källkorrelation |
| uart2.42.04 / a55c2 / 4 | Kompressorfrekvens enhet 3 | Följa respektive källenhets kompressor. | kodkedja och källkorrelation |
| uart2.42.04 / a55c2 / 5 | Kompressorfrekvens enhet 4 | Följa respektive källenhets kompressor. | kodkedja och källkorrelation |
| uart2.42.04 / a55c2 / 6 | Kompressorfrekvens enhet 5 | Följa respektive källenhets kompressor. | kodkedja och källkorrelation |
| uart2.42.04 / a55c2 / 7 | Kompressorfrekvens enhet 6 | Följa respektive källenhets kompressor. | kodkedja och källkorrelation |
| uart2.42.05 / a5628 / 6 | Använd värmekälla | Visa vilket slags värmekälla som används. | kodkedja och källkorrelation |
| uart2.42.05 / a5628 / 7 | Varmvattenproduktionens värmekällfas | Skilja normalfas, värmepump och elektrisk eftervärmning. | kodkedja och källkorrelation |
| uart2.42.05 / a5628 / 10 | Hybridens valprioritet | Visa prioriteringsvalet för jämförelse mellan värmekällor. | kodkedja och källkorrelation |
| uart2.42.07 / a5724 / 3,4 | Förbrukad effekt | Följa effekt; upplösning och samtidighet begränsar live-COP. | kodkedja och källkorrelation |
| uart2.42.07 / a5724 / 5,6 | Producerad effekt | Följa effekt; upplösning och samtidighet begränsar live-COP. | kodkedja och källkorrelation |
| uart2.42.07 / a5724 / 7 | Förbrukningsberäkning tillgänglig | Bedöma om effekt- och energifälten kan användas; inte ny energimätning. | kodkedja och källkorrelation |
| uart2.42.07 / a5724 / 8 | Produktionsberäkning tillgänglig | Bedöma om effekt- och energifälten kan användas; inte ny energimätning. | kodkedja och källkorrelation |
| uart2.42.07 / a5724 / 9 | Värmefunktion tillgänglig | Bedöma om effekt- och energifälten kan användas; inte ny energimätning. | kodkedja och källkorrelation |
| uart2.42.07 / a5724 / 10 | Energiberäkningens status | Bedöma om effekt- och energifälten kan användas; inte ny energimätning. | kodkedja och källkorrelation |
| uart2.42.07 / a5724 / 11,12 | Ackumulerad förbrukningsräknare | Följa förbrukning över tid; hantera omslag och period separat. | kodkedja och källkorrelation |
| uart2.42.09 / a57a4 / 1,2 | Valt rumsmål zon 1 | Visa aktivt rumsmål med hänsyn till drift- och semesterläge. | kodkedja och källkorrelation |
| uart2.42.09 / a57a4 / 3,4 | Valt rumsmål zon 2 | Visa aktivt rumsmål med hänsyn till drift- och semesterläge. | kodkedja och källkorrelation |
| uart2.42.09 / a57a4 / 11 | Temperaturfall för varmvattenåterladdning | Visa inställd temperaturgräns som används av regleringen. | kodkedja och källkorrelation |
| uart2.42.09 / a57a4 / 12 | Högsta tillåtna framledningsmål | Visa inställd temperaturgräns som används av regleringen. | kodkedja och källkorrelation |
| uart2.42.09 / a57a4 / 13 | Lägsta tillåtna framledningsmål | Visa inställd temperaturgräns som används av regleringen. | kodkedja och källkorrelation |
| uart2.42.0b / a5832 / 1,2 | Rumstemperatur zon 1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0b / a5832 / 3,4 | Rumstemperatur zon 2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0b / a5832 / 8,9 | Köldmediets vätsketemperatur TH2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0c / a58a2 / 1,2 | Primär framledning THW1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0c / a58a2 / 3 | Kompakt givarkanal: Primär framledning THW1 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0c / a58a2 / 4,5 | Primär retur THW2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0c / a58a2 / 6 | Kompakt givarkanal: Primär retur THW2 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0c / a58a2 / 7,8 | Varmvattentemperatur THW5B | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0c / a58a2 / 9 | Kompakt givarkanal: Varmvattentemperatur THW5B | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0c / a58a2 / 10,11 | Varmvattentemperatur THW5A | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0c / a58a2 / 12 | Kompakt givarkanal: Varmvattentemperatur THW5A | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0d / a591c / 1,2 | Framledning zon 1 THW6 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0d / a591c / 3 | Kompakt givarkanal: Framledning zon 1 THW6 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0d / a591c / 4,5 | Retur zon 1 THW7 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0d / a591c / 6 | Kompakt givarkanal: Retur zon 1 THW7 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0d / a591c / 7,8 | Framledning zon 2 THW8 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0d / a591c / 9 | Kompakt givarkanal: Framledning zon 2 THW8 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0d / a591c / 10,11 | Retur zon 2 THW9 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0d / a591c / 12 | Kompakt givarkanal: Retur zon 2 THW9 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0e / a599a / 1,2 | Extern pannas framledning THWB1 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0e / a599a / 3 | Kompakt givarkanal: Extern pannas framledning THWB1 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0e / a599a / 4,5 | Extern pannas retur THWB2 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0e / a599a / 6 | Kompakt givarkanal: Extern pannas retur THWB2 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0f / a59e4 / 1,2 | Bufferttankens temperatur THW10 | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0f / a59e4 / 3 | Kompakt givarkanal: Bufferttankens temperatur THW10 | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0f / a59e4 / 4,5 | Kondenserings-/mättnadstemperatur | Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas. | kodkedja och källkorrelation |
| uart2.42.0f / a59e4 / 6 | Kompakt givarkanal: Kondenserings-/mättnadstemperatur | Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare. | kodkedja och källkorrelation |
| uart2.42.0b / a5832 / 10 | Kompakt givarkanal för köldmediet | Alternativ representation för TH2-kanalen. | kodkedja och källkorrelation |
| uart2.42.0b / a5832 / 11 | Utetemperatur TH7 | Visa temperatur utomhus. | kodkedja och källkorrelation |
| uart2.42.10 / a5a3e / 1 | Termostatingång zon 1 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | kodkedja och källkorrelation |
| uart2.42.10 / a5a3e / 2 | Termostatingång zon 2 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | kodkedja och källkorrelation |
| uart2.42.10 / a5a3e / 3 | Flödesvakt 1 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | kodkedja och källkorrelation |
| uart2.42.10 / a5a3e / 4 | Flödesvakt 2 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | kodkedja och källkorrelation |
| uart2.42.10 / a5a3e / 5 | Flödesvakt 3 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | kodkedja och källkorrelation |
| uart2.42.10 / a5a3e / 6 | Extern ingång IN4 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | kodkedja och källkorrelation |
| uart2.42.10 / a5a3e / 7 | Extern ingång IN5 | Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften. | kodkedja och källkorrelation |
| uart2.42.11 / a5a7e / 1,2 | FTC DIP-bank SW1 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | kodkedja och källkorrelation |
| uart2.42.11 / a5a7e / 3,4 | FTC DIP-bank SW2 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | kodkedja och källkorrelation |
| uart2.42.11 / a5a7e / 5,6 | FTC DIP-bank SW3 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | kodkedja och källkorrelation |
| uart2.42.11 / a5a7e / 7,8 | FTC DIP-bank SW4 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | kodkedja och källkorrelation |
| uart2.42.11 / a5a7e / 9,10 | FTC DIP-bank SW5 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | kodkedja och källkorrelation |
| uart2.42.11 / a5a7e / 11,12 | FTC DIP-bank SW6 | Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare. | kodkedja och källkorrelation |
| uart2.42.13 / a5b08 / 1 | Kompressor i drift | Skilja kompressordrift från stopp. | kodkedja och källkorrelation |
| uart2.42.13 / a5b08 / 2 | Kompressordrift per källenhet | Visa driftmask för sex enheter. | kodkedja och källkorrelation |
| uart2.42.13 / a5b08 / 3,4,5 | Samlad kompressordrifttid | Följa drifttid; delarna bildar en gemensam räknare. | kodkedja och källkorrelation |
| uart2.42.13 / a5b08 / 6,7 | Drifttid källenhet 1 | Jämföra drifttid mellan anslutna enheter. | kodkedja och källkorrelation |
| uart2.42.13 / a5b08 / 8,9 | Drifttid källenhet 2 | Jämföra drifttid mellan anslutna enheter. | kodkedja och källkorrelation |
| uart2.42.13 / a5b08 / 10,11 | Drifttid källenhet 3 | Jämföra drifttid mellan anslutna enheter. | kodkedja och källkorrelation |
| uart2.42.14 / a5b7a / 6,7 | Drifttid källenhet 4 | Jämföra drifttid mellan anslutna enheter. | kodkedja och källkorrelation |
| uart2.42.14 / a5b7a / 8,9 | Drifttid källenhet 5 | Jämföra drifttid mellan anslutna enheter. | kodkedja och källkorrelation |
| uart2.42.14 / a5b7a / 10,11 | Drifttid källenhet 6 | Jämföra drifttid mellan anslutna enheter. | kodkedja och källkorrelation |
| uart2.42.14 / a5b7a / 2 | Eltillskott steg 1 | Visa aktivering av tillskott; inte direkt uppmätt eleffekt. | kodkedja och källkorrelation |
| uart2.42.14 / a5b7a / 3 | Eltillskott steg 2 | Visa aktivering av tillskott; inte direkt uppmätt eleffekt. | kodkedja och källkorrelation |
| uart2.42.14 / a5b7a / 4 | Eltillskott extra steg | Visa aktivering av tillskott; inte direkt uppmätt eleffekt. | kodkedja och källkorrelation |
| uart2.42.14 / a5b7a / 5 | Varmvattentankens elpatron | Visa aktivering av tillskott; inte direkt uppmätt eleffekt. | kodkedja och källkorrelation |
| uart2.42.14 / a5b7a / 12 | Primärt vattenflöde | Följa cirkulationen genom värmepumpen. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 1 | Primär cirkulationspump i drift | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 2 | Primärpumpens styrsignal | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 3 | Primärpumpens återkoppling | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 4 | Cirkulationspump 2 | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 5 | Zonpump på OUT3 | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 6 | Trevägsventil 1 | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 7 | Trevägsventil 2 | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 10 | Shuntventilens steg | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.15 / a5bf8 / 11 | Shuntventilens rörelsestatus | Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet. | kodkedja och källkorrelation |
| uart2.42.16 / a5c62 / 1 | Varmvattenpump 4 | Visa pumpens utgångsstatus. Fysisk cirkulation kräver separat verifiering. | kodkälla med publik portkorrelation |
| uart2.42.16 / a5c62 / 2 | Zonpump på OUT13 | Visa pumpens utgångsstatus. Fysisk cirkulation kräver separat verifiering. | kodkälla med publik portkorrelation |
| uart2.42.16 / a5c62 / 3 | Ytterligare zonpumpsutgång | Visa pumpens utgångsstatus. Fysisk cirkulation kräver separat verifiering. | kodkälla med publik portkorrelation |
| uart2.42.1a / a5e76 / 1,2 | Felkod från källenhet 1 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | kodfamilj identifierad; full kodlista saknas |
| uart2.42.1a / a5e76 / 3,4 | Felkod från källenhet 2 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | kodfamilj identifierad; full kodlista saknas |
| uart2.42.1a / a5e76 / 5,6 | Felkod från källenhet 3 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | kodfamilj identifierad; full kodlista saknas |
| uart2.42.1a / a5e76 / 7,8 | Felkod från källenhet 4 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | kodfamilj identifierad; full kodlista saknas |
| uart2.42.1a / a5e76 / 9,10 | Felkod från källenhet 5 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | kodfamilj identifierad; full kodlista saknas |
| uart2.42.1a / a5e76 / 11,12 | Felkod från källenhet 6 | Identifiera vilken ansluten enhet som rapporterar en avvikelse. | kodfamilj identifierad; full kodlista saknas |
| uart2.42.1b / a5efc / 1 | Vattenflöde utanför tillåtet område | Visa resultatet av min-/maxflödesövervakningen. | kodkedja och källkorrelation |
| uart2.42.26 / a612c / 3 | Systemets på/av-läge | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | kodkedja och källkorrelation |
| uart2.42.26 / a612c / 4 | Aktivt driftläge | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | kodkedja och källkorrelation |
| uart2.42.26 / a612c / 5 | Varmvattenläge | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | kodkedja och källkorrelation |
| uart2.42.26 / a612c / 6 | Reglerläge zon 1 | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | kodkedja och källkorrelation |
| uart2.42.26 / a612c / 7 | Reglerläge zon 2 | Visa valt/aktivt driftläge; inte samma sak som att kompressorn går. | kodkedja och källkorrelation |
| uart2.42.26 / a612c / 8,9 | Varmvattenbörvärde | Visa temperaturmålet som styr värmeproduktionen. | kodkedja och källkorrelation |
| uart2.42.26 / a612c / 10,11 | Framledningsmål zon 1 | Visa temperaturmålet som styr värmeproduktionen. | kodkedja och källkorrelation |
| uart2.42.26 / a612c / 12,13 | Framledningsmål zon 2 | Visa temperaturmålet som styr värmeproduktionen. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 3 | Tvingad varmvattenladdning | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 4 | Semesterläge | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 5 | Spärr för varmvatten | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 6 | Spärr för värme zon 1 | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 7 | Spärr för kyla zon 1 | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 8 | Spärr för värme zon 2 | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 9 | Spärr för kyla zon 2 | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 10 | Extern styrnings ägarskap | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.28 / a61f2 / 11 | Extern styrnings kompletterande status | Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla. | kodkedja och källkorrelation |
| uart2.42.29 / a624e / 3 | Värme-/kylval | Skilja vald temperaturfunktion. | kodkedja och källkorrelation |
| uart2.42.29 / a624e / 4,5 | Kompletterande temperaturmål zon 1 | Visa den andra målkanalen; exakt relation till valt reglerläge behöver konsumentvillkoren. | namngiven del |
| uart2.42.29 / a624e / 6,7 | Kompletterande temperaturmål zon 2 | Visa den andra målkanalen; exakt relation till valt reglerläge behöver konsumentvillkoren. | namngiven del |
| uart2.42.a1 / a8e38 / 1,2,3 | Energipostens datum | Koppla energier till samma period innan de jämförs. | kodkedja och källkorrelation |
| uart2.42.a1 / a8e38 / 4,5,6 | Förbrukad energi för värme | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | kodkedja och källkorrelation |
| uart2.42.a1 / a8e38 / 7,8,9 | Förbrukad energi för kyla | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | kodkedja och källkorrelation |
| uart2.42.a1 / a8e38 / 10,11,12 | Förbrukad energi för varmvatten | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | kodkedja och källkorrelation |
| uart2.42.a2 / a8eb6 / 1,2,3 | Energipostens datum | Koppla energier till samma period innan de jämförs. | kodkedja och källkorrelation |
| uart2.42.a2 / a8eb6 / 4,5,6 | Producerad energi för värme | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | kodkedja och källkorrelation |
| uart2.42.a2 / a8eb6 / 7,8,9 | Producerad energi för kyla | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | kodkedja och källkorrelation |
| uart2.42.a2 / a8eb6 / 10,11,12 | Producerad energi för varmvatten | Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP. | kodkedja och källkorrelation |
| uart2.42.a3 / a8f34 / 1,2 | Servicekod för svaret | Koppla svaret till beställd A3-fråga. | kodkedja och källkorrelation |
| uart2.42.a3 / a8f34 / 3 | Servicevärdets format/status | Avgöra hur svaret ska tolkas och om ett resultat finns. | kodkedja och källkorrelation |
| uart2.42.a3 / a8f34 / 4,5 | Servicefrågans resultat | Läsa värdet enligt den specifika A3-kodens betydelse. | kodkedja och källkorrelation |
| uart2.42.50 / a629c / 2,4 | Legionellakörning tillåten | Läsa konfigurationen för legionellakörning tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.50 / a629c / 5,7 | Varmvattenmål | Läsa konfigurationen för varmvattenmål. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.50 / a629c / 8,9,10 | Temperaturfall före varmvattenstart | Läsa konfigurationen för temperaturfall före varmvattenstart. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.50 / a629c / 11,12,13 | Maximal varmvattenkörtid | Läsa konfigurationen för maximal varmvattenkörtid. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.51 / a630e / 2,3,4 | Paus mellan varmvattenkörningar | Läsa konfigurationen för paus mellan varmvattenkörningar. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.51 / a630e / 5,7 | Normal/eco-varmvatten | Läsa konfigurationen för normal/eco-varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.51 / a630e / 8,9,10 | Legionellatemperatur | Läsa konfigurationen för legionellatemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.51 / a630e / 11,12,13 | Intervall mellan legionellakörningar | Läsa konfigurationen för intervall mellan legionellakörningar. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.52 / a6376 / 2,3,4 | Starttid för legionellakörning | Läsa konfigurationen för starttid för legionellakörning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.52 / a6376 / 5,6,7 | Maximal legionellakörtid | Läsa konfigurationen för maximal legionellakörtid. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.52 / a6376 / 8,9,10 | Temperaturhålltid vid legionellakörning | Läsa konfigurationen för temperaturhålltid vid legionellakörning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.53 / a63d4 / 2,4 | Reglerläge zon 1 | Läsa konfigurationen för reglerläge zon 1. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.53 / a63d4 / 5,7 | Reglerläge zon 2 | Läsa konfigurationen för reglerläge zon 2. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.59 / a7816 / 2,3,4 | Semesterfunktioner | Läsa konfigurationen för semesterfunktioner. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.59 / a7816 / 5,6,7 | Semesterns startdatum | Läsa konfigurationen för semesterns startdatum. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.59 / a7816 / 8,9,10 | Semesterns slutdatum | Läsa konfigurationen för semesterns slutdatum. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.5c / a7938 / 2,4 | Displayspråk | Läsa konfigurationen för displayspråk. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.5c / a7938 / 5,7 | Temperaturenhet | Läsa konfigurationen för temperaturenhet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.5c / a7938 / 8,10 | Temperaturvisning | Läsa konfigurationen för temperaturvisning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.5e / a79e2 / 2,4 | Tidsformat | Läsa konfigurationen för tidsformat. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.5e / a79e2 / 5,7 | Fjärrkontrollens zon | Läsa konfigurationen för fjärrkontrollens zon. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.5e / a79e2 / 8,10 | Rumsgivare zon 1 | Läsa konfigurationen för rumsgivare zon 1. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.5e / a79e2 / 11,13 | Rumsgivare zon 2 | Läsa konfigurationen för rumsgivare zon 2. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.60 / a7afc / 2,4 | Kalibrering THW1 framledning | Läsa konfigurationen för kalibrering thw1 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.60 / a7afc / 5,7 | Kalibrering THW2 retur | Läsa konfigurationen för kalibrering thw2 retur. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.60 / a7afc / 8,10 | Kalibrering THW5 varmvatten | Läsa konfigurationen för kalibrering thw5 varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.60 / a7afc / 11,13 | Kalibrering THW6 zon 1 framledning | Läsa konfigurationen för kalibrering thw6 zon 1 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.61 / a7b88 / 2,4 | Kalibrering THW7 zon 1 retur | Läsa konfigurationen för kalibrering thw7 zon 1 retur. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.61 / a7b88 / 5,7 | Kalibrering THW8 zon 2 framledning | Läsa konfigurationen för kalibrering thw8 zon 2 framledning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.61 / a7b88 / 8,10 | Kalibrering THW9 zon 2 retur | Läsa konfigurationen för kalibrering thw9 zon 2 retur. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.61 / a7b88 / 11,13 | Kalibrering THWB1 pannframledning | Läsa konfigurationen för kalibrering thwb1 pannframledning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.63 / a7c6e / 2,4 | Tillåt ekonomistopp av pump 1 | Läsa konfigurationen för tillåt ekonomistopp av pump 1. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.63 / a7c6e / 5,7 | Villkor för pumpstopp | Läsa konfigurationen för villkor för pumpstopp. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.63 / a7c6e / 8,10 | Frysskyddets framledningsmål | Läsa konfigurationen för frysskyddets framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.63 / a7c6e / 11,13 | Frysskyddets utetemperaturgräns | Läsa konfigurationen för frysskyddets utetemperaturgräns. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.64 / a7ce6 / 2,4 | Eltillskott för värme tillåtet | Läsa konfigurationen för eltillskott för värme tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.64 / a7ce6 / 5,7 | Fördröjning före eltillskott värme | Läsa konfigurationen för fördröjning före eltillskott värme. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.64 / a7ce6 / 8,10 | Eltillskott för varmvatten tillåtet | Läsa konfigurationen för eltillskott för varmvatten tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.64 / a7ce6 / 11,13 | Fördröjning före eltillskott varmvatten | Läsa konfigurationen för fördröjning före eltillskott varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.65 / a7d48 / 2,4 | Shuntens fulla gångtid | Läsa konfigurationen för shuntens fulla gångtid. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.65 / a7d48 / 5,7 | Intervall mellan shuntkorrigeringar | Läsa konfigurationen för intervall mellan shuntkorrigeringar. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.65 / a7d48 / 8,10 | Konfigurerad nivå för primärpump | Läsa konfigurationen för konfigurerad nivå för primärpump. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.66 / a7d9e / 2,4 | Val av värmekälla | Läsa konfigurationen för val av värmekälla. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.66 / a7d9e / 5,7 | Samtidig värme och varmvatten | Läsa konfigurationen för samtidig värme och varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.66 / a7d9e / 8,10 | Utetemperatur för samtidig drift | Läsa konfigurationen för utetemperatur för samtidig drift. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.66 / a7d9e / 11,13 | Lågtemperaturväxling tillåten | Läsa konfigurationen för lågtemperaturväxling tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.67 / a7dfe / 2,4 | Utetemperatur för lågtemperaturväxling | Läsa konfigurationen för utetemperatur för lågtemperaturväxling. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.67 / a7dfe / 5,7 | Rumsregleringens tidsintervall | Läsa konfigurationen för rumsregleringens tidsintervall. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.67 / a7dfe / 8,10 | Lägsta framledningsmål | Läsa konfigurationen för lägsta framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.67 / a7dfe / 11,13 | Högsta framledningsmål | Läsa konfigurationen för högsta framledningsmål. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.68 / a7e84 / 2,4 | Temperaturhysteres aktiverad | Läsa konfigurationen för temperaturhysteres aktiverad. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.68 / a7e84 / 5,7 | Nedre temperaturhysteres | Läsa konfigurationen för nedre temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.68 / a7e84 / 8,10 | Övre temperaturhysteres | Läsa konfigurationen för övre temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.69 / a7ee8 / 2,3,4 | Värmepumpens beräkningskapacitet | Läsa konfigurationen för värmepumpens beräkningskapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.69 / a7ee8 / 5,7 | Eltillskott 1 kapacitet | Läsa konfigurationen för eltillskott 1 kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.69 / a7ee8 / 8,10 | Eltillskott 2 kapacitet | Läsa konfigurationen för eltillskott 2 kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.69 / a7ee8 / 11,13 | Hybridens prioritering | Läsa konfigurationen för hybridens prioritering. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.6a / a7f52 / 2,4 | Hybridens utetemperaturgräns | Läsa konfigurationen för hybridens utetemperaturgräns. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.6a / a7f52 / 5,7 | Pannans verkningsgrad | Läsa konfigurationen för pannans verkningsgrad. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.6a / a7f52 / 8,9,10 | Pannbränslets pris | Läsa konfigurationen för pannbränslets pris. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.6a / a7f52 / 11,12,13 | Elens CO2-faktor | Läsa konfigurationen för elens co2-faktor. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.6b / a7fca / 2,3,4 | Pannbränslets CO2-faktor | Läsa konfigurationen för pannbränslets co2-faktor. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.71 / a8290 / 2,4 | Varmvattenpatronens beräkningskapacitet | Läsa konfigurationen för varmvattenpatronens beräkningskapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.71 / a8290 / 5,6,7 | Elmätarens pulsfaktor | Läsa konfigurationen för elmätarens pulsfaktor. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.71 / a8290 / 8,9,10 | Värmemätarens pulsfaktor | Läsa konfigurationen för värmemätarens pulsfaktor. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.71 / a8290 / 11,12,13 | Pump 1 beräkningsbidrag | Läsa konfigurationen för pump 1 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.72 / a830c / 2,3,4 | Pump 2 beräkningsbidrag | Läsa konfigurationen för pump 2 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.72 / a830c / 5,6,7 | Pump 3 beräkningsbidrag | Läsa konfigurationen för pump 3 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.72 / a830c / 8,10 | Korrigering av producerad energi | Läsa konfigurationen för korrigering av producerad energi. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.72 / a830c / 11,13 | Flödesgivarens nedre skalpunkt | Läsa konfigurationen för flödesgivarens nedre skalpunkt. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.73 / a8378 / 2,4 | Flödesgivarens övre skalpunkt | Läsa konfigurationen för flödesgivarens övre skalpunkt. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.73 / a8378 / 5,7 | Varmvattentillskott | Läsa konfigurationen för varmvattentillskott. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.73 / a8378 / 8,10 | Normal/snabb rumsreglering | Läsa konfigurationen för normal/snabb rumsreglering. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.75 / a8a20 / 2,3,4 | Golvtorkning start-/sluttemperatur | Läsa konfigurationen för golvtorkning start-/sluttemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.75 / a8a20 / 5,6,7 | Golvtorkning maxtemperatur | Läsa konfigurationen för golvtorkning maxtemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.75 / a8a20 / 8,9,10 | Golvtorkning hålltid | Läsa konfigurationen för golvtorkning hålltid. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.75 / a8a20 / 11,12,13 | Golvtorkning uppsteg | Läsa konfigurationen för golvtorkning uppsteg. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.76 / a8a90 / 2,3,4 | Golvtorkning hålltid uppåt | Läsa konfigurationen för golvtorkning hålltid uppåt. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.76 / a8a90 / 5,6,7 | Golvtorkning nedsteg | Läsa konfigurationen för golvtorkning nedsteg. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.76 / a8a90 / 8,9,10 | Golvtorkning hålltid nedåt | Läsa konfigurationen för golvtorkning hålltid nedåt. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.76 / a8a90 / 11,12,13 | Funktionsval för IN4 och IN5 | Läsa konfigurationen för funktionsval för in4 och in5. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.77 / a8afe / 2,4 | Smart-grid temperaturbidrag varmvatten | Läsa konfigurationen för smart-grid temperaturbidrag varmvatten. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.77 / a8afe / 5,7 | Smart-grid temperaturbidrag värme | Läsa konfigurationen för smart-grid temperaturbidrag värme. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.77 / a8afe / 8,10 | Termo-ON-utgångens val | Läsa konfigurationen för termo-on-utgångens val. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.77 / a8afe / 11,13 | Startgivare för varmvattenåterladdning | Läsa konfigurationen för startgivare för varmvattenåterladdning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.78 / a8b6c / 2,4 | Variabel flödesstyrning | Läsa konfigurationen för variabel flödesstyrning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.78 / a8b6c / 5,7 | Analog 0–10 V-styrning | Läsa konfigurationen för analog 0–10 v-styrning. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.78 / a8b6c / 8,10 | Analogstyrningens intervall | Läsa konfigurationen för analogstyrningens intervall. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.78 / a8b6c / 11,13 | Analogstyrningens effektparameter | Läsa konfigurationen för analogstyrningens effektparameter. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.79 / a8bcc / 2,3,4 | Pump 4 beräkningsbidrag | Läsa konfigurationen för pump 4 beräkningsbidrag. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.79 / a8bcc / 5,7 | Värmepumpskretsens pumpnivå | Läsa konfigurationen för värmepumpskretsens pumpnivå. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.79 / a8bcc / 8,10 | Analogstyrningens prioritet | Läsa konfigurationen för analogstyrningens prioritet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.79 / a8bcc / 11,13 | Värmepumpens minflöde | Läsa konfigurationen för värmepumpens minflöde. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7a / a8c24 / 2,4 | Värmepumpens maxflöde | Läsa konfigurationen för värmepumpens maxflöde. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7a / a8c24 / 5,7 | Hybridens temperaturhysteres | Läsa konfigurationen för hybridens temperaturhysteres. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7a / a8c24 / 8,10 | Buffertgivarens kalibrering | Läsa konfigurationen för buffertgivarens kalibrering. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7a / a8c24 / 11,13 | Smart-grid-reglering för värme | Läsa konfigurationen för smart-grid-reglering för värme. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7b / a8c92 / 2,4 | Värmemål vid rekommenderad smart-grid-drift | Läsa konfigurationen för värmemål vid rekommenderad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7b / a8c92 / 5,7 | Värmemål vid tvingad smart-grid-drift | Läsa konfigurationen för värmemål vid tvingad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7b / a8c92 / 8,10 | Kylmål vid rekommenderad smart-grid-drift | Läsa konfigurationen för kylmål vid rekommenderad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7b / a8c92 / 11,13 | Kylmål vid tvingad smart-grid-drift | Läsa konfigurationen för kylmål vid tvingad smart-grid-drift. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7c / a8d1e / 2,4 | Periodisk pumpdrift under värme | Läsa konfigurationen för periodisk pumpdrift under värme. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7c / a8d1e / 5,7 | Periodisk pumpdrift under kyla | Läsa konfigurationen för periodisk pumpdrift under kyla. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7c / a8d1e / 8,10 | Pumpcykelns intervall | Läsa konfigurationen för pumpcykelns intervall. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7c / a8d1e / 11,13 | Smart-grid-reglering för kyla | Läsa konfigurationen för smart-grid-reglering för kyla. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7d / a8d78 / 2,4 | Begränsning av eltillskottets kapacitet | Läsa konfigurationen för begränsning av eltillskottets kapacitet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7d / a8d78 / 5,7 | Sommarläge tillåtet | Läsa konfigurationen för sommarläge tillåtet. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7d / a8d78 / 8,9,10 | Sommarlägets temperaturgränser | Läsa konfigurationen för sommarlägets temperaturgränser. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7d / a8d78 / 11,12,13 | Sommarlägets tidsgränser | Läsa konfigurationen för sommarlägets tidsgränser. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7e / a8dda / 2,4 | Sommarlägets tvångsstarttemperatur | Läsa konfigurationen för sommarlägets tvångsstarttemperatur. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7e / a8dda / 5,7 | Tyst drift tillåten | Läsa konfigurationen för tyst drift tillåten. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7e / a8dda / 8,9,10 | Tyst drift start-/sluttid | Läsa konfigurationen för tyst drift start-/sluttid. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.7e / a8dda / 11,13 | Tyst drift nivå | Läsa konfigurationen för tyst drift nivå. Formatbyte och värde hör ihop; inte tre mätningar. | SD-formatkorrelation; fysisk tillämpning ej provad |
| uart2.42.62 / a7c14 / 2,4 | Kalibrering THWB2 pannretur | Korrigera givarens temperaturbidrag. | SD-formatkorrelation |
| uart2.42.62 / a7c14 / 11,13 | Kalibrering THW5A övre varmvatten | Korrigera givarens temperaturbidrag. | SD-formatkorrelation |
| uart2.42.6c / a8008 / 2 | Format för tabellvärden | Tolka de efterföljande värdena med samma format. | kodkedja och källkorrelation |
| uart2.42.6c / a8008 / 3,4 | Konfigurerad COP-punkt 1 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6c / a8008 / 5,6 | Konfigurerad COP-punkt 2 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6c / a8008 / 7,8 | Konfigurerad COP-punkt 3 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6c / a8008 / 9,10 | Konfigurerad COP-punkt 4 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6c / a8008 / 11,12 | Konfigurerad COP-punkt 5 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6c / a8008 / 13,14 | Konfigurerad COP-punkt 6 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6d / a80a0 / 2 | Format för tabellvärden | Tolka de efterföljande värdena med samma format. | kodkedja och källkorrelation |
| uart2.42.6d / a80a0 / 3,4 | Konfigurerad COP-punkt 7 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6d / a80a0 / 5,6 | Konfigurerad COP-punkt 8 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6d / a80a0 / 7,8 | Konfigurerad COP-punkt 9 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6d / a80a0 / 9,10 | Konfigurerad COP-punkt 10 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6d / a80a0 / 11,12 | Konfigurerad COP-punkt 11 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6d / a80a0 / 13,14 | Konfigurerad COP-punkt 12 | Underlag för val av värmekälla; inte uppmätt live-COP. | SD-format och native konsument |
| uart2.42.6f / a8184 / 2 | Format för tabellvärden | Tolka de efterföljande värdena med samma format. | kodkedja och källkorrelation |
| uart2.42.6f / a8184 / 3,4 | Elpris 1 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.6f / a8184 / 5,6 | Elpris 2 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.6f / a8184 / 7,8 | Elpris 3 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.6f / a8184 / 9,10 | Elpris 4 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.6f / a8184 / 11,12 | Elpris 5 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.6f / a8184 / 13,14 | Elpris 6 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.70 / a821c / 2 | Format för tabellvärden | Tolka de efterföljande värdena med samma format. | kodkedja och källkorrelation |
| uart2.42.70 / a821c / 3,4 | Elpris 7 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.70 / a821c / 5,6 | Elpris 8 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.70 / a821c / 7,8 | Elpris 9 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.70 / a821c / 9,10 | Elpris 10 | Underlag för hybridens kostnadsjämförelse. | SD-format och native konsument |
| uart2.42.57 / a77b8 / 2,3,4 | Årsperiod för veckoprogram 2 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.6e / a8138 / 2,3,4 | Period för elprissäsong 2 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.6e / a8138 / 5,6,7 | Period för elprissäsong 3 | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.5d / a7984 / 2,3,4,5,6,7,8,9,10 | Kontakttelefon på manöverpanelen | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.5f / a7a3a / 4,5,6,7,8,9,10,11,12,13 | Tidsstyrt rumsgivarval för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.55 / a653e / 4,5,6,7,8,9 | Värmekurvans tre punkter för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.5a / a7874 / 4,5,6,7,8,9,10,11 | Semesterbörvärden för vald zon | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.56 / a6642 / 5,6,7,8,9,10,11,12,13,14 | Veckoprogrammets valda tidsblock | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.74 / a8402 / 4,5,6,7,8,9,10,11,12,13 | Elprisschemats valda tidsblock | Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans. | strukturell korrelation; delkodning begränsad |
| uart2.42.54 / a6426 / 3 | Vald zon | Ange vilken zon inställningssvaret gäller. | kodkedja och källkorrelation |
| uart2.42.54 / a6426 / 2 | Format för zoninställningen | Tolka efterföljande inställningsvärden. | kodkedja och källkorrelation |
| uart2.42.55 / a653e / 3 | Vald zon | Ange vilken zon inställningssvaret gäller. | kodkedja och källkorrelation |
| uart2.42.55 / a653e / 2 | Format för zoninställningen | Tolka efterföljande inställningsvärden. | kodkedja och källkorrelation |
| uart2.42.5a / a7874 / 3 | Vald zon | Ange vilken zon inställningssvaret gäller. | kodkedja och källkorrelation |
| uart2.42.5a / a7874 / 2 | Format för zoninställningen | Tolka efterföljande inställningsvärden. | kodkedja och källkorrelation |
| uart2.42.5f / a7a3a / 3 | Vald zon | Ange vilken zon inställningssvaret gäller. | kodkedja och källkorrelation |
| uart2.42.5f / a7a3a / 2 | Format för zoninställningen | Tolka efterföljande inställningsvärden. | kodkedja och källkorrelation |
| uart2.42.54 / a6426 / 5 | Rumsbörvärde värme | Visa börvärdet för den valda zonen och reglerformen. | kodkedja och källkorrelation |
| uart2.42.54 / a6426 / 7 | Fast framledningsmål värme | Visa börvärdet för den valda zonen och reglerformen. | kodkedja och källkorrelation |
| uart2.42.54 / a6426 / 9 | Värmekurvans temperaturmål | Visa börvärdet för den valda zonen och reglerformen. | kodkedja och källkorrelation |
| uart2.42.54 / a6426 / 11 | Rumsbörvärde kyla | Visa börvärdet för den valda zonen och reglerformen. | kodkedja och källkorrelation |
| uart2.42.54 / a6426 / 13 | Fast framledningsmål kyla | Visa börvärdet för den valda zonen och reglerformen. | kodkedja och källkorrelation |
| uart2.42.07 / a5724 / 1,2 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | native konstantretur |
| uart2.42.14 / a5b7a / 13 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | native konstantretur |
| uart2.42.15 / a5bf8 / 12,13 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | native konstantretur |
| uart2.42.1c / a5f1a / 1,2,3,4,5,6,7,8,9,10,11,12,13,14 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | native konstantretur |
| uart2.42.1d / a5f8c / 1,2,3,4,5,6,7,8,9,10,11,12,13 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | native konstantretur |
| uart2.42.1e / a5ff6 / 1,2,3,4,5,6,7,8,9,10,11,12,13,14 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | native konstantretur |
| uart2.42.1f / a6068 / 1,2,3,4,5,6,7,8,9,10,11,12 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | native konstantretur |
| uart2.42.27 / a61b2 / 3,4,5,6,7,8 | Reserverat nollfält | Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation. | native konstantretur |
|  / a8ff8 / 1 | Fast FF-svar på CC-frågan | Avsluta CC-svaret; överordnad protokollavsikt är fortfarande okänd. | native konstantretur |
| uart2.42.c8 / a8f74 / 1 | Godkännande av inställningssession | Rapportera om överföringssessionen accepteras. | kodkedja och källkorrelation |
| uart2.42.56 / a6642 / 3 | Val av veckoprogram | Ange programbanken som svarsdatan hör till. | kodkedja och källkorrelation |
| uart2.42.74 / a8402 / 3 | Val av elprissäsong och veckodag | Ange vilket schemablock som efterfrågas. | kodkedja och källkorrelation |
| uart2.42.56 / a6642 / 4 | Val av dag/tidsblock | Välja del av veckoprogrammet tillsammans med första väljaren. | kodkedja och källkorrelation |
| uart2.42.09 / a57a4 / 5,6 | Aktivt temperaturmål zon 1 | Visa målet som valts för zonens värme-/kylreglering. Kan vara rums- eller framledningsmål beroende på reglerläge. | kodkedja och källkorrelation |
| uart2.42.09 / a57a4 / 7,8 | Aktivt temperaturmål zon 2 | Visa zonens aktuella målkanal beroende på reglerläge. | målkanal identifierad; lägesdetaljer begränsade |
| uart2.42.09 / a57a4 / 9,10 | Legionellacykelns temperaturmål | Visa den särskilda temperaturreferensen för legionellakörning. | kodkedja och källkorrelation |
| uart2.42.05 / a5628 / 5 | Effektbegränsningens rapporterade nivå | Visa den mest begränsande effektgränsen, inte producerad kW. | begränsningskedja följd; exakt tabellenhet öppen |
| uart2.42.03 / a5540 / 9 | Cykel-/temperaturhysteresens tillstånd zon 1 | Följa zonens särskilda reglergren vid återkommande värmestarter. | reglergren följd; aktivering på Geodan ej provad |
| uart2.42.03 / a5540 / 10 | Cykel-/temperaturhysteresens tillstånd zon 2 | Följa samma reglergren för den andra zonen. | reglergren följd; aktivering på Geodan ej provad |
| uart2.42.14 / a5b7a / 1 | Extern panna aktiverad | Visa pannstyrningens utgångstillstånd efter drift- och skyddsvillkor. | native utgångskedja |
| uart2.42.05 / a5628 / 11,12,13 | Beräknad värmekostnad för panna | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | native källkedja + SD-faktornamn |
| uart2.42.06 / a56a4 / 1,2,3 | Beräknad värmekostnad för värmepump | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | native källkedja + SD-faktornamn |
| uart2.42.06 / a56a4 / 4,5,6 | Beräknat CO2-bidrag för panna | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | native källkedja + SD-faktornamn |
| uart2.42.06 / a56a4 / 7,8,9 | Beräknat CO2-bidrag för värmepump | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | native källkedja + SD-faktornamn |
| uart2.42.06 / a56a4 / 10,11,12 | Aktivt elpris för hybridberäkning | Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata. | native källkedja + SD-faktornamn |
| uart2.42.02 / a54f8 / 4 | Eltillskottets drift och eftergång | Visa om eltillskott är aktivt eller nyligen har varit aktivt; skiljer direkt drift från eftergång. | indirekt tillståndsproducent följd |
| uart2.42.02 / a54f8 / 6 | Extern pannas drift och eftergång | Visa om pannutgångarna är aktiva eller befinner sig i eftergång. | indirekt tillståndsproducent följd |
| uart2.42.03 / a5540 / 12 | Valda källenheter för drift | Visa vilka av upp till sex källenheter som har valts för att täcka behovet. | native urvalskedja |
| uart2.42.04 / a55c2 / 8 | Bestående temperaturavvikelse utan frekvensändring | Skilja kvarstående positiv eller negativ temperaturavvikelse när kompressorns Hz ligger still. Hjälp för analys av reglerrespons, inte bevis på maximal effekt. | indirekt producent och villkor följda |
| uart2.42.15 / a5bf8 / 8 | Shuntmotor: aktiveringsutgång OUT5A | Tillsammans med OUT5B: 00/01 stopp,10 öppna,11 stäng. Rapporterar utgång, inte mekanisk position. | native bitkoppling och servicemanual |
| uart2.42.15 / a5bf8 / 9 | Shuntmotor: riktningsutgång OUT5B | Tillsammans med OUT5A: 00/01 stopp,10 öppna,11 stäng. Rapporterar utgång, inte mekanisk position. | native bitkoppling och servicemanual |
| uart2.frame.5b / a8f8a / 6 | FTC-generationens identifierare | Används av klienten för att välja kompatibel funktionalitet. | native fält + publik klientkorrelation |
| uart2.frame.5b / a8f8a / 8 | Förbrukningsberäkning konfigurerad | Visa att förbrukningsberäkningens lägesval inte är noll; skilj från GET07:s striktare värden1/2. | native källa |

## Fält som ännu saknar användarsyfte

| Kommando / packare | Position | Native underlag |
|---|---|---|
| uart2.42.01 / a5480 | 11 | [{'instruction': 'ram:000a54e5', 'operand_source': 'R0L'}] |
| uart2.42.01 / a5480 | 12 | [{'instruction': 'ram:000a54ec', 'operand_source': 'R0L'}] |
| uart2.42.01 / a5480 | 13 | [{'instruction': 'ram:000a54f3', 'operand_source': 'R0L'}] |
| uart2.42.02 / a54f8 | 5 | [{'instruction': 'ram:000a552e', 'operand_source': 'R0L'}] |
| uart2.42.02 / a54f8 | 7 | [{'instruction': 'ram:000a553c', 'operand_source': 'R0L'}] |
| uart2.42.03 / a5540 | 6 | [{'instruction': 'ram:000a5582', 'operand_source': 'R0L'}] |
| uart2.42.03 / a5540 | 7 | [{'instruction': 'ram:000a5589', 'operand_source': 'R0L'}] |
| uart2.42.04 / a55c2 | 9 | [{'instruction': 'ram:000a561a', 'operand_source': 'R0L'}] |
| uart2.42.04 / a55c2 | 10 | [{'instruction': 'ram:000a5623', 'operand_source': 'R0L'}] |
| uart2.42.05 / a5628 | 1 | [{'instruction': 'ram:000a564b', 'operand_source': 'R0L'}] |
| uart2.42.05 / a5628 | 2 | [{'instruction': 'ram:000a5654', 'operand_source': 'R0L'}] |
| uart2.42.05 / a5628 | 3 | [{'instruction': 'ram:000a565d', 'operand_source': 'R0L'}] |
| uart2.42.05 / a5628 | 4 | [{'instruction': 'ram:000a5666', 'operand_source': 'R0L'}] |
| uart2.42.05 / a5628 | 8 | [{'instruction': 'ram:000a5682', 'operand_source': 'R0L'}] |
| uart2.42.05 / a5628 | 9 | [{'instruction': 'ram:000a5689', 'operand_source': 'R0L'}] |
| uart2.42.0b / a5832 | 5 | [{'instruction': 'ram:000a5873', 'operand_source': '-0x5[FB]'}] |
| uart2.42.0b / a5832 | 6 | [{'instruction': 'ram:000a5878', 'operand_source': '-0x6[FB]'}] |
| uart2.42.0b / a5832 | 7 | [{'instruction': 'ram:000a5883', 'operand_source': 'R0L'}] |
| uart2.42.26 / a612c | 14 | [{'instruction': 'ram:000a61ad', 'operand_source': 'R0L'}] |
| uart2.42.28 / a61f2 | 12 | [{'instruction': 'ram:000a6249', 'operand_source': 'R0L'}] |
| uart2.frame.5b / a8f8a | 1 | [{'instruction': 'ram:000a8fa9', 'operand_source': '-0x1[FB]'}] |
| uart2.frame.5b / a8f8a | 2 | [{'instruction': 'ram:000a8fae', 'operand_source': '-0x2[FB]'}] |
| uart2.frame.5b / a8f8a | 3 | [{'instruction': 'ram:000a8fb3', 'operand_source': '-0x3[FB]'}] |
| uart2.frame.5b / a8f8a | 4 | [{'instruction': 'ram:000a8fb8', 'operand_source': '-0x4[FB]'}] |
| uart2.frame.5b / a8f8a | 5 | [{'instruction': 'ram:000a8fc1', 'operand_source': 'R0L'}] |
| uart2.frame.5b / a8f8a | 7 | [{'instruction': 'ram:000a8fd3', 'operand_source': 'R0L'}] |
| uart2.frame.5b / a8f8a | 9 | [{'instruction': 'ram:000a8fe5', 'operand_source': 'R0L'}] |
|  / a901e | 1 | [{'instruction': 'ram:000a902d', 'operand_source': '#0xa'}] |
|  / a901e | 2 | [{'instruction': 'ram:000a9031', 'operand_source': '#0x1'}] |
|  / a901e | 4 | [{'instruction': 'ram:000a9038', 'operand_source': '#0x40'}] |
|  / a901e | 7 | [{'instruction': 'ram:000a9042', 'operand_source': '#0x6'}] |
|  / a901e | 8 | [{'instruction': 'ram:000a9046', 'operand_source': '#0x2'}] |
|  / a901e | 9 | [{'instruction': 'ram:000a904a', 'operand_source': '#0x7a'}] |
