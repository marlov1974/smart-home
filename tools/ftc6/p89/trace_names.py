"""P0089 bounded producer/consumer audit for every previously unnamed route.

Reads existing private exports. Operand mentions include immediate constants and
indexed aliases; they are candidate references, never automatic semantic proof.
"""
import argparse, hashlib, json, re
from collections import defaultdict
from pathlib import Path
import overview

OPS = '57 59 5c 5d 5e 5f 6a 6e 73 75 76 7d 7e'.split()
OTHER = ['41.33','42.06','42.19','42.1a','42.1b','42.20','frame.02.00','frame.02.01','frame.5c','frame.5d']
BOUNDARIES = {
'57':'Tre stagingbytes1FA9..1FAB. D-utökad väljare500 når samma triple. Ingen namngiven aktiv konsument hittad; schemadatum är ännu bara en hypotes.',
'59':'Staging1940..1948 delas mellan kategorier. Semesterfamilj är kandidat, men kategori4-importBD20E börjar vid194A. De observerade DHW/zon-konsumenterna har kategori1/2 och kan inte användas som bevis för59 i kategori4.',
'5c':'Staging1940..1948. Samma bytes används för DHW/zonlägen under andra kategorier. Ingen betydelse som grundinställningar kan fastställas genom adresslikheten.',
'5d':'Staging1949..1954. Temperatur-/DHW-konsumenterna är kategori1/2/4; avsedd kategori5-betydelse är inte visad.',
'5e':'Staging1955..1960. Kategori5-importBD28E kopierar195A→076F;076F har bara direktreferenser i import/persistens i exporten. UI-/peerbetydelsen saknas.',
'5f':'Zonvalt staging1961..197E. B984A läser flera av dessa bytes men endast i kategori2. Det ger inte namn åt kategori5-innehållet.',
'6a':'Konsumentkedja till temperaturgränsC2B96 och jämförelseberäkningC34F8; namngivna delar, individuella kostnads-/CO2-faktorer kvarstår.',
'6e':'Två stagingtriplar19E5..19EA; D-väljare601/602. Ingen lokal aktiv konsument hittad; frånvaro av direkta referenser utesluter inte indirekt peeranvändning.',
'73':'07CB→CE554→CE422→322E identifierar flödessensorns övre skalpunkt.07D2 påverkar BB160:s temperaturrespons.07C9 påverkar BF8A6:s tillskottsvillkor.',
'75':'Fyra stagingtriplar1C7B..1C86; D-väljare801..804. Inga direkta aktiva konsumenter hittade i exporten.',
'76':'0750/0751→8DCAC byter hur externa styrsignaler förs vidare. Tre återstående triplar1C87..1C8F motsvarar D805..807 och saknar namngiven konsument.',
'7d':'07FC och staging1CDE..1CE6. D-väljare10..12;07FC syns i persistens/import men ingen direkt aktiv konsument. Sommarstyrning är inte bevisad.',
'7e':'Staging1CE7..1CF2; D-väljare13..16. Ingen namngiven aktiv konsument hittad. Anslutningen till7D ger inte i sig ett funktionsnamn.',
'41.33':'Intern händelse2 och generiskt svarA5430. Ingen verksam konsument bevisad i befintlig avgränsad händelsesökning; får inte döpas till en styrfunktion utan belägg.',
'42.06':'C371C kopierar C34F8-resultat till packarens källor; C2E60/C2F48 använder jämförelsetalen. Namngiven beräkningsfamilj, inga uppmätta watt påstås.',
'42.19':'C163A/C16C2 och BF66C binder delar av fälten till övervakning/spärrar. Några statusplatser saknar identifierad producent.',
'42.1a':'8D9AA fyller sex separata poster från D-vägen. A4544 läser kodfältet; C396C konsumerar samma poster. Enhetsspecifika tillståndskoder, inte sex temperaturer.',
'42.1b':'A5EFC läser49B6 viaA4410. Den befintliga instruction-exporten innehåller ingen annan direkt referens till49B6. Indirekta skrivningar är inte uteslutna.',
'42.20':'A9080/A906A nollställer svaret; A60CC skriver bara huvud/längd/kod. Därmed tom datafunktion i denna image.',
'frame.02.00':'Descriptor13→intern95→CF518 avslutar session2372; CE920 behandlar95 i timeoutvillkoret; A901E lämnar konstant informationssvar.',
'frame.02.01':'Descriptor14→intern96, A51E2 accepterar nollparameter, A9056 lämnar nollkvittens. Ingen särskild funktion hos96 bevisad utöver protokollkvittensen.',
'frame.5c':'Descriptor11→intern93; A5172 kräver anslutning ochCC; A8FF8/A4ADE svararCC FF. Innehållets avsedda funktion saknar belägg.',
'frame.5d':'Descriptor12→intern94; A519C kräver anslutning ochCC; A900E svararCC. Ingen särskild verksam konsument bevisad; inte ett bevis för generell effektfrihet.',
}
from sd_names import ROWS as SD_ROWS
for _op, (_name, _enum, _offsets, _packer, _status) in SD_ROWS.items():
    if _op in BOUNDARIES:
        BOUNDARIES[_op] += ' Senare SD-korrelation: '+_name+'; '+_enum+' offset '+str(_offsets)+'. Se sd-tool-correlation.md; tidigare stopp är inte längre slutläget.'
BOUNDARIES['42.1b'] = 'Indirekt producent funnen:85702 rad7 pekar på49B6 och callbacktabell882FC. ACB52 skriver callbackresultatet. D2C00 jämför primärflödet322E med min/max07E8/07E9; D2D5A returnerar status. Namn: övervakning av tillåtet vattenflöde. Se fault1b-trace.md.'

ROOTS = '8dcac 8d9aa a4410 a4544 a4f68 a4fe0 a51c6 a51e2 a5250 a5172 a519c a535e a53d6 a5430 a901e a9056 a9080 a9090 a906a a8ff8 a900e a4ade ce920 cf518 ce422 ce554 bb160 bf8a6 b984a bb9dc bbbea bbfca bd20e bd28e c371c c34f8 c2e60 c2f48 c396c c163a c16c2 bf66c'.split()

def build(private):
    image=(private.parent.parent/'P0082/private/ftc6.bin').read_bytes()
    expected='d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a'
    if hashlib.sha256(image).hexdigest()!=expected:raise ValueError('wrong image')
    listing=private/'pump-timing-first/instructions.tsv'
    owners=defaultdict(list); mentions=defaultdict(set)
    for line in listing.read_text().splitlines():
        addr,ins,owner=line.split('\t'); owner=owner.removeprefix('ram:000')
        owners[owner].append(line)
        for match in re.finditer(r'0x([0-9a-f]+)',ins):mentions[int(match[1],16)].add(owner)
    prior=json.loads((overview.P88/'command-port-matrix.json').read_text())
    routes={r['id']:r for r in prior['rows']}
    current={r['id']:r for r in overview.build()['rows']}
    result=[]
    roots=set(ROOTS)
    for key in OPS+OTHER:
        rid='uart2.'+('42.'+key if key in OPS else key)
        src=routes[rid]; roots.update(src['handlers'])
        fields=set()
        for fn in src['handlers']:
            path=private/'catalog'/f'{fn}.c'
            if path.exists():
                fields.update(int(m,16) for m in re.findall(r'(?:near_|Near)([0-9a-f]{4})',path.read_text()))
        fields={n for n in fields if n<0x2340 or n>=0x2600}
        result.append(dict(id=rid,paired_set=('uart2.41.'+key if key in OPS else None),
            name=current[rid]['name'],status=current[rid]['status'],boundary=BOUNDARIES[key],
            candidate_operand_mentions={f'{n:04x}':sorted(mentions[n]) for n in sorted(fields)}))
    hashes={}
    for root in sorted(roots):
        if not owners[root]:raise ValueError('missing root '+root)
        hashes[root]=hashlib.sha256(('\n'.join(owners[root])+'\n').encode()).hexdigest()
    return dict(image_sha256=expected,listing_sha256=hashlib.sha256(listing.read_bytes()).hexdigest(),
        scope='All 13 previously unnamed setting pairs and 10 other routes; existing bounded export, no universal absence proof',
        warning='Operand mentions are search candidates, not typed references. Indexed references and category aliases require separate interpretation.',
        roots=hashes,rows=result,physical_tests=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('private',type=Path);args=p.parse_args()
    data=build(args.private)
    (overview.OUT/'function-traces.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    lines=['# P0089 — återstående kommandon följda till konsument eller belagd gräns','',
           'Alla 23 tidigare luckor har granskats. Ett ändläge utan funktionsnamn är fortfarande öppet, inte ett färdigt namn. Läs/skrivparet redovisas tillsammans. Inga enheter kontaktade.','',
           '| Kommando | Kedjans ändläge |','|---|---|']
    lines += [f"| {r['id'].removeprefix('uart2.')} | {r['boundary']} |" for r in data['rows']]
    lines += ['', 'Direkta operandträffar och hash för granskade assemblyrötter finns i JSON. Sökningen är inte en fullständig analys av alla indirekta skrivningar. P88-underlaget är oförändrat.','']
    (overview.OUT/'function-traces.md').write_text('\n'.join(lines))
    print(f"{len(data['rows'])} gaps traced; {len(data['roots'])} assembly roots")
