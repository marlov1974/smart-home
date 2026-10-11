"""P0089 names for the bounded CN105 inventory, including raw field occurrences."""
import json
from collections import Counter
import overview
from purpose_fields import PURPOSES

FIELD_NAMES = {
'command':'Kommandokod', 'constant zero':'Konstant nollvärde',
'direction':'Överföringsriktning', 'action':'Sessionsåtgärd',
'category mask':'Kategorimask', 'category on following settings block':'Kategori för nästa inställningsblock',
'consumed power':'Förbrukad effekt', 'produced power':'Producerad effekt',
'increasing consumed counter':'Ackumulerad förbrukningsräknare',
'configured DHW pump level':'Inställd pumpnivå för varmvatten',
'configured heating pump level':'Inställd pumpnivå för värme',
'selector':'Servicekod', 'echo selector':'Återgiven servicekod',
'format':'Resultatformat', 'value':'Servicevärde',
'CC marker':'CC-markör', 'constant FF':'Konstant FF-värde',
}

def build():
    data=overview.build()
    atlas=json.loads((overview.P88/'command-atlas.json').read_text())
    extra=json.loads((overview.OUT/'field-purpose-audit.json').read_text())['bindings']
    fields=[]
    for row in atlas['rows']:
        if row['path']!='uart2':continue
        for direction in ('rx_fields','tx_fields'):
            for index,field in enumerate(row[direction]):
                original=field['name']
                raw=original=='unresolved response byte'
                if raw:
                    # Position labels identify a byte; they make no semantic claim.
                    response=row['id'].split('.')[2]
                    name=f'Svar {int(response)} – databyte {field["position"]}'
                else:
                    name=FIELD_NAMES[original]  # Fail closed if inventory gains a new kind.
                purpose = next((PURPOSES[(h,field['position'])] for h in row['handler'] if (h,field['position']) in PURPOSES), None) if direction=='tx_fields' else None
                if not purpose and direction=='tx_fields':
                    purpose=next((extra[f'{h}:{field["position"]}'] for h in row['handler'] if f'{h}:{field["position"]}' in extra),None)
                if purpose:
                    name = purpose['name']
                fields.append(dict(purpose_trace=purpose, id=f'{row["id"]}/{direction}/{index}',
                    name=name, name_kind=('protokollroll belagd' if purpose.get('kind')=='protokoll' else 'syfte med SD-korrelation' if 'SD' in purpose['confidence'] else 'syfte med källkorrelation' if 'korrelation' in purpose['confidence'] or 'strukturell' in purpose['confidence'] else 'syfte följt i kod') if purpose else 'tekniskt positionsnamn' if raw else 'befintlig fältroll',
                    semantic_status=purpose['confidence'] if purpose else 'Fysisk betydelse okänd' if raw else row['semantic_confidence'],
                    source_row=row['id'], direction=direction, original_field=field,
                    evidence=row['evidence'], handlers=row['handler']))
    return dict(scope='P0089:142 CN105 routes,159 A3 entries and all P0088 CN105 field occurrences; excludes other ports and undiscovered fields',
        physical_tests=0, commands=data['rows'], services=data['services'], fields=fields,
        counts=dict(commands=len(data['rows']),services=len(data['services']),field_occurrences=len(fields),
                    field_name_kinds=dict(Counter(f['name_kind'] for f in fields))),
        caveat='Namn är referensetiketter. Tekniska positionsnamn löser inte okänd fysisk betydelse. Överlappande råbytes och sammansatta fält är inte oberoende funktioner.')

def render(data):
    lines=['# Namnregister — CN105 och A3','',
        'Alla poster inom den katalogiserade omfattningen har nu ett namn. Namn, beskrivning och säkerhetsgrad är separata. Detta betyder inte att alla fysiska funktioner är identifierade.','',
        data['caveat'],'',
        f"Omfattning: {data['counts']['commands']} kommandovägar, {data['counts']['services']} A3-koder och {data['counts']['field_occurrences']} fältförekomster. Andra portar och ännu inte katalogiserade fält ingår inte.",'',
        '## Kommandon','', '| Kod | Namn | Bedömning |','|---|---|---|']
    lines += [f"| {r['id']} | {r['name']} | {r['status']} |" for r in data['commands']]
    lines += ['', '## A3-koder (decimal)','', '| Kod | Namn | Bedömning |','|---|---|---|']
    lines += [f"| {r['code_decimal']} | {r['name']} | {r['naming_status']} |" for r in data['services']]
    lines += ['', '## Läs- och skrivfält','',
        'RX/TX är relativt FTC. ID behåller originalpost, riktning och fältindex. Flera katalogposter kan beskriva samma byte; de har inte slagits ihop eller fått gissade givarnamn.', '',
        '| Fält-ID | Namn | Syfte | Namngrund |','|---|---|---|---|']
    lines += [f"| {r['id']} | {r['name']} | {r['purpose_trace']['purpose'] if r['purpose_trace'] else 'Inte fördjupat här'} | {r['name_kind']} |" for r in data['fields']]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    data=build()
    (overview.OUT/'name-registry.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (overview.OUT/'name-registry.md').write_text(render(data))
    print(json.dumps(data['counts'],ensure_ascii=False))
