from pathlib import Path
import json,gzip
from datetime import datetime
root=Path(__file__).resolve().parent;result={}
for path in sorted(root.glob('p72-r3-*.jsonl.gz')):
 rows=[json.loads(x) for x in gzip.decompress(path.read_bytes()).decode().splitlines()]
 if not rows or 'kind' not in rows[0]:continue
 tele=[r['data'] for r in rows if r['kind']=='telemetry'];app=[r for r in rows if r['kind']=='applied'];cmd=[r for r in rows if r['kind']=='command'];done=[r for r in rows if r['kind']=='finished'];final=[r for r in rows if r['kind']=='final_control']
 summary={'first':rows[0]['timestamp'],'last':rows[-1]['timestamp'],'applied':app[0]['timestamp'] if app else None,'commands':[{'timestamp':r['timestamp'],'words':r['data']['words']} for r in cmd],'finished':done[-1]['data'] if done else None,'final_control':final[-1]['data'] if final else None,'samples':len(tele),'metrics':{}}
 for name in tele[0]['samples'] if tele else []:
  values=[r['samples'][name]['value'] for r in tele if r['samples'][name]['value'] is not None]
  summary['metrics'][name]={'min':min(values),'max':max(values),'last':values[-1],'n':len(values)} if values else {'n':0}
 if app and len(cmd)>1:summary['applied_to_auto_seconds']=(datetime.fromisoformat(cmd[-1]['timestamp'])-datetime.fromisoformat(app[0]['timestamp'])).total_seconds()
 summary['first_running_sample']=next((r['timestamp'] for r in tele if (r['samples']['compressor_Hz']['value'] or 0)>0),None)
 result[path.name.removesuffix('.gz')]=summary
(root/'p72-r3-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
