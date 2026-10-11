"""P0089: purpose traced through fault descriptors, not inferred from byte position."""
# opcode, payload position, state pointer, name, user purpose, terminal evidence
ROWS = [
('17',1,'3ed6','Övertemperatur i primärkretsen','Upptäcka att framledning eller retur blir för varm.','B7CEE→B7E76: valid0662/0664>=8000, timed'),
('17',2,'3ed8','Övertemperatur i varmvattentanken','Upptäcka för hög temperatur i varmvattnet.','B7FD4→B812E:0668>=7500, timed'),
('17',3,'3e8a','Fel på primär framledningsgivare','Visa när framledningstemperaturen inte kan användas som tillförlitligt mätvärde.','B1602→B1730:0A80;8DDD0→0658;986E2→0662'),
('17',4,'3e8c','Fel på primär returgivare','Visa när returtemperaturen inte kan användas som tillförlitligt mätvärde.','B17A0→B18CE:0A81;8DDD0→065A;98702→0664'),
('17',5,'3e8e','Fel på varmvattengivare THW5B','Upptäcka bortfall eller fel i den nedre varmvattengivarens kanal.','B193E→B1A6C:0A83;8DDD0→065E;98762→0668'),
('17',6,'4945','Fel på framledningsgivare zon 1','Kontrollera att zon 1 har ett användbart framledningsvärde.','CA5EC→CA71A:0A84;8DDD0→0672;A3/509→067E'),
('17',7,'4947','Fel på returgivare zon 1','Kontrollera att zon 1 har ett användbart returvärde.','CA78A→CA8B8:0A85;8DDD0→0674;987AE→0680;A3/512'),
('17',8,'4949','Fel på framledningsgivare zon 2','Kontrollera att zon 2 har ett användbart framledningsvärde.','CA928→CAA56:0A87;8DDD0→0676;987CE→0682;A3/513'),
('17',9,'494b','Fel på returgivare zon 2','Kontrollera att zon 2 har ett användbart returvärde.','CAAC6→CABF4:0A88;8DDD0→0678;987EE→0684;A3/514'),
('17',10,'3eeb','Frysrisk i primärkretsen','Upptäcka farligt låg vattentemperatur i framledning eller retur.','B8C6C→B8E14: valid0662<=100 or0664<=300, timed'),
('17',13,'4994','Fel på varmvattengivare THW5A','Övervaka den övre varmvattengivaren; felet används också när temperaturkälla väljs.','D1486→D15B8:0A82;8DDD0→065C;98762 checks4994 for666/668 selection'),
('18',1,'3edd','Orimlig temperaturrespons i primärkretsen','Upptäcka utebliven temperaturökning under värmeproduktion tillsammans med orimligt förhållande mellan framledning och retur.','B845A→B85E6/B85AE:0662/0668 increase<=100 and0662-0664<-500; mode gates'),
('18',2,'494d','Omvänt temperaturförhållande i zon 1','Upptäcka att zonens retur är mer än 5 grader varmare än framledningen under övervakad drift.','CAC6C→CADF4/CADE4: valid067E-0680<-500 after delay'),
('18',3,'4950','Omvänt temperaturförhållande i zon 2','Upptäcka att zonens retur är mer än 5 grader varmare än framledningen under övervakad drift.','CAF32→CB0A4/CB094: valid0682-0684<-500 after delay'),
('18',4,'3ed2','Otillräckligt primärflöde','Upptäcka för liten vattencirkulation via flödesvakt eller flödesmätare.','B79D6→B7BAA→A2F6C:069C or322E<500 or322E<07CA*100 when enabled'),
('18',8,'3eda','Fel på köldmediets vätsketemperaturgivare','Kontrollera att köldmediets temperaturkanal ger ett användbart värde.','B822A→B8360:0A7F;8DDD0→063A/0642;A3/505'),
('18',9,'4919','För kallt under övervakad drift eller avfrostning','Upptäcka låga köldmedie-/vattentemperaturer i särskilda driftlägen.','C7B28→C7CC0: mode0B timer>359 and063A<-499; or3D07=2,0664<1501,063A<-1599'),
('18',10,'3f84','Övertemperatur vid extern panna','Upptäcka för hög temperatur på pannans framledning.','C22C2→C23D4: valid067A>=8000, timed;A3/515'),
('18',11,'3f80','Fel på pannans framledningsgivare','Kontrollera att den externa pannans framledningstemperatur är användbar.','C1F98→C20C8:0A89;8DDD0→066E;9880E→067A;A3/515'),
('18',12,'3f82','Fel på delad panna-/buffertgivarkanal','Visa fel i givarkanalen som konfigurationen använder för pannretur eller bufferttank.','C2150→C2282:0A8B;8DDD0→0670/068E;9882E/9884E→067C/0690'),
('19',1,'3f79','För låg framledning i zon 1 under särskild drift','Upptäcka att zon 1 förblir under 25 grader när det övervakade driftläget kräver uppvärmning.','C1A70→C1BE6: valid067E<2500 with timed mode-specific gates'),
('19',2,'3f86','Frysrisk vid extern panna','Upptäcka mycket låg temperatur på pannans framledning efter startvillkor och väntetider.','C24A6→C2634: valid067A<=100, timers3DCE/3DD4>600 and other gates'),
('19',3,'492e','Oförenlig värmekällekonfiguration','Upptäcka kombinationer av värmekälla, tillgängliga enheter och systemval som inte stöds.','C914C→C91A6/C91EC/C9204: source selection0720, unit masks399E/399F, configuration06D4/06D5'),
('19',6,'491c','Samlad avvikelse från anslutna källenheter','Visa om någon vald källenhet har den avvikelse som rapporteras i enheternas sammanfattande statusmask.','C7D6E:399E &39A1 &3F; exact peer fault category unresolved'),
('19',7,'495a','Misslyckad varmvatten-/växlingssekvens','Upptäcka utebliven tankuppvärmning eller för hög primärtemperatur under särskilda varmvattensekvenser.','CCCCE→CCD16→CCD9A/CCDD4/CCE58/CCEB2: modes9/10, event count,0668 and0662/0664; precise actuator diagnosis unresolved'),
]
ROWS += [
('18',5,'3f7c','Utlöst flödesvakt 2','Upptäcka utebliven cirkulation på kretsen som övervakas av flödesvakt 2.','C1CC8→C1E96:069F;8DCAC:0542 with DIP polarity;A3/569 fault selector'),
('18',6,'490d','Utlöst flödesvakt 3','Upptäcka utebliven cirkulation på kretsen som övervakas av flödesvakt 3.','C6BA8→C6D7C:06A1;8DCAC:0554 with DIP polarity;A3/569 fault selector'),
('18',7,'3e84/4953','Fel på någon av zonernas rumsgivare','Visa om rumstemperaturen för zon 1 eller zon 2 inte går att lita på.','A4446 combines3E84/4953;B1180→B12B8:0828;CB1F6→CB32C:0829;AE2CC maps1/8 to manual567 TH1A/TH1B'),
('19',8,'4974','Fel på vattenflödesmätarens givarkanal','Skilja ett fel på själva flödesgivaren från ett giltigt men för lågt vattenflöde.','CE730→CE86A:0A86;CE422 uses same fault flag to qualify322E flow calculation'),
]
ROWS += [
('19',4,'3f17','Kommunikationsövervakning av rumsgivarmottagaren','Upptäcka att giltig kommunikation från rumsgivarmottagaren uteblir under för lång tid.','BFB6E/BFBE6: timer3BD6 reset by3F21 or39E7;C06DC sets3F21 from UART6 accepted reception;C1056 provides temporary grace'),
('19',5,'3f18/3f19/3f1a/3f1b/3f1c/3f1d/3f1e/3f1f','Spärrad rumsreglering per rumskanal','Visa vilka av de åtta rumskanalerna som rapporterar status som hindrar rumsreglering.','A4482→fault callbacks→39E6;8F75E←C025E;A2BA0/A2BC0 select room bit;BE2CC/BE43E/BEE16/BEF6C require bit clear; exact radio cause unknown'),
]
PACKERS={'17':'a5c86','18':'a5d3a','19':'a5df6'}
PURPOSES={(PACKERS[op],pos):dict(opcode=op,position=pos,state_pointer=ptr,name=name,purpose=purpose,evidence=proof,
    confidence='namngiven del' if (op,pos) in [('18',9),('19',1),('19',3),('19',4),('19',5),('19',6),('19',7)] else 'native villkor följt',
    limitation='Övervakningsstatus, inte mätvärde. Tids- och aktiveringsvillkor gäller; inget liveprov. Ingen slutsats om fysisk felorsak från denna signal ensam.')
    for op,pos,ptr,name,purpose,proof in ROWS}
