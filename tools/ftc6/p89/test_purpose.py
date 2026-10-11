"""P0089 regressions for native purpose traces and uncertainty preservation."""
import json
import os
from pathlib import Path
import unittest
import overview
import name_registry
import purpose_report
from purpose_fields import PURPOSES

class PurposeTests(unittest.TestCase):
    def test_descriptors_bind_to_actual_state_and_callable_rom(self):
        d=json.loads((overview.OUT/'purpose-analysis.json').read_text())
        self.assertEqual(len(d['fields']),31)
        for field in d['fields']:
            for record in field['descriptors']:
                raw=bytes.fromhex(record['hex'])
                self.assertEqual(int.from_bytes(raw[2:4],'little'),int(record['state_pointer'],16))
                self.assertEqual(int.from_bytes(raw[9:13],'little'),int(record['callback_table'],16))
                table=bytes.fromhex(record['callback_hex'])
                for start in range(2,30,4):
                    self.assertTrue(0x80000 <= int.from_bytes(table[start:start+4],'little') < 0x100000)
        self.assertEqual((overview.OUT/'purpose-analysis.md').read_text(),purpose_report.render(d))
    def test_registrations_cover_each_new_purpose_once_without_inventing_missing_fields(self):
        fields=[f for f in name_registry.build()['fields'] if f['purpose_trace'] and 'state_pointer' in f['purpose_trace']]
        keys=[(f['purpose_trace']['opcode'],f['purpose_trace']['position']) for f in fields]
        self.assertEqual(len(keys),len(set(keys)))
        self.assertEqual(len(keys),31)
        self.assertEqual({p for op,p in keys if op=='17'},set(range(1,11))|{13})
        self.assertEqual({p for op,p in keys if op=='18'},set(range(1,13)))
        self.assertIn(('19',4),keys)
        self.assertIn(('19',5),keys)
        for f in fields:self.assertEqual(f['name_kind'],'syfte följt i kod')
    @unittest.skipUnless(os.getenv('P89_PRIVATE'),'private firmware/export fixtures absent')
    def test_private_native_evidence_reproduces(self):
        actual=purpose_report.build(Path(os.environ['P89_PRIVATE']))
        self.assertEqual(json.loads((overview.OUT/'purpose-analysis.json').read_text()),actual)
        base=Path(os.environ['P89_PRIVATE'])/'purpose-next'
        self.assertIn('CMP.w #0x1f40,0x662',(base/'b7e76.asm').read_text())
        self.assertIn('CMP.w #0x1d4c,0x668',(base/'b812e.asm').read_text())
        self.assertIn('SUB.w 0x680,R0',(base/'cadf4.asm').read_text())
        self.assertIn('CMP.w #0xfe0c,R0',(base/'cadf4.asm').read_text())

if __name__=='__main__':unittest.main()
