from pathlib import Path
import hashlib,json,subprocess,tempfile
r=Path.cwd();g=r/'P0080/implementation-smart-home';d=g/'requirements/package-runs/P0083';t=g/'tools/ftc6/p83'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(*a,ok=True):
 p=subprocess.run(['python3',*map(str,a)],capture_output=True,text=True)
 assert (p.returncode==0)==ok,p.stderr
 return p
with tempfile.TemporaryDirectory() as tmp:
 z=Path(tmp);out=z/'out.json'
 run(t/'extract_evidence.py',r/'P0082/private/ftc6.bin',out,'--targets',z/'seeds')
 assert out.read_bytes()==(d/'address-evidence.json').read_bytes()
 assert (z/'seeds').read_bytes()==(r/'P0083/private/repro-targets.txt').read_bytes()
 run(t/'crosscheck.py',r/'P0081/mapping-20261010T205704Z/direct/readings.jsonl',out)
 assert out.read_bytes()==(d/'physical-crosscheck.json').read_bytes()
 bad=z/'bad';bad.write_bytes(b'not qualified')
 run(t/'extract_evidence.py',bad,out,ok=False)
 run(t/'patch_module.py',bad,z/'module',ok=False)
 assert not (z/'module').exists()
 rows=[json.loads(l) for l in (r/'P0081/mapping-20261010T205704Z/direct/readings.jsonl').read_text().splitlines()]
 a=next(x for x in rows if x['code']==7);b=bytearray.fromhex(a['raw_rx']);b[-1]^=1;a['raw_rx']=b.hex();bad.write_text(json.dumps(a)+'\n')
 run(t/'crosscheck.py',bad,out,ok=False)
 for p in t.glob('*.py'):compile(p.read_text(),str(p),'exec')
 run(t/'make_vectors.py',z/'vectors')
 assert (z/'vectors').read_bytes()==(r/'P0083/private/vectors2.bin').read_bytes()
a={str(p.relative_to(r/'P0083/private/final')):h(p) for p in (r/'P0083/private/final').rglob('*') if p.is_file()}
b={str(p.relative_to(r/'P0083/private/final-repeat')):h(p) for p in (r/'P0083/private/final-repeat').rglob('*') if p.is_file()}
assert a==b and len(a)==366
log=(r/'P0083/private/vectors-final.log').read_text();assert log.count('PASS case=')==11 and log.count('PASS ROT n=')==20
v=dict(package='P0083',date='2026-10-11',result='PASS for offline deliverables; research tracks PARTIAL',tracks=dict(A='PARTIAL',B='PARTIAL',C='PARTIAL'),live_requests=0,device_writes=0,firmware_deploys=0,tests=dict(decoder_cases=11,rotate_emulation_cases=20,repeat_export_files=366,repeat_export_equal=True,compact_extraction_repeat='PASS',historical_frames=12,historical_derivation_repeat='PASS',bad_image_rejected='PASS',bad_module_rejected_without_output='PASS',bad_frame_checksum_rejected='PASS',python_syntax='PASS',synthetic_fixture_repeat='PASS'),input_hashes={str(p.relative_to(r)):h(p) for p in [r/'P0082/private/ftc6.mot',r/'P0082/private/ftc6.id',r/'P0082/private/ftc6.bin']},tool_hashes={p.name:h(p) for p in sorted(t.iterdir()) if p.is_file()},evidence_hashes={p.name:h(p) for p in [d/'address-evidence.json',d/'physical-crosscheck.json']},private_export_hashes=a,limitations=['Image 20.01 candidate versus physical FTC21.00','No exact board attribution','Decoder subset only','UART ownership, settings write path and accounting boundary unresolved'])
(d/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
print('PASS: 31 decoder checks, 366 identical exports, deterministic derivations and negative guards')
