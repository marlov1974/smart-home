"""P0089 deterministic report/schema checks. Reads tracked evidence only."""
import argparse,json
from pathlib import Path

def build(folder):
    folder=Path(folder);c=json.loads((folder/'cn105-contracts.json').read_text());e=json.loads((folder/'evidence.json').read_text())
    required={'id','p88_id','frame_type','opcode','selector','zone','category','positions','name','enable','encoding','source_consumer','effect','readback','retry','proof','remaining','scope','new_in_p89','static_effect_known','offline_codec_ready','physical_test_ready','physically_verified'}
    if len({r['id'] for r in c['fields']})!=len(c['fields']):raise ValueError('duplicate fields')
    for r in c['fields']:
        if not required<=r.keys() or not r['proof'] or not r['remaining']:raise ValueError('missing contract evidence')
        if not set(r['proof'])<=set(e['assembly_sha256']):raise ValueError('unverified proof root')
        if r['physical_test_ready'] or r['physically_verified']:raise ValueError('physical claim not allowed in this batch')
    if [r['opcode'] for r in c['settings_blocks']]!=[f'{n:02x}' for n in range(0x50,0x7f)]:raise ValueError('settings ledger incomplete')
    coverage=dict(package='P0089',status='PARTIAL',structural_cn105_routes=len(c['backlog']),settings_blocks=47,
        new_field_contracts=len(c['fields']),offline_models=sum(x['offline_codec_ready'] for x in c['fields']),
        whole_operational_transactions_complete=0,physical_tests=0,physical_status='NOT RUN',repeated_exports=e['repeat_count'],
        direct_category6_writes=sum(len(x) for x in e['category6_direct_writes'].values()),
        metric='Field-level edges with explicit residuals; not new unique features or complete commands')
    return c,e,coverage

def render(c):
    def esc(x):return str(x).replace('|','/').replace('\n',' ')
    lines=['# P0089 – nya styr- och läskontrakt','','**PARTIAL, FTC20.01; fysisk verifiering NOT RUN.** Tidigare P88-fynd räknas inte som nya. Varje rad anger den nya slutna länken och vad som återstår.','','|Kod / fält|Funktion|Nytt samband|Återläsning|Kvar|','|---|---|---|---|---|']
    for r in c['fields']:
        lines.append('|'+ '|'.join(esc(x) for x in [r['frame_type']+'/'+r['opcode']+' p'+','.join(map(str,r['positions'])),r['name'],r['effect'],r['readback'],r['remaining']])+'|')
    lines+=['','SET32 p4 och SET33 är uttryckligen kvar som ofullständiga. Ingen hel fysisk transaktion markeras klar. Se cn105-contracts.json för aktiveringsbitar, kodning, modellstatus och bevisadresser.','']
    return '\n'.join(lines)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);a=p.parse_args();c,e,v=build(a.folder)
    (a.folder/'control-contracts.md').write_text(render(c));(a.folder/'coverage.json').write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps(v,indent=2))
