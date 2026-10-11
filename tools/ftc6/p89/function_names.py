"""P0089 functional names, with deliberately bounded claims.

A name on a mixed packet describes its identified members, not every byte.
"""
# key: name, confidence, evidence, qualification
SETTINGS = {
'50': ('Varmvattenmål, temperaturfall och maximal körtid', 'namngiven del', 'A629C; BD190:1947/1948→0714,194A/194B→0716; A3FF2; OCH722A DHW menu', 'Temperaturfall är kopplat till samma källa som GET09; körtidsnamnet stöds av minutomvandling och manualen. Övriga fält återstår.'),
'51': ('Varmvattenläge, återhämtningspaus och legionellamål', 'trolig', 'A630E:3912; BD190:194D/194E→0718,1953/1954→071A; 959DE defaults; OCH722A DHW menu', 'Läge är direkt identifierat. Paus och legionellamål är funktionshypoteser från import, standardvärden och manual; inte full konsumentkedja.'),
'52': ('Legionellacykelns tidsinställningar', 'trolig', 'A6376; BD190:195C/195D→071C (hours),195F/1960→071E (minutes); 959DE defaults; OCH722A DHW menu', 'Tidsenheterna och standardvärdena passar maximal cykeltid och temperaturhålltid. Alla fält är inte namngivna.'),
'53': ('Zonernas värme-/kylreglerläge', 'identifierad', 'A63D4:3913/3914; C979E; P0084/settings-trace.md', 'Inställningssessionens väg; skilj begärt läge från valt läge.'),
'54': ('Zonernas temperaturbörvärden', 'identifierad', 'A6426; A6410 zone selection; C979E:38DC..38F6; P0088/cn105-control-fields.md', 'Blocket omfattar flera temperaturmål per zon, inte ett enda framledningsmål.'),
'56': ('Veckoprogram för värme/kyla och varmvatten', 'trolig', 'A6642; A65CC:3*28+2*14+2*7+weekday; P0088/settings-transfer-map.md; S1/S2 files in atlas-ledger.md', 'Sjudagarsindex och schemabanker stöder familjen. Exakt betydelse av samtliga programväljare är ännu inte fastställd.'),
'5a': ('Semesterlägets temperaturmål', 'identifierad', 'A7874; BD20E:194A..195D→0733/0735/0737/0739/0781/0783/0785; B9C9E/B9D5A; P0088/cn105-control-fields.md', 'Flera mål och zonval; inte själva semesteraktiveringen.'),
'60': ('Kalibrering av temperaturgivare, grupp 1', 'identifierad', 'A7AFC:0729/072B/072F/0771; 986E2/98702; P0087/flow-target-trace.md', 'Framledning och retur är belagda. Alla givarnamn i gruppen återstår.'),
'61': ('Kalibrering av temperaturgivare, grupp 2', 'identifierad', 'A7B88:0773/0775/0777/0779; 987AE and adjacent sensor writers', 'Kalibreringsfamilj identifierad; tilldelning till varje fysisk givare återstår.'),
'62': ('Kalibrering av temperaturgivare, grupp 3', 'identifierad', 'A7C14:077B/072D; 959DE zero-offset defaults; sensor writer family986E2..9884E', 'Två ytterligare kalibreringsvärden; fysisk givartilldelning inte fullständigt belagd.'),
'63': ('Cirkulationspumpens ekonomi- och temperaturvillkor', 'trolig', 'A7C6E:073D/0723/0725/0727; AF12E/AF660/C132A; 959DE; OCH722A auxiliary menu', 'Pumpvillkor och fördröjning har native konsumenter. Gruppens fullständiga fältnamn återstår.'),
'64': ('Eltillskottets tillåtelse och fördröjningar', 'trolig', 'A7CE6:073C/0721/073B/07FD; BE24E; 959DE defaults30/15min; OCH722A auxiliary menu', 'Standardvärden och tillståndsvillkor stöder namnet; inte ett bevis för varje tillskottssteg.'),
'65': ('Shuntventilens gångtid/intervall och varmvattenpumpens nivå', 'namngiven del', 'A7D48:077D/077F/0770; C47FE/C4126; 959DE defaults120s/2min; P0083/pump-control-trace.md; OCH722A mixing valve menu', 'Rättar tidigare alltför snävt namn DHW settings. Shuntnamnet är korrelerat via tider, utgångar och manual; pumpnivån är tidigare belagd.'),
'66': ('Val av värmekälla och samtidig värme/varmvatten', 'trolig', 'A7D9E:0720/073E/073F/0741; BF750; 959DE; OCH722A simultaneous operation menu', 'BF750 kombinerar utetemperaturvillkor med zonspärrar. Namnet är en arbetshypotes för blandat block.'),
'67': ('Värmeregleringens temperaturgränser och tidsintervall', 'namngiven del', 'A7DFE:0742/0744/0746/0748; A400C/A4026→GET09; B4F42; OCH722A heating menu', 'Framledningens min/max har läskoppling. Övriga villkor och intervall ska inte likställas med dessa gränser.'),
'68': ('Värmepumpens temperaturhysteres', 'trolig', 'A7E84:0753/0754/0756; AC3AE; 959DE offsets153/154; OCH722A thermo diff.adjust', 'Standardvärden +5/-5 och användning i regleringen stöder familjen; aktiveringens fulla semantik återstår.'),
'69': ('Värmekällornas kapaciteter för hybridberäkning', 'trolig', 'A7EE8:074A/074C/074E/0752; C3374; 959DE defaults11.2/2/4; OCH722A hybrid menu', 'Matchar värmepumpskapacitet och två tillskott. Sista fältet är inte slutligt namngivet.'),
'71': ('Energiberäkning: tillskott och primärpump', 'namngiven del', 'A8290:075B/075D/07CC/07D3; P0084/settings-trace.md', 'Blocket innehåller energiberäkningens konfiguration; varje kapacitetsfält är inte slutligt namngivet.'),
'72': ('Energiberäkning: extra pumpar och energikorrigering', 'namngiven del', 'A830C:07D5/07D6/07D7/07CA; P0084/settings-trace.md', 'Pump2/3 och korrigeringen tidigare belagda; återstående byte öppet.'),
'74': ('Ytterligare veckoprogram', 'trolig', 'A8402; A83BE:three groups*7days; settings-transfer-map selectors651..785', 'Sjudagarsstruktur belagd. Tyst drift är en kandidat, men ännu inte tillräckligt belagd för att ingå i namnet.'),
'77': ('Rumsgivarval och externa temperaturbidrag', 'namngiven del', 'A8AFE:07D9/07DB/07DD/07DE; D1334→4990/4992; 98762 uses07DE for666/668 selection', 'Givarval är belagt. Temperaturbidragens roll och de övriga fälten är inte slutligt namngivna.'),
'79': ('Värmepumpens cirkulationspumpnivå och närliggande driftval', 'namngiven del', 'A8BCC:07E5/07E6/07E7/07E8; P0083/pump-control-trace.md', 'Endast pumpnivåns funktion fullt namngiven; tre andra driftval kvarstår.'),
'7a': ('Temperaturkorrigering och omkopplingsvillkor', 'namngiven del', 'A8C24:07E9/07EA/07EC/07EE; 9884E; C2B96; AF660', 'Blandat block. Namnet beskriver identifierade typer, inte samtliga funktioner; 07EC är kalibreringsbidrag.'),
'7b': ('Smart-grid-temperaturmål för värme och kyla', 'trolig', 'A8C92:07EF/07F1/07F3/07F5; BAB56; 959DE defaults50/55/15/10; OCH722A smart-grid menu', 'Värmens mål kopplas till två externa tillstånd. Identiteten smart-grid och kylparet behöver sista konsumentkontrollen.'),
'7c': ('Periodisk cirkulation under värmedrift', 'trolig', 'A8D1E:07F7/07F8/07F9/07FB; AF660; 959DE default10min; OCH722A pump cycles', 'Pumpvillkor och tiominutersintervall stöder familjen; alla fyra val är inte identifierade.'),
}

SETTINGS.update({
'55': ('Värmekurvans punkter per zon', 'trolig', 'A653E/A6410:zone-select and three staged point groups; adjacent53/54 mode/target blocks', 'Zonval och punktstruktur stöder namnet. Exakt kurvtolkning är en hypotes och inte härledd enbart från ordningsföljden.'),
'58': ('Reserverad inställningsplats 58', 'platshållare', 'A77F2 only session-status/category; A910F switch index8→ABB8B', 'Läsaren lämnar inget inställningsinnehåll och skrivgrenen går direkt till gemensamt slut i denna image.'),
'5b': ('Reserverad inställningsplats 5B', 'platshållare', 'A7914 only session-status/category; A910F switch index11→ABB8B', 'Läsaren lämnar inget inställningsinnehåll och skrivgrenen går direkt till gemensamt slut i denna image.'),
'6b': ('Omräkningsfaktor för jämförelse mellan värmekällor', 'namngiven del', 'A7FCA:0769; BC148/BC29C expands adjacent packed value; C2F48 denominator076B/076D', 'Används i jämförelse av värmekällor. Om faktorn avser kostnad eller CO2 är ännu inte slutligt fastställt.'),
'6c': ('Temperaturberoende prestandatabell, första delen', 'namngiven del', 'A8008:0800..080A; C3050 indexes0800 using outdoor/target temperatures', 'Tabellens funktion i temperaturberoende beräkning är belagd; storhetens absoluta enhet återstår.'),
'6d': ('Temperaturberoende prestandatabell, andra delen', 'namngiven del', 'A80A0:080C..0816; C3050 indexed0800 table', 'Fortsättningen av samma tabell; inte en oberoende fysisk funktion.'),
'6f': ('Valbara faktorer för jämförelse mellan värmekällor, grupp 1', 'namngiven del', 'A8184:0787/078D/0793/0799/079F/07A5; BC148 expansion; C34F8 selection', 'Sex lagrade faktorer väljs i jämförelseberäkningen. Pris-/CO2-betydelse inte slutligt fastställd.'),
'70': ('Valbara faktorer för jämförelse mellan värmekällor, grupp 2', 'namngiven del', 'A821C:07AB/07B1/07B7/07BD; BC148; C34F8 selection', 'Fyra fortsättningsvärden i samma familj; inga gissade enheter.'),
'78': ('Analog utgång: prioritet, intervall och energibidrag', 'trolig', 'A8B6C:07DF/07E0/07E1/07E3; 959DE defaults5min/0; OCH722A analog output menus', 'Namnförslag från tids-/effektformat och manual. Full utgångskonsument måste bekräfta identiteten.'),
})

# Third pass: explicit consumer chains, with category aliases kept visible.
SETTINGS.update({
'6a': ('Hybridvalets temperaturgräns och jämförelseparametrar', 'namngiven del', 'A7F52→0758/075A/0763/07C3; C2B96 temperature threshold; BC148/BC29C; C34F8→C2E60/C2F48', 'Temperaturgräns och faktorer som används vid jämförelse av värmekällor. Enskilda pris-/CO2-etiketter är ännu inte säkra.'),
'73': ('Tillskottsvillkor, flödessensorns övre skalpunkt och reglerrespons', 'namngiven del', 'A8378→07C9/07CB/07D2; BF8A6; CE554→CE422→322E primary flow; BB160/D0892/D08FA', 'Blandat paket:07C9 påverkar tillskottets tillåtelse,07CB sätter flödessensorns övre skalpunkt via CE554→CE422→322E,07D2 ändrar temperaturregleringens respons. Exakta menynamn återstår.'),
'76': ('Val av funktion för externa styringångar', 'namngiven del', 'A8A90→0750/0751; 8DCAC selects0527→069A versus0530→069D and055D→06A2 versus0539→069E; B4A7C/B4CFA', 'Två val avgör hur externa signaler används. Ytterligare stagingfält i samma paket saknar namngiven konsument.'),
})

EXTRA_ROUTES = {
'42.06': ('Jämförelsevärden för val av värmekälla', 'namngiven del', 'A56A4→A3E0C/A3E34/A3E5C→262C/2634/263C; C371C←C34F8; C2E60/C2F48', 'Beräknade jämförelsevärden, inte uppmätt förbrukad/producerad effekt. Exakt kostnads-/CO2-etikett återstår.'),
'42.1a': ('Rapporterade tillståndskoder från sex anslutna enheter', 'namngiven del', 'A5E76→A4544→3952+12*i; 8D9AA unit-index1..6 reads D513; C396C inspects the same records', 'En kod per enhet. Kodernas fulla betydelse och fysisk tilldelning är inte slutligt fastställda.'),
'42.19': ('Övervaknings- och spärrstatus för driftutgångar', 'namngiven del', 'A5DF6→A4410/A4482; C163A/C16C2 inspect3F79/3F86; BF66C uses495A to inhibit3A44 bits', 'Identifierade delar påverkar tillåtelsen för driftutgångar. Övriga statusplatser saknar producent eller fysisk etikett.'),
'42.20': ('Tom reserverad datasvarsplats 20', 'platshållare', 'A60CC only writes frame/type/length/opcode; A9080→A906A clears reply first (P0088 port-sprint)', 'Datafältet lämnas tomt i denna referensfirmware. Avsedd funktion i andra versioner är okänd.'),
}

EXTRA_ROUTES['frame.02.00'] = (
    'Avsluta inställningssession och lämna alternativt informationssvar', 'namngiven del',
    'RX descriptor13 internal149=95h; A51C6/A5250; CF518 atCF639→2372=0; CE920 watchdog; TX149→A901E',
    'Detta beskriver belagd funktion i FTC. Syftet med de konstanta informationsbytena är ännu inte namngivet; kommandot är inte effektfri läsning.')

# Fourth pass: independent named consumer in the vendor's SD configuration tool.
from sd_names import names as sd_names
SETTINGS.update(sd_names())

EXTRA_ROUTES.update({
'42.1b': ('Status för övervakning av värmepumpens tillåtna vattenflöde', 'identifierad', 'A5EFC→49B6; table85702 row7 state pointer49B6/callback table882FC; ACB52 indirect writer; D2C00 compares322E with07E8/07E9; D2D5A returns49B7 fault status', 'Rapporterar övervakning av min-/maxflöde, inte flödet i l/min. Indirekt producent bevisar varför direktreferenssökningen inte räckte.'),
'41.33': ('Generisk SET-kvittens för 33; tillämpning ej identifierad', 'namngiven del', 'RX SET33→internal2; A5430 emits generic zero ACK; bounded consumer audit', 'Protokollrollen är namngiven. Vilken eventuell inställning anroparen avser och om en indirekt tillämpning finns är fortfarande okänt.'),
'frame.02.01': ('Nollkvittens i det alternativa 02-protokollet', 'namngiven del', 'A51E2 requires FF/FF and zero parameter; internal96→A9056; A9090 alternative header', 'Belagd transportfunktion. Överordnad avsikt och eventuell indirekt sidoeffekt är inte identifierade.'),
'frame.5c': ('Anslutningsbunden CC-fråga med CC/FF-svar', 'namngiven del', 'A5172 requires connected state and CC; internal93→A8FF8/A4ADE', 'Funktionsnamnet beskriver observerbar protokollfunktion. Det är inte belägg för en fysisk styrfunktion eller fullständig effektfrihet.'),
'frame.5d': ('Anslutningsbunden CC-kvittens', 'namngiven del', 'A519C requires connected state and CC; internal94→A900E', 'Funktionsnamnet beskriver observerbar protokollfunktion. Överordnad avsikt och indirekta sidoeffekter är fortfarande öppna.'),
})

# P0089 purpose pass: follow indirect fault callbacks to their actual conditions.
EXTRA_ROUTES.update({
'42.17': ('Givarfel, övertemperatur och frysrisk', 'namngiven del', 'purpose-analysis.json; A5C86→fault descriptors→B7E76/B812E/B8E14 and sensor callbacks', 'Visar om temperaturvärden och temperaturgränser är användbara för säker drift. Alla11 skrivna statusfält har nu följts. Tids-/aktiveringsvillkor gäller; statuskod0 betyder inte generellt frisk givare.'),
'42.18': ('Temperaturrespons, cirkulation och givarfel', 'namngiven del', 'purpose-analysis.json; A5D3A→B85E6/CADF4/CB0A4/A2F6C and fault callbacks', 'Upptäcker utebliven uppvärmning, omvänd temperaturskillnad i zonerna, flödesvaktsfel och flera givarfel. Alla12 skrivna statusfält har nu följts; dessa signaler bevisar inte en viss fysisk felorsak.'),
'42.19': ('Driftskydd, värmekällekonfiguration och flödesgivarfel', 'namngiven del', 'purpose-analysis.json; A5DF6→C1BE6/C2634/C914C/CCCCE/CE86A', 'Skiljer bland annat låg temperatur, oförenlig systemkonfiguration och fel på flödesgivaren. Alla åtta fält har syftesbeskrivning, inklusive kommunikation med rumsgivarmottagaren och spärrar per rumskanal. Exakt radioorsak bakom spärrar återstår.'),
})

# Field-level continuation; configuration factors are not live measurements.
SETTINGS.update({
'6a':('Hybridens utetemperaturgräns, pannverkningsgrad, bränslepris och elens CO2-faktor','namngiven del','field-purpose-audit.json;A7F52→0758/075A/07C3/0763;BD296;SD_SV_Pos105/108/111/117','Faktornamnen stöds av kategorikvalificerad SD-import. Skala och fysisk tillämpning är separata frågor.'),
'6b':('Pannbränslets CO2-faktor för hybridval','namngiven del','field-purpose-audit.json;A7FCA→0769;BD296;SD_SV_Pos123;C34F8/C2F48','Konfigurerad jämförelsefaktor, inte uppmätt utsläpp eller effekt.'),
})
EXTRA_ROUTES['42.06']=('Hybridjämförelse: kostnad, CO2 och valt elpris','namngiven del','field-purpose-audit.json;C34F8→C371C→262C..263E→A3E0C/A3E34/A3E5C','Beräknade jämförelsevärden baserade på pris-, verkningsgrads- och COP-konfiguration. Inte uppmätt effekt eller live-COP; absoluta skalenheter återstår.')
EXTRA_ROUTES['42.10']=('Termostatingångar, flödesvakter och externa styringångar','identifierad','field-purpose-audit.json;A4156..A41B6;8DCAC','Visar sju separata ingångar. Tidigare samlingsnamn termostaternas värmebehov var för snävt; externa ingångarnas funktion beror på konfiguration.')
