#!/usr/bin/env python3
import hashlib,json,math,re,shutil,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; EXP=HERE.parent
P1=EXP/"gt_fr0_d1_production_shaped"; P3=EXP/"gt_fr0_d1_byte_boundary_pmu"
R9=EXP/"gt_fr0_d1_route9_pmu"; M5C=EXP/"gt_fr0_basemul_arithmetic"
M5D=EXP/"gt_fr0_inverse_consumer"; M5E=EXP/"gt_fr0_inverse_asm_realization"
M5RD=EXP/"gt_forward_level2_one_mul_b3"; TOP=EXP/"gt_2x9x16_ld3_top_split"
B1=EXP/"gt_fr0_handwritten_basemul"; M5O=EXP/"gt_forward_full_poly_ntt_asm"
STOCK=HERE.parents[4]/"NTRU+864"; COMMON=HERE.parents[4]/"common"
HOST="pi@100.99.191.9"; REMOTE="/home/pi/ntruplus-experiments/gt864-p3b4-selected-bytes"
OUT=HERE/"build"; VARIANTS=("official","gt_base","gt_bytes"); OPS=("keypair","encaps","decaps")
def command(a): return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def ssh(s): return command(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",HOST,s])
def pct(v,p):
 v=sorted(v); x=(len(v)-1)*p/100; lo=math.floor(x); hi=math.ceil(x)
 return v[lo] if lo==hi else v[lo]*(hi-x)+v[hi]*(x-lo)
def summarize(rows):
 out={}
 for op in OPS:
  out[op]={}
  for v in VARIANTS:
   z=[r for r in rows if r[0]==op and r[1]==v]
   out[op][v]={m:{f"p{p}":pct([r[i] for r in z],p) for p in (10,25,50,75,90)} for i,m in enumerate(("cycles","instructions","branches"),2)}
  out[op]["bytes_minus_base"]={m:out[op]["gt_bytes"][m]["p50"]-out[op]["gt_base"][m]["p50"] for m in ("cycles","instructions","branches")}
  out[op]["bytes_minus_official"]={m:out[op]["gt_bytes"][m]["p50"]-out[op]["official"][m]["p50"] for m in ("cycles","instructions","branches")}
 return out
def parse(s):
 pat=re.compile(r"^sample,operation=(\w+),index=\d+,position=\d+,variant=(\w+),cycles=([0-9.]+),instructions=([0-9.]+),branches=([0-9.]+)$")
 rows=[(m.group(1),m.group(2),float(m.group(3)),float(m.group(4)),float(m.group(5))) for line in s.splitlines() if (m:=pat.match(line))]
 assert len(rows)==41*3*3,len(rows); return rows
def main():
 sync=OUT/"sync"; raw=OUT/"raw"; sync.mkdir(parents=True,exist_ok=True); raw.mkdir(exist_ok=True)
 command(["python3",str(P3/"generate.py")]); command(["python3",str(R9/"generate_tables.py")])
 sources={
  "Makefile":HERE/"pi5-Makefile","test_kem.c":HERE/"test_kem.c","bench_kem_pmu.c":HERE/"bench_kem_pmu.c","selected_byte_api.c":HERE/"selected_byte_api.c",
  "gt864_poly_api.c":P1/"gt864_poly_api.c","gt864_poly_api.h":P1/"gt864_poly_api.h","byte_boundary.c":P3/"byte_boundary.c","byte_boundary.h":P3/"byte_boundary.h","gather.h":P3/"build/gather.h","tables.h":P3/"build/tables.h","route9.c":R9/"route9.c","route9.h":R9/"route9.h","p3b1_tables.h":R9/"build/p3b1_tables.h","stock_wrapper.S":P3/"stock_wrapper.S",
  "kem_stock.c":COMMON/"kem.c","gt864_forward_poly_ntt.S":M5RD/"gt864_forward_poly_ntt_all_one_mul_b3.S","gt864_forward_six_bank.S":M5RD/"gt864_forward_six_bank_all_one_mul_b3.S","gt864_top_split.s":TOP/"gt864_top_split.s","gt864_fr0_basemul.c":M5C/"gt864_fr0_basemul.c","gt864_fr0_basemul.h":M5C/"gt864_fr0_basemul.h","gt864_fr0_basemul_d1.c":B1/"gt864_fr0_basemul_d1.c","gt864_fr0_basemul_d1.h":B1/"gt864_fr0_basemul_d1.h","gt864_fr0_inverse_asm_wrapper.c":M5E/"gt864_fr0_inverse_asm_wrapper.c","gt864_fr0_inverse_asm.h":M5E/"gt864_fr0_inverse_asm.h","gt864_fr0_inverse9_block.S":M5E/"gt864_fr0_inverse9_block.s","gt864_inverse16_blocks.s":M5E/"gt864_inverse16_blocks.s",
  "poly.c":STOCK/"poly.c","poly.h":STOCK/"poly.h","params.h":STOCK/"params.h","api.h":STOCK/"api.h","symmetric.c":STOCK/"symmetric.c","symmetric.h":STOCK/"symmetric.h","randombytes.h":STOCK/"randombytes.h","add.s":STOCK/"asm/add.s","ntt.s":STOCK/"asm/ntt.s","base.s":STOCK/"asm/base.s","crepmod3.s":STOCK/"asm/crepmod3.s","pack.s":STOCK/"asm/pack.s","cbd.s":STOCK/"asm/cbd.s","NO_CE/fips202.c":STOCK/"NO_CE/fips202.c","NO_CE/fips202.h":STOCK/"NO_CE/fips202.h"}
 for n,p in sources.items(): d=sync/n; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,d)
 command(["python3",str(M5C/"generate_tables.py"),"--header",str(sync/"gt864_fr0_basemul_tables.h")]); command(["python3",str(M5D/"generate_tables.py"),"--header",str(sync/"gt864_fr0_inverse_tables.h")]); command(["python3",str(M5E/"generate_barrett_tables.py"),"--header",str(sync/"gt864_fr0_inverse_barrett_tables.h")]); command(["python3",str(M5O/"generate_official_map.py"),str(sync/"gt864_fr0_to_official_map.h"),str(sync/"gt864_fr0_to_official_map.json")])
 (OUT/"manifest.json").write_text(json.dumps({n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in sources.items()},indent=2))
 ssh(f"mkdir -p {REMOTE}"); print(command(["rsync","-av","--delete","--exclude=build",str(sync)+"/",HOST+":"+REMOTE+"/"]))
 env=ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled"); assert "Cortex-A76" in env and "throttled=0x0" in env; (raw/"environment-before.txt").write_text(env)
 try:
  build=ssh(f"cd {REMOTE} && make clean && make -B all && make check && size build/test-kem build/bench-kem && readelf -r build/kem_gt_bytes.o && objdump -d build/bench-kem")
 except subprocess.CalledProcessError as error:
  (raw/"build-failure.log").write_text(error.output)
  print(error.output)
  raise
 assert "p3b4_kem=pass cases=8 mismatches=0" in build; assert "gt_bytes_poly_tobytes" in build and "gt_bytes_poly_frombytes" in build; (raw/"build-correctness-object.log").write_text(build)
 reps=[]; allrows=[]
 for rep in range(3):
  rows=[]
  for order in ("ODB","BDO"):
   s=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-kem {order}"); (raw/f"rep{rep}-{order}.log").write_text(s); rows+=parse(s)
  reps.append(summarize(rows)); allrows+=rows
  thermal=ssh("vcgencmd measure_temp; vcgencmd get_throttled"); assert "throttled=0x0" in thermal; (raw/f"environment-rep{rep}.txt").write_text(thermal)
 result={"experiment":"D1-P3B4","host":HOST,"core":3,"correctness":"pass","overall":summarize(allrows),"repetitions":reps,"throttled":"0x0","production_linked":False}
 (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,indent=2))
if __name__=="__main__": main()
