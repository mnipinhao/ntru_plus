"""Summarize paired user-space PMU samples (p3a=baseline, p3b=candidate)."""
import csv,json,statistics
from collections import defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent
absolute=defaultdict(list);paired=defaultdict(list)
paths=sorted((P/'build/pi5').glob('run*.csv'));assert len(paths)==6
for path in paths:
    rows=defaultdict(list)
    with path.open() as f:
        assert f.readline().strip()=='correctness=pass valid=24 tampered=24 inverse_exact=256 alias=256'
        for kind,boundary,variant,*values in csv.reader(f):
            values=list(map(float,values));rows[kind,boundary,variant].append(values)
            for counter,value in zip(('cycles','instructions','branches'),values):
                absolute[boundary,variant,counter].append(value)
    for kind,boundary,variant in rows:
        if variant!='p3a':continue
        for a,b in zip(rows[kind,boundary,'p3a'],rows[kind,boundary,'p3b'],strict=True):
            for i,counter in enumerate(('cycles','instructions','branches')):
                paired[boundary,counter].append(b[i]-a[i])
report={}
for boundary in ('inverse','keygen','encaps','decaps'):
    report[boundary]={}
    for counter in ('cycles','instructions','branches'):
        d=paired[boundary,counter]
        report[boundary][counter]=dict(baseline=statistics.median(absolute[boundary,'p3a',counter]),candidate=statistics.median(absolute[boundary,'p3b',counter]),paired_delta=statistics.median(d),samples=len(d),q1=statistics.quantiles(d,n=4)[0],q3=statistics.quantiles(d,n=4)[2])
(P/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
