"""Write synthetic instructions, never vendor data."""
from pathlib import Path
import sys
codes=["04","f3","fb","fc40550d","fd40550d","fe04","fefc","f40400","f5fcff","63","7580341208","e154","e124","e184","e1f4"]
b=bytearray([4]*32*len(codes))
for k,code in enumerate(codes):
 c=bytes.fromhex(code);b[k*32:k*32+len(c)]=c
Path(sys.argv[1]).write_bytes(b)
