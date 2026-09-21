#!/usr/bin/env python3
"""Correctness-gated, same-ELF SUPERCOP-derived W/M diagnostic campaign."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
CLEAN = EXP.parent.parent / "clean" / "avx2-gt32-clean"
REPO = next(p for p in EXP.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0,str(REPO / "scripts"))
from supercop_workflow import read_lock, verify_supercop  # noqa: E402
sys.path.insert(0,str(EXP/"tools"))
import generate_encap_wire_asm as asmgen  # noqa: E402
import audit_encap_wire_asm as audit_asm  # noqa: E402

REGIONS = ["forward_r", "forward_m", "forward_2x", "r_state_and_hash_bytes",
           "complete_polynomial_island"]
VARIANTS = ["current_M", "W_Mont_1packet", "W_Mont_2packet", "current_M_fused_add"]
SRC = [EXP / "bench/bench_encap_wire_short.c",
       EXP / "generated/encap_wire_forward.S",
       EXP / "generated/encap_wire_codec.S",
       EXP / "generated/encap_wire_muladd.S",
       EXP / "generated/encap_wire_m_add_control.S"]
CONTROL = [CLEAN / x for x in ("ntt.s","ntt_m.s","pack.s","basemul.s",
                                  "baseinv.c","consts.c","add.s")]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stq(values: list[int]) -> list[float]:
    s = sorted(v for v in values for _ in range(8))
    n = len(values)
    return [sum(s[n+2*n*i:n+2*n*(i+1)])/(2*n) for i in range(3)]


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command,check=True,text=True,capture_output=True,**kwargs)


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--supercop-root",required=True,type=Path)
    ap.add_argument("--cpu",type=int,default=1)
    ap.add_argument("--tag",required=True)
    args=ap.parse_args()
    if run(["git","branch","--show-current"],cwd=REPO).stdout.strip()!="avx2-gt-ntt":
        raise SystemExit("wrong branch")
    expected={f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor":"performance",
              "/sys/devices/system/cpu/intel_pstate/no_turbo":"1"}
    for path,want in expected.items():
        if Path(path).read_text().strip()!=want:
            raise SystemExit(f"host timing preflight failed: {path}")
    lock=read_lock(REPO / "bench/supercop.lock")
    verified=verify_supercop(args.supercop_root,lock)
    schedule=json.loads((EXP/"generated/tile4_encap_wire_schedule.json").read_text())
    packets=schedule["packets"]
    for name,body in (("forward",asmgen.fwd_source(packets)),
                      ("codec",asmgen.codec_source(packets)),
                      ("muladd",asmgen.muladd_source(packets)),
                      ("m_add_control",asmgen.m_fused_control_source())):
        if (EXP/f"generated/encap_wire_{name}.S").read_text()!=body:
            raise SystemExit(f"generator reproducibility failed: {name}")
    libs=list((args.supercop_root/"bench").glob("*/lib/nontimecop/amd64/libcpucycles.a"))
    if len(libs)!=1: raise SystemExit("expected one built SUPERCOP cpucycles library")
    lib=libs[0]
    header=lib.parents[3]/"include/nontimecop/amd64"
    result=EXP/"results"/args.tag
    if result.exists():raise SystemExit(f"refusing overwrite: {result}")
    result.mkdir(parents=True)
    build=[os.environ.get("CC","cc"),"-O3","-march=native","-mtune=native",
           "-mavx2","-fwrapv","-fPIC","-fPIE","-gdwarf-4",
           "-ffunction-sections","-fdata-sections","-Wl,--gc-sections",
           "-I"+str(CLEAN),"-I"+str(header),
           *map(str,SRC+CONTROL),str(lib),"-o",str(result/"measure")]
    built=run(build)
    (result/"build.log").write_text(built.stdout+built.stderr)
    checksources=[EXP/"tests/test_encap_wire_asm.c",
                  EXP/"src/encap_wire_research.c",*SRC[1:],*CONTROL,
                  CLEAN/"encap.c",CLEAN/"symmetric.c",CLEAN/"fips202.c",
                  CLEAN/"KeccakP-1600-AVX2.s",CLEAN/"cbd.s"]
    check=build[:build.index(str(SRC[0]))]+list(map(str,checksources))+["-o",str(result/"check")]
    compiled=run(check)
    (result/"check.build.log").write_text(compiled.stdout+compiled.stderr)
    validated=run([str(result/"check")])
    (result/"check.out").write_text(validated.stdout+validated.stderr)
    san=check[:]
    san[san.index("-O3")]="-O1"
    san[san.index("-o")+1]=str(result/"sanitize")
    san[san.index("-o"):san.index("-o")]=["-g","-fsanitize=address,undefined",
                                       "-fno-omit-frame-pointer"]
    run(san)
    checked=run([str(result/"sanitize")],
                env={**os.environ,"ASAN_OPTIONS":"detect_leaks=0"})
    (result/"sanitize.out").write_text(checked.stdout+checked.stderr)
    linked={name:audit_asm.audit(result/"measure",audit_asm.PREFIX+name)
            for name in audit_asm.SYMBOLS}
    (result/"linked-audit.json").write_text(json.dumps(linked,indent=2,sort_keys=True)+"\n")
    metadata=dict(label="supercop-derived diagnostic, not native KEM",
        lock=lock, verified_supercop=verified, compiler_command=build,
        source_sha256={str(p.relative_to(REPO)):sha(p) for p in
            SRC+CONTROL+[EXP/"tests/test_encap_wire_asm.c",
                         EXP/"src/encap_wire_research.c",
                         EXP/"tools/generate_encap_wire_schedule.py",
                         EXP/"tools/generate_encap_wire_asm.py",
                         EXP/"tools/audit_encap_wire_asm.py"]},
        elf_sha256=sha(result/"measure"),cpucycles_library_sha256=sha(lib),
        linked_audit="linked-audit.json",
        host=dict(cpu=args.cpu,platform=platform.platform(),controls=expected,
                  sibling_list=Path(f"/sys/devices/system/cpu/cpu{args.cpu}/topology/thread_siblings_list").read_text().strip()),
        regions=REGIONS,variants=VARIANTS)
    (result/"metadata.json").write_text(json.dumps(metadata,indent=2,sort_keys=True)+"\n")
    rows=[]
    for launch in range(3):
        measured=run(["taskset","-c",str(args.cpu),str(result/"measure")])
        (result/f"launch-{launch}.csv").write_text(measured.stdout)
        (result/f"launch-{launch}.err").write_text(measured.stderr)
        if "preflight=pass" not in measured.stderr:
            raise SystemExit(f"launch {launch} preflight missing")
        for line in measured.stdout.splitlines()[1:]:
            region,variant,block,slot,cycles=map(int,line.split(","))
            rows.append((launch,region,variant,block,slot,cycles))
    bykey=defaultdict(list)
    for launch,region,variant,block,slot,cycles in rows:
        bykey[region,variant].append(cycles)
    output={}
    for region,name in enumerate(REGIONS):
        control=stq(bykey[region,0])
        output[name]={"current_M":control}
        for variant in (1,2,3):
            values=stq(bykey[region,variant])
            launch_delta=[]
            for launch in range(3):
                c=[r[5] for r in rows if r[0]==launch and r[1]==region and r[2]==0]
                v=[r[5] for r in rows if r[0]==launch and r[1]==region and r[2]==variant]
                launch_delta.append(stq(v)[1]-stq(c)[1])
            output[name][VARIANTS[variant]]=dict(stq=values,
                delta_stq2=values[1]-control[1],launch_delta=launch_delta,
                favorable_launches=sum(x<0 for x in launch_delta))
    (result/"summary.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"result":str(result),"summary":output},indent=2))


if __name__=="__main__": main()
