"""P0089 naming coverage without upgrading evidence."""
import json
import unittest
import overview
import name_registry

class RegistryTests(unittest.TestCase):
    def test_names_cover_commands_services_and_every_catalogued_field(self):
        d=name_registry.build()
        atlas=json.loads((overview.P88/'command-atlas.json').read_text())
        expected={f'{r["id"]}/{k}/{i}':(f,r) for r in atlas['rows'] if r['path']=='uart2'
                  for k in ('rx_fields','tx_fields') for i,f in enumerate(r[k])}
        self.assertEqual({f['id'] for f in d['fields']},set(expected))
        for kind in ('commands','services','fields'):
            self.assertTrue(all(r['name'].strip() for r in d[kind]))
        self.assertEqual(len(d['fields']),len(expected))
        for f in d['fields']:
            original,row=expected[f['id']]
            self.assertEqual(f['original_field'],original)
            self.assertEqual(f['evidence'],row['evidence'])
            if original['name']=='unresolved response byte' and not f['purpose_trace']:
                self.assertEqual(f['semantic_status'],'Fysisk betydelse okänd')
                self.assertEqual(f['name_kind'],'tekniskt positionsnamn')
    def test_artifacts_reproduce(self):
        d=name_registry.build()
        self.assertEqual(json.loads((overview.OUT/'name-registry.json').read_text()),d)
        self.assertEqual((overview.OUT/'name-registry.md').read_text(),name_registry.render(d))
    def test_short_names_preserve_service_description_and_uncertainty(self):
        d=name_registry.build();s={r['code_decimal']:r for r in d['services']}
        self.assertIn('Geodan obekräftat',s[351]['name'])
        self.assertIn('ej verifierat på Geodan',s[351]['description'])
        self.assertEqual(s[351]['naming_status'],'namngiven del')
        self.assertIn('inte mätfråga',s[351]['side_effect'])

if __name__=='__main__':unittest.main()
