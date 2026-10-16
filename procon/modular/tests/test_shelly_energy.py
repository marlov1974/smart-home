import unittest
from pathlib import Path
import json
import subprocess
import importlib.util

SOURCE=Path(__file__).resolve().parents[1]/'shelly/energy_pair_v1.js'

class ShellyEnergyScriptTest(unittest.TestCase):
    def setUp(self): self.source=SOURCE.read_text()
    def test_rolling_plan_replaces_fixed_curve(self):
        self.assertIn('PLANKEY = "vp.energy.plan", PLANVER = 1',self.source)
        self.assertIn('if (q === 0) return planQ0',self.source)
        self.assertIn('planQ0 + planQ1 + planQ2 + planQ3',self.source)
        self.assertNotIn('if (q === 0 || q === 6) return 1500',self.source)
        self.assertIn('All validation precedes installPlan',self.source)
    def test_scalar_optimizer(self):
        for forbidden in ('new Array','Array(','.push(','.split(','.map(','.filter('):
            self.assertNotIn(forbidden,self.source)
    def test_executor_is_constant_time(self):
        planner=self.source[self.source.index('function learnResponseGain'):self.source.index('function nextSeq')]
        self.assertIn('var objective = cumulativeTargetWh(q) + debtWh',planner)
        self.assertIn('objective - totalWh - assumedWh - committed',planner)
        self.assertNotIn('while (',planner)
        self.assertNotIn('Timer.set(',planner)
        self.assertNotIn('scoreCandidate',self.source)
    def test_telemetry_chain_is_serialized(self):
        tick=self.source[self.source.index('function tick()'):]
        self.assertIn('if (busy) return;',tick)
        self.assertIn('busy = 1;',tick)
        self.assertIn('integrate(t);',tick)
        self.assertIn('cycle++;',tick)
        self.assertIn('refreshPlan(t, function () { afterPlanRefresh(',tick)
        after=self.source[self.source.index('function afterPlanRefresh'):self.source.index('function tick()')]
        self.assertIn('busy = 0;',after)
    def test_transient_feedback_failure_holds_and_recovers(self):
        test=Path(__file__).with_name('test_energy_transient_feedback.js')
        result=subprocess.run(
            ['node',str(test)],check=True,text=True,capture_output=True
        )
        self.assertIn('PASS energy transient feedback',result.stdout)
    def test_installer_reads_complete_script_in_bounded_chunks(self):
        path=SOURCE.parents[1]/'tools'/'run_shelly_energy.py'
        spec=importlib.util.spec_from_file_location('run_shelly_energy_test',path)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        content='x'*2500; calls=[]
        def fake_rpc(method,params=None,retries=5):
            self.assertEqual(method,'Script.GetCode'); calls.append(dict(params))
            offset=params['offset']; length=params['len']; data=content[offset:offset+length]
            return {'data':data,'left':max(0,len(content)-offset-len(data))}
        module.rpc=fake_rpc
        self.assertEqual(module.script_code(7),content)
        self.assertEqual([c['offset'] for c in calls],[0,1024,2048])
        self.assertTrue(all(c['len']==1024 for c in calls))
    def test_bounded_runtime_and_restoration(self):
        self.assertIn('QCOUNT = 4',self.source)
        self.assertIn('QSEC = 900',self.source)
        self.assertIn('values: [0xc072',self.source)
        self.assertIn('Script.Stop',self.source)
        self.assertIn('var VALIDATEONLY = 0;',self.source)
        self.assertIn('if (VALIDATEONLY)',self.source)
        after=self.source[self.source.index('function afterPlanRefresh'):self.source.index('function tick()')]
        validate=after.index('if (VALIDATEONLY)')
        stale=after.index('if (!fresh1 || !fresh2)')
        self.assertLess(validate,stale)
    def test_runtime_validation_stops_with_unready_feedback(self):
        test=Path(__file__).with_name('test_energy_validation.js')
        result=subprocess.run(
            ['node',str(test)],check=True,text=True,capture_output=True
        )
        self.assertIn('PASS energy runtime validation',result.stdout)
    def test_energy_debt_is_cumulative(self):
        self.assertIn('var objective = cumulativeTargetWh(q) + debtWh',self.source)
        self.assertIn('objective - totalWh - assumedWh - committed',self.source)
        self.assertNotIn('qTargetWh(q) - qWh',self.source)
    def test_lag_and_reachability_replace_fixed_correction(self):
        self.assertIn('RESPONSESEC = 300',self.source)
        self.assertIn('t - stable1 < RESPONSESEC',self.source)
        self.assertIn('var committed = (actualPower + responseStart) * 0.5 * lag / 3600',self.source)
        self.assertIn('required > maxAverage || required < minAverage',self.source)
        self.assertIn('shortfall = Math.max(0, required - maxAverage)',self.source)
        self.assertNotIn('energyCorrection',self.source)
        self.assertNotIn('referenceWh(',self.source)
    def test_temperature_limiter_prevents_positive_windup(self):
        self.assertIn('(why === 4 || why === 15) && (ph === 4 || ph === 7 || ph === 8)',self.source)
        self.assertIn('if (thermalLimiter(ph, why))',self.source)
        self.assertIn('if (p < 0 || age >= 60) return cap;',self.source)
        self.assertIn('return clip(p + 500, 3000, 12000)',self.source)
        self.assertIn('read(sid, 321, 16',self.source)
        self.assertIn('clip(rawCommand, FLOORPAIR, reachPair)',self.source)
    def test_replanning_does_not_retarget_effect_every_tick(self):
        self.assertIn('t - lastRetarget >= 120',self.source)
        self.assertIn('limitedDown || recovery || t - lastRetarget >= 120',self.source)
        self.assertIn('t - lastRecovery >= 120',self.source)
        self.assertIn('commandPair + RECOVERYSTEP',self.source)
    def test_deadline_projection_and_collapse_recovery_fixture(self):
        test=Path(__file__).with_name('test_energy_deadline_recovery.js')
        result=subprocess.run(
            ['node',str(test)],check=True,text=True,capture_output=True
        )
        self.assertIn('PASS energy deadline projection',result.stdout)
    def test_odd_pair_command_is_preserved_exactly(self):
        split=self.source[self.source.index('function splitCommand'):self.source.index('function plan')]
        self.assertIn('high = commandPair - low',split)
        self.assertNotIn('round500(commandPair / 2)',self.source)
        command=self.source[self.source.index('function commandBoth'):self.source.index('function restoreLoop')]
        self.assertIn('commandOne(SID1, target1',command)
        self.assertIn('commandOne(SID2, target2',command)
        self.assertIn('|sent=',self.source)
    def test_cap_aware_split_preserves_sum_and_uses_peer_headroom(self):
        # Execute the production split function in Node after replacing only
        # the script startup tail with a test hook into its private scalars.
        marker='  publish("starting");\n'
        self.assertIn(marker,self.source)
        instrument='''  globalThis.__split = function(pair, one, two, lead) {
    commandPair = pair; cap1 = one; cap2 = two; responseGain1 = 1000; responseGain2 = 1000;
    splitLead = lead; sent1 = -1; sent2 = -1; splitCommand(0);
    return {one: target1, two: target2, lead: splitLead};
  };\n'''
        program='var Shelly={getComponentStatus:function(){return {unixtime:0};}};\n'+self.source.replace(marker,instrument+'  return;\n',1)
        program+='''
var cases = [
  __split(14000, 4000, 10000, 1),
  __split(14000, 4000, 12000, 2),
  __split(6500, 12000, 12000, 1),
  __split(6500, 12000, 12000, 2)
];
console.log(JSON.stringify(cases));
'''
        result=subprocess.run(
            ['node','-e',program],check=True,text=True,capture_output=True
        )
        cases=json.loads(result.stdout.strip())
        self.assertEqual((cases[0]['one'],cases[0]['two']),(4000,10000))
        self.assertEqual((cases[1]['one'],cases[1]['two']),(4000,10000))
        self.assertEqual((cases[2]['one'],cases[2]['two']),(3500,3000))
        self.assertEqual((cases[3]['one'],cases[3]['two']),(3000,3500))
        for case in cases:
            self.assertIn(case['one'] % 500,(0,))
            self.assertIn(case['two'] % 500,(0,))
            self.assertGreaterEqual(case['one'],3000)
            self.assertGreaterEqual(case['two'],3000)
    def test_each_pump_energy_is_integrated_independently(self):
        integrate=self.source[self.source.index('function integrate'):self.source.index('function learnResponseGain')]
        self.assertIn('if (valid1)',integrate)
        self.assertIn('if (valid2)',integrate)
        self.assertIn('fresh1 && lastFresh1',integrate)
        self.assertIn('fresh2 && lastFresh2',integrate)
        self.assertIn('if (!valid1 || !valid2) {',integrate)
        self.assertIn('qUnknownS += dt',integrate)
    def test_energy_is_split_at_exact_quarter_boundary(self):
        integrate=self.source[self.source.index('function integrate'):self.source.index('function learnResponseGain')]
        self.assertIn('cut = start + (oldq + 1) * QSEC',integrate)
        self.assertIn('qSave(oldq, qWh); qWh = carriedWh',integrate)
        self.assertIn('var carriedWh = afterWh',integrate)
        self.assertNotIn('function boundary(',self.source)
    def test_plan_runtime_regression_fixture(self):
        test=Path(__file__).with_name('test_energy_plan_kvs.js')
        result=subprocess.run(
            ['node',str(test)],check=True,text=True,capture_output=True
        )
        self.assertIn('PASS rolling KVS energy plan',result.stdout)
    def test_clock_regression_fixture(self):
        test=Path(__file__).with_name('test_energy_clock.js')
        result=subprocess.run(
            ['node',str(test)],check=True,text=True,capture_output=True
        )
        self.assertIn('PASS energy clock gate',result.stdout)
    def test_uid_bound_model_persistence_fixture_and_size(self):
        test=Path(__file__).with_name('test_energy_model_persistence.js')
        result=subprocess.run(
            ['node',str(test)],check=True,text=True,capture_output=True
        )
        self.assertIn('PASS UID-bound Shelly gain persistence',result.stdout)
        self.assertLess(len(self.source.encode()),32768)
        self.assertIn('MODELKEY = "vp.effect.a."',self.source)
        self.assertIn('values: [0xc077, m.savedGain, m.u0, m.u1, m.u2, m.u3, m.u4, m.u5]',self.source)
        self.assertNotIn('|bias=',self.source)
        self.assertNotIn('|trim=',self.source)
    def test_status_fits_observed_kvs_value_limit(self):
        marker='  publish("starting");\n'
        instrument='''  globalThis.__status = function() {
    start = 4294966500; qWh = 1000000; totalWh = 7000000;
    p1 = 2000000; p2 = 2000000; wantedPair = 24000;
    commandPair = 24000; sent1 = 12000; sent2 = 12000; reachPair = 24000;
    shortfall = 1920000; forecastErrorWh = 7000000;
    phase1 = 4; reason1 = 15; phase2 = 4; reason2 = 15; unknownS = 6300;
    planRevision = 2147483647; planState = 7;
    q0 = 1000000; q1 = 1000000; q2 = 1000000; q3 = 1000000;
    return status("restoring");
  };\n'''
        program='var Shelly={getComponentStatus:function(){return {unixtime:4294970099};},call:function(){}};\n'+self.source.replace(marker,instrument+'  return;\n',1)
        program+='console.log(JSON.stringify(__status()));\n'
        result=subprocess.run(
            ['node','-e',program],check=True,text=True,capture_output=True
        )
        status=json.loads(result.stdout.strip())
        self.assertLess(len(status.encode()),254)
        self.assertLessEqual(len(status.encode()),253)

if __name__=='__main__': unittest.main()
