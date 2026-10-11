"""Semantic groups in the FTC6 reference image; positions are payload bytes.

Multi-byte members share a purpose, not independent measurements. SD correlations
remain hypotheses where a complete native consumer chain is not established.
"""
GROUPS=[]
def add(packer, positions, name, purpose, evidence, confidence='kodkedja och källkorrelation', kind='mätning/status'):
    GROUPS.append(dict(packer=packer,positions=list(positions),name=name,purpose=purpose,evidence=evidence,confidence=confidence,kind=kind))
def seq(packer, rows):
    for positions,name,purpose,evidence in rows:add(packer,positions,name,purpose,evidence)
seq('a5480',[(range(1,4),'Styrenhetens datum','Datera drift och scheman.','A39FC→38B4..38B6'),(range(4,7),'Styrenhetens klockslag','Tidsätta drift och scheman.','A4B72→38B8..38BA'),(range(7,11),'FTC-programmets identitetsbytes','Identifiera programversion; alla fyra delars presentationsformat är inte fastställt.','A3A18→ROM80000..80003')])
add('a54f8',[1,2],'Rumsgivarval per zon','Visa vilka rumskanaler zonerna använder.','A3A7C→393F/3940;A2BA0/A2BC0 väljer motsvarande bit')
add('a54f8',[3],'Avfrostningsstatus','Visa källenhetens avfrostningsläge.','A3A8A→3D07; pinned Process0x02')
seq('a5540',[([1],'Köldmedie-/källfelklass','Skilja felklass från den detaljerade felkoden.','A3B2E→3A02;Process0x03'),([2,3],'Rapporterad felkod','Visa systemets felkod.','A3B5E→3A06;Process0x03'),([4,5],'Formaterad felkod','Överföra felkodens andra representation.','A3B7A→A4D3C(3A08);Process0x03'),([8],'Aktiva värmezoner','Visa om båda zonerna eller bara en deltar.','A3BDC→3A54..3A59;Process0x03'),([11],'Tillgängliga källenheter','Ange vilka enheter som ingår i systemet.','A3C70→399E;C914C')])
add('a55c2',[1],'Kompressorfrekvens','Följa kompressorns arbetsnivå.','A3C88→062C &7F;A3/016')
for i in range(6):add('a55c2',[i+2],f'Kompressorfrekvens enhet {i+1}','Följa respektive källenhets kompressor.','A3C98→395A+12*(unit−1)')
add('a5628',[6],'Använd värmekälla','Visa vilket slags värmekälla som används.','A3D6E→3A4A')
add('a5628',[7],'Varmvattenproduktionens värmekällfas','Skilja normalfas, värmepump och elektrisk eftervärmning.','A3DA2→06E0;Process0x05')
add('a5628',[10],'Hybridens valprioritet','Visa prioriteringsvalet för jämförelse mellan värmekällor.','A3DEA→0752;SD_SV_Pos102')
for p in (3,5):add('a5724',[p,p+1],'Förbrukad effekt' if p==3 else 'Producerad effekt','Följa effekt; upplösning och samtidighet begränsar live-COP.','A3E98/A3EB2;P0086 power trace')
for p,name,proof in [(7,'Förbrukningsberäkning tillgänglig','A4BEA→099B'),(8,'Produktionsberäkning tillgänglig','A4C06→099C'),(9,'Värmefunktion tillgänglig','A4C4E→0900/05D3/06D6'),(10,'Energiberäkningens status','A4C74→099A')]:add('a5724',[p],name,'Bedöma om effekt- och energifälten kan användas; inte ny energimätning.',proof)
add('a5724',[11,12],'Ackumulerad förbrukningsräknare','Följa förbrukning över tid; hantera omslag och period separat.','A4C80;P0086 energy trace')
for p,name,proof in [(1,'Valt rumsmål zon 1','A3ECC→38DC/38E2/0735/0739'),(3,'Valt rumsmål zon 2','A3F32'),(5,'Valt temperaturmål från 3908/390A','A3F98'),(7,'Valt temperaturmål från 3910/391C','A3FBC'),(9,'Temperaturreferens från 390E','A3FE0')]:
    if p<5:add('a57a4',[p,p+1],name,'Visa aktivt rumsmål med hänsyn till drift- och semesterläge.',proof)
for p,name,proof in [(11,'Temperaturfall för varmvattenåterladdning','A3FF2→0714'),(12,'Högsta tillåtna framledningsmål','A400C→0748'),(13,'Lägsta tillåtna framledningsmål','A4026→0746')]:add('a57a4',[p],name,'Visa inställd temperaturgräns som används av regleringen.',proof)
for pack,items in {
'a5832':[(1,'Rumstemperatur zon 1','066C'),(3,'Rumstemperatur zon 2','068C'),(8,'Köldmediets vätsketemperatur TH2','063A')],
'a58a2':[(1,'Primär framledning THW1','0662'),(4,'Primär retur THW2','0664'),(7,'Varmvattentemperatur THW5B','0668'),(10,'Varmvattentemperatur THW5A','0666')],
'a591c':[(1,'Framledning zon 1 THW6','067E'),(4,'Retur zon 1 THW7','0680'),(7,'Framledning zon 2 THW8','0682'),(10,'Retur zon 2 THW9','0684')],
'a599a':[(1,'Extern pannas framledning THWB1','067A'),(4,'Extern pannas retur THWB2','067C')],
'a59e4':[(1,'Bufferttankens temperatur THW10','0690'),(4,'Kondenserings-/mättnadstemperatur','0692')],
}.items():
    for p,name,src in items:
        add(pack,[p,p+1],name,'Följa temperaturen för reglering och felsökning. Givargiltighet måste beaktas.',f'Native getter→{src};OCH722A service table;pinned temperature decoder correlation')
        if pack!='a5832':add(pack,[p+2],f'Kompakt givarkanal: {name}','Överföra den tillhörande givarens alternativa bytevärde; inte en extra fysisk givare.',f'A4144→0ACE[index];{pack}')
add('a5832',[10],'Kompakt givarkanal för köldmediet','Alternativ representation för TH2-kanalen.','A4144(1)→0ACF')
add('a5832',[11],'Utetemperatur TH7','Visa temperatur utomhus.','A4088→0686;Process0x0B')
for p,name,src in [(1,'Termostatingång zon 1','051E'),(2,'Termostatingång zon 2','054B'),(3,'Flödesvakt 1','0515'),(4,'Flödesvakt 2','0542'),(5,'Flödesvakt 3','0554'),(6,'Extern ingång IN4','0527'),(7,'Extern ingång IN5','055D')]:add('a5a3e',[p],name,'Visa ingångens tillstånd; konfiguration avgör hur den påverkar driften.',f'A4156..A41B6→{src};8DCAC')
for i in range(6):add('a5a7e',[1+2*i,2+2*i],f'FTC DIP-bank SW{i+1}','Visa hårdvarukonfigurationen; detta är FTC:s brytare, inte Procons adressbrytare.',f'A41C6..A4216→3875..387A;SW6 masked18')
add('a5b08',[1],'Kompressor i drift','Skilja kompressordrift från stopp.','A4244→3A2C')
add('a5b08',[2],'Kompressordrift per källenhet','Visa driftmask för sex enheter.','A4254→3959+12*i')
add('a5b08',[3,4,5],'Samlad kompressordrifttid','Följa drifttid; delarna bildar en gemensam räknare.','A4286→3D8C;A4292→14FC;Process0x13')
for i in range(6):add('a5b08' if i<3 else 'a5b7a',[6+2*(i%3),7+2*(i%3)],f'Drifttid källenhet {i+1}','Jämföra drifttid mellan anslutna enheter.','A42A0→395B+12*(unit−1)')
for p,name,src in [(2,'Eltillskott steg 1','06C5'),(3,'Eltillskott steg 2','06C7'),(4,'Eltillskott extra steg','06C9'),(5,'Varmvattentankens elpatron','06CB')]:add('a5b7a',[p],name,'Visa aktivering av tillskott; inte direkt uppmätt eleffekt.',f'A42D6..A4306→{src};Process0x14')
add('a5b7a',[12],'Primärt vattenflöde','Följa cirkulationen genom värmepumpen.','A4316→322E/100;A3/540')
for p,name,src in [(1,'Primär cirkulationspump i drift','3A34'),(2,'Primärpumpens styrsignal','3A38'),(3,'Primärpumpens återkoppling','3E9D'),(4,'Cirkulationspump 2','06A9'),(5,'Zonpump på OUT3','06AB'),(6,'Trevägsventil 1','3A3B'),(7,'Trevägsventil 2','06B3'),(10,'Shuntventilens steg','06C0'),(11,'Shuntventilens rörelsestatus','06C2')]:add('a5bf8',[p],name,'Visa begärt/rapporterat utgångstillstånd; detta bevisar inte fysisk rotation eller täthet.',f'A4334..A43C8→{src};Process0x15',kind='utgångsstatus')
for p,name,src in [(1,'Varmvattenpump 4','06AD'),(2,'Zonpump på OUT13','06B9'),(3,'Ytterligare zonpumpsutgång','06BB')]:add('a5c62',[p],name,'Visa pumpens utgångsstatus. Fysisk cirkulation kräver separat verifiering.',f'A4BBA/A4BCA/A4BDA→{src};Process0x16',confidence='kodkälla med publik portkorrelation')
for i in range(6):add('a5e76',[1+2*i,2+2*i],f'Felkod från källenhet {i+1}','Identifiera vilken ansluten enhet som rapporterar en avvikelse.','A4544→A4D3C(3952+12*i);C396C',confidence='kodfamilj identifierad; full kodlista saknas')
add('a5efc',[1],'Vattenflöde utanför tillåtet område','Visa resultatet av min-/maxflödesövervakningen.','49B6→D2C00 compares322E with07E8/07E9')
for p,name,proof in [(3,'Systemets på/av-läge','A4570→38BF'),(4,'Aktivt driftläge','A45C0→3CB7'),(5,'Varmvattenläge','A4610→3912'),(6,'Reglerläge zon 1','A464E→3916'),(7,'Reglerläge zon 2','A464E→3918')]:add('a612c',[p],name,'Visa valt/aktivt driftläge; inte samma sak som att kompressorn går.',proof)
for p,name,proof in [(8,'Varmvattenbörvärde','A46B2→3906'),(10,'Framledningsmål zon 1','A46E6→38E8'),(12,'Framledningsmål zon 2','A46E6→3900')]:add('a612c',[p,p+1],name,'Visa temperaturmålet som styr värmeproduktionen.',proof)
for p,name,proof in [(3,'Tvingad varmvattenladdning','A471C→3919'),(4,'Semesterläge','A4750→391B'),(5,'Spärr för varmvatten','A4784→399A bit0'),(6,'Spärr för värme zon 1','A47BA'),(7,'Spärr för kyla zon 1','A47F0'),(8,'Spärr för värme zon 2','A4826'),(9,'Spärr för kyla zon 2','A485C'),(10,'Extern styrnings ägarskap','A4892→39A3'),(11,'Extern styrnings kompletterande status','A48C2→39EC')]:add('a61f2',[p],name,'Visa styr- och spärrlägen som påverkar vilka behov FTC får uppfylla.',proof)
add('a624e',[3],'Värme-/kylval','Skilja vald temperaturfunktion.','A4B8E→3916')
for p,src,z in [(4,'38EA',1),(6,'3902',2)]:add('a624e',[p,p+1],f'Kompletterande temperaturmål zon {z}','Visa den andra målkanalen; exakt relation till valt reglerläge behöver konsumentvillkoren.',f'A46E6→{src}',confidence='namngiven del')
for pack,direction in [('a8e38','Förbrukad'),('a8eb6','Producerad')]:
    add(pack,[1,2,3],'Energipostens datum','Koppla energier till samma period innan de jämförs.','A48F2→496C..496E')
    for p,mode in [(4,'värme'),(7,'kyla'),(10,'varmvatten')]:add(pack,[p,p+1,p+2],f'{direction} energi för {mode}','Jämföra daterade energimängder; kvoten är period-COP, inte momentan COP.','A490E;Process0xA1/A2;P0086 energy trace')
for p,name,purpose in [([1,2],'Servicekod för svaret','Koppla svaret till beställd A3-fråga.'),([3],'Servicevärdets format/status','Avgöra hur svaret ska tolkas och om ett resultat finns.'),([4,5],'Servicefrågans resultat','Läsa värdet enligt den specifika A3-kodens betydelse.')]:add('a8f34',p,name,purpose,'A49FA/A4A28/A4A44→3240/3244/3242',kind='protokoll')

# Settings triples: format + one/two value bytes, not three independent functions.
# SD offsets are category-qualified and documented separately from native certainty.
SETTINGS={
'a629c':('SD_DHW_Pos',[(0,'Legionellakörning tillåten'),(3,'Varmvattenmål'),(6,'Temperaturfall före varmvattenstart'),(9,'Maximal varmvattenkörtid')]),
'a630e':('SD_DHW_Pos',[(12,'Paus mellan varmvattenkörningar'),(15,'Normal/eco-varmvatten'),(18,'Legionellatemperatur'),(21,'Intervall mellan legionellakörningar')]),
'a6376':('SD_DHW_Pos',[(24,'Starttid för legionellakörning'),(27,'Maximal legionellakörtid'),(30,'Temperaturhålltid vid legionellakörning')]),
'a63d4':('SD_HtCl_Pos',[(0,'Reglerläge zon 1'),(3,'Reglerläge zon 2')]),
'a7816':('SD_Hol_Pos',[(0,'Semesterfunktioner'),(3,'Semesterns startdatum'),(6,'Semesterns slutdatum')]),
'a7938':('SD_Is_Pos',[(0,'Displayspråk'),(3,'Temperaturenhet'),(6,'Temperaturvisning')]),
'a79e2':('SD_Is_Pos',[(21,'Tidsformat'),(24,'Fjärrkontrollens zon'),(27,'Rumsgivare zon 1'),(30,'Rumsgivare zon 2')]),
'a7afc':('SD_SV_Pos',[(0,'Kalibrering THW1 framledning'),(3,'Kalibrering THW2 retur'),(6,'Kalibrering THW5 varmvatten'),(9,'Kalibrering THW6 zon 1 framledning')]),
'a7b88':('SD_SV_Pos',[(12,'Kalibrering THW7 zon 1 retur'),(15,'Kalibrering THW8 zon 2 framledning'),(18,'Kalibrering THW9 zon 2 retur'),(21,'Kalibrering THWB1 pannframledning')]),
'a7c6e':('SD_SV_Pos',[(27,'Tillåt ekonomistopp av pump 1'),(30,'Villkor för pumpstopp'),(33,'Frysskyddets framledningsmål'),(36,'Frysskyddets utetemperaturgräns')]),
'a7ce6':('SD_SV_Pos',[(39,'Eltillskott för värme tillåtet'),(42,'Fördröjning före eltillskott värme'),(45,'Eltillskott för varmvatten tillåtet'),(48,'Fördröjning före eltillskott varmvatten')]),
'a7d48':('SD_SV_Pos',[(51,'Shuntens fulla gångtid'),(54,'Intervall mellan shuntkorrigeringar'),(57,'Konfigurerad nivå för primärpump')]),
'a7d9e':('SD_SV_Pos',[(60,'Val av värmekälla'),(63,'Samtidig värme och varmvatten'),(66,'Utetemperatur för samtidig drift'),(69,'Lågtemperaturväxling tillåten')]),
'a7dfe':('SD_SV_Pos',[(72,'Utetemperatur för lågtemperaturväxling'),(75,'Rumsregleringens tidsintervall'),(78,'Lägsta framledningsmål'),(81,'Högsta framledningsmål')]),
'a7e84':('SD_SV_Pos',[(84,'Temperaturhysteres aktiverad'),(87,'Nedre temperaturhysteres'),(90,'Övre temperaturhysteres')]),
'a7ee8':('SD_SV_Pos',[(93,'Värmepumpens beräkningskapacitet'),(96,'Eltillskott 1 kapacitet'),(99,'Eltillskott 2 kapacitet'),(102,'Hybridens prioritering')]),
'a7f52':('SD_SV_Pos',[(105,'Hybridens utetemperaturgräns'),(108,'Pannans verkningsgrad'),(111,'Pannbränslets pris'),(117,'Elens CO2-faktor')]),
'a7fca':('SD_SV_Pos',[(123,'Pannbränslets CO2-faktor')]),
'a8290':('SD_SV_Pos',[(231,'Varmvattenpatronens beräkningskapacitet'),(234,'Elmätarens pulsfaktor'),(237,'Värmemätarens pulsfaktor'),(240,'Pump 1 beräkningsbidrag')]),
'a830c':('SD_SV_Pos',[(243,'Pump 2 beräkningsbidrag'),(246,'Pump 3 beräkningsbidrag'),(249,'Korrigering av producerad energi'),(252,'Flödesgivarens nedre skalpunkt')]),
'a8378':('SD_SV_Pos',[(255,'Flödesgivarens övre skalpunkt'),(258,'Varmvattentillskott'),(261,'Normal/snabb rumsreglering')]),
'a8a20':('SD_SV2_Pos',[(315,'Golvtorkning start-/sluttemperatur'),(318,'Golvtorkning maxtemperatur'),(321,'Golvtorkning hålltid'),(324,'Golvtorkning uppsteg')]),
'a8a90':('SD_SV2_Pos',[(327,'Golvtorkning hålltid uppåt'),(330,'Golvtorkning nedsteg'),(333,'Golvtorkning hålltid nedåt'),(336,'Funktionsval för IN4 och IN5')]),
'a8afe':('SD_SV2_Pos',[(339,'Smart-grid temperaturbidrag varmvatten'),(342,'Smart-grid temperaturbidrag värme'),(345,'Termo-ON-utgångens val'),(348,'Startgivare för varmvattenåterladdning')]),
'a8b6c':('SD_SV2_Pos',[(351,'Variabel flödesstyrning'),(354,'Analog 0–10 V-styrning'),(357,'Analogstyrningens intervall'),(360,'Analogstyrningens effektparameter')]),
'a8bcc':('SD_SV2_Pos',[(363,'Pump 4 beräkningsbidrag'),(366,'Värmepumpskretsens pumpnivå'),(369,'Analogstyrningens prioritet'),(372,'Värmepumpens minflöde')]),
'a8c24':('SD_SV2_Pos',[(375,'Värmepumpens maxflöde'),(378,'Hybridens temperaturhysteres'),(381,'Buffertgivarens kalibrering'),(384,'Smart-grid-reglering för värme')]),
'a8c92':('SD_SV2_Pos',[(387,'Värmemål vid rekommenderad smart-grid-drift'),(390,'Värmemål vid tvingad smart-grid-drift'),(393,'Kylmål vid rekommenderad smart-grid-drift'),(396,'Kylmål vid tvingad smart-grid-drift')]),
'a8d1e':('SD_SV2_Pos',[(399,'Periodisk pumpdrift under värme'),(402,'Periodisk pumpdrift under kyla'),(405,'Pumpcykelns intervall'),(408,'Smart-grid-reglering för kyla')]),
'a8d78':('SD_SV2_Pos',[(411,'Begränsning av eltillskottets kapacitet'),(414,'Sommarläge tillåtet'),(417,'Sommarlägets temperaturgränser'),(420,'Sommarlägets tidsgränser')]),
'a8dda':('SD_SV2_Pos',[(423,'Sommarlägets tvångsstarttemperatur'),(426,'Tyst drift tillåten'),(429,'Tyst drift start-/sluttid'),(432,'Tyst drift nivå')]),
}
for pack,(enum,fields) in SETTINGS.items():
    for i,(offset,name) in enumerate(fields):
        add(pack,range(2+3*i,5+3*i),name,'Läsa konfigurationen för '+name.lower()+'. Formatbyte och värde hör ihop; inte tre mätningar.',f'{pack.upper()}; category-qualified {enum} offset{offset};SD Tool ReadSER/ReadDHW/ReadINIT;native import/export',confidence='SD-formatkorrelation; fysisk tillämpning ej provad',kind='inställning')
for start,offset,name in [(2,24,'Kalibrering THWB2 pannretur'),(11,264,'Kalibrering THW5A övre varmvatten')]:add('a7c14',range(start,start+3),name,'Korrigera givarens temperaturbidrag.',f'A7C14→077B/072D;SD_SV_Pos offset{offset}',confidence='SD-formatkorrelation',kind='inställning')
for pack,offset in [('a8008',0),('a80a0',6),('a8184',0),('a821c',6)]:
    cop=pack in ('a8008','a80a0')
    add(pack,[2],'Format för tabellvärden','Tolka de efterföljande värdena med samma format.',f'{pack}:shared format byte',kind='protokoll')
    for i in range(6 if pack!='a821c' else 4):
        name=f'Konfigurerad COP-punkt {i+offset+1}' if cop else f'Elpris {i+offset+1}'
        add(pack,[3+2*i,4+2*i],name,'Underlag för val av värmekälla; inte uppmätt live-COP.' if cop else 'Underlag för hybridens kostnadsjämförelse.',f'{pack};SD_SV_Pos offset{129+3*(i+offset) if cop else 171+6*(i+offset)};C3050/C34F8',confidence='SD-format och native konsument',kind='inställning')
for pack,positions,name,proof in [
('a77b8',[2,3,4],'Årsperiod för veckoprogram 2','SD_Sch_Pos105'),
('a8138',[2,3,4],'Period för elprissäsong 2','SD_SV_Pos165'),
('a8138',[5,6,7],'Period för elprissäsong 3','SD_SV_Pos168'),
('a7984',range(2,11),'Kontakttelefon på manöverpanelen','SD_Is_Pos9..18'),
('a7a3a',range(4,14),'Tidsstyrt rumsgivarval för vald zon','SD_Is_Pos33..60'),
('a653e',range(4,10),'Värmekurvans tre punkter för vald zon','SD_HtCl_Pos21/24/27 or39/42/45'),
('a7874',range(4,12),'Semesterbörvärden för vald zon','SD_Hol_Pos9..27'),
('a6642',range(4,15),'Veckoprogrammets valda tidsblock','A65CC:bank/day/slot indexing'),
('a8402',range(4,15),'Elprisschemats valda tidsblock','A83BE:3 seasons*7 days;SD ReadSER2'),
]:add(pack,positions,name,'Läsa schemats eller inställningens innehåll; delbytes måste tolkas tillsammans.',f'{pack};{proof};sd-tool-correlation.md',confidence='strukturell korrelation; delkodning begränsad',kind='inställning')
for pack in ('a6426','a653e','a7874','a7a3a'):
    add(pack,[3],'Vald zon','Ange vilken zon inställningssvaret gäller.',f'{pack}→234B;A6410',kind='protokoll')
    add(pack,[2],'Format för zoninställningen','Tolka efterföljande inställningsvärden.',f'{pack} writes2360',kind='protokoll')
for p,name in [(5,'Rumsbörvärde värme'),(7,'Fast framledningsmål värme'),(9,'Värmekurvans temperaturmål'),(11,'Rumsbörvärde kyla'),(13,'Fast framledningsmål kyla')]:add('a6426',[p],name,'Visa börvärdet för den valda zonen och reglerformen.','A6426→38DC..38E4 or38EE..38F6;C979E;SD_HtCl_Pos',kind='inställning')
for pack,positions,proof in [('a5724',[1,2],'A3E84/A3E8E'),('a5b7a',[13],'A432A'),('a5bf8',[12,13],'A43FC/A4406'),('a5f1a',range(1,15),'A4CD2'),('a5f8c',range(1,14),'A4CD2'),('a5ff6',range(1,15),'A4CD2'),('a6068',range(1,13),'A4CD2'),('a61b2',range(3,9),'A4CD2')]:add(pack,positions,'Reserverat nollfält','Ger alltid noll i referensfirmwaren. Inget mätvärde och ingen dold brinetemperatur i denna implementation.',f'{pack}→{proof};native constant-return helper',confidence='native konstantretur',kind='protokoll')
add('a8ff8',[1],'Fast FF-svar på CC-frågan','Avsluta CC-svaret; överordnad protokollavsikt är fortfarande okänd.','A4ADE returnsFF',confidence='native konstantretur',kind='protokoll')
add('a8f74',[1],'Godkännande av inställningssession','Rapportera om överföringssessionen accepteras.','CF9C4;C8 session lifecycle',kind='protokoll')
add('a6642',[3],'Val av veckoprogram','Ange programbanken som svarsdatan hör till.','234B→A65CC',kind='protokoll')
add('a8402',[3],'Val av elprissäsong och veckodag','Ange vilket schemablock som efterfrågas.','234B→A83BE',kind='protokoll')
# The second selector in56 is protocol metadata, not schedule content.
for g in GROUPS:
    if g['packer']=='a6642' and g['name']=='Veckoprogrammets valda tidsblock':g['positions'].remove(4)
add('a6642',[4],'Val av dag/tidsblock','Välja del av veckoprogrammet tillsammans med första väljaren.','234C→A65CC',kind='protokoll')
add('a57a4',[5,6],'Aktivt temperaturmål zon 1','Visa målet som valts för zonens värme-/kylreglering. Kan vara rums- eller framledningsmål beroende på reglerläge.','A3F98→3908/390A;97D48;BA9FC/BAB56;A2A68')
add('a57a4',[7,8],'Aktivt temperaturmål zon 2','Visa zonens aktuella målkanal beroende på reglerläge.','A3FBC→3910/391C;BA9FC/BA03C;A2AB2',confidence='målkanal identifierad; lägesdetaljer begränsade')
add('a57a4',[9,10],'Legionellacykelns temperaturmål','Visa den särskilda temperaturreferensen för legionellakörning.','A3FE0→390E;97D48/BBAC8 copy071A;SD_DHW_Pos18')
add('a5628',[5],'Effektbegränsningens rapporterade nivå','Visa den mest begränsande effektgränsen, inte producerad kW.','AC9A8:min(100,0600,3933,3934)→05FE;A3D18→8929D lookup',confidence='begränsningskedja följd; exakt tabellenhet öppen')
add('a5540',[9],'Cykel-/temperaturhysteresens tillstånd zon 1','Följa zonens särskilda reglergren vid återkommande värmestarter.','A3C62→C7A00→4912;C795A/C701C;P0087 continuation',confidence='reglergren följd; aktivering på Geodan ej provad')
add('a5540',[10],'Cykel-/temperaturhysteresens tillstånd zon 2','Följa samma reglergren för den andra zonen.','A3C62→C7A00→4912;C795A/C701C;P0087 continuation',confidence='reglergren följd; aktivering på Geodan ej provad')
add('a5b7a',[1],'Extern panna aktiverad','Visa pannstyrningens utgångstillstånd efter drift- och skyddsvillkor.','A42C6→06CF;C163A:heating phase8/source4;3F79/3F86 inhibits',confidence='native utgångskedja')
for pack,positions,name,proof in [
('a5628',[11,12,13],'Beräknad värmekostnad för panna','A3E0C(0)→262C/262E←265C/265E;C371C;C34F8 uses07C7/075A;SD111/108'),
('a56a4',[1,2,3],'Beräknad värmekostnad för värmepump','A3E0C(1)→2630/2632←2640/2642;C34F8 electricity price/COP selection'),
('a56a4',[4,5,6],'Beräknat CO2-bidrag för panna','A3E34(0)→2634/2636←2670/2672;C34F8 uses076D/075A;SD123/108'),
('a56a4',[7,8,9],'Beräknat CO2-bidrag för värmepump','A3E34(1)→2638/263A←2644/2646;C34F8 electricity factor/COP selection'),
('a56a4',[10,11,12],'Aktivt elpris för hybridberäkning','A3E5C(0)→263C/263E←26A0/26A2;C34F8 selects price1..10'),
]:add(pack,positions,name,'Jämföra värmekällor utifrån konfiguration. Inte mätvärde eller live-COP; enhet och skalning måste hållas separata.',proof,confidence='native källkedja + SD-faktornamn')
add('a54f8',[4],'Eltillskottets drift och eftergång','Visa om eltillskott är aktivt eller nyligen har varit aktivt; skiljer direkt drift från eftergång.','descriptor81850→823CA→99620/996AE:06C5/06C7/06C9/06D1;3D28;timer36DE',confidence='indirekt tillståndsproducent följd')
add('a54f8',[6],'Extern pannas drift och eftergång','Visa om pannutgångarna är aktiva eller befinner sig i eftergång.','descriptor8186A→86D22→C14E0/C155C:06CF/06CD;3F6C;timer36E4',confidence='indirekt tillståndsproducent följd')
add('a5540',[12],'Valda källenheter för drift','Visa vilka av upp till sex källenheter som har valts för att täcka behovet.','C0DD0 selects up to3944 units using25F4 ordering and399E availability;3937[]→C0BBC→393D',confidence='native urvalskedja')
add('a55c2',[8],'Bestående temperaturavvikelse utan frekvensändring','Skilja kvarstående positiv eller negativ temperaturavvikelse när kompressorns Hz ligger still. Hjälp för analys av reglerrespons, inte bevis på maximal effekt.','descriptor819A2→87298;C8388→C83F6/C8478 checks3947>=200 or<=−100, unchanged062C,not defrost,timers;C84FA→4925',confidence='indirekt producent och villkor följda')
add('a5bf8',[8],'Shuntmotor: aktiveringsutgång OUT5A','Tillsammans med OUT5B: 00/01 stopp,10 öppna,11 stäng. Rapporterar utgång, inte mekanisk position.','A439C→C4B32(0);A3/175 at8C5AB→bit4;OCH722A output175/553 table',confidence='native bitkoppling och servicemanual',kind='utgångsstatus')
add('a5bf8',[9],'Shuntmotor: riktningsutgång OUT5B','Tillsammans med OUT5A: 00/01 stopp,10 öppna,11 stäng. Rapporterar utgång, inte mekanisk position.','A43AC→C4B32(1);A3/175 at8C5B8→bit5;OCH722A output175/553 table',confidence='native bitkoppling och servicemanual',kind='utgångsstatus')
add('a8f8a',[6],'FTC-generationens identifierare','Används av klienten för att välja kompatibel funktionalitet.','A4AA4(1) returns3;pinned Process0xC9 reads FTCVersion at6',confidence='native fält + publik klientkorrelation',kind='identifikation')
add('a8f8a',[8],'Förbrukningsberäkning konfigurerad','Visa att förbrukningsberäkningens lägesval inte är noll; skilj från GET07:s striktare värden1/2.','A4AA4(3):099B!=0;native assembly',confidence='native källa',kind='status')
