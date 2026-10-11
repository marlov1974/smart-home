"""P0083: hash-gated, compact derived evidence; no firmware or full listing export."""
import argparse
import hashlib
import json
from pathlib import Path

IMAGE_SHA = 'd828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a'
BASE = 0x80000

def read_image(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != IMAGE_SHA:
        raise ValueError('Not the qualified P0082 FF-filled image')
    return data

def extract(data):
    def at(address, size):
        return data[address-BASE:address-BASE+size]
    def u32(raw):
        return int.from_bytes(raw, 'little')
    routes=[]
    for command in (7, 0x15, 0x65, 0x79, 0xa1, 0xa2, 0xa3):
        index=at(0x84c56+command,1)[0]
        matches=[]
        for row in range(15):
            address=0x892a8+row*59
            rec=at(address,59)
            if rec[0:2]==bytes([0xfc,0x42]) and rec[2]<=command<=rec[3]:
                internal=rec[9+index]
                tx=at(0x84d56+internal*16,16)
                assert tx[0]==internal and tx[1]==0x62 and tx[2]==22
                matches.append(dict(command=hex(command),input_descriptor=hex(address),lookup_index=index,
                                    internal_id=hex(internal),output_descriptor=hex(0x84d56+internal*16),
                                    header=hex(u32(tx[4:8])),packer=hex(u32(tx[8:12])),checksum=hex(u32(tx[12:16]))))
        assert len(matches)==1
        routes+=matches
    classes=[]
    for code in (17,18,19,27,28,52,54,175,176,340,506,511,520,521,522,523,524,525,526,527,528,529,530,531,532,540,550):
        for i in range(26):
            rec=at(0x806ac+i*3,3)
            if code<=int.from_bytes(rec[:2],'little'):
                classes.append(dict(selector=code,class_id=rec[2],table_row=hex(0x806ac+i*3)));break
    return dict(image_binary_sha256=IMAGE_SHA,version_caution='image 20.01 candidate; physical P0081 FTC21.00',get_routes=routes,service_classes=classes)

def targets(data):
    def ptr(a):return int.from_bytes(data[a-BASE:a-BASE+4],'little')
    out=set()
    for i in range(151):
        assert data[0x4d56+i*16]==i
        out.update(ptr(0x84d56+i*16+j) for j in (4,8,12))
    for i in range(15):out.add(ptr(0x892a8+i*59+5))
    for i in range(4):out.update(ptr(0x859c0+i*18+j) for j in (2,6,10,14))
    for i in (0,6,15,16,22,31,32):out.update(ptr(0x87a60+i*21+j) for j in (5,9,13,17))
    out.update((0xa4f3c,0xa4f68,0xa535e))
    assert all(BASE<=a<0x100000 for a in out)
    return ','.join(f'{a:x}' for a in sorted(out))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('output',type=Path);p.add_argument('--targets',type=Path)
    a=p.parse_args();b=read_image(a.binary)
    a.output.write_text(json.dumps(extract(b),indent=2)+'\n')
    if a.targets:a.targets.write_text(targets(b)+'\n')
