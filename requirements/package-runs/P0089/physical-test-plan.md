# P0089 – senare fysisk handoff

NOT RUN. Detta paket ger ingen liveauktorisation.

1. Separat godkänd, icke-mutativ observation: befintlig säkert etablerad GET26/28 samt kandidatGET05 endast efter hela dess dispatchergranskning. Spara rå ram, tid, fysisk driftsituation, begärt/valt/native läge och svarstyp. Inga krav på att rå intern nivå motsvarar kW. Stoppa vid kommunikationsfel eller oförenliga värden; inga automatiska styrförsök. En lyckad ram utan känd acquisition-age är inte färskhetsbevis.
2. Settings read/close först efter peerberoendet kvalificerats. En enhet, kategori6, inga apply-åtgärder; dokumenterad start/end/close och slutligtidle samt oförändrade driftsvärden. Timeout lämnar sessionstillstånd osäkert tills det observerats; fabricera ingen ACK.
3. Pump5→4→5 först när hela berörda kategorin kan bevaras, rätt profil/defaults validerats och återställningen kan observeras. Läs alla berörda värden före, efter och efter återställning. Skilj konfigurerat steg från PWM och flöde. Vid partiell apply: inventera aktuella värden och återställ med kvalificerad transaktion; reset är inte rollback. Saknas den förmågan får provet inte börja.

Nödvändig extra evidens: naturlig peertransaktion eller peerfirmware; installerad21.00 korrelation; timer/acquisition-age vid relevanta nyfunktioner. Ingen D-injektion, kabeländring eller säkerhetsbypass.
