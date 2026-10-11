"""P0089: presentation names only; never upgrade semantic confidence."""
ROUTES = {
'41.32':'Ställ driftläge och temperaturmål',
'41.34':'Ställ driftspärrar och extern styrning',
'41.35':'Ställ zonernas temperaturmål',
'41.c8':'Styr inställningsöverföring',
'42.01':'Läs styrenhetens tid',
'42.02':'Läs avfrostnings- och termostatstatus',
'42.03':'Läs fel och zonstatus',
'42.04':'Läs kompressorfrekvens och enhetsstatus',
'42.05':'Läs värmekälla och varmvattenstatus',
'42.07':'Läs effekt och förbrukningsräknare',
'42.09':'Läs temperaturmål och gränser',
'42.0b':'Läs rumstemperaturer och valda givare',
'42.0c':'Läs primärkretsens och varmvattnets temperaturer',
'42.0d':'Läs zonernas framledning och retur',
'42.0e':'Läs pannans framledning och retur',
'42.0f':'Läs extra temperaturgivare',
'42.10':'Läs termostaternas värmebehov',
'42.11':'Läs DIP-konfiguration',
'42.13':'Läs kompressordrift och drifttid',
'42.14':'Läs ingångar, tillskott och vattenflöde',
'42.15':'Läs pump- och ventilstatus',
'42.16':'Läs extra pumpars status',
'42.17':'Läs givarfel, övertemperatur och frysrisk',
'42.18':'Läs temperaturrespons och cirkulationsfel',
'42.26':'Läs driftlägen och temperaturmål',
'42.28':'Läs driftspärrar och extern styrstatus',
'42.29':'Läs värme-/kylläge och zonmål',
'42.a1':'Läs förbrukad energi',
'42.a2':'Läs producerad energi',
'42.a3':'Beställ och läs serviceresultat',
'42.c8':'Läs inställningssessionens status',
'frame.5b':'Läs styrenhetsinformation',
'41.33':'Kvittera SET33',
'frame.02.00':'Avsluta session och svara med information',
'frame.02.01':'Kvittera alternativ ram 02',
'frame.5c':'Besvara ansluten CC-fråga',
'frame.5d':'Kvittera ansluten CC-ram',
}
for op in ('1c','1d','1e','1f','27'):
    ROUTES['42.'+op]='Läs nollfyllt svar '+op.upper()

SERVICES = {160:'Läs modellprofil',161:'Läs hårdvaruvariant',350:'Nollställ serviceval'}
for code in range(351,358):
    SERVICES[code]=f'Välj serviceläge {code-350}'
for code,field,value in [(358,'39FF',1),(359,'39FF',2),(360,'3A00',1),(361,'3A00',2),(362,'3A01',1),(363,'3A01',2)]:
    SERVICES[code]=f'Sätt serviceval {field} till {value}'
SERVICES[350]='Återställ källsidans serviceläge'
SERVICES[351]='Pump-down-val (SUZ; Geodan obekräftat)'
ROUTES['42.10']='Läs termostater, flödesvakter och externa ingångar'
