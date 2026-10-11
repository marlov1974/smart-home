"""P0088: known command codes and cross-interface relationships, offline only."""
import argparse
import hashlib
import json
from pathlib import Path
from port_matrix import PORTS

RELATIONS = [
    dict(function='Varmvattenboost', members=['uart2.41.34','uart6.command.4a'],
         codes='CN105 SET34 p3, enable p1.bit0 ↔ UART6 typ4A p9 (svar6A)',
         relation='Gemensam setter B95E0 /3919; olika validering, inte identiska paket', evidence='uart6-room-path.md'),
    dict(function='Semesterläge', members=['uart2.41.34','uart6.command.4b'],
         codes='CN105 SET34 p4, enable p1.bit1 ↔ UART6 typ4B p9 (svar6B)',
         relation='Gemensam setter C0AD0 /391B', evidence='uart6-room-path.md'),
    dict(function='Framledningsbörvärde', members=['uart2.41.32','source.packet.82c2a'],
         codes='CN105 SET32 → källänk familj05, variant1',
         relation='Styrkedja via urval/överstyrning; vidareförmedlat effektivt värde, inte kodalias', evidence='source-outgoing.md'),
    dict(function='Servicefråga / Running information', members=['uart2.42.a3','source.packet.82eee','source.service-result.1d'],
         codes='CN105 GET A3 + serviceval → källänk1C → svar1D → A3-resultat',
         relation='Villkorad vidarebefordran; lokala serviceval går inte alla till underkortet', evidence='a3-job-lifecycle.md'),
    dict(function='Inställningssession', members=['uart2.41.c8','d.settings.advertisement1005','d.settings.extended-end'],
         codes='CN105 SET C8 → D intern service1005 (decimal) → överföring / slutmarkör',
         relation='Sessionskedja;1005 är inte ett externt A3-val eller fristående wire-opcode', evidence='settings-d-events.md'),
    dict(function='Återläsning av hjälptillstånd', members=['uart2.41.34','uart2.42.28'],
         codes='SET34 p11/p12 → GET28 p11/p12',
         relation='Delade tillstånd39EC/39A4; skrivning och läsning, inte samma operation', evidence='cn105-control-fields.md'),
]

def codes(row):
    w=row['wire'];path=row['path']
    if path=='source-software' and row['counting_unit']=='outgoing packet template':
        constants=[f"b{f['position']}.bits{f['bit_offset']}..{f['bit_offset']+f['bit_length']-1}=0x{f['source_sink'].split(':')[1].upper()}" for f in row['tx_fields'] if f.get('source_sink','').startswith('constant:')]
        return '; '.join(constants) or 'Ingen fast kod identifierad; se fältlayout'
    if path=='uart2' and 'opcode' in w:
        return f"FC / typ0x{w['type'].upper()} / kod0x{w['opcode'].upper()}"
    if path=='uart0':
        return f"operation0x{w['operation_byte']:02X}; lokalt mall-ID {w['local_id']} (decimal); {w['filename']}"
    if path=='d' and 'selector_min' in w:
        return f"utökad väljare {w['selector_min']}..{w['selector_max']} (decimal); extended.bit0={w['extended_word_bit0']}"
    if path=='d' and w.get('internal_service'):
        return f"intern service {w['internal_service']} (decimal), wirekod ej fristående fastställd"
    if row['id']=='d.settings.extended-end':return 'utökad väljare0; intern markör0x4000'
    return '; '.join(f'{k}={json.dumps(v,ensure_ascii=False)}' + (' (hex)' if k in {'frame','type','reply_type','header','subcommand','type_low_five_bits'} else ' (decimal)' if isinstance(v,int) and not isinstance(v,bool) else '') for k,v in w.items()) or 'OKÄND'

def build(folder):
    folder=Path(folder)
    matrix=json.loads((folder/'command-port-matrix.json').read_text())
    atlas=json.loads((folder/'command-atlas.json').read_text())['rows']
    rows=[]
    for r in matrix['rows']:
        effect=r['effect']
        rows.append(dict(id=r['id'],interface=r['path'],port=r['port'],port_confidence=r['physical_confidence'],
            kind=r['counting_unit'],code=codes(r),wire=r['wire'],function=r['name'],
            effect='Funktion/effekt ännu okänd' if effect=='UNKNOWN' else effect,
            evidence=r['evidence'],remaining=r['gap']))
    ids={r['id'] for r in rows}
    for rel in RELATIONS:
        if not set(rel['members'])<=ids:raise ValueError('unresolved relationship')
    services=[dict(id=r['id'],code=r['wire'],function=r['functional_name'],effect=r['side_effects'],
        reachability=r['reachability'],gates=r['gates'],evidence=r['evidence']) for r in atlas if r['path']=='shared-service']
    return dict(package='P0088',reference='FTC20.01; inte verifierat mot installerad21.00',
        scope='Alla poster i nuvarande portmatris, alla gemensamma serviceposter samt alla råkodöversättningar. Inte bevisat komplett för hela firmwaren.',
        inputs={n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ['command-port-matrix.json','command-atlas.json']},
        routes=rows,services=services,translations=matrix['wire_translation'],relationships=RELATIONS,
        rejected_slots=matrix['rejected_lookup_slots'],structural_residuals=matrix['structural_residuals'])

def render(report):
    def cell(x):
        if isinstance(x,(dict,list)):x=json.dumps(x,ensure_ascii=False)
        return str(x).replace('|',' / ').replace('\n',' ')
    def table(headers,values):
        return ['|'+'|'.join(headers)+'|','|'+'|'.join('---' for _ in headers)+'|',*['|'+'|'.join(cell(v) for v in row)+'|' for row in values]]
    lines=['# Kommandokatalog – FTC6', '',report['reference']+'.', '',report['scope'], '',
        '**Läsnyckel:** hex anges med0x eller enligt uttrycklig kolumnnotering. Serviceval anges i decimal. ROM-adresser är spårnings-ID, inte kommandon. En gemensam svarsrutin bevisar inte att flera koder gör samma sak. Okända funktioner behålls i listan.', '',
        '## Portar och gränssnitt','']
    lines+=table(['Gränssnitt','Port','Säkerhet i kopplingen','Poster'],[(p,v[0],v[1],sum(r['interface']==p for r in report['routes'])) for p,v in PORTS.items()])
    lines+=['','269 rutter/mallar/intervall är inte269 oberoende funktioner. Serviceval och interna översättningar redovisas separat. Procons Modbus-register och bootloader tillhör ett annat firmwarelager; inga likheter i nummer används som bevis för koppling.','','## Samma funktion eller kedja över flera gränssnitt','']
    lines+=table(['Funktion','Kod/koder','Vad sambandet betyder','Källa'],[(r['function'],r['codes'],r['relation'],f"[{r['evidence']}]({r['evidence']})") for r in report['relationships']])
    for path,port in PORTS.items():
        lines+=['',f'## {path} – {port[0]}','',
            'Alla kända poster på denna väg. Okänd funktion betyder att rutten är identifierad men ännu inte semantiskt kartlagd.','']
        lines+=table(['Kod / underkod','Funktion','Vad den gör / känd effekt','Spårnings-ID'],[(r['code'],r['function'],r['effect'],r['id']) for r in report['routes'] if r['interface']==path])
        lines+=['',f"Port- och protokollunderlag: [{port[2]}]({port[2]}). Fält, villkor och återstående luckor finns i JSON-katalogen och kommandomatrisen."]
    lines+=['','## Serviceval och interna serviceklasser','',
        'Dessa är underkoder/klassificeringsintervall, inte nya fysiska portar. CN105 A3 använder den gemensamma tjänsten; vissa val är lokala, andra vidarebefordras. Interna val är inte automatiskt tillgängliga via A3. Klassintervall överlappar enskilda val och ska inte dubbelräknas.','']
    lines+=table(['Kod (decimal om numerisk)','Funktion','Effekt','Nåbarhet / villkor','ID'],[(r['code'],r['function'],'Okänd' if r['effect']=='UNKNOWN' else r['effect'],r['reachability']+'; '+r['gates'],r['id']) for r in report['services']])
    lines+=['','## Råkoder till interna händelser','',
        'Råkoder är hex; normaliserade händelser är decimal. Historik kan undertrycka eller ändra resultatet. D TX är lokala sändningsnotifieringar, inte inkommande kommandon. Dessa rader kan överlappa paketfamiljer ovan.','']
    lines+=table(['Väg / portkandidat','Råkod','Intern händelse','Kandidat / funktion'],[(r['path']+(' / CN3C' if r['path']=='source_rx' else ' / CN22'),'0x'+r['raw'],r['normalized'],'Ingen normaliserad händelse' if r['normalized']==0 else r['candidate_branch']+'; funktion ej fullständigt fastställd; '+','.join(r['candidate_handlers'])) for r in report['translations']])
    lines+=['','## Ej kommandon och återstående täckning','',f"{len(report['rejected_slots'])} CN105 default/avvisade uppslag listas i JSON, men räknas inte som kommandon.",
        'Interna grenar utan styrkt extern kod behålls som strukturella luckor i JSON och command-atlas.json. Ingen port eller funktion har hittats på för att fylla en tom ruta.','','Källor: [portmatris](command-port-matrix.md), [maskinläsbar katalog](command-catalog.json), [rå atlas](command-atlas.json).','']
    return '\n'.join(lines)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);args=parser.parse_args()
    report=build(args.folder)
    (args.folder/'command-catalog.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (args.folder/'command-catalog.md').write_text(render(report))
    print(f"{len(report['routes'])} routes; {len(report['services'])} service records; {len(report['translations'])} translations; {len(RELATIONS)} cross-interface relationships")
