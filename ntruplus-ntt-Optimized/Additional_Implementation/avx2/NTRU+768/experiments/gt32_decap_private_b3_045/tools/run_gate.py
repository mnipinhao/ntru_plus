#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, random, re, statistics, subprocess
from pathlib import Path

OPS=("keypair","enc","dec")

def decode_line(line: str) -> list[int]:
    fields=line.split(); base=int(fields[-2])
    return [base+int(x) for x in re.findall(r"[+-]\d+",fields[-1])]

def parser_self_test() -> None:
    got=decode_line("enc_cycles - 28000 -10+5+20")
    if got != [27990,28005,28020]: raise AssertionError(got)

def stq2(values: list[int]) -> float:
    expanded=sorted(v for v in values for _ in range(8)); n=len(values)
    return sum(expanded[3*n:5*n])/(2*n)

def launch(path: Path,cpu:int)->dict[str,float]:
    completed=subprocess.run([str(path.resolve())],text=True,capture_output=True,
        check=True,preexec_fn=lambda:os.sched_setaffinity(0,{cpu}))
    values={op:[] for op in OPS}
    for line in completed.stdout.splitlines():
        for op in OPS:
            if line.startswith(op+"_cycles "): values[op].extend(decode_line(line))
    return {op:stq2(values[op]) for op in OPS}

def ci(values:list[float])->list[float]:
    rng=random.Random(0x045); boot=sorted(statistics.median(rng.choices(values,k=len(values))) for _ in range(20000))
    return [boot[499],boot[19499]]

def main()->None:
    parser_self_test()
    p=argparse.ArgumentParser(); p.add_argument("--build",type=Path,required=True)
    p.add_argument("--blocks",type=int,default=256); p.add_argument("--warmup",type=int,default=8)
    p.add_argument("--cpu",type=int,default=1); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    bins={x:a.build/f"measure-{x}" for x in ("C","P")}
    for _ in range(a.warmup):
        for x in ("C","P"): launch(bins[x],a.cpu)
    rows=[]
    for block in range(a.blocks):
        order=("C","P") if block%2==0 else ("P","C"); values={x:launch(bins[x],a.cpu) for x in order}
        rows.append({"block":block+1,"order":order,"values":values})
    summary={}
    for op in OPS:
        delta=[r["values"]["P"][op]-r["values"]["C"][op] for r in rows]
        summary[op]={"paired_median_delta":statistics.median(delta),"favorable_blocks":sum(x<0 for x in delta),"bootstrap_95_ci":ci(delta)}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps({"schema":"gt32-decap-private-b3-045-v1","parser_self_test":"pass","cpu":a.cpu,"blocks":a.blocks,"summary":summary,"rows":rows},indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()

