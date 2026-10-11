# P0089 – läsning och service

Ny läslänk: GET05 p5 går viaA3D18 till vald05FE. Kod0 motsvarar tabellindex10, kod10 index0, däremellan1..9. Det är en kvantiserad intern styrnivå; inte producerad effekt och inte lagrat SET34 p13. GET0B p11:s avrundning är nu kvalificerad: signed16, plus4000, division50 mot noll, klamp0..255. Ingen validitetsflagga införs av hjälparen.

P88:s0B/0C/14/15/26/28 råkällor och heltalsflödets wrap bevaras. Samplade följeslagarbytes benämns fortsatt råa; fysisk givartilldelning, ålder och ogiltigmarkering är inte lösta. GET04 fjärrposternas producenter och GET07 enheter/uppdatering återstår. Inga råFFFF-värden konverteras generiskt till giltiga temperaturer.

## Familjer ska identifieras med typ och kod

-5B/C9 kräver connected2342.bit0, headerhelperA5204==3 och selectorC9. Publicerad16-byte payload från P88 återanvänds; inte samma som42/C9.
-5C/CC och5D/CC har motsvarande predicate; tidigare kvalificerade svarCC FF respektiveCC. Konstant packer är inte bevis för hela transaktionens effektfrihet.
-02/00 och02/01 behålls som separata öppna descriptorfamiljer. Ingen planner för dessa.

Current API600 bygger zero-parameterGET42 eller tillåtnaA3. Den kan inte representera alternativa typer eller godtyckliga parametriserade/sessionbundna frågor. Framing-fixtures i P89 kan pröva header/typ/längd/checksum men kvalificerar inte ett okänt kommando.

## A3: resultat är inte automatiskt färskt

Återanvända bevis: CEDFA/CEBEE jämför vidarebefordrad väljare; identisk fråga kan läsa cache utan nytt jobb. Native9D598 har separat försöksräknare; Procon svc_sent räknar varje hostpoll och format0 förbrukar dess tiopollsbudget utan att vara kommunikationsfel. P89 separerar pending_polls, transport_failures, cached-age-unknown, stale och cancelled. Ägd selector matchas; ett sent resultat efter observerad cancellation godtas inte som nytt. Exakt rearm av samma selector återstår, så ingen nyförvärvsålder skapas vid ett nytt svar.

Format0=pending.1/2/3/4/7 behålls som typade råresultat med LE16 och formatetikett; ingen universell enhet/signedness uppfinns.6 är tvetydigt busy/guard/failure. Okänt format avvisas. Detta är en bredare offlinebehållare, inte en ny fysisk sensor. Current service.c accepterar endast1/2; framtida adapter ska skilja skaltyp och ålder per selector.

520..531 är research-only: odd BCD-trunkering, icke-atomiska par, tvingad fold och förlust av divisionens rest bevaras genom P86-regressionerna.532 och340 är uteslutna från läsplanering. Ingen high-low-high-pollning. GET07 har direkta effektord men motsvarar inte hela historiska energibankerna. Ingen ny bevisat effektfri alternativväg till exakt dessa energipar hittades i denna begränsade batch; det är inte ett globalt omöjlighetsbevis.
