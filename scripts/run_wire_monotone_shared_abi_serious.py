#!/usr/bin/env python3
"""Run four-control same-ELF serious pricing for the shared MA2 ABI."""
from __future__ import annotations
import argparse,json,platform,re,shutil,statistics,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_gt9x16_prod3_price import bootstrap_median_ci
from run_supercop_benchmark import decode_observations,stabilized_quartiles
from supercop_workflow import LOCK_PATH,read_lock,sha256_file
PREFIX="wire_monotone_shared_abi"
LABELS=tuple(f"{PREFIX}_{v}_pos{p}_cycles" for v in ("control","candidate") for p in range(4))
def checked(c):
 if subprocess.run(c,text=True).returncode:raise SystemExit("command failed: "+" ".join(c))
def launch(binary,cpu,off):
 c=["taskset","-c",str(cpu)]+(["setarch",platform.machine(),"-R"] if off else [])+[str(binary.resolve())];r=subprocess.run(c,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if r.returncode:raise SystemExit(r.stdout)
 obs={n:decode_observations(r.stdout,n) for n in LABELS};bad={n:len(v) for n,v in obs.items() if len(v)!=96}
 if bad:raise SystemExit(f"observation counts changed: {bad}")
 m=re.search(r"^wire_monotone_shared_abi_runtime_addresses ((?:0x[0-9a-fA-F]+\s*){2})$",r.stdout,re.M)
 if not m:raise SystemExit("runtime addresses missing")
 return r.stdout,obs,[int(x,16) for x in m.group(1).split()]
def cell(obs,v):
 values=[]
 for p in range(4):values+=obs[f"{PREFIX}_{v}_pos{p}_cycles"]
 return stabilized_quartiles(values)[1]
def analyze(records):
 rows=[]
 for n,(_,obs,addr) in enumerate(records,1):
  c=cell(obs,"control");w=cell(obs,"candidate");rows.append({"launch":n,"control":c,"candidate":w,"delta":w-c,"addresses":addr})
 ds=[r["delta"] for r in rows]
 return {"launches":rows,"median_delta_cycles":statistics.median(ds),"bootstrap_95pct_ci_median":bootstrap_median_ci(ds,seed=0x57495245),"negative_launches":sum(x<0 for x in ds),"positive_launches":sum(x>0 for x in ds),"median_control_cycles":statistics.median(r["control"] for r in rows),"median_candidate_cycles":statistics.median(r["candidate"] for r in rows),"unique_runtime_address_tuples":len({tuple(r["addresses"]) for r in rows})}
def main():
 p=argparse.ArgumentParser();p.add_argument("--campaign-root",type=Path,required=True);p.add_argument("--normal-implementation",required=True);p.add_argument("--reversed-implementation",required=True);p.add_argument("--cpu",type=int,required=True);p.add_argument("--compiler-wrapper",type=Path,required=True);p.add_argument("--launches",type=int,default=9);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise SystemExit(f"refusing overwrite {a.output}")
 a.output.mkdir(parents=True);build=a.output/"builds";build.mkdir();runner=Path(__file__).with_name("run_supercop_benchmark.py");bins={};builds={}
 for placement,impl in (("normal",a.normal_implementation),("reversed",a.reversed_implementation)):
  out=build/placement;checked(["python3",str(runner),"--campaign-root",str(a.campaign_root),"--parameter","1152","--implementation",impl,"--cpu",str(a.cpu),"--mode","derived-wire-monotone-shared-abi","--fresh-launches","1","--result-dir",str(out),"--compiler-wrapper",str(a.compiler_wrapper),"--require-frequency-control"]);bins[placement]=out/"measure";builds[placement]={"implementation":impl,"elf_sha256":sha256_file(bins[placement])}
 settings={};root=a.output/"settings";root.mkdir()
 for placement in ("normal","reversed"):
  for off in (False,True):
   name=f"{placement}-aslr-{'off' if off else 'on'}";d=root/name;d.mkdir();records=[]
   for n in range(1,a.launches+1):
    text,obs,addr=launch(bins[placement],a.cpu,off);(d/f"launch-{n:02d}.out").write_text(text);records.append((text,obs,addr))
   settings[name]=analyze(records);unique=settings[name]["unique_runtime_address_tuples"]
   if (off and unique!=1) or (not off and unique<2):raise SystemExit(f"ASLR control failed: {name}")
 fastest=min(("normal","reversed"),key=lambda x:settings[f"{x}-aslr-on"]["median_control_cycles"]);headline=f"{fastest}-aslr-on"
 gate5_pass=all(value["negative_launches"]==a.launches and value["bootstrap_95pct_ci_median"][1]<0 for value in settings.values())
 summary={**read_lock(),"created_at":datetime.now(timezone.utc).isoformat(),"benchmark_class":"supercop-derived-wire-monotone-shared-abi","boundary":"two coefficient-domain forwards + r exact-wire fanout + PK decode/MA2 + ciphertext exact-wire egress","excluded":"hash_g/SOTP/random generation; not native KEM","cpu":a.cpu,"launches_per_setting":a.launches,"compiler_policy":"fixed-common-O3GC","builds":builds,"settings":settings,"headline_setting":headline,"headline":settings[headline],"gate5_pass":gate5_pass,"decision":"select as the next research caller-island ABI; native KEM and production promotion remain separate gates" if gate5_pass else "reject or investigate shared ABI before caller integration"}
 (a.output/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n");shutil.copy2(LOCK_PATH,a.output/"supercop.lock");print(json.dumps({"headline_setting":headline,"headline":settings[headline]},indent=2))
if __name__=="__main__":main()
