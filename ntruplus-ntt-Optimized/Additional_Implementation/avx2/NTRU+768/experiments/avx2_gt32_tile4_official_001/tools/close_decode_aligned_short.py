#!/usr/bin/env python3
"""Three-launch decoder experiment: no Native substitution or promotion claim."""
import argparse
from collections import defaultdict
import csv
import json
import re
import shutil
from pathlib import Path
from run_encap_live_b3_short import command,sha,stq
from run_caller_profile_v2 import LABELS,WINDOWS

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();root=a.root
    meta=json.loads((root/'metadata.json').read_text())
    assert meta['launches']==3 and not meta['sanitized']
    assert meta['variant_roles']['m']=='aligned decoder'
    assert sha(root/'measure')==meta['ELF_sha256']
    dis=command(['objdump','-d','--no-show-raw-insn',root/'measure']).stdout
    (root/'counter-disassembly.txt').write_text(dis)
    functions={};cur=None
    for line in dis.splitlines():
        m=re.match(r'^([0-9a-f]+) <(.+)>:',line)
        if m:cur=int(m[1],16);functions[cur]=[]
        elif cur is not None:functions[cur].append(line)
    audit={}
    for line in (root/'symbols.txt').read_text().splitlines():
        w=line.split()
        if len(w)<3 or not w[-1].startswith(('o_diag_','g_diag_','m_diag_')):continue
        name=w[-1];address=int(w[0],16);todo=[address];seen=set();calls=[]
        while todo:
            pc=todo.pop()
            if pc in seen or pc not in functions:continue
            seen.add(pc)
            for ins in functions[pc]:
                if re.search(r'call\s+\*.*<cpucycles>',ins):calls.append(ins.strip())
                m=re.search(r'\b(?:call|jmp)\s+([0-9a-f]+) <',ins)
                if m:todo.append(int(m[1],16))
        op,cut=name.split('_diag_')[1].rsplit('_',1);cut=int(cut)
        expected=0 if LABELS[op][cut]=='external_total' else 2 if op in WINDOWS else 1
        assert len(calls)==expected and address%32==0,(name,calls)
        audit[name]={'address':hex(address),'counter_calls':calls,'expected':expected}
    (root/'linked-counter-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    raw=defaultdict(list)
    for launch in range(3):
        for r in csv.DictReader((root/f'launch-{launch}.csv').open()):
            raw[launch,r['op'],int(r['cut']),r['variant']].append(int(r['cycles']))
    assert all(len(v)==96 and min(v)>0 for v in raw.values())
    rows=[]
    for op,cut in [('encap_ingress',0),('decap_ingress',0),('encap',10),('decap',11)]:
        vals={v:stq([x for k in range(3) for x in raw[k,op,cut,v]]) for v in 'ogm'}
        deltas=[stq(raw[k,op,cut,'m'])[1]-stq(raw[k,op,cut,'g'])[1] for k in range(3)]
        rows.append({'operation':op,'cut':LABELS[op][cut],'StQ':vals,
                     'candidate_minus_current':vals['m'][1]-vals['g'][1],
                     'candidate_minus_official':vals['m'][1]-vals['o'][1],
                     'launch_candidate_minus_current':deltas,'favorable_launches':sum(x<0 for x in deltas)})
    decision={r['operation']:('short_directional_win' if max(r['launch_candidate_minus_current'])<0 else
        'short_directional_regression' if min(r['launch_candidate_minus_current'])>0 else 'inconclusive') for r in rows}
    result={'label':'supercop-derived-poly diagnostic; three fresh processes',
            'counter':meta['counter_reports'][0],'audited_entries':len(audit),'rows':rows,
            'decision':decision,'Native':'not_run','production':'not_qualified',
            'scope':'fixed normal ASLR-on image; no serious or placement confirmation'}
    (root/'aligned-short-summary.json').write_text(json.dumps(result,indent=2)+'\n')
    shutil.copyfile(Path(__file__),root/'harness-sources'/Path(__file__).name)
    print(json.dumps({'rows':rows,'decision':decision,'audited_entries':len(audit)},indent=2))

if __name__=='__main__':main()
