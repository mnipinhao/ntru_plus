#!/usr/bin/env python3
import argparse,json,os,random,statistics,subprocess
from pathlib import Path
NAMES=("OO","GO","OG","GG","DUP")
def launch(p,cpu):
 r=subprocess.run([str(p.resolve())],capture_output=True,text=True,check=True,
  preexec_fn=lambda:os.sched_setaffinity(0,{cpu}))
 d={};
 for line in r.stdout.splitlines(): k,v=line.split();d[k]=int(v)
 if set(d)!=set(NAMES):raise RuntimeError((d,r.stderr))
 return d
def ci(v,seed):
 rng=random.Random(seed);b=sorted(statistics.median(rng.choices(v,k=len(v))) for _ in range(20000));return [b[499],b[19499]]
def main():
 p=argparse.ArgumentParser();p.add_argument("--binary",type=Path,required=True);p.add_argument("--blocks",type=int,default=256);p.add_argument("--warmup",type=int,default=4);p.add_argument("--cpu",type=int,default=1);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 for _ in range(a.warmup):launch(a.binary,a.cpu)
 rows=[{"launch":i+1,"values":launch(a.binary,a.cpu)} for i in range(a.blocks)]
 base=[r["values"]["OO"] for r in rows];summary={"absolute_medians":{n:statistics.median([r["values"][n] for r in rows]) for n in NAMES}}
 for j,n in enumerate(NAMES[1:]):
  d=[r["values"][n]-r["values"]["OO"] for r in rows];summary[n+"_minus_OO"]={"median":statistics.median(d),"ci95":ci(d,0x530+j),"positive_launches":sum(x>0 for x in d)}
 interaction=[(r["values"]["GG"]-r["values"]["GO"])-(r["values"]["OG"]-r["values"]["OO"]) for r in rows]
 summary["interaction"]={"median":statistics.median(interaction),"ci95":ci(interaction,0x539)}
 out={"schema":"gt32-hash-code-address-053-v1","cpu":a.cpu,"blocks":a.blocks,"summary":summary,"rows":rows};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(summary,indent=2))
if __name__=="__main__":main()

