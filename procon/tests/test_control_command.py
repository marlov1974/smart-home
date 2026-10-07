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
if __name__=='__main__':unittest.main()
