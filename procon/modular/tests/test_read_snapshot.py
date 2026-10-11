import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from read_snapshot import read_snapshot
class Reader:
 def __init__(self,interfere=0):self.seq=0;self.interfere=interfere
 def __call__(self,a,n):
  if a==400:self.seq+=1
  if a==402 and self.interfere:self.seq+=1;self.interfere-=1
  w=[0x5380,1,0,self.seq,0,20,0,0]+[0xffff,65535,1,1,2,9]*20
  return w[a-400:a-400+n]
v=read_snapshot(Reader(1));assert v['sequence']==3 and v['samples']['flow_cC']['value']==-1 and v['samples']['flow_cC']['age_ms']==65538
try:read_snapshot(Reader(10))
except RuntimeError:pass
else:raise AssertionError('must reject concurrent replacement')
try:read_snapshot(lambda a,n:[0]*n)
except ValueError:pass
else:raise AssertionError('must reject old firmware')
print('PASS snapshot reader: signed/age decoding, replacement retry, bounded failure, unsupported header')
