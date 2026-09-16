#!/usr/bin/env python3
from pathlib import Path
import re,json,hashlib,collections
H=Path(__file__).resolve().parent;B=H/'build';SOURCE=H.parent/'gt864_p3b34_consumer_reset/build/sync/raw/gt864_forward_six_bank.S'
def main():
    B.mkdir(exist_ok=True);text=SOURCE.read_text();lines=text.splitlines();start=lines.index('.Lgt864_a1t1_one_bank:')+1;end=next(i for i in range(start,len(lines)) if lines[i].strip()=='ret')
    regs={};uses=collections.defaultdict(list);defs={};writes=collections.defaultdict(list);moves=[];loads=[]
    for i in range(start,end):
        line=lines[i].split('//')[0].strip()
        if not line:continue
        op=line.split()[0];tokens=list(re.finditer(r'\b([vq])(\d+)\b(?:\.(8[Hh]|4[Ss]|2[Dd]|16[Bb]|[Hh]\[(\d+)\]))?',line))
        if not tokens:continue
        dest=int(tokens[0][2]);sources=tokens[1:]
        if op=='ldp':sources=[]
        if op=='mls':sources=[tokens[0]]+sources
        for token in sources:
            reg=int(token[2]);version=regs.get(reg,('entry',reg));lane=int(token[4]) if token[4] else None
            uses[version].append({'line':i+1,'register':reg,'lanes':[lane] if lane is not None else list(range(8)),'rmw':op=='mls' and token==tokens[0]})
        destinations=[int(t[2]) for t in tokens] if op=='ldp' else [dest]
        for d in destinations:regs[d]=(i,d);defs[(i,d)]=line;writes[d].append(i)
        if op=='mov' and 'P3B' in lines[i]:moves.append((i,dest,int(tokens[1][2])))
        if op=='ldr' and re.search(r'\[x[23]\]',line):loads.append((i,dest))
    move_report=[]
    for i,d,s in moves:
        consumers=uses[(i,d)];last=max((u['line']-1 for u in consumers),default=i)
        overwrite=next((w for w in writes[s] if w>i),None)
        rmw=any(u['rmw'] for u in consumers)
        safe=bool(consumers) and not rmw and (overwrite is None or overwrite>=last)
        # An overwrite in the last consuming instruction reads before writing.
        move_report.append({'line':i+1,'destination':d,'source':s,'consumers':consumers,'source_next_write':None if overwrite is None else overwrite+1,'simple_forward_coalescing':safe,'reason':'source_clobbered_before_last_use' if overwrite is not None and overwrite<last else 'destructive_destination_consumer' if rmw else 'local_read_rewrite_possible' if safe else 'requires_liveout_check'})
    load_report=[]
    for i,d in loads:
        u=uses[(i,d)];lanes=sorted({l for x in u for l in x['lanes']})
        load_report.append({'line':i+1,'instruction':lines[i].strip(),'used_lanes':lanes,'uses':u,'dead':not u,'pointer_side_effect':'postincrement 16 bytes must be preserved or offsets retabled'})
    result={'gate':'P3B35-A','source_sha256':hashlib.sha256(text.encode()).hexdigest(),'moves':move_report,'constant_loads':load_report,'counts':{'moves':len(moves),'simple_coalescible':sum(x['simple_forward_coalescing'] for x in move_report),'constant_loads':len(loads),'dead_constant_loads':sum(x['dead'] for x in load_report)},'assembly_changed':False}
    (B/'liveness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['counts']))
if __name__=='__main__':main()
