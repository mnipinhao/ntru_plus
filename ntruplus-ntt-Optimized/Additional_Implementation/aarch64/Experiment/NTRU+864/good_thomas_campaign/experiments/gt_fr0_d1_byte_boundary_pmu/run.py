#!/usr/bin/env python3
import subprocess,shutil,json,statistics,hashlib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
HOST="pi@100.99.191.9";REMOTE="/home/pi/ntruplus-experiments/gt864-p3b3-bytes"
OUT=HERE/"build";SYNC=OUT/"sync";RAW=OUT/"raw"
def cmd(args):return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT)
def ssh(s):return cmd(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",HOST,s])
def main():
 SYNC.mkdir(parents=True,exist_ok=True);RAW.mkdir(exist_ok=True)
 print(cmd(["python3",str(HERE/"generate.py")]),flush=True)
 p1=HERE.parent/"gt_fr0_d1_route9_pmu"
 subprocess.run(["python3","generate_tables.py"],cwd=p1,check=True)
 files={f:HERE/f for f in ["byte_boundary.c","byte_boundary.h","harness.c","stock_wrapper.S"]}
 files.update({"Makefile":HERE/"pi5-Makefile","tables.h":OUT/"tables.h","gather.h":OUT/"gather.h","route9.c":p1/"route9.c","route9.h":p1/"route9.h","p3b1_tables.h":p1/"build/p3b1_tables.h","pack.s":HERE.parents[4]/"NTRU+864/asm/pack.s"})
 for dst,src in files.items():shutil.copy2(src,SYNC/dst)
 (OUT/"manifest.json").write_text(json.dumps({f:hashlib.sha256(p.read_bytes()).hexdigest() for f,p in files.items()},indent=2))
 if "--local" in sys.argv:
  log=cmd(["make","-B","-C",str(SYNC),"CC=clang","CFLAGS=-O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd -D_DEFAULT_SOURCE","check"])
  (RAW/"local-correctness.txt").write_text(log);print(log);return
 ssh(f"mkdir -p {REMOTE}")
 print(cmd(["rsync","-av","--exclude=*.o","--exclude=test",str(SYNC)+"/",HOST+":"+REMOTE+"/"]),flush=True)
 env=ssh("uname -a; gcc --version | head -1; vcgencmd get_throttled")
 (RAW/"environment.txt").write_text(env);assert "throttled=0x0" in env
 try: log=ssh(f"cd {REMOTE} && make -B all && make check && size test && objdump -d test")
 except subprocess.CalledProcessError as e:
  (RAW/"build-failure.txt").write_text(e.output);print(e.output);raise
 (RAW/"build-disassembly.txt").write_text(log);assert "correctness=pass" in log
 allrows=[];reps=[]
 for rep in range(3):
  rows=[]
  for order in range(2):
   s=ssh(f"cd {REMOTE} && taskset -c 3 ./test {order}")
   (RAW/f"rep{rep}-{order}.txt").write_text(s)
   parsed=[l.split(",") for l in s.splitlines() if l.startswith("sample,")]
   assert len(parsed)==410
   rows += [(r[1],*[float(x) for x in r[2:]]) for r in parsed]
  allrows+=rows
  reps.append(summarize(rows))
  assert "throttled=0x0" in ssh("vcgencmd get_throttled")
 result={"correctness":"pass","overall":summarize(allrows),"repetitions":reps}
 (OUT/"summary.json").write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
def summarize(rows):
 return {op:{metric:statistics.median(r[i] for r in rows if r[0]==op) for i,metric in enumerate(["cycles","instructions","branches"],1)} for op in sorted({r[0] for r in rows})}
if __name__=="__main__":main()
