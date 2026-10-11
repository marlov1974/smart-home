"""Evidence regressions: prevent empty telemetry and configuration becoming measurements."""
import json,os,unittest
from pathlib import Path
import overview,field_audit,name_registry
class FieldAuditTests(unittest.TestCase):
    def test_inventory_partition_and_original_evidence_preserved(self):
        d=json.loads((overview.OUT/'field-purpose-audit.json').read_text())
        remaining={r['id'] for r in d['remaining']}
        raw=[f for f in name_registry.build()['fields'] if f['original_field']['name']=='unresolved response byte']
        self.assertEqual(len(raw),996)
        self.assertEqual({f['source_row'] for f in raw if not f['purpose_trace']},remaining)
        self.assertEqual(d['counts']['new_classified_occurrences']+len(remaining)+31,996)
        self.assertEqual((overview.OUT/'field-purpose-audit.md').read_text(),field_audit.render(d))
    def test_semantic_boundaries_and_motor_pair(self):
        d=json.loads((overview.OUT/'field-purpose-audit.json').read_text())['bindings']
        for pack in ('a5f1a','a5f8c','a5ff6','a6068'):
            self.assertEqual(d[pack+':1']['kind'],'protokoll')
            self.assertIn('alltid noll',d[pack+':1']['purpose'])
        self.assertIn('inte uppmätt live-COP',d['a8008:3']['purpose'])
        self.assertIn('inte bevis på maximal effekt',d['a55c2:8']['purpose'])
        for p in (8,9):self.assertIn('00/01 stopp,10 öppna,11 stäng',d[f'a5bf8:{p}']['purpose'])
        self.assertNotIn('a901e:4',d) # A constant is not automatically an understood capability.
    @unittest.skipUnless(os.getenv('P89_PRIVATE'),'private exports absent')
    def test_reproduce_and_independent_native_witnesses(self):
        root=Path(os.environ['P89_PRIVATE']);d=field_audit.build(root)
        self.assertEqual(json.loads((overview.OUT/'field-purpose-audit.json').read_text()),d)
        get=root.parent.parent/'P0088/private/getters'
        self.assertIn('MOV.b 0,-0x1[FB]',(get/'a4cd2.asm').read_text())
        self.assertIn('CMP.w #0xc8',(root/'field-leaves/c83f6.asm').read_text())
        self.assertIn('CMP.w #0xff9c',(root/'field-leaves/c8478.asm').read_text())
        self.assertIn('MOV.w 0x2640,0x2630',(root/'field-final/c371c.asm').read_text())
if __name__=='__main__':unittest.main()
