# P0089 – inställningssessionens gräns

PARTIAL; endast syntetisk offlineobservatör. P86/P88:s statiska sekvens återanvänds; den är inte ny fysisk verifiering.

(a) **CN105 ensamt:** ingen komplett sekvens kvalificerad. C8 annonserar önskad kategori/riktning, men första steget kräver intern1002 och dataavslut kräver accepterad D tag1/väljare0. Externa A3-val>=700 är filtrerade. Granskade ordinary41/42-rutter,5B/C9,5C/CC,5D/CC ger ingen belagd ersättning.02-familjens återstående native-effekter är fortfarande en specifik lucka; därför görs inget universellt omöjlighetspåstående.

(b) **CN105 med normalt ansluten skärm/peer:** förenligt med annonseringsvägen1005, men peerens polling/start/överföring/slut/close är inte observerad här. Vi kan inte lova att den nu anslutna skärmen fullföljer detta.

(c) **Ytterligare peerhändelse:** minsta saknade evidens är en tidsstämplad, naturligt initierad kategori6 read/close-transaktion med CN105 och D-händelser korrelerade, eller motsvarande peerfirmware. Inga D-paket eller förbikopplingar föreslås för detta paket.

## Två kontrakt

Read utan apply: idle0 → C8 open direction1/mask20hex →1 → peer1002 low2=2 →7 → GET →8 → accepterat peer-end →9 (data) → C8 action1 →10 → action2 →11 → peer1002 low2=3 →12 → close-response →0. GET-status måste vara0 för giltiga data, inte1/FF. Slutlig0 och oförändrad drift måste observeras separat.

Write: idle0 → direction0/mask20 →1 → peer1002 low2=0 →2 → matching stage →3 → action1 **importerar kategori och går till4** → peer-end →5 → action2 →6 → peer1002 low2=1 →12 → close-response →0. Apply sker före slutkvittensen. Flera kategoribitar är inte samma sak som kategorinummer; offlineobservatören accepterar bara en uttrycklig kategori.

Timeout, abort/action3, disconnect och restart är aldrig bevis för rollback. CF518 återställer sessionsläge men återställer inte de redan importerade aktiva fälten. Länk/roll/riktning och driftövergång kan avsluta sessionen. Timrar840CE/840C2/840D4 har descriptor-ticks, inte här kvalificerade sekunder. Efter restart är aktiva värden en fråga om faktiskt sparad bild, inte observatörens minne.

P89-modellen bevarar `applied=True` och separat `persisted=False` efter timeout; syntetiska peerhändelser måste anges explicit. Den modellerar bara de listade övergångarna och avvisar okända. Upprepning, ägarskap och alla parserordningar utanför dessa kanter är fortsatt öppna.

Lagringsverifiering: önskad==shadow räcker inte (P88 tredjefelsgren kan avancera shadow). Kräver oberoende läsning efter apply och separat godkänd omstart för boot-verifiering. Ingen settings-serializer eller liveplan aktiveras.
