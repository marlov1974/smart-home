"""P0089 breadth inventory conservation and claim boundaries."""
import json
import unittest
import overview
from function_names import SETTINGS
from service_names import NAMES

class OverviewTests(unittest.TestCase):
    def test_conserves_routes_and_adds_connection(self):
        data=overview.build()
        old=json.loads((overview.P88/'command-port-matrix.json').read_text())
        expected={r['id'] for r in old['rows'] if r['path']=='uart2'}|{'uart2.frame.5a'}
        actual=[r['id'] for r in data['rows']]
        self.assertEqual(set(actual),expected)
        self.assertEqual(len(actual),len(expected))
        self.assertEqual(sum(data['counts'].values()),len(expected))
    def test_paired_blocks_and_partial_names(self):
        rows={r['id']:r for r in overview.build()['rows']}
        for op, (name, status, proof, caveat) in SETTINGS.items():
            for typ in ('41','42'):
                row=rows[f'uart2.{typ}.{op}']
                self.assertEqual(row['name'],name)
                self.assertEqual(row['status'],status)
                self.assertIn(proof,row['evidence'])
                self.assertIn(caveat,row['function'])
        self.assertEqual(rows['uart2.42.65']['status'],'namngiven del')
        self.assertEqual(rows['uart2.42.78']['status'],'identifierad')
        self.assertEqual(rows['uart2.42.57']['status'],'trolig')
    def test_service_boundaries(self):
        rows=overview.build()['services']
        codes=[r['code_decimal'] for r in rows]
        self.assertEqual(len(codes),len(set(codes)))
        self.assertTrue(all(c<700 for c in codes))
        bycode={r['code_decimal']:r for r in rows}
        self.assertEqual(bycode[27]['name'],'Brine in TH32')
        self.assertIn('avvisar',bycode[200]['routing'])
        for code in (340,342,343,344):
            self.assertIn('Nollställning',bycode[code]['side_effect'])
        self.assertIn('fold',bycode[520]['side_effect'])
        self.assertEqual(sum(r['naming_status']=='manualnamn' for r in rows),len(NAMES))
    def test_artifacts_reproduce(self):
        data=overview.build()
        self.assertEqual(json.loads((overview.OUT/'cn105-function-overview.json').read_text()),data)
        self.assertEqual((overview.OUT/'cn105-function-overview.md').read_text(),overview.render(data))


class NamingEvidenceTests(unittest.TestCase):
    def test_all_setting_pairs_have_at_least_a_qualified_name(self):
        rows={r['id']:r for r in overview.build()['rows']}
        for op in range(0x50,0x7f):
            for typ in ('41','42'):
                self.assertNotIn(rows[f'uart2.{typ}.{op:02x}']['status'],('okänd','familj känd'))
    def test_sd_evidence_matches_published_names_and_warns_about_cop(self):
        from sd_names import ROWS
        d=json.loads((overview.OUT/'sd-tool-correlation.json').read_text())
        self.assertEqual({r['command'] for r in d['rows']},set(ROWS))
        for r in d['rows']:
            self.assertEqual(r['name'],SETTINGS[r['command']][0])
            self.assertTrue(set(r['symbols'].values()) <= set(r['offsets_decimal']))
        for op in ('6c','6d'):self.assertIn('INTE live-COP',SETTINGS[op][3])
    def test_fault_status_pointer_and_callback_are_not_direct_reference_assumptions(self):
        d=json.loads((overview.OUT/'fault1b-trace.json').read_text())
        b=bytes.fromhex(d['descriptor_hex'])
        self.assertEqual(int.from_bytes(b[2:4],'little'),0x49b6)
        self.assertEqual(int.from_bytes(b[9:13],'little'),0x882fc)
        self.assertEqual(int(d['descriptor_base'],16)+d['descriptor_index']*d['stride'],int(d['descriptor_address'],16))
        self.assertTrue({'d2c00','d2d5a','acb52'} <= set(d['functions']))
    def test_additional_service_resets_remain_side_effectful(self):
        rows={r['code_decimal']:r for r in overview.build()['services']}
        for code in (341,532):self.assertIn('Nollställning',rows[code]['side_effect'])
        self.assertIn('fold',rows[520]['side_effect'])
        self.assertEqual(rows[570]['name'],'Primärpumpens återrapporterade signal vid fel')

    def test_a3_service_controls_keep_uncertainty_and_side_effects(self):
        rows={r['code_decimal']:r for r in overview.build()['services']}
        for code in range(350,364):
            self.assertIn('inte mätfråga',rows[code]['side_effect'])
            self.assertEqual(rows[code]['naming_status'],'namngiven del')
        self.assertIn('ej verifierat på Geodan',rows[351]['description'])
        for code in range(352,364):
            self.assertIn('fysisk funktion okänd',rows[code]['description'])
        self.assertEqual(rows[536]['naming_status'],'trolig')
        self.assertIn('0692',rows[536]['evidence'][0])

    def test_a3_indirect_descriptor_locations(self):
        evidence=json.loads((overview.OUT/'a3-naming-evidence.json').read_text())
        b=bytes.fromhex(evidence['descriptor_hex'])
        fields={int.from_bytes(b[n+2:n+6],'little'):(b[n],b[n+1])
                for n in range(6,len(b)-6,6)}
        # Decode existing firmware records, not generated name-table labels.
        self.assertEqual(fields[0x3a00],(9,0x12))
        self.assertEqual(fields[0x3a01],(11,0x12))
        self.assertEqual(fields[0x39ff],(13,0x12))
        self.assertEqual(fields[0x39fe],(17,0x13))
        self.assertEqual(b[-6],0xff)

if __name__=='__main__':unittest.main()
