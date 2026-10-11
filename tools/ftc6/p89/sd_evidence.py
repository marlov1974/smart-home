"""Extract selected vendor symbol evidence without executing the Windows program.
Requires dnfile/dncil; optional private input, no hardware access.
"""
import argparse,hashlib,json
from pathlib import Path
from sd_names import ROWS
import overview
EXPECTED='823c2b3613630341ddf08db17d77e144c5c47ca0a0a54cbfe3a560e016f87102'
SOURCE='https://www.nukumi.cz/data/files/26/software-s-nazvem-ecodan-sd-tool-pro-ftc6-1757948609.zip?v=c7fc5bae'
def build(path):
    import dnfile
    from dncil.cil.body import CilMethodBody
    from dncil.cil.body.reader import CilMethodBodyReaderBytes
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=EXPECTED:raise ValueError('wrong SD tool executable')
    pe=dnfile.dnPE(data=data)
    constants={id(c.Parent.row):c.Value.value for c in pe.net.mdtables.Constant}
    enums={}; methods={}
    for t in pe.net.mdtables.TypeDef:
        name=str(t.TypeName)
        if name.startswith('SD_') or name=='ItemCode':
            enums[name]={str(f.row.Name):int.from_bytes(constants[id(f.row)],'little') for f in t.FieldList if id(f.row) in constants}
        if name=='RCFile':
            for m in t.MethodList:
                method=m.row
                if str(method.Name) not in ('SDRead','ReadINIT','ReadHOL','ReadSER1','ReadSER2','ReadSCH'):continue
                body=CilMethodBody(CilMethodBodyReaderBytes(pe.get_data(method.Rva)))
                methods[str(method.Name)]={'token':f'06000000+{m.row_index:x}','rva':f'{method.Rva:x}','sha256':hashlib.sha256(pe.get_data(method.Rva,body.size)).hexdigest()}
    rows=[]
    for op,(name,enum,offsets,packer,status) in ROWS.items():
        symbols={k:v for k,v in enums[enum].items() if v in offsets}
        rows.append(dict(command=op,name=name,status=status,packer=packer,enum=enum,offsets_decimal=offsets,symbols=symbols))
    return dict(source=SOURCE,archive_sha256='4ebfb4e89f4a584ed8fe6ddf5b925fa845df39ecff8ec4c95b134bf5738cea3d',exe_sha256=EXPECTED,version='FTC6 SD Tool 1.01 basic (2020)',methods=methods,rows=rows,limitation='Symbol and format correlation, not live validation. Shared staging addresses require category. Vendor files stay private.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('exe',type=Path);a=p.parse_args()
    result=build(a.exe)
    (overview.OUT/'sd-tool-correlation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(result["rows"])} command correlations, {len(result["methods"])} serializer method hashes')
