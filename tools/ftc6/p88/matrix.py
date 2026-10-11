"""Human functional matrix, with unresolved manual actions explicitly preserved."""
import json
from pathlib import Path
HERE=Path(__file__).parent
OUT=HERE.parents[2]/'requirements/package-runs/P0088'
def render(out=OUT):
    m=json.loads((HERE/'menu_inventory.json').read_text())
    lines=['# Functional matrix and manual parity backlog','','R/W mean externally observable read/report and request/write, respectively; they do not authorize actuation. P = proven static route, S = session/sequence incomplete, U = untraced. Unknown does not mean unsupported. Each action is separate from physical connector assignment.','','| Action | CN105 R | CN105 W | UART6 R | UART6 W | UART0 R | UART0 W | UART1 R | UART1 W | D R | D W |','|---|---|---|---|---|---|---|---|---|---|---|']
    known=[
    ('Actual compressor Hz','P GET04','U','U','U','U','U','U','U','U','U'),
    ('Requested compressor Hz','P A3/17 forwarded','U','U','U','U','U','U','U','S shared services','U'),
    ('Brine inlet temperature','P A3/27 forwarded','U','U','U','U','U','U','U','S shared services','U'),
    ('Brine outlet temperature','P A3/28 forwarded','U','U','U','U','U','U','U','S shared services','U'),
    ('Brine pump level','P A3/18 forwarded','U','U','U','U','U','U','U','S shared services','U'),
    ('Brine pump RPM','P A3/19 forwarded','U','U','U','U','U','U','U','S shared services','U'),
    ('Frequency limitation/state','P A3/52 forwarded','U','U','U','U','U','U','U','S shared services','U'),
    ('Flow temperature','P GET0B/A3/511','U','U','U','U','U','P12/00 bytes62–63','U','S services','U'),
    ('Return temperature','P GET0B/A3/506','U','U','U','U','U','P12/00 bytes64–65','U','S services','U'),
    ('Primary water flow','P GET14/A3/540','U','U','U','U','U','P12/01 bytes61–62','U','S services','U'),
    ('Configured heating pump level','S GET79 p7','S SET79 whole block','U','U','S SER imports','S SER file','P near read20.01','U','S settings','S settings'),
    ('Configured DHW pump level','S GET65 p10','S SET65 whole block','U','U','S SER imports','S SER file','P near read20.01','U','S settings','S settings'),
    ('Eight wireless room temperatures','U full channels','U','U','P48..4B peer reports','U','U','P near read20.01','U','U','U'),
    ('Zone selected room target','P GET09','P SET32 flags','P reply aggregate','P49 p1/mode/zone','S AC file','S AC file','P near read20.01','U','S shared setters','S shared setters'),
    ('DHW boost','P GET28','P SET34','P p5','P4A p9','U','U','P12/00','U','S shared state','S shared state'),
    ('Holiday enable','P GET28','P SET34','P p6','P4B p9','S HOL file','S HOL file','P12/00','U','S shared state','S shared state'),
    ('Live consumed/produced power','P GET07 raw, units unvalidated','U','U','U','U','U','U','U','U','U'),
    ('Energy running counters','P A3/520..531; side effects','U','U','U','U','U','P near memory, uncalibrated','U','S shared services','U'),
    ('Energy snapshot/reset','P historical GETA1/A2','S A3/532 mutates','U','U','U','U','U','U','S shared services','S shared services'),
    ('Diagnostic traffic log','U','U','U','U','P file protocol, distinct log','P dated log writer','P F0 drains','U','U','U'),
    ('Near16 diagnostic memory','U','U','U','U','U','U','P low1 aliases16-bit','U','U','U'),
    ('Metadata/about','P5B/C9','U','U','U','U','U','P12/00','U','U','U')]
    for row in known:lines.append('| '+' | '.join(row)+' |')
    lines += ['', '## Source-peer and job functions', '',
      'Directions below are relative to FTC. They describe the traced software link, not a qualified CN3C pinout or a new Procon command.', '',
      '| Action | FTC receives | FTC sends / changes | Qualification |',
      '|---|---|---|---|',
      '| Forwarded service result | Type1D, selector10 bits, format3 bits, raw16 | Shared class1 A3 cache updated | No selector-equality check in CECFA; outer gates remain |',
      '| Selected temperature target | U | Descriptor82C2A byte1 from39EF | Half-degree quantization; active profile must be established |',
      '| Selected temperature feedback | U | Descriptor82C2A byte3 from39F1 | Half-degree quantization; heating/DHW selection inBA962 |',
      '| Return temperature | U | Descriptor82C2A byte2 low6 from39F3 | Whole-degree encoding, range0..60 |',
      '| Primary flow feedback | U | Descriptor82C2A byte4 from39F5 | Feature gate and nonlinear encoding; source-outgoing.md |',
      '| A3 job polling | Cached status viaCN105 | Same forwarded selector normally preserves job | Pending differs from failed transport; a new measurement needs rearming |',
      '| A3 job cancellation | Non-A3 internal command can clear ownership | Falling0402 sets0868; service queue bits cleared | Conditional native path, no live test |',
      '| Settings pending-request announcement | Internal service1005 | State1 format1, category mask and direction | D peer schedule unresolved; not externally callable A3 |',
      '| Settings extended end event | D tag1, selector0 | CF978 consumes completion prerequisite | Full transfer sequence remains incomplete |']
    lines += ['','## Manual-derived action inventory','','Source: '+m['source']+'. These are required parity targets, not claims of resolved command mappings. See the first table and atlas for established subsets. UI-local is a hypothesis until screen firmware or a transport proves ownership.','', '| Group | Individual action | Classification / remaining edge |','|---|---|---|']
    for group,actions in m['groups'].items():
        for action in actions:
            state='Screen-local candidate; wire/native owner untraced' if group=='Initial/UI' and action!='Date/time' else 'Optional applicability; per-field native route untraced' if 'optional' in group else 'FTC/menu action; exact per-field route/transaction not yet closed'
            lines.append(f'| {group} | {action} | {state} |')
    lines += ['','The inventory does not certify pressure/current/voltage channels absent: source-controller analog values and diagnostic arrays need further name/unit tracing. Pairing identity and battery status remain unlabeled; indexed room channels are not proof of radio pairing control. Full semantic parity is therefore PARTIAL.','']
    (out/'function-matrix.md').write_text('\n'.join(lines))
if __name__=='__main__':render()
