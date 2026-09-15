#!/usr/bin/env python3
"""Analyze Encap leaf intervals in the frozen Experiment 099 images."""
import argparse,json,re,statistics,subprocess
from collections import defaultdict
from pathlib import Path

CALLS={
 "official":[
  (0x604e,"decode",True),(0x60d1,"cbd_r",True),(0x60de,"ntt_r",True),
  (0x60ee,"pack_rhat",True),(0x6111,"sotp_m",True),(0x611e,"ntt_m",True),
  (0x6138,"basemul",True),(0x614f,"add_m",True),(0x615c,"pack_ct",True)],
 "gt":[
  (0x3d1f,"decode",False),(0x3da1,"cbd_r",True),(0x3db6,"frontend_r",True),
  (0x3dcb,"ntt_r",True),(0x3ddb,"pack_rhat",True),(0x3dfb,"sotp_m",True),
  (0x3e10,"frontend_m",True),(0x3e25,"ntt_m",True),(0x3e3f,"basemul",True),
  (0x3e57,"add_pack_ct",True),(0x9e0a,"decode_body",True)]}
MMAP=re.compile(r"\[0x([0-9a-f]+)\(0x([0-9a-f]+)\) @ 0x([0-9a-f]+).+\]: r-xp (.+)$")
BR=re.compile(r"0x([0-9a-f]+)/0x([0-9a-f]+)/[^/]*/[^/]*/[^/]*/(\d+)/([^/]*)/")

def perf(data,*args):
 return subprocess.run(["perf","script","-i",str(data),*args],capture_output=True,text=True,check=True).stdout
def mapping(data,binary):
 wanted=str(binary.resolve());found=[]
 for line in perf(data,"--show-mmap-events").splitlines():
  m=MMAP.search(line)
  if m and str(Path(m.group(4)).resolve())==wanted:
   start,size,off=(int(m.group(i),16) for i in range(1,4));found.append((start,size,off))
 if not found:raise RuntimeError(f"mapping {wanted}: {found}")
 bases={start-off for start,size,off in found}
 if len(bases)!=1:raise RuntimeError(f"inconsistent PIE bases {wanted}: {found}")
 return bases.pop()
def summarize(xs):
 if not xs:return None
 xs=sorted(xs)
 return {"observations":len(xs),"median":statistics.median(xs),"p10":xs[round((len(xs)-1)*.1)],"p90":xs[round((len(xs)-1)*.9)]}
def trace(data,binary,impl):
 base=mapping(data,binary);returns={a+5:(n,leaf) for a,n,leaf in CALLS[impl]};vals=defaultdict(list)
 for line in perf(data,"-F","brstack").splitlines():
  for m in BR.finditer(line):
   target=int(m.group(2),16)-base
   if m.group(4)=="RET" and target in returns:
    name,leaf=returns[target]
    if leaf:vals[name].append(int(m.group(3)))
 return {name:summarize(xs) for name,xs in vals.items()}
def launch_summary(rows):
 keys=sorted({k for row in rows for k in row["intervals"]})
 return {k:summarize([row["intervals"][k]["median"] for row in rows if row["intervals"].get(k)]) for k in keys}
def main():
 p=argparse.ArgumentParser();p.add_argument("--manifest",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 manifest=json.loads(a.manifest.read_text());bins={k:Path(v["path"]) for k,v in manifest["binaries"].items()};rows=[];groups=defaultdict(list)
 for rec in manifest["rows"]:
  impl=rec["implementation"];row={**rec,"intervals":trace(a.manifest.parent/rec["perf_data"],bins[impl],impl)};rows.append(row);groups[impl].append(row)
 sums={k:launch_summary(v) for k,v in groups.items()};off=sums["official"];gt=sums["gt"]
 specs={
  "decode":(["decode"],["decode_body"]),"cbd_r":(["cbd_r"],["cbd_r"]),
  "r_producer":(["ntt_r"],["frontend_r","ntt_r"]),"rhat_serializer":(["pack_rhat"],["pack_rhat"]),
  "sotp_m":(["sotp_m"],["sotp_m"]),"m_producer":(["ntt_m"],["frontend_m","ntt_m"]),
  "basemul":(["basemul"],["basemul"]),"sum_and_ct_serializer":(["add_m","pack_ct"],["add_pack_ct"])}
 semantic={}
 for name,(ok,gk) in specs.items():
  if all(k in off for k in ok) and all(k in gt for k in gk):
   ov=sum(off[k]["median"] for k in ok);gv=sum(gt[k]["median"] for k in gk)
   semantic[name]={"official_core_cycles":ov,"gt_core_cycles":gv,"gt_minus_official":gv-ov}
 semantic["mapped_leaf_total"]={"official_core_cycles":sum(v["official_core_cycles"] for v in semantic.values()),"gt_core_cycles":sum(v["gt_core_cycles"] for v in semantic.values())}
 semantic["mapped_leaf_total"]["gt_minus_official"]=semantic["mapped_leaf_total"]["gt_core_cycles"]-semantic["mapped_leaf_total"]["official_core_cycles"]
 out={"schema":"gt32-encap-perf-profile-127-lbr-v1","warning":"leaf LBR medians are descriptive, not an additive reconstruction of full Encap","summaries":sums,"semantic_leaf_map":semantic,"rows":rows};a.output.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(semantic,indent=2))
if __name__=="__main__":main()
