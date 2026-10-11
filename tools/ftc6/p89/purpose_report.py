"""P0089 offline evidence report. No hardware access."""
import hashlib
import json
from pathlib import Path
import overview
from purpose_fields import ROWS, PURPOSES, PACKERS

def build(private_root):
    image=(private_root.parent.parent/'P0082/private/ftc6.bin').read_bytes()
    digest=hashlib.sha256(image).hexdigest()
    if digest!='d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a':raise ValueError('wrong image')
    records=[]
    # Only the bounded descriptor regions already established in P88/P89.
    descriptors=list(range(0x81084,0x81684,32))+list(range(0x85702,0x85a02,32))
    for (packer,pos),purpose in PURPOSES.items():
        traces=[]
        for ptr in purpose['state_pointer'].split('/'):
            matches=[]
            for addr in descriptors:
                raw=image[addr-0x80000:addr-0x80000+32]
                if int.from_bytes(raw[2:4],'little')==int(ptr,16):
                    callback=int.from_bytes(raw[9:13],'little')
                    table=image[callback-0x80000:callback-0x80000+60]
                    matches.append(dict(address=f'{addr:x}',hex=raw.hex(),callback_table=f'{callback:x}',callback_hex=table.hex()))
            if len(matches)!=1:raise ValueError((ptr,matches))
            traces.append(dict(state_pointer=ptr,**matches[0]))
        records.append(dict(**purpose,packer=packer,descriptors=traces))
    exports={}
    for folder in ['purpose','purpose-next','purpose-leaves','purpose-last','purpose-final','purpose-radio']:
        for path in sorted((private_root/folder).glob('*.asm')):
            exports[f'{folder}/{path.name}']=hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(status='PARTIAL',image_sha256=digest,physical_tests=0,fields=records,exports=exports,
        decoding='A4410 maps source0→0;1/2→1;3/4/5→(flag?2:0). Other states fall back0. Do not label the wire byte a universal boolean fault flag.',
        remaining='GET19 receiver mask has unknown radio-level cause; A3 service modes350..363 still need peer semantics; other commands/fields remain outside this purpose pass.')

def render(data):
    lines=['# Vad avläsningarna används till','',
        'Denna fortsättning följer 31 fält i GET17, GET18 och GET19 till övervakningens faktiska villkor. Detta är ny syftesanalys, inte bara nya namn. Inga pumpar har kontaktats.','',
        '**Inte klart för hela protokollet.** GET17:s11 och GET18:s12 skrivna statusfält är följda; GET19:s8 är följda. Tidigare namn på hela paketen var för snäva.','',
        '| Kommando / databyte | Begripligt namn | Syfte |','|---|---|---|']
    for r in data['fields']:
        lines.append(f"| GET{r['opcode'].upper()} / {r['position']} | {r['name']} | {r['purpose']} |")
    lines += ['', '## Vad fynden innebär','',
        '- Fel på flödesgivaren och för lågt vattenflöde är olika signaler. Ett transportmässigt läsbart flöde behöver därför inte vara användbart.',
        '- Zonernas omvända temperaturförhållande övervakas med giltiga givare och mer än5 graders skillnad, efter drift- och tidsvillkor. Signalen kan hjälpa felsökning men bevisar inte rundgång.',
        '- Övertemperaturövervakningen använder bland annat80 grader i primärkretsen och75 grader i tanken. Detta är referensfirmwarens utlösningsvillkor, inte rekommenderade börvärden eller våra styrgränser.',
        '- Läsningarna rapporterar status från skyddslogik; de är inte kommandon för att aktivera eller avaktivera skydd.',
        '- Trösklar är inte omedelbara larmgränser. Timer, driftläge, konfiguration och givargiltighet ingår. Exakta tider har inte kvalificerats här.', '',
        '## Statuskodernas betydelse','',data['decoding'], '',
        'En nolla är alltså inte generellt ett friskintyg. Den kan även uppstå när ett tillstånd inte exponeras av just den fältvarianten. Ursprungstillstånd och flagga måste beaktas.', '',
        '## Kvarstående gränser','',data['remaining'], '',
        'GET19:s låga zontemperatur och sekvensfel har användbara syften men ännu inte fullständiga menynamn/orsaksdiagnoser. Fältet för källenheter har en mask med tidsvillkor; exakt peer-felklass återstår.', '',
        '## Reproduktion och källor','',
        'purpose-analysis.json sparar descriptorbytes, tillhörande callbacktabeller och hash för nya native exporter. Kedjan är svarspackare → tillstånd → indirekt descriptor → utlösningsvillkor. ManualOCH722A:s A3/504–515 och567/569 används för fysisk givartilldelning. C-dekompilering kontrolleras mot native instruktioner; privata exporter ingår inte i public repo.', '']
    return '\n'.join(lines)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--private',type=Path,required=True);a=p.parse_args()
    d=build(a.private)
    (overview.OUT/'purpose-analysis.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    (overview.OUT/'purpose-analysis.md').write_text(render(d))
    print(len(d['fields']))
