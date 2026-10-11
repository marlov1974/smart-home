import ast,hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from extract import Image,extract,SHA
from atlas import build
from uart6 import frame,room_value,target_value,decode
from uart1_snapshot import decode as snapshot
from addressing import bit_address
from source_result import decode as source_result
from source_tx import descriptors,pack_logical,call_sites
from settings_peer import advertisement,control_response
from verify_artifacts import verify
from settings_transfer import ranges as transfer_ranges,resolve,extended_fields,admitted
ROOT=Path(__file__).resolve().parents[3]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
energy=load('p86energy',ROOT/'tools/ftc6/p86/energy.py')
uart1=load('p86uart1',ROOT/'tools/ftc6/p86/uart1.py')
class Offline(unittest.TestCase):
    def test_extended_settings_direction(self):
        for selector in (0,1,589,1023):
            for direction in (0,1):
                for fmt in range(16):
                    word=(selector<<6)|(direction<<5)|(fmt<<1)|1
                    self.assertEqual(extended_fields(word),{'selector':selector,'format':fmt,'direction':direction})
                    self.assertTrue(admitted(word,direction,0x16,2))
                    self.assertFalse(admitted(word,1-direction,0x16,2))
                    self.assertFalse(admitted(word,direction,4,2))
                    self.assertFalse(admitted(word,direction,0x16,1))
        for word in (-1,0,65536):
            with self.assertRaises(ValueError):extended_fields(word)
    def test_public_artifacts(self):
        import shutil
        source=ROOT/'requirements/package-runs/P0088'
        self.assertEqual(verify(source)['result'],'PASS')
        with tempfile.TemporaryDirectory() as temporary:
            target=Path(temporary)
            for name in ('command-atlas.json','command-atlas.csv','atlas-ledger.md','coverage.json','source-tx-descriptors.json','structural-inventory.json'):
                shutil.copyfile(source/name,target/name)
            (target/'atlas-ledger.md').write_text('corrupt ledger\n')
            with self.assertRaises(ValueError):verify(target)
    def test_source_call_sites(self):
        row={'address':'82c2a'}
        listing='ram:0009bb9d\tPUSH.w #0x8\tram:0009b9a8\nram:0009bba1\tPUSH.w #0x2c2a\tram:0009b9a8\nram:0009bba5\tJSR.w 0x0009c228\tram:0009b9a8\n'
        self.assertEqual(call_sites([row],listing)[0]['qualified_call_sites'],['0009bb9d'])
        for bad in ('',listing.replace('0009bba1','0009bba2'),listing.replace('0x0009c228','0x0009c229')):
            with self.assertRaises(ValueError):call_sites([row],bad)
    def test_settings_advertisement(self):
        self.assertEqual(advertisement(1,0,0x20),(1,128))
        self.assertEqual(advertisement(1,1,0x20),(1,129))
        for state in range(13):
            for direction in range(2):
                self.assertEqual(advertisement(state,direction,255,True),(6,0))
                for mask in range(256):
                    fmt,value=advertisement(state,direction,mask)
                    self.assertEqual(value&1,direction)
                    self.assertEqual(fmt,1 if state==1 else 6)
                    self.assertLessEqual(value,509)
        for args in ((13,0,0),(0,2,0),(0,0,256)):
            with self.assertRaises(ValueError):advertisement(*args)
    def test_source_result(self):
        for selector in (0,27,28,149,1023):
            for fmt in range(8):
                word=selector | (fmt << 13)
                f=bytes([0x1d,word&255,word>>8,5,0])
                f+=bytes([-sum(f)&255])
                result=source_result(f)
                self.assertEqual((result['selector'],result['format'],result['raw_word_le']),(selector,fmt,5))
                for bad in (f[:-1],f+b'\0',f[:-1]+bytes([f[-1]^1])):
                    with self.assertRaises(ValueError):source_result(bad)
        with self.assertRaises(ValueError):source_result(bytes(6))
    def test_indexed_bit_address(self):
        self.assertEqual(bit_address(0x1367,6),(0x1367,6))
        self.assertEqual(bit_address(0xffff,8),(0,0))
        for index in range(32):self.assertEqual(bit_address(0x100,index),(0x100+index//8,index%8))
    def test_snapshot(self):
        for sub,n in [(0,100),(1,66),(2,62),(16,13)]:
            f=bytearray(n);f[:4]=bytes([0x12,n,sub,2]);f[-1]=-sum(f)&255
            self.assertEqual(snapshot(f)['subcommand'],sub)
            f[-1]^=1
            with self.assertRaises(ValueError):snapshot(f)
            with self.assertRaises(ValueError):snapshot(f[:-1])
    def test_wrong_image(self):
        for b in (b'',bytes(0x80000)):
            with self.assertRaises(ValueError):Image(b)
    def test_uart6_all_bytes(self):
        for b in range(256):
            self.assertEqual(room_value(b),None if b==255 else 50*(min(208,max(128,b))-128))
            self.assertEqual(target_value(b),50*(b-128) if 128<=b<=248 else None)
    def test_uart6_envelope(self):
        p=bytes([0x27,128,130,140,150,160,170,208,255]+[0]*7)
        f=bytes.fromhex('fc48040310')+p;f+=bytes([-sum(f[1:])&255])
        self.assertEqual(decode(f)['room_centi_c'],[0,100,600,1100,1600,2100,4000,None])
        for bad in (f[:-1],f+b'\0',bytes([0])+f[1:],f[:3]+b'\x7a'+f[4:],f[:-1]+bytes([f[-1]^1])):
            with self.assertRaises(ValueError):decode(bad)
    def test_regression_energy_side_effect(self):
        self.assertEqual(energy.fold(59),0)
        self.assertEqual(energy.fold(60),1)
        self.assertLess(energy.fold(59)*2,energy.fold(118))
        self.assertFalse(energy.pair(520,0x0001,0x2300)['atomic'])
    def test_regression_near_alias(self):
        self.assertEqual(uart1.effective_addresses(0x81234,2),[0x1234,0x1235])
        with self.assertRaises(ValueError):uart1.memory(0x81234,2)
    def test_no_transport_imports(self):
        forbidden={'socket','serial','requests','urllib','http','subprocess'}
        for p in Path(__file__).parent.glob('*.py'):
            tree=ast.parse(p.read_text())
            for n in ast.walk(tree):
                if isinstance(n,ast.Import):self.assertFalse(forbidden.intersection(a.name.split('.')[0] for a in n.names))
                if isinstance(n,ast.ImportFrom):self.assertNotIn((n.module or '').split('.')[0],forbidden)
class LocalImage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        cls.path=os.environ.get('P88_IMAGE');cls.catalog=os.environ.get('P88_CATALOG')
        if not cls.path or not cls.catalog:raise unittest.SkipTest('P88_IMAGE and P88_CATALOG needed for private-ROM checks')
        cls.image=Image(Path(cls.path).read_bytes())
    def test_anchor_routes(self):
        inv=extract(self.image);m={(x['frame'],x['opcode']):x for x in inv['cn105_routes']}
        for c,i in [('07',0x3b),('15',0x49),('65',0x73),('79',0x87),('a3',0x8f)]:self.assertEqual(m['42',c]['internal'],i)
        self.assertEqual(sum(t['count'] for t in inv['tables']),256)
        self.assertEqual(len(inv['cn105_routes']),512)
    def test_corrupt_table(self):
        b=bytearray(self.image.data);b[0x96a8]^=1
        with self.assertRaises(ValueError):Image(bytes(b))
        # Exercise structural rejection independently of the image identity gate.
        fake=object.__new__(Image);b=bytearray(self.image.data);b[0x92ad:0x92b1]=bytes(4);fake.data=bytes(b)
        with self.assertRaises(ValueError):extract(fake)
    def test_bounds(self):
        for a,n in [(0x7ffff,1),(0x100000,1),(0x80000,-1)]:
            with self.assertRaises(ValueError):self.image.at(a,n)
    def test_source_tx(self):
        rows=descriptors(self.image)
        self.assertEqual(len(rows),37)
        self.assertEqual(sum(len(r['fields']) for r in rows),249)
        target=next(r for r in rows if r['address']=='82c2a')
        values={('memory-byte',0x39a7):0,('callback',0x9a336):70,
                ('callback',0x9a36a):30,('callback',0x9a39e):64,('callback',0x9a3d2):14}
        self.assertEqual(pack_logical(target,values),bytes.fromhex('05465e400e09'))
        with self.assertRaises(KeyError):pack_logical(target,{})
        for r in rows:
            values={(f['kind'],f['source']):255 for f in r['fields'] if f['kind']!='constant'}
            packed=pack_logical(r,values)
            self.assertEqual(len(packed),r['length'])
            if r['checksum_kind']:self.assertEqual(sum(packed)&255,0 if r['checksum_kind']==1 else 255)
    def test_settings_transfer_ranges(self):
        table=transfer_ranges(self.image)
        self.assertEqual(len(table),33)
        self.assertEqual(resolve(table,0)['kind'],'end-marker')
        self.assertEqual(resolve(table,120)['staging_address'],0x1979)
        self.assertEqual(resolve(table,589)['staging_address'],0x1979)
        self.assertEqual(resolve(table,1000)['kind'],'unmapped')
        covered=set()
        for selector in range(1,1024):
            result=resolve(table,selector)
            matching=[r for r in table if r['first']<=selector<=r['last']]
            self.assertEqual(result['kind']=='triple',bool(matching))
            if matching:
                self.assertEqual(result['range_index'],matching[0]['index'])
                covered.update(range(result['staging_address'],result['staging_address']+3))
        self.assertIn(0x197b,covered)
        self.assertNotIn(0x1cb0,covered)
        for row in table:
            self.assertEqual(resolve(table,row['first'])['staging_address'],row['staging_first'])
            self.assertEqual(resolve(table,row['last'])['staging_address']+2,row['staging_last'])
        fake=object.__new__(Image);data=bytearray(self.image.data)
        data[0x7ec:0x7ee]=bytes(2);fake.data=bytes(data)
        with self.assertRaises(ValueError):transfer_ranges(fake)
    def test_settings_response_matrix(self):
        actions=set()
        for state in range(13):
            for direction in range(2):
                for selector in (1002,1003,1004,0,9999,100):
                    for argument in range(4):
                        r=control_response(self.image,state,direction,selector,argument,(6,0xac,0x55))
                        actions.add(r['action'])
                        self.assertEqual(len(r['result']),3)
                        self.assertTrue(all(0<=x<=255 for x in r['result']))
                        if r['action']==9:self.assertEqual(r['result'],(6,0xac,0x55))
        self.assertEqual(actions,{0,1,2,4,5,9,10,11})
        with self.assertRaises(ValueError):control_response(self.image,13,0,0,0,(0,0,0))
    def test_missing_ref(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):build(self.image,Path(d))
    def test_determinism_schema(self):
        a=build(self.image,Path(self.catalog));b=build(self.image,Path(self.catalog));self.assertEqual(a,b)
        rows=a[1];self.assertEqual(len(rows),len({r['id'] for r in rows}))
        required={'wire','rx_fields','tx_fields','accepted_predicate','gates','completion','side_effects','baseline','physical_validation','evidence'}
        for r in rows:self.assertTrue(required<=r.keys())
        for s in a[0]['switches']:
            self.assertEqual(len([r for r in rows if r['id'].startswith(s['id']+'.')]),s['count'])
if __name__=='__main__':unittest.main()
