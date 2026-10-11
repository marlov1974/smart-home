"""P0085 reproducibility/identity/negative-input verification. Offline only."""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from evidence import derive


def verify(binary, first, second, report):
    def snapshot(root):
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob('*') if p.is_file()}
    a, b = snapshot(first), snapshot(second)
    if not a or a != b:
        raise ValueError('Nonidentical or missing exports')
    requested=(first/'requested.tsv').read_text().splitlines()
    if not requested or any('NO_FUNCTION' in line for line in requested):
        raise ValueError('Unresolved requested function')
    result=derive(binary, first/'instructions.tsv')
    evidence=report/'address-evidence.json'
    if json.loads(evidence.read_text()) != result:
        raise ValueError('Published evidence differs')
    with tempfile.TemporaryDirectory() as directory:
        bad=Path(directory)/'bad.bin'; bad.write_bytes(b'not the qualified image')
        try: derive(bad, first/'instructions.tsv')
        except ValueError: pass
        else: raise AssertionError('Wrong input accepted')
        missing=Path(directory)/'missing.tsv';missing.write_text('')
        try: derive(binary,missing)
        except ValueError: pass
        else: raise AssertionError('Missing instructions accepted')
        changed=Path(directory)/'changed.tsv'
        changed.write_text((first/'instructions.tsv').read_text().replace('MOV.b #0x65,0x0248','MOV.b #0x15,0x0248'))
        try: derive(binary,changed)
        except ValueError: pass
        else: raise AssertionError('Changed operand accepted')
    verification={'package':'P0085','result':'PASS','research_result':'PARTIAL',
        'image_sha256':result['image_sha256'],'identical_export_files':len(a),
        'requested_functions':len(requested),'vector_checks':len(result['vectors']),
        'exact_operand_checks':len(result['operands']),
        'negative_tests':['wrong-image rejected','missing-instructions rejected','changed-UART-mode rejected'],
        'export_manifest_sha256':hashlib.sha256(json.dumps(a,sort_keys=True).encode()).hexdigest(),
        'live_requests':0,'device_writes':0,'cloud_access':False,
        'vendor_firmware_published':False,'decoder_changes':False,
        'areas':{'hardware':'PARTIAL','protocol':'PARTIAL','rights':'PARTIAL','evidence':'PASS'},
        'limits':['20.01 static image differs from installed21.00','UART0/UART1/D connector ownership unknown',
                  'CNIT purpose and privileges unknown','No physical tests','Full far-pointer decoder semantics unqualified']}
    (report/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    print(json.dumps(verification,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('binary','first','second','report'):p.add_argument(name,type=Path)
    a=p.parse_args();verify(a.binary,a.first,a.second,a.report)
