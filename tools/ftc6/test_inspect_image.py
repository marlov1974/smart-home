"""P0082 tests use synthetic records, no vendor firmware."""
import unittest
from inspect_image import parse_srec

def record(address,payload):
    b=bytes([len(payload)+4])+address.to_bytes(3,'big')+payload
    return ('S2'+(b+bytes([255-(sum(b)&255)])).hex()+'\n').encode()
class SRecordTest(unittest.TestCase):
    def test_address(self):
        m,c,e,d=parse_srec(record(0x80000,b'\x04\xf3'))
        self.assertEqual(m,{0x80000:4,0x80001:243});self.assertEqual(d,0)
    def test_checksum(self):
        with self.assertRaisesRegex(ValueError,'checksum'):parse_srec(b'S2050800000400\n')
    def test_length(self):
        with self.assertRaisesRegex(ValueError,'count'):parse_srec(b'S20608000004ee\n')
    def test_conflict(self):
        with self.assertRaisesRegex(ValueError,'overlap'):parse_srec(record(0x80000,b'a')+record(0x80000,b'b'))
    def test_identical(self):
        self.assertEqual(parse_srec(record(0x80000,b'a')*2)[3],1)
    def test_sparse(self):
        m,*_=parse_srec(record(0x80000,b'a')+record(0xfffff,b'z'))
        self.assertEqual(len(m),2);self.assertNotIn(0x80001,m)
if __name__=='__main__':unittest.main()
