"""Offline checks for the Shelly four-quarter field-runner contract."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


RUNNER=Path(__file__).resolve().parents[1]/'tools'/'run_shelly_energy.py'


def load_runner():
    spec=importlib.util.spec_from_file_location('run_shelly_energy_unit',RUNNER)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeShelly:
    """Small stateful RPC model for the host runner's mutation boundary."""
    def __init__(self):
        self.code='original Script 7 source'
        self.config={'id':7,'name':'original-name','enable':True}
        self.running=False
        self.serial={'id':100,'mode':'mb_client','serial':{'baud':9600,'format':'8N1'}}
        self.kvs={'vp.energy.plan':'previous-plan','vp.energy.status':'previous-status'}
        self.calls=[]
        self.fail_next_put=False

    def __call__(self,method,params=None,retries=5):
        params=params or {}
        self.calls.append((method,params))
        if method=='Script.GetCode':
            offset=params['offset'];length=params['len'];data=self.code[offset:offset+length]
            return {'data':data,'left':offset+len(data)<len(self.code)}
        if method=='Script.GetConfig': return dict(self.config)
        if method=='Script.GetStatus': return {'running':self.running,'errors':[]}
        if method=='Script.Stop': self.running=False;return {}
        if method=='Script.Start':
            if 'var VALIDATEONLY = 1;' in self.code:
                self.kvs['vp.energy.status']='v=1|phase=validated|q=0'
                self.running=False
            else:
                self.running=True
            return {}
        if method=='Script.SetConfig':
            self.config.update(params['config']);return {}
        if method=='Script.PutCode':
            if self.fail_next_put:
                self.fail_next_put=False
                raise RuntimeError('injected upload failure')
            if params.get('append'): self.code+=params['code']
            else: self.code=params['code']
            return {}
        if method=='Serial.GetConfig': return json.loads(json.dumps(self.serial))
        if method=='KVS.Get':
            if params['key'] not in self.kvs: raise RuntimeError('not found')
            return {'value':self.kvs[params['key']]}
        if method=='KVS.Set': self.kvs[params['key']]=params['value'];return {}
        if method=='KVS.Delete': self.kvs.pop(params['key'],None);return {}
        raise AssertionError((method,params))


class RunShellyEnergyTest(unittest.TestCase):
    def setUp(self):
        self.runner=load_runner()

    def test_plan_encoder_is_exact_and_strict(self):
        self.assertGreaterEqual(self.runner.VALIDATION_TIMEOUT_SECONDS,60)
        raw=self.runner.encode_plan(17,1800000000,(1500,2000,2500,4000))
        self.assertEqual(
            raw,
            'v=1|rev=17|start=1800000000|q0=1500|q1=2000|q2=2500|q3=4000',
        )
        self.assertEqual(self.runner.aligned_plan_start(1800000899),1800000000)
        for revision in (0,2147483648,True,1.0):
            with self.subTest(revision=revision),self.assertRaises(ValueError):
                self.runner.encode_plan(revision,1800000000,(1500,2000,2500,4000))
        for start in (1799999999,1800000001,True):
            with self.subTest(start=start),self.assertRaises(ValueError):
                self.runner.encode_plan(1,start,(1500,2000,2500,4000))
        for quarters in (
            (1500,2000,2500),
            (1499,2000,2500,4000),
            (1500,2000,2500,6001),
            (1500,2000,True,4000),
        ):
            with self.subTest(quarters=quarters),self.assertRaises(ValueError):
                self.runner.encode_plan(1,1800000000,quarters)

    def test_plan_is_set_then_read_back_byte_for_byte(self):
        calls=[]
        raw='v=1|rev=17|start=1800000000|q0=1500|q1=2000|q2=2500|q3=4000'
        def fake_rpc(method,params=None,retries=5):
            calls.append((method,params))
            if method=='KVS.Get': return {'value':raw}
            return {}
        self.runner.rpc=fake_rpc
        self.assertEqual(self.runner.set_plan(raw),{'value':raw})
        self.assertEqual(
            calls,
            [
                ('KVS.Set',{'key':'vp.energy.plan','value':raw}),
                ('KVS.Get',{'key':'vp.energy.plan'}),
            ],
        )

        self.runner.rpc=lambda method,params=None,retries=5: (
            {'value':'different'} if method=='KVS.Get' else {}
        )
        with self.assertRaisesRegex(RuntimeError,'readback mismatch'):
            self.runner.set_plan(raw)

    def test_cleanup_does_not_overwrite_a_plan_rolled_by_l4(self):
        writes=[]
        self.runner.kvs_snapshot=lambda key: {'present':True,'value':'newer-plan'}
        self.runner.rpc=lambda method,params=None,retries=5: writes.append((method,params))
        result=self.runner.restore_plan(
            {'present':True,'value':'pre-trial-plan'},'runner-plan'
        )
        self.assertFalse(result['restored'])
        self.assertEqual(result['external_value_preserved']['value'],'newer-plan')
        self.assertEqual(writes,[])

    def test_validation_guard_precedes_plan_and_every_upload(self):
        fake=FakeShelly()
        raw='v=1|rev=17|start=1800000000|q0=1500|q1=2000|q2=2500|q3=4000'
        self.runner.rpc=fake
        self.runner.baseline=lambda sid: {'sid':sid}
        with tempfile.TemporaryDirectory() as directory:
            self.runner.OUT=Path(directory)
            self.runner.observe(False,True,raw)
        plan_index=next(i for i,c in enumerate(fake.calls)
                        if c[0]=='KVS.Set' and c[1].get('key')=='vp.energy.plan'
                        and c[1].get('value')==raw)
        first_put=next(i for i,c in enumerate(fake.calls) if c[0]=='Script.PutCode')
        for boundary in (plan_index,first_put):
            earlier=fake.calls[:boundary]
            self.assertIn(('Script.Stop',{'id':7}),earlier)
            self.assertIn(
                ('Script.SetConfig',{'id':7,'config':{'enable':False}}),earlier,
            )
            last_config=next(c for c in reversed(earlier) if c[0]=='Script.GetConfig')
            last_status=next(c for c in reversed(earlier) if c[0]=='Script.GetStatus')
            self.assertEqual(last_config[0],'Script.GetConfig')
            self.assertEqual(last_status[0],'Script.GetStatus')

    def test_original_script_evidence_is_complete_and_never_overwritten(self):
        fake=FakeShelly();self.runner.rpc=fake
        snapshot=self.runner.script_snapshot()
        serial=self.runner.serial_config()
        with tempfile.TemporaryDirectory() as directory:
            self.runner.OUT=Path(directory)
            value={'script':snapshot,'serial':serial}
            self.runner.write_evidence_once('script7-original.json',value)
            recorded=json.loads((Path(directory)/'script7-original.json').read_text())
            self.assertEqual(recorded,value)
            with self.assertRaises(FileExistsError):
                self.runner.write_evidence_once('script7-original.json',{'changed':True})
            self.assertEqual(
                json.loads((Path(directory)/'script7-original.json').read_text()),value,
            )

    def test_upload_failure_restores_complete_original_slot_and_kvs(self):
        fake=FakeShelly();fake.fail_next_put=True
        original_code=fake.code;original_config=dict(fake.config)
        self.runner.rpc=fake;self.runner.baseline=lambda sid: {'sid':sid}
        raw='v=1|rev=17|start=1800000000|q0=1500|q1=2000|q2=2500|q3=4000'
        with tempfile.TemporaryDirectory() as directory:
            self.runner.OUT=Path(directory)
            with self.assertRaisesRegex(RuntimeError,'injected upload failure'):
                self.runner.validate_observe(raw)
        self.assertEqual(fake.code,original_code)
        self.assertEqual(fake.config,original_config)
        self.assertFalse(fake.running)
        self.assertEqual(fake.kvs['vp.energy.plan'],'previous-plan')
        self.assertEqual(fake.kvs['vp.energy.status'],'previous-status')

    def test_success_installs_exact_production_stopped_disabled(self):
        fake=FakeShelly();self.runner.rpc=fake;self.runner.baseline=lambda sid: {'sid':sid}
        raw='v=1|rev=17|start=1800000000|q0=1500|q1=2000|q2=2500|q3=4000'
        with tempfile.TemporaryDirectory() as directory:
            self.runner.OUT=Path(directory)
            result=self.runner.validate_observe(raw)
            evidence=json.loads((Path(directory)/'runtime-validation-result.json').read_text())
        self.assertIn('phase=validated',result['kvs'])
        self.assertEqual(evidence['kvs'],result['kvs'])
        self.assertEqual(fake.code,self.runner.SOURCE.read_text())
        self.assertFalse(fake.config['enable'])
        self.assertFalse(fake.running)
        self.assertEqual(fake.kvs['vp.energy.plan'],'previous-plan')
        self.assertEqual(fake.kvs['vp.energy.status'],'previous-status')

    def test_serial_invariant_failure_rolls_back_original_script(self):
        fake=FakeShelly();self.runner.rpc=fake;self.runner.baseline=lambda sid: {'sid':sid}
        original_code=fake.code;original_config=dict(fake.config)
        original_validate=self.runner.validate_runtime
        def mutate_serial_then_validate():
            result=original_validate()
            fake.serial['serial']['baud']=115200
            return result
        self.runner.validate_runtime=mutate_serial_then_validate
        raw='v=1|rev=17|start=1800000000|q0=1500|q1=2000|q2=2500|q3=4000'
        with tempfile.TemporaryDirectory() as directory:
            self.runner.OUT=Path(directory)
            with self.assertRaisesRegex(RuntimeError,'serial invariant'):
                self.runner.validate_observe(raw)
        self.assertEqual(fake.code,original_code)
        self.assertEqual(fake.config,original_config)
        self.assertFalse(fake.running)

    def test_deadline_is_exactly_four_quarters_plus_cleanup(self):
        self.assertEqual(self.runner.PLAN_QUARTERS,4)
        self.assertEqual(self.runner.trial_timeout_seconds(),4*900+360)

    def test_identity_and_model_diagnostics_are_in_baseline_evidence(self):
        calls=[]
        def fake_read(sid,addr,qty):
            calls.append((sid,addr,qty))
            if addr==0:
                values=[0]*16;values[0]=888;values[1]=76;values[11]=1;return values
            if addr==72:return list(range(72,87))
            if addr==308:return list(range(308,320))
            if addr==346:return [19]
            if addr==320:return list(range(32))
            raise AssertionError((sid,addr,qty))
        self.runner.read=fake_read
        self.runner.control=lambda sid: {
            'state':0,'accepted':0,'applied':0,'rejected':0,'error':0,
            'saved':0,'touched':0,'mode':0,'lease_s':0,'acks':0,
        }
        self.runner.native=lambda sid: {
            'power':1,'mode':2,'flow':3000,'dhw':5000,'boost':0,
            'operating_mode':1,'diagnostic_age_s':0,
        }
        evidence=self.runner.baseline(1)
        self.assertEqual(evidence['identity']['values'],list(range(72,87)))
        self.assertEqual(evidence['identity']['registers']['I86'],86)
        self.assertEqual(evidence['model']['values'],list(range(308,320)))
        self.assertEqual(evidence['model']['registers']['I310'],310)
        self.assertEqual(evidence['model']['registers']['I346'],19)
        self.assertEqual(evidence['model']['seed_sequence'],19)
        self.assertIn((1,72,15),calls)
        self.assertIn((1,308,12),calls)
        self.assertIn((1,346,1),calls)


if __name__=='__main__':
    unittest.main()
