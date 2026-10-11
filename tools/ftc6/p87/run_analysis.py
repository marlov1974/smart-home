#!/usr/bin/env python3
"""P87 local-only extraction on an existing independent copy of finalized P86."""
import argparse
from pathlib import Path
import subprocess
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('workspace',type=Path)
p.add_argument('project',choices=('fresh-a','fresh-b'))
a=p.parse_args(); w=a.workspace.resolve(); repo=Path(__file__).resolve().parents[3]
roots=(repo/'tools/ftc6/p87/roots.txt').read_text().strip()
cmd=[str(w/'P0082/run_headless.sh'),str(w/'P0087/private/projects'),a.project,
     '-process','ftc6.mot','-noanalysis','-scriptPath',str(repo/'tools/ftc6/p83'),
     '-postScript','P83Seed.java',roots,'2','-postScript','P83Trace.java',
     str(w/'P0087/private'/a.project),roots,'-log',str(w/'P0087/private'/(a.project+'.log'))]
raise SystemExit(subprocess.call(cmd,cwd=w))
