"""Bind semantic groups to actual native payload writes; emit explicit residuals."""
import argparse,hashlib,json,re
from pathlib import Path
from collections import Counter
import overview
from field_purposes import GROUPS
from purpose_fields import PURPOSES

def build(private):
    image=private.parent.parent/'P0082/private/ftc6.bin'
    digest=hashlib.sha256(image.read_bytes()).hexdigest()
    if digest!='d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a':raise ValueError('wrong reference image')
    atlas=json.loads((overview.P88/'command-atlas.json').read_text())
    p88=private.parent.parent/'P0088/private/catalog'
    mapping={};exports={};groups=[]
    routes=overview.build()['rows']
    route_map={}
    for r in routes:
        for h in r['handlers']:route_map.setdefault(h,[]).append(r['id'])
    for group in GROUPS:
        pack=group['packer'];path=p88/(pack+'.asm');native=path.read_text()
        exports[pack]=hashlib.sha256(path.read_bytes()).hexdigest()
        if pack in ('a6642','a8402'):
            end={'a6642':0xa77b8,'a8402':0xa8a20}[pack]
            full=private.parent.parent/'P0088/private/pump-timing-first/instructions.tsv'
            native='\n'.join(line for line in full.read_text().splitlines() if line.startswith('ram:') and int(pack,16)<=int(line.split('\t')[0][4:],16)<end)
            exports['full_instructions']=hashlib.sha256(full.read_bytes()).hexdigest()
        # These are written-byte occurrences. Do not fabricate implicit zero members.
        writes={int(m.group(1),16)-0x235e for m in re.finditer(r',0x(23[56][0-9a-f])(?:\s|$)',native) if 0x235e<=int(m.group(1),16)<=0x236d}
        if pack in ('a6642','a8402'):
            cpath=p88/(pack+'.c')
            exports[pack+'.c']=hashlib.sha256(cpath.read_bytes()).hexdigest()
            writes.update(int(v,16)-0x235e for v in re.findall(r'DAT_near_(23[56][0-9a-f]) =',cpath.read_text()) if 0x235e<=int(v,16)<=0x236d)
        active=[p for p in group['positions'] if p in writes]
        if not active:raise ValueError(('no payload writes for semantic group',group))
        group=dict(group,commands=route_map.get(pack,[]),observed_positions=active);groups.append(group)
        for pos in active:
            key=f'{pack}:{pos}'
            if key in mapping:raise ValueError(('duplicate mapping',key))
            mapping[key]=dict(name=group['name'],purpose=group['purpose'],evidence=group['evidence'],confidence=group['confidence'],kind=group['kind'],packer=pack,position=pos)
    routes=overview.build()['rows']
    settings={h for r in routes if r['id'].startswith('uart2.42.') and 0x50<=int(r['wire']['opcode'],16)<=0x7e for h in r['handlers']}
    classified=[];remaining=[]
    for row in atlas['rows']:
        if row['path']!='uart2':continue
        for field in row['tx_fields']:
            if field['name']!='unresolved response byte':continue
            pos=field['position'];pack=row['handler'][0];key=f'{pack}:{pos}'
            if (pack,pos) in PURPOSES:continue
            if key not in mapping:
                name=purpose=confidence=None
                source=row['evidence'][0].get('operand_source','')
                if pack=='a5472':name='Kvittens för inställningsskrivning';purpose='Bekräfta protokollsvaret; inte bevis på fysisk tillämpning.'
                elif pack in settings and pos==1:name='Inställningssessionens status';purpose='Visa om inställningsblocket får lämnas ut; CFB18.'
                elif pack in settings and pos==15:name='Inställningskategori';purpose='Koppla blocket till rätt inställningssession; källa2357.'
                elif pos==0 and pack not in ('a901e','a9056'):name='Svarskod';purpose='Koppla svaret till rätt fråga; ingen fysisk mätstorhet.'
                elif source in ('0','#0x0'):name='Konstant nollfält';purpose='Platshållare i denna firmware; betyder inte uppmätt noll.'
                if name:mapping[key]=dict(name=name,purpose=purpose,evidence=row['evidence'],confidence='native protokollroll',kind='protokoll',packer=pack,position=pos)
            if key in mapping:classified.append(row['id'])
            else:remaining.append(dict(id=row['id'],commands=route_map.get(pack,[]),packer=pack,position=pos,evidence=row['evidence']))
    for folder in ('field-final','field-states','field-leaves','field-controls','field-tail'):
        for path in sorted((private/folder).glob('*.asm')):
            exports[folder+'/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted((private.parent.parent/'P0088/private/getters').glob('*.asm')):
        exports['getters/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    # Only keep bindings occurring in the original atlas, leaving no apparent invented fields.
    return dict(image_sha256=digest,status='PARTIAL_SEMANTIC_COVERAGE',physical_tests=0,groups=groups,bindings=mapping,remaining=remaining,exports=exports,
        counts=dict(new_classified_occurrences=len(classified),remaining_raw_occurrences=len(remaining),semantic_groups=len(groups),bindings=len(mapping)),
        caveat='Counts are overlapping field occurrences, not functions. SD-format correlation is not native proof or hardware validation. Protocol labels do not resolve unknown peer semantics.')

def render(d):
    lines=['# Återstående läsfält — syfteskartläggning','',d['caveat'],'',str(d['counts']),'',
           '| Kommando / packare / payloadbytes | Funktion | Syfte | Evidensnivå |','|---|---|---|---|']
    for g in d['groups']:lines.append(f"| {','.join(g['commands'])} / {g['packer']} / {','.join(map(str,g['observed_positions']))} | {g['name']} | {g['purpose']} | {g['confidence']} |")
    lines+=['','## Fält som ännu saknar användarsyfte','','| Kommando / packare | Position | Native underlag |','|---|---|---|']
    for r in d['remaining']:lines.append(f"| {','.join(r['commands'])} / {r['packer']} | {r['position']} | {r['evidence']} |")
    return '\n'.join(lines)+'\n'
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--private',type=Path,required=True);a=p.parse_args();d=build(a.private)
    (overview.OUT/'field-purpose-audit.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    (overview.OUT/'field-purpose-audit.md').write_text(render(d));print(d['counts'])
