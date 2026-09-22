"""Audit actual counter calls and summarize matched cumulative evidence honestly."""
import argparse
import csv
import json
import random
import re
import shutil
from collections import defaultdict
from pathlib import Path
from run_encap_live_b3_short import command,sha,stq
from run_caller_profile_v2 import LABELS,WINDOWS

def ci(values):
    rng=random.Random(76820260922)
    samples=sorted(sum(rng.choices(values,k=len(values)))/len(values) for _ in range(10000))
    return [samples[249],samples[9749]]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();root=a.root
    metadata=json.loads((root/'metadata.json').read_text())
    assert metadata['launches']==9 and not metadata['sanitized']
    assert sha(root/'measure')==metadata['ELF_sha256']
    dis=command(['objdump','-d','--no-show-raw-insn',str(root/'measure')]).stdout
    (root/'annotated-counter-disassembly.txt').write_text(dis)
    functions={};cur=None
    for line in dis.splitlines():
        m=re.match(r'^([0-9a-f]+) <(.+)>:',line)
        if m:cur=int(m[1],16);functions[cur]={'name':m[2],'lines':[]}
        elif cur is not None:functions[cur]['lines'].append(line)
    names={}
    for line in (root/'symbols.txt').read_text().splitlines():
        fields=line.split()
        if len(fields)>=3 and fields[-1].startswith(('o_diag_','g_diag_','m_diag_')):
            names[fields[-1]]=int(fields[0],16)
    audit={}
    for name,addr in names.items():
        todo=[addr];visited=set();counter=[];direct=[]
        while todo:
            x=todo.pop()
            if x in visited or x not in functions:continue
            visited.add(x)
            for line in functions[x]['lines']:
                if re.search(r'call\s+\*.*<cpucycles>',line):counter.append(line.strip())
                m=re.search(r'\b(?:call|jmp)\s+([0-9a-f]+) <',line)
                if m:
                    dest=int(m[1],16)
                    if dest in functions:todo.append(dest)
        opcut=name.split('_diag_')[1];op,cut=opcut.rsplit('_',1);cut=int(cut)
        expected=0 if LABELS[op][cut]=='external_total' else 2 if op in WINDOWS else 1
        assert len(counter)==expected,(name,counter,expected)
        assert addr%32==0,(name,addr)
        audit[name]={'address':hex(addr),'mod32':addr%32,'mod64':addr%64,
                     'reachable_counter_calls':counter,'expected':expected,
                     'reachable_functions':[functions[x]['name'] for x in sorted(visited)]}
    (root/'linked-counter-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    raw=defaultdict(list)
    for launch in range(9):
        for r in csv.DictReader((root/f'launch-{launch}.csv').open()):
            raw[launch,r['op'],int(r['cut']),r['variant']].append(int(r['cycles']))
    for values in raw.values():assert len(values)==96 and min(values)>0
    rows=[]
    for op,labels in LABELS.items():
        for cut,label in enumerate(labels):
            for v in ('g','m') if op.startswith('encap') else ('g',):
                for control in ('o','g') if v=='m' else ('o',):
                    cumulative=[];increments=[]
                    for k in range(9):
                        delta=stq(raw[k,op,cut,v])[1]-stq(raw[k,op,cut,control])[1]
                        prev=(stq(raw[k,op,cut-1,v])[1]-stq(raw[k,op,cut-1,control])[1]) if cut else 0
                        cumulative.append(delta);increments.append(delta-prev)
                    for metric,values in [('cumulative_delta',cumulative),('increment_delta',increments)]:
                        interval=ci(values)
                        rows.append({'op':op,'cut':label,'candidate':v,'control':control,'metric':metric,
                                     'launch_mean':sum(values)/9,'CI95_launch_bootstrap':interval,
                                     'favorable_launches':sum(x<0 for x in values),'launch_values':values,
                                     'interpretation':('instrumentation_residual_not_component' if label=='external_total' and metric=='increment_delta' else
                                         'directional_in_this_diagnostic_image' if interval[1]<0 or interval[0]>0 else 'unresolved_at_this_resolution')})
    # Negative prefix differences are resolution/geometry failures, not physical costs.
    negatives=[]
    for r in csv.DictReader((root/'waterfall.csv').open()):
        if r['label']!='external_total' and float(r['increment_StQ2'])<0:negatives.append(r)
    output={'estimator':'cumulative pooled StQ2 waterfall; uncertainty separately bootstraps mean of nine per-launch StQ2 deltas',
            'not_a_promotion_test':True,'negative_increments_invalid_as_physical_cost':negatives,'comparisons':rows,
            'raw_observations_per_region_variant':864,'audited_entries':len(audit)}
    (root/'attribution-evidence.json').write_text(json.dumps(output,indent=2)+'\n')
    summary=json.loads((root/'summary.json').read_text())
    native=root.parent/'maskstore-native-qualification-20260922'
    native_values={}
    for v,d in [('o','native-official'),('g','native-current'),('m','native-candidate')]:
        native_values[v]=json.loads((native/d/'stq-summary.json').read_text())
    # Preserve source JSON rather than infer its schema; extracted values follow below.
    (root/'previous-native-summaries.json').write_text(json.dumps(native_values,indent=2)+'\n')
    residual=[]
    for op in ('keygen','encap','decap'):
        data=summary[op]
        for v in ('g','m') if op=='encap' else ('g',):
            full=data['external_total']['StQ'][v][1]-data['external_total']['StQ']['o'][1]
            prefix=data['clear_total']['StQ'][v][1]-data['clear_total']['StQ']['o'][1]
            native_op={'keygen':'keypair_cycles','encap':'enc_cycles','decap':'dec_cycles'}[op]
            native_delta=native_values[v]['operations'][native_op]['stq2']-native_values['o']['operations'][native_op]['stq2']
            residual.append({'op':op,'variant':v,'diagnostic_full_delta':full,
                'cumulative_last_cut_delta':prefix,'instrumentation_image_residual':full-prefix,
                'previous_native_delta':native_delta,'native_minus_diagnostic_delta':native_delta-full,
                'note':'not missing arithmetic; includes instrumentation/code geometry/estimation differences'})
    (root/'residual.json').write_text(json.dumps(residual,indent=2)+'\n')
    shutil.copyfile(Path(__file__),root/'harness-sources'/Path(__file__).name)
    print(json.dumps({'audited_entries':len(audit),'negative_increments':negatives},indent=2))

if __name__=='__main__':main()
