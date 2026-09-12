"""Inspect final artifact after generic log regex misreads search failures."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent;B=P/'build'
log=(B/'slothy.log').read_text();asm=(B/'candidate.clean.S').read_text()
assert 'selfcheck:OK!' in log and 'Minimum number of stalls: 23' in log
assert 'Traceback' not in log
body=asm.split('p8_slothy_start:')[1].split('p8_slothy_end:')[0]
lines=[l.strip() for l in body.splitlines() if l.strip()]
assert len(lines)==32
assert not re.search(r'\b(?:v|q|d)(?:8|9|1[0-5])\b',body,re.I)
assert 'sp' not in body and '<' not in body
assert sum(l.startswith('ldr ') for l in lines)==4
assert sum(l.startswith('str ') for l in lines)==4
report=dict(status='pass',instructions=32,expected_cycles=31,spills=0,
  preserved_v8_v15=True,DFG_selfcheck='pass',
  sha256=hashlib.sha256(asm.encode()).hexdigest(),
  generic_parser_caveat='Intermediate infeasible bounds/config timeout are not final solve failures; see RESULTS.md')
(P/'artifact-review.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
