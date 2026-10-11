"""P0072 r2 offline wire golden fixture and rejected intents."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from control_command import encode
class Commands(unittest.TestCase):
 def test_fixed_golden(self):
  r=encode(1,'fixed-flow',38,lease=900)
  self.assertFalse(r['sent'])
  self.assertEqual(r['rtu_hex'],'01 10 01 2c 00 08 10 c0 72 00 01 00 02 0e d8 00 00 03 84 00 01 00 02 8e 26')
 def test_auto(self):self.assertEqual(encode(2,'auto')['words'],[49266,2,1,0,0,0,0,2])
 def test_invalid(self):
  for args in [(0,'off',None,None,30),(1,'off',38,None,30),(1,'fixed-flow',46,None,30),(1,'fixed-flow',38,None,29),(1,'dhw',None,61,30),(1,'auto',None,None,30),(1,'targets',None,None,30),(1,'fixed-flow','nan',None,30)]:
   with self.assertRaises(ValueError):encode(*args)
 def test_addressed_legacy_preserves_payload(self):
  first=bytes.fromhex(encode(1,'fixed-flow',38,lease=900)['rtu_hex'])
  second=bytes.fromhex(encode(1,'fixed-flow',38,lease=900,slave=2)['rtu_hex'])
  self.assertEqual(second[0],2)
  self.assertEqual(first[1:-2],second[1:-2])
  self.assertNotEqual(first[-2:],second[-2:])
 def test_effect_contract(self):
  result=encode(1,'effect',lease=900,slave=2,target_w=6000,max_flow=38,boundary_verified=True)
  self.assertEqual(result['words'],[0xc076,1,5,6000,3800,900,1,3])
  self.assertEqual(result['slave_id'],2)
  frame=bytes.fromhex(result['rtu_hex'])
  self.assertEqual(frame[:7],bytes.fromhex('02 10 01 2c 00 08 10'))
  self.assertEqual(len(frame),25)
  self.assertFalse(result['sent'])
 def test_effect_limits_and_boundary_gate(self):
  base=dict(lease=900,slave=2,target_w=6000,max_flow=38,boundary_verified=True)
  for change in ({'target_w':999},{'target_w':12001},{'target_w':18000},{'target_w':True},
                 {'target_w':6000.5},{'max_flow':29.99},{'max_flow':55.01},{'max_flow':'nan'},
                 {'lease':89},{'lease':1801},{'boundary_verified':False},{'boundary_verified':1},
                 {'flow':38},{'dhw':50},{'slave':0},{'slave':248}):
   with self.subTest(change=change),self.assertRaises(ValueError):encode(1,'effect',**dict(base,**change))
  self.assertEqual(encode(1,'effect',lease=90,target_w=1000,max_flow=30,boundary_verified=True)['words'][3:6],[1000,3000,90])
  self.assertEqual(encode(1,'effect',lease=1800,target_w=12000,max_flow=55,boundary_verified=True)['words'][3:6],[12000,5500,1800])
 def test_bad_unicast_and_no_v2_option_repurposing(self):
  for slave in (0,248,-1,True,1.0,'2'):
   with self.subTest(slave=slave),self.assertRaises(ValueError):encode(1,'auto',slave=slave)
  for option in ({'target_w':6000},{'max_flow':38},{'boundary_verified':True}):
   with self.assertRaises(ValueError):encode(1,'auto',**option)
  for seq in (True,1.0):
   with self.assertRaises(ValueError):encode(seq,'auto')
  with self.assertRaises(ValueError):encode(1,'off',lease=True)
if __name__=='__main__':unittest.main()
