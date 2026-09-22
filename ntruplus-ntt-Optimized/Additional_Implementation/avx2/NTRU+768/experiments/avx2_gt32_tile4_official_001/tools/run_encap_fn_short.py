#!/usr/bin/env python3
"""Matched function/island diagnostic. No Native, PMU or production installation."""
import argparse
import csv
import hashlib
import io
import json
import os
import platform
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from run_encap_live_b3_short import REPO, EXP, CLEAN, stq, command, sha, read_lock, verify_supercop
from vector_mapping_source_ledger import stats

REGIONS=["forward_r","forward_m","forward_2x","PK_decode","BaseMul","BaseMul_add",
         "r_pack","c_pack","r_state_hashbytes","full_polynomial_island","frontend","NTT32_terminal"]
VARIANTS=["Official","current_M","eager_M"]

def audit(elf):
    report={}
    symbols=command(["nm","-S",str(elf)]).stdout
    for name in ["ntruplus768_basemul_general_m_avx2","ntruplus768_exp001_basemul_eager_m"]:
        symbol=re.search(r"^([0-9a-f]+) ([0-9a-f]+) T "+name+"$",symbols,re.M)
        assert symbol
        raw=command(["objdump","-d","--no-show-raw-insn","--disassemble="+name,str(elf)]).stdout
        ins=[]
        for line in raw.splitlines():
            m=re.match(r"\s*([0-9a-f]+):\s+(.+)",line)
            if m:
                ins.append((int(m[1],16),m[2].split("#")[0].strip()))
        ins=ins[:next(i for i,(_,x) in enumerate(ins) if x.startswith("ret"))+1]
        assert not any(re.search(r"%(?:rsp|rbp)\b",x) for _,x in ins)
        assert not any(x.startswith(("call","push","pop")) for _,x in ins)
        assert not any(re.search(r"%(?:rbx|r1[2-5])\b",x) for _,x in ins)
        branches=[i for i,(_,x) in enumerate(ins) if re.match(r"j\w+ ",x)]
        assert len(branches)==1 and ins[branches[0]][1].startswith("jne ")
        end=branches[0]
        target=int(ins[end][1].split()[1],16)
        begin=next(i for i,(a,_) in enumerate(ins) if a==target)
        body=[x for _,x in ins[begin:end]]+["jne public_loop"]
        path=[x for _,x in ins[:begin]]+body*12+[x for _,x in ins[end+1:]]
        path=[x for x in path if not x.startswith(("nop","data16","cs "))]
        linked=stats(path,("r8","r9"))
        assert int(symbol[1],16)%32==0
        report[name]=dict(address=symbol[1],bytes=int(symbol[2],16),alignment_mod32=0,
            alignment_mod64=int(symbol[1],16)%64,linked_ledger=linked,
            branch="one public 12-block loop",stack_bytes=0,spills=0,
            disassembly=raw)
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--supercop-root",type=Path,required=True)
    ap.add_argument("--tag",required=True)
    ap.add_argument("--cpu",type=int,default=1)
    ap.add_argument("--launches",type=int,choices=(3,9),default=3)
    ap.add_argument("--candidate",choices=("eager","identity14"),default="eager")
    args=ap.parse_args()
    assert command(["git","branch","--show-current"]).stdout.strip()=="avx2-gt-ntt"
    host_files=[f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor",
                "/sys/devices/system/cpu/intel_pstate/no_turbo",
                f"/sys/devices/system/cpu/cpu{args.cpu}/topology/thread_siblings_list",
                "/proc/sys/kernel/randomize_va_space"]
    host={p:Path(p).read_text().strip() for p in host_files}
    if host[host_files[0]]!="performance" or host[host_files[1]]!="1" or host[host_files[3]]=="0":
        raise SystemExit("timing host preflight failed; no sysfs changes")
    lock=read_lock(REPO/"bench/supercop.lock")
    verified=verify_supercop(args.supercop_root,lock)
    identity=args.candidate=="identity14"
    variants=["Official","current_M","identity14_M" if identity else "eager_M"]
    command(["python3","tools/generate_pack_identity14.py" if identity else "tools/generate_encap_fn_eager.py","--check"])
    tests=command(["make","pack-identity14-check"] if identity else
                  ["make","encap-fn-eager-check","encap-fn-eager-sanitize"])
    root=EXP/"results"/args.tag
    root.mkdir(exist_ok=False)
    (root/".gitignore").write_text("*.o\nmeasure\n")
    (root/"correctness.log").write_text(tests.stdout+tests.stderr)
    libs=list((args.supercop_root/"bench").glob("*/lib/nontimecop/amd64/libcpucycles.a"))
    assert len(libs)==1
    lib=libs[0];headers=lib.parents[3]/"include/nontimecop/amd64"
    official=args.supercop_root/"crypto_kem/ntruplus768/avx2"
    cc=os.environ.get("CC","cc")
    flags=["-O3","-march=native","-mtune=native","-mavx2","-fwrapv",
           "-fno-strict-aliasing","-fPIE","-ffunction-sections","-fdata-sections"]
    commands=[];sources=[];objects=[]
    for name in ["ntt.s","basemul.s","pack.s","consts.c"]:
        src=official/name;obj=root/(name+".o")
        cmd=[cc,*flags,"-I"+str(official),"-c",str(src),"-o",str(obj)]
        commands.append(cmd);command(cmd)
        cmd=["objcopy","--prefix-symbols=official_",str(obj)]
        commands.append(cmd);command(cmd)
        objects.append(obj);sources.append(src)
    clean_names=["baseinv.c","consts.c","poly.c","symmetric.c","fips202.c",
        "KeccakP-1600-AVX2.s","cbd.s","crepmod3.s","add.s","ntt.s","ntt_m.s",
        "basemul.s","batch_inverse.s","pack.s"]
    sources += [EXP/"bench/bench_encap_fn.c",EXP/("generated/pack_identity14.S" if identity else "generated/encap_fn_eager.S")]
    sources += [CLEAN/x for x in clean_names]
    elf=root/"measure"
    build=[cc,*flags,"-Wl,--gc-sections","-I"+str(CLEAN),"-I"+str(headers),
           *map(str,sources[4:]),*map(str,objects),str(lib),"-o",str(elf)]
    if identity:build.insert(1,"-DFN_PACK_IDENTITY14")
    commands.append(build);built=command(build)
    (root/"build.log").write_text(built.stdout+built.stderr)
    if identity:
        from run_pack_identity14_audit import audit as pack_audit
        linked=pack_audit(elf)
    else:linked=audit(elf)
    (root/"linked-audit.json").write_text(json.dumps(linked,indent=2)+"\n")
    (root/"sections.txt").write_text(command(["readelf","-SW",str(elf)]).stdout)
    (root/"symbols.txt").write_text(command(["nm","-n","-S",str(elf)]).stdout)
    metadata=dict(label="supercop-derived-poly diagnostic; not Native",lock=lock,verified=verified,
        host=host,platform=platform.platform(),cpu_topology=command(["lscpu","-J"]).stdout,
        compiler=command([cc,"--version"]).stdout,
        commands=commands,source_sha256={str(x):sha(x) for x in sources},
        frozen_clean_manifest={str(x.relative_to(CLEAN)):sha(x) for x in sorted(CLEAN.rglob("*")) if x.is_file()},
        elf_sha256=sha(elf),cpucycles_library_sha256=sha(lib),
        stq_header_sha256=sha(args.supercop_root/"include/stq.h"),variants=variants,regions=REGIONS,
        inputs="actual CBD1 and SOTP functions; independent canonical PK bytes",
        residency="8 banks per variant; same bank per balanced block; rotated physical slots; symmetric untimed reset/warmup",
        input_copy="Official destructive Forward reset OUTSIDE timing; GT necessary frontend scratch inside",
        setting="normal placement / ASLR on; not selected by measured speed",
        timed_dispatch="one matched indirect call; operation pointer selected before t0; no timed selector/sink")
    groups=defaultdict(list);bylaunch=defaultdict(list);backends=[]
    metadata["fresh_process_launches"]=args.launches
    for launch in range(args.launches):
        proc=command(["taskset","-c",str(args.cpu),str(elf)])
        (root/f"launch-{launch}.csv").write_text(proc.stdout)
        (root/f"launch-{launch}.err").write_text(proc.stderr)
        assert "preflight=pass" in proc.stderr
        backends.append(proc.stderr.strip())
        for row in csv.DictReader(io.StringIO(proc.stdout)):
            r,v,c=(int(row[x]) for x in ("region","variant","cycles"))
            groups[r,v].append(c);bylaunch[launch,r,v].append(c)
    metadata["counter_backend_fresh_process"]=backends
    summary={}
    for r,name in enumerate(REGIONS):
        values={variants[v]:stq(groups[r,v]) for v in range(3) if (r,v) in groups}
        delta=[stq(bylaunch[k,r,2])[1]-stq(bylaunch[k,r,1])[1] for k in range(args.launches)]
        key="identity14_minus_M_stq2" if identity else "eager_minus_M_stq2"
        summary[name]=dict(stq=values,**{key:values[variants[2]][1]-values["current_M"][1]},
            launch_deltas=delta,favorable_launches=sum(x<0 for x in delta),
            changed_function=r in ((6,7,8,9) if identity else (4,5,9)))
    (root/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    (root/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
