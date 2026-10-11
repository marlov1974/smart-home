"""P0084 verification; run from the private workspace root, never a device."""
from pathlib import Path
import hashlib, json, tempfile
from evidence import derive
r=Path.cwd();g=r/'P0080/implementation-smart-home';d=g/'requirements/package-runs/P0084';t=g/'tools/ftc6/p84'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=r/'P0084/private/final';b=r/'P0084/private/final-repeat';binary=r/'P0082/private/ftc6.bin'
expected=derive(binary,a/'instructions.tsv')
assert expected==json.loads((d/'address-evidence.json').read_text())
assert expected==derive(binary,b/'instructions.tsv')
assert expected['relative_switches'][0]['count']==25
assert expected['relative_switches'][0]['targets'][13]=='0x9f5cc'
assert expected['receive_nibble_map'][11]==14
for command,target in [('0x65','0xaaca5'),('0x79','0xaba09')]:
 row=next(x for x in expected['routes'] if x['type']=='0x41' and x['command']==command)
 assert row['staging_branch']==target
assert '0x2352,0x197b' in expected['operand_excerpts']['0xaaccc']
assert '0x234f,0x1cb0' in expected['operand_excerpts']['0xaba24']
with tempfile.TemporaryDirectory() as s:
 p=Path(s)/'bad';p.write_bytes(b'not the image')
 try:derive(p,a/'instructions.tsv')
 except ValueError:pass
 else:raise AssertionError('wrong image accepted')
 p.write_text('')
 try:derive(binary,p)
 except ValueError:pass
 else:raise AssertionError('missing operand evidence accepted')
ah={str(p.relative_to(a)):h(p) for p in a.rglob('*') if p.is_file()}
bh={str(p.relative_to(b)):h(p) for p in b.rglob('*') if p.is_file()}
assert ah==bh and len(ah)==273
assert 'NO_FUNCTION' not in (a/'requested.tsv').read_text()
for p in t.glob('*.py'):compile(p.read_text(),str(p),'exec')
log=(r/'P0084/private/rejected-bounds.log').read_text()
assert 'unqualified switch bounds' in log and 'SWITCH 9f315 index=' not in log
for name in ['review.md','design.md','functions.md','screen-cn22-trace.md','screen-cn105-parity-matrix.md','transport-comparison.md','open-questions.md','CHANGELOG.md']:
 assert (d/name).is_file()
v=dict(package='P0084',date='2026-10-11',result='PARTIAL',complete_display_parity='NOT ESTABLISHED',scope='offline only',live_requests=0,device_writes=0,firmware_deploys=0,checks=dict(manual_pages_visually_checked=[11,63],uart2_vector_entries='PASS',selected_get_set_routes='PASS',pump_staging_operands='PASS',service_candidate_route='PASS',wrong_image_rejected='PASS',missing_operand_evidence_rejected='PASS',bad_switch_bounds_rejected_readonly='PASS',fresh_project_replay='PASS',requested_functions_present='PASS',repeat_export_files=len(ah),repeat_export_equal=True,compact_derivation_repeat='PASS',python_syntax='PASS'),input_hashes={str(p.relative_to(r)):h(p) for p in [binary,r/'P0082/private/ftc6.mot',r/'P0083/private/OCH722A.pdf']},tool_hashes={p.name:h(p) for p in sorted(t.iterdir()) if p.is_file()},compact_evidence_sha256=h(d/'address-evidence.json'),private_export_hashes=ah,limitations=['D-path connector ownership unproved','20.01 candidate image versus physical21.00','Settings transaction/persistence/range checks incomplete','10–15 second display latency not timed or attributed','Decoder remains subset-qualified; assembly governs'])
(d/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
print('PASS: 273 identical exports, field/routes/vectors, negative input/bounds guards; parity remains NOT ESTABLISHED')
