#!/usr/bin/env python3
"""P0086: local-only wrapper around the pinned headless analysis installation."""
import argparse
from pathlib import Path
import subprocess
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('workspace',type=Path)
p.add_argument('project',choices=('fresh-a','fresh-b'))
p.add_argument('--proof',action='store_true')
a=p.parse_args()
w=a.workspace.resolve();repo=Path(__file__).resolve().parents[3]
script=repo/'tools/ftc6/p86' if a.proof else repo/'tools/ftc6/p83'
cmd=[str(w/'P0082/run_headless.sh'),str(w/'P0086/private/projects'),a.project,'-process','ftc6.mot','-noanalysis','-scriptPath',str(script)]
if a.proof:cmd+=['-readOnly','-postScript','P86AddressProof.java']
else:cmd+=['-postScript','P83Seed.java',(repo/'tools/ftc6/p86/roots.txt').read_text().strip(),'2','-postScript','P83Trace.java',str(w/'P0086/private'/a.project),(repo/'tools/ftc6/p86/targets.txt').read_text().strip()]
cmd+=['-log',str(w/'P0086/private'/(a.project+('-proof' if a.proof else '')+'.log'))]
raise SystemExit(subprocess.call(cmd,cwd=w))
