"""P0069: read vendor updater IL without executing the updater or accessing serial ports."""
from pathlib import Path
import zipfile
import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes
ROOT=Path(__file__).resolve().parents[1]

def main():
    with zipfile.ZipFile(ROOT/'reference/original/Proon+Firmware+Update+Tool+(v3.1.05).zip') as z:
        name=next(n for n in z.namelist() if n.endswith('/FirmwareDownloader.dll'))
        pe=dnfile.dnPE(data=z.read(name))
    def resolve(token):
        if not hasattr(token,'value'):return str(token)
        v=token.value
        if v>>24==0x70:return repr(pe.net.user_strings.get(v&0xffffff).value)
        table={4:pe.net.mdtables.Field,6:pe.net.mdtables.MethodDef,10:pe.net.mdtables.MemberRef}.get(v>>24)
        return str(table.rows[(v&0xffffff)-1].Name) if table else str(token)
    lines=['P0069 vendor updater IL; offsets below are method-relative IL offsets.']
    for row in pe.net.mdtables.MethodDef.rows:
        if str(row.Name) not in ('init_serialport','buttonProgram_Click','backgroundWorker1_DoWork'):continue
        lines.append(f'\nMETHOD {row.Name} RVA={row.Rva:#x}')
        for ins in CilMethodBody(CilMethodBodyReaderBytes(pe.get_data(row.Rva))).instructions:
            lines.append(f'{ins.offset:#x} {ins.opcode.name} {resolve(ins.operand)}')
    out=ROOT/'analysis';out.mkdir(exist_ok=True)
    (out/'updater-il.txt').write_text('\n'.join(lines)+'\n')
    print('PASS updater IL extracted statically; no updater execution or device access')

if __name__=='__main__':main()
