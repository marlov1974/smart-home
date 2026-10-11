"""P0088 public-input command/port worklist. No device access or firmware edits."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

PORTS = {
    'uart2': ('CN105', 'protocol/P81 corroborated', 'cn105-new-capabilities.md'),
    'source-software': ('CN3C candidate', 'software path proven; connector inferred', 'source-link.md'),
    'd': ('CN22 candidate', 'connector inferred; peer implementation absent', 'settings-d-events.md'),
    'uart6': ('CNRF candidate', 'room protocol proven; connector inferred', 'uart6-room-path.md'),
    'uart0': ('CN108/storage candidate', 'file protocol proven; connector inferred', 'uart0-storage-path.md'),
    'uart1': ('CNIT candidate', 'diagnostic protocol; connector unbound', 'uart1-snapshots.md'),
}
# Contracts connect already published findings; never declare whole-command completion
# merely because one field or callback is named.
CONTRACTS = {
    'uart2.41.32': {
        'name': 'Operating controls including zone1 fixed-flow target',
        'effect': 'Enabled BE16 target ->38DE -> mode/holiday/override selection ->3908 ->BA962 ->39EF; requested and effective targets differ',
        'links': ['source.packet.82c2a'],
        'evidence': ['../P0087/flow-target-trace.md', 'source-outgoing.md'],
        'gap': 'Finish all SET32 flags/fields and profile gates; ordinary zone1 target chain is qualified',
    },
    'uart2.41.c8': {
        'name': 'Settings category session action',
        'effect': 'Write action1 schedules category import before end acknowledgment; timeout/reset is not rollback',
        'links': ['d.settings.advertisement1005', 'd.settings.extended-end'],
        'evidence': ['settings-apply-order.md', 'settings-d-events.md'],
        'gap': 'Peer scheduling/close sequence needs peer firmware or authorized passive capture',
    },
    'uart2.41.79': {
        'name': 'Stage heating settings including pump level',
        'effect': 'Stages1CB0; category6 import BD780 writes07E6; physical actuator consumption is separate',
        'evidence': ['settings-apply-order.md', 'settings-store-model.md', 'pump-consumers-and-timing.md'],
        'gap': 'Name all neighboring fields and qualify category/session completion',
    },
    'uart2.42.a3': {
        'name': 'Service selector/result gateway',
        'effect': 'Classified local or forwarded job; same-selector polling can read pending/cache; some energy selectors mutate counters',
        'links': ['source.service-result.1d', 'source.packet.82eee'],
        'evidence': ['a3-job-lifecycle.md', 'source-link.md', '../P0086/energy-qualification.md'],
        'gap': 'Per-selector formats/side effects and admission; never treat all A3 queries as harmless reads',
    },
}

def build(folder):
    folder = Path(folder)
    names = ('command-atlas.json', 'source-tx-descriptors.json', 'port-sprint-evidence.json')
    inputs = {n: hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in names}
    atlas = json.loads((folder/names[0]).read_text())['rows']
    descriptors = json.loads((folder/names[1]).read_text())
    ids = [r['id'] for r in atlas]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate atlas IDs')
    byid = {r['id']: r for r in atlas}
    rows, used = [], set()
    raw_by_handler = defaultdict(list)
    raw_registry = {}
    for r in atlas:
        if r['path'] == 'uart2' and r['operation_class'] == 'raw field':
            for h in r['handler']:
                positions = [f['position'] for f in r['tx_fields']]
                key = hashlib.sha256(json.dumps([h, positions, r['evidence']],sort_keys=True).encode()).hexdigest()[:16]
                if key not in raw_registry:
                    raw_registry[key] = dict(handler=h, positions=positions, evidence=r['evidence'], atlas_ids=[])
                    raw_by_handler[h].append(key)
                raw_registry[key]['atlas_ids'].append(r['id'])

    def add(r, kind):
        port, confidence, doc = PORTS[r['path']]
        raw = sorted({key for h in r.get('handler', []) for key in raw_by_handler[h]})
        row = dict(id=r['id'], path=r['path'], counting_unit=kind,
                   port=port, physical_confidence=confidence,
                   name=r['functional_name'], wire=r['wire'],
                   handlers=r.get('handler', []), rx_fields=r.get('rx_fields', []),
                   tx_fields=r.get('tx_fields', []), raw_response_fields=raw,
                   effect=r.get('side_effects', 'UNKNOWN'),
                   gates=r.get('gates', 'UNKNOWN'),
                   completion=r.get('completion', 'UNKNOWN'),
                   semantic_evidence=r.get('semantic_confidence', 'unresolved'),
                   status='PARTIAL', fully_documented=False,
                   evidence=[doc, *r.get('evidence', [])],
                   gap=r.get('next_verification', 'Trace handler to field effects and completion'), links=[])
        contract = CONTRACTS.get(r['id'])
        if contract:
            for k in ('name', 'effect', 'gap', 'links'):
                if k in contract:
                    row[k] = contract[k]
            row['evidence'] += contract['evidence']
            row['semantic_evidence'] = 'cross-report static contract; not every field complete'
        rows.append(row)
        used.add(r['id'])

    for r in atlas:
        ident = r['id']
        if ident.startswith(('uart2.41.', 'uart2.42.')) and r.get('disposition') == 'mapped':
            add(r, 'mapped command route')
        elif ident.startswith('uart2.frame.'):
            add(r, 'alternate frame route')
        elif ident.startswith(('d.transfer.range.', 'd.settings.')):
            add(r, 'selector range' if '.range.' in ident else 'session event')
        elif ident.startswith(('uart6.command.', 'uart6.connect')):
            add(r, 'command route')
        elif ident.startswith('uart1.'):
            add(r, 'personality-specific command route')
        elif ident.startswith('uart0.transaction.'):
            add(r, 'default transaction' if ident.endswith('.00') else 'local transaction template')
        elif ident == 'source.service-result.1d':
            add(r, 'receive family')

    # These maps precede state/history gates: retain raw selectors without
    # presenting branch callbacks as unconditional command handlers.
    proof = json.loads((folder/names[2]).read_text())
    translation = []
    for name, item in proof['translations'].items():
        prefix = 'source.dispatch.' if name == 'source_rx' else 'd.dispatch.'
        bound = 16 if name == 'source_rx' else 25
        expected = 32 if name == 'source_rx' else 16
        if len(item['values']) != expected:
            raise ValueError('wrong translation length')
        for raw, normalized in enumerate(item['values']):
            if not 0 <= normalized <= bound:
                raise ValueError('invalid normalized selector')
            index = min((normalized-1) & 255, bound-1)
            branch = byid[prefix+f'{index:02d}']
            translation.append(dict(path=name, raw=f'{raw:02x}', normalized=normalized,
                candidate_branch=branch['id'], candidate_handlers=branch['handler'],
                disposition='no normalized event' if normalized == 0 else 'pre-history candidate',
                evidence=[item['address'], '9CBF6' if name == 'source_rx' else '9F152'],
                gate='History/status gates may suppress or remap; see port-sprint.md'))
    about = next(r for r in rows if r['id'] == 'uart2.frame.5b')
    about['tx_fields'] = [dict(position=i, source=value) for i,value in enumerate(
        [201, *proof['about']['rom84ade'],20,3,'RAM05B2','RAM099B != 0',1]+[0]*6)]
    about['semantic_evidence'] = 'all16 response bytes sourced; external field labels partly unknown'
    about['gap'] = 'Name capability fields and trace native request effects; payload layout is closed'
    about['evidence'].append('port-sprint-evidence.json')
    get04 = next(r for r in rows if r['id'] == 'uart2.42.04')
    get04['name'] = 'Native and multi-unit status fields (raw sources)'
    get04['tx_fields'] = [dict(position=i,source=src) for i,src in enumerate(proof['get04']['sources'])]
    get04['semantic_evidence'] = 'all16 response-byte sources; remote-record meanings still partial'
    get04['gap'] = 'Identify395A/3958 record producers and physical units; payload layout is closed'
    get04['evidence'].append('port-sprint-evidence.json')
    for ident, values in (('uart2.frame.5c',[204,255]),('uart2.frame.5d',[204])):
        r=next(r for r in rows if r['id']==ident)
        r['tx_fields']=[dict(position=i,constant=v) for i,v in enumerate(values)]
        r['gap']='Reply payload is fully constant; trace request dispatch effects before calling it a no-op'
        r['evidence'].append('port-sprint.md')

    seen = set()
    for d in descriptors:
        if d['address'] in seen:
            raise ValueError('duplicate source descriptor')
        seen.add(d['address'])
        fields = [byid[f"source.tx.{d['address']}.{i:02d}"] for i in range(len(d['fields']))]
        used.update(f['id'] for f in fields)
        r = dict(fields[0], id='source.packet.'+d['address'],
                 functional_name='Source packet template '+d['address'],
                 wire={k: v for k, v in d.items() if k != 'fields'},
                 tx_fields=[f['tx_fields'][0] for f in fields],
                 evidence=['source-outgoing.md', *[e for f in fields for e in f['evidence']]],
                 next_verification='Name staged fields and profile selection; peer effects require peer evidence')
        add(r, 'outgoing packet template')
        rows[-1]['semantic_evidence'] = 'Field structure proven; constants are not named command semantics'
        if d['address'] == '82c2a':
            rows[-1].update(name='Target/return/feedback/flow packet, family05 variant1',
                effect='Encodes selected temperatures and nonlinear primary-flow value; not direct compressor-Hz control',
                links=['uart2.41.32'],
                gap='Resolve upper address bits, active installed profile and peer application')
        elif d['address'] == '82b94':
            rows[-1]['name'] = 'Native demand packet, family05 variant0'
        elif d['address'] == '82eee':
            rows[-1]['name'] = 'Queued source service request template'

    for r in rows:
        if r['gap'].startswith('finish named dataflow'):
            r['gap'] = 'Trace '+','.join(r['handlers'])+' and its callees: field encoding, enable masks, effect and completion; stop at15min'
    rowids = {r['id'] for r in rows}
    if len(rowids) != len(rows):
        raise ValueError('duplicate matrix IDs')
    for r in rows:
        if not set(r['links']) <= rowids:
            raise ValueError('dangling cross-port link '+r['id'])
    residual = []
    for path in ('d', 'source', 'shared-service', 'settings'):
        rr = [r for r in atlas if r['path'] == path and r['id'] not in used]
        if rr:
            residual.append(dict(path=path, kind='structural records, NOT additional proven commands',
                count=len(rr), unique_handler_sets=len({tuple(r['handler']) for r in rr}),
                ids=[r['id'] for r in rr],
                gap='Recover raw selectors, aliases and acceptance before promotion into command rows'))
    rejected = [r['id'] for r in atlas if r['id'].startswith(('uart2.41.', 'uart2.42.'))
                and r.get('disposition') != 'mapped']
    summary = {}
    for path in PORTS:
        rr = [r for r in rows if r['path'] == path]
        summary[path] = dict(units=dict(Counter(r['counting_unit'] for r in rr)),
            fully_documented=sum(r['fully_documented'] for r in rr),
            partial=len(rr), known_total_all_commands=None,
            with_any_reviewed_detail=sum(r['semantic_evidence'] != 'unresolved' for r in rr))
    return dict(schema_version=1, package='P0088', status='PARTIAL',
        scope='Public-input consolidation of FTC20.01; no complete-command or installed-profile claims',
        input_sha256=inputs, summary=summary, rows=rows,
        structural_residuals=residual, rejected_lookup_slots=rejected, wire_translation=translation,
        raw_field_registry=raw_registry,
        completion_rule='All request/reply fields, gates, effect, completion/error and persistence qualified; physical connector confidence separate')


def render(report):
    def cell(value):
        return str(value).replace('|', '/').replace('\n', ' ')
    lines = ['# P0088 command-to-port matrix', '',
        'Generated by tools/ftc6/p88/port_matrix.py from tracked evidence. FTC20.01 only.', '',
        '**PARTIAL.** A packet template, selector range, alias and field are not independent commands. '
        'Fully documented requires every field plus gates/effect/completion/error/persistence; no row currently satisfies that strict whole-command criterion. '
        'This does not erase the qualified field-level findings. Physical confidence is separate.', '',
        '## Coverage by counting unit', '', '|Path|Port|Units|Fully documented|Partial|', '|---|---|---|---|---|']
    for path, s in report['summary'].items():
        lines.append('|'+ '|'.join(map(cell,(path, PORTS[path][0],s['units'],s['fully_documented'],s['partial'])))+'|')
    lines += ['', f"{len(report['rejected_lookup_slots'])} default/rejected slots retained in JSON; not promoted into commands.", '',
        '## Cross-port chains', '',
        '- CN105 SET32 -> selected/effective heating target -> source82C2A, subject to profile/mode selection. See [target chain](../P0087/flow-target-trace.md).',
        '- CN105 settings C8 -> D1005 advertisement -> peer1002/transfer/end -> category import; import may precede end. See [ordering](settings-apply-order.md).',
        '- CN105 A3 -> shared classifier/job -> source82EEE request -> source1D result -> cached service response. See [lifecycle](a3-job-lifecycle.md).', '',
        '## Command and template worklist', '']
    for path in PORTS:
        lines += [f'### {path} — {PORTS[path][0]}', '', PORTS[path][1]+'.', '',
                  '|ID / kind|Function|Handlers|Fields RX/TX/raw stores|Remaining gap|', '|---|---|---|---|---|']
        for r in report['rows']:
            if r['path'] != path:
                continue
            values = (r['id']+' / '+r['counting_unit'],r['name'],','.join(r['handlers']),
                      f"{len(r['rx_fields'])}/{len(r['tx_fields'])}/{len(r['raw_response_fields'])}",r['gap'])
            lines.append('|'+'|'.join(map(cell,values))+'|')
        lines += ['', f"Evidence and port qualification: [{PORTS[path][2]}]({PORTS[path][2]}). Full wire, fields, gates and cross-links are in command-port-matrix.json.", '']
    lines += ['## Raw command/event translation before history gates', '',
              'These are conditional candidates, not ready-to-send packets. Zero has no normalized event. '
              'D transmit events are local transmission notifications, not new incoming commands.', '',
              '|Path|Raw|Normalized|Candidate branch / handlers|', '|---|---|---|---|']
    for r in report['wire_translation']:
        dest = 'none' if r['normalized']==0 else r['candidate_branch']+' / '+','.join(r['candidate_handlers'])
        lines.append('|'+ '|'.join(map(cell,(r['path'],r['raw'],r['normalized'],dest)))+'|')
    lines += ['', '## Structural residuals (separate denominator)', '']
    for r in report['structural_residuals']:
        lines.append(f"- {r['path']}: {r['count']} records, {r['unique_handler_sets']} unique handler sets. {r['gap']}.")
    lines += ['', 'See [timeboxed work and residual plan](port-sprint.md) for the next evidence-producing actions.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    report = build(args.folder)
    (args.folder/'command-port-matrix.json').write_text(json.dumps(report, indent=2)+'\n')
    (args.folder/'command-port-matrix.md').write_text(render(report))
    print(json.dumps(report['summary'], indent=2))

if __name__ == '__main__':
    main()
