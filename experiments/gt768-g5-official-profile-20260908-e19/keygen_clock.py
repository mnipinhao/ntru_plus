"""Independent on-CPU-time sampling when fixed cycle periods alias Keygen."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parent;B=R/'.build'
d=json.loads((R/'measurements-summary.json').read_text())
(B/'varied-period-measurements.json').write_text(json.dumps(d,indent=2)+'\n')
d['runs']=[r for r in d['runs'] if r['mode']!='Keygen']
def run(cmd,name):
    p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
    (B/name).write_text(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(name+'\n'+p.stderr[-1000:])
    return p.stdout+p.stderr
for rep in range(3):
    for v in (['GT','Official'] if rep%2==0 else ['Official','GT']):
        tag=f'{v}-Keygen-clock-{rep}';exe=B/v/'workload'
        for suffix,events in [('core','cycles:u,instructions:u'),('memory','ld_spec:u,st_spec:u,stall_backend:u')]:
            run(['perf','stat','-x',',','-e',events,'taskset','-c','3',exe,0,100000],tag+'-'+suffix+'.csv')
        run(['perf','record','-q','-e','cpu-clock:u','-F','997','-o',B/(tag+'.data'),'--','taskset','-c','3',exe,0,500000],tag+'-record.log')
        report=run(['perf','report','-i',B/(tag+'.data'),'--stdio','--no-children','--percent-limit','0','--field-separator',',','-F','overhead,symbol'],tag+'-report.csv')
        assert 'Total Lost Samples: 0' in report
        run(['perf','script','-i',B/(tag+'.data'),'-F','ip,dso,dsoff,sym'],tag+'-samples.txt')
        d['runs'].append({'variant':v,'mode':'Keygen','rep':rep,'tag':tag,'operations':100000,'sample_operations':500000,'event':'cpu-clock:u','frequency':997,'lost_samples':0})
        print(tag,'PASS',flush=True)
d['keygen_control']='Cycle-period samples remained unstable; accepted Keygen attribution uses 997Hz on-CPU-time self samples, three 500000-operation runs. PMU totals remain separate 100000-operation unsampled runs.'
d['environment_end']=run(['bash','-c','vcgencmd get_throttled; vcgencmd measure_temp'],'clock-environment-end.log')
(R/'measurements-summary.json').write_text(json.dumps(d,indent=2)+'\n')
