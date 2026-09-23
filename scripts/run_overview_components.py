#!/usr/bin/env python3
"""Same-ELF component profiler for the 2026-09-23 AVX2 overview (diagnostic).

build      compile every implementation tree (all .c/.s/.S files, as SUPERCOP
           would) plus its adapter from bench/overview/ with the common O3GC
           recipe, archive the tree and `ld -r` the adapter against it (only
           needed members, as SUPERCOP's library link) into one object, prefix every defined global
           symbol with the role name (objcopy --redefine-syms), and link all
           roles plus bench/overview/harness.c and the campaign's libcpucycles
           into ONE ELF.  Writes build-manifest.json (tree / ELF hashes).
run        N fresh launches of that ELF pinned to --cpu, ASLR as configured
           by the host (on); raw CSV per launch plus metadata.json into
           --result-dir.  Wrap it in phase_b_batch.py for hygiene.
summarize  pooled SUPERCOP StQ1/2/3 per (component, role), per-launch StQ2,
           and for every non-baseline role the same-ELF delta vs --baseline
           with a launch-resampling 95% CI (launches resampled jointly, since
           every launch measures every role) and favourable launch count.

--role NAME=DIR:ADAPTER[:DEFINE,...]  ADAPTER is official|gt768|exp017;
DEFINEs are passed as -D flags to the adapter only (e.g. OVB_FORWARD=sym).
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_lazy/tools"))
from supercop_workflow import read_lock, sha256_file, sha256_tree  # noqa: E402

OVB = REPO / "bench/overview"
SUPPORT = REPO / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_lazy/tests/support"
PRISTINE = Path("/home/nuc/src/supercop-pristine-20260831")
CFLAGS = ["-march=native", "-mtune=native", "-O3", "-fwrapv", "-fPIC", "-fPIE",
          "-ffunction-sections", "-fdata-sections", "-gdwarf-4", "-Wall"]
ADAPTERS = {"official": "adapter_official.c", "gt768": "adapter_gt768.c",
            "exp017": "adapter_official.c"}


def run(cmd, **kw):
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw)
    if p.returncode:
        raise SystemExit(f"command failed: {' '.join(map(str, cmd))}\n{p.stdout[-4000:]}")
    return p.stdout


def parse_role(spec):
    name, rest = spec.split("=", 1)
    parts = rest.split(":")
    directory, adapter = Path(parts[0]).resolve(), parts[1]
    defines = [d for d in (parts[2].split(",") if len(parts) > 2 else []) if d]
    if adapter == "exp017":
        defines.append("OVB_EXP017")
    if not re.fullmatch(r"[a-z][a-z0-9]*", name) or adapter not in ADAPTERS:
        raise SystemExit(f"bad role {spec}")
    return name, directory, adapter, defines


def cpucycles_paths(campaign: Path):
    machine = [d for d in (campaign / "bench").iterdir() if (d / "lib/nontimecop/amd64/libcpucycles.a").is_file()]
    if len(machine) != 1:
        raise SystemExit("expected one campaign bench/<machine> with libcpucycles.a")
    return machine[0] / "include/nontimecop/amd64", machine[0] / "lib/nontimecop/amd64/libcpucycles.a"


def build(args):
    out = args.build_dir.resolve()
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    out.mkdir(parents=True)
    cpu_inc, cpu_lib = cpucycles_paths(args.campaign_root.resolve())
    roles = [parse_role(r) for r in args.role]
    manifest = {"schema": "ntruplus-overview-component-build/v1", "parameter": args.param,
                "created_at": datetime.now(timezone.utc).isoformat(), "cflags": CFLAGS,
                "link": "-Wl,--gc-sections", "cc": run(["gcc", "--version"]).splitlines()[0],
                "supercop_version": read_lock()["version"], "roles": {}}
    objects = []
    for name, directory, adapter, defines in roles:
        rdir = out / name
        rdir.mkdir()
        inc = ["-I", str(directory), "-I", str(OVB), "-I", str(SUPPORT),
               "-I", str(PRISTINE / "cryptoint"), "-I", str(PRISTINE / "include")]
        objs = []
        for src in sorted(directory.iterdir()):
            if src.suffix not in (".c", ".s", ".S") or not src.is_file():
                continue
            obj = rdir / (src.name + ".o")
            run(["gcc", *CFLAGS, *inc, "-c", "-o", str(obj), str(src)])
            objs.append(obj)
        aobj = rdir / "adapter.o"
        run(["gcc", *CFLAGS, *inc, *[f"-D{d}" for d in defines], "-c", "-o", str(aobj),
             str(OVB / ADAPTERS[adapter])])
        # Like SUPERCOP, archive the tree's objects and pull only the members
        # the adapter (KEM + components) needs; exp017 carries unused members
        # with duplicate definitions.
        lib = rdir / "impl.a"
        run(["ar", "rcs", str(lib), *map(str, objs)])
        merged = rdir / "merged.o"
        run(["ld", "-r", "-o", str(merged), f"-Map={rdir / 'merged.map'}", str(aobj), str(lib)])
        members = sorted(set(re.findall(r"impl\.a\(([^)]+)\)", (rdir / "merged.map").read_text())))
        syms = sorted({line.split()[-1] for line in run(["nm", "-g", "--defined-only", str(merged)]).splitlines()
                       if line.strip()})
        if "ovb_impl_desc" not in syms:
            raise SystemExit(f"{name}: adapter descriptor missing")
        (rdir / "redefine.map").write_text("".join(f"{s} {name}_{s}\n" for s in syms))
        final = out / f"{name}.o"
        run(["objcopy", f"--redefine-syms={rdir / 'redefine.map'}", str(merged), str(final)])
        undefined = sorted({line.split()[-1] for line in run(["nm", "-u", str(final)]).splitlines() if line.strip()})
        objects.append(final)
        manifest["roles"][name] = {"directory": str(directory), "adapter": ADAPTERS[adapter],
                                   "adapter_sha256": sha256_file(OVB / ADAPTERS[adapter]),
                                   "adapter_defines": defines, "tree_sha256": sha256_tree(directory),
                                   "sources": len(objs), "renamed_symbols": len(syms),
                                   "linked_members": members,
                                   "undefined_symbols": undefined}
    first = roles[0][1]
    elf = out / f"overview-components-{args.param}"
    roles_macro = " ".join(f"X({r[0]})" for r in roles)
    run(["gcc", *CFLAGS, "-Wl,--gc-sections", f"-DOVB_ROLES={roles_macro}", "-I", str(OVB),
         "-I", str(first), "-I", str(cpu_inc), "-o", str(elf), str(OVB / "harness.c"),
         *map(str, objects), str(cpu_lib)])
    manifest.update({"elf": str(elf), "elf_sha256": sha256_file(elf),
                     "harness_sha256": sha256_file(OVB / "harness.c"),
                     "ovb_h_sha256": sha256_file(OVB / "ovb.h"),
                     "link_order": [r[0] for r in roles],
                     "size": run(["size", "-A", str(elf)])})
    (out / "build-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(elf)


def launch(args):
    out = args.result_dir.resolve()
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    (out / "launches").mkdir(parents=True)
    elf = args.binary.resolve()
    started = datetime.now(timezone.utc).isoformat()
    for k in range(1, args.launches + 1):
        with (out / "launches" / f"launch-{k:02d}.csv").open("w") as so, \
                (out / "launches" / f"launch-{k:02d}.err").open("w") as se:
            code = subprocess.call(["taskset", "-c", str(args.cpu), str(elf)], stdout=so, stderr=se)
        if code:
            raise SystemExit(f"launch {k} failed ({code})")
        if "preflight=pass" not in (out / "launches" / f"launch-{k:02d}.err").read_text():
            raise SystemExit(f"launch {k}: no preflight pass")
    meta = {"schema": "ntruplus-overview-component-run/v1", "binary": str(elf),
            "elf_sha256": sha256_file(elf), "cpu": args.cpu, "launches": args.launches,
            "aslr_randomize_va_space": Path("/proc/sys/kernel/randomize_va_space").read_text().strip(),
            "placement": "normal (link order = role order)", "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(), "kernel": platform.release(),
            "cpucycles": (out / "launches/launch-01.err").read_text().strip().splitlines()[-1],
            "build_manifest_sha256": sha256_file(elf.parent / "build-manifest.json"),
            "benchmark_class": "supercop-derived-component (diagnostic, not Native)"}
    (out / "metadata.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    print(out)


def summarize(args):
    from summarize_extended import stq_sorted
    res = args.result_dir.resolve()
    files = sorted((res / "launches").glob("launch-*.csv"))
    data = defaultdict(lambda: defaultdict(list))  # (comp, role) -> launch -> values
    for li, f in enumerate(files):
        lines = f.read_text().splitlines()
        # cpucycles_tracesetup() prints its probe lines before the CSV header.
        for line in lines[lines.index("component,role,block,obs,cycles") + 1:]:
            comp, role, _b, _o, cyc = line.split(",")
            data[(comp, role)][li].append(int(cyc))
    rng = random.Random(args.seed)
    nl = len(files)
    comps = {}
    for (comp, role), per in data.items():
        pooled = sorted(v for vs in per.values() for v in vs)
        q = stq_sorted(pooled)
        comps.setdefault(comp, {})[role] = {
            "stq1": q[0], "stq2": q[1], "stq3": q[2], "observations": len(pooled),
            "launch_stq2": [stq_sorted(sorted(per[i]))[1] for i in range(nl)]}
    for comp, roles in comps.items():
        base = roles.get(args.baseline)
        if not base:
            continue
        for role, e in roles.items():
            if role == args.baseline:
                continue
            boot = []
            for _ in range(args.resamples):
                pick = [rng.randrange(nl) for _ in range(nl)]
                a = sorted(v for i in pick for v in data[(comp, args.baseline)][i])
                b = sorted(v for i in pick for v in data[(comp, role)][i])
                boot.append(stq_sorted(b)[1] - stq_sorted(a)[1])
            boot.sort()
            ld = [x - y for x, y in zip(e["launch_stq2"], base["launch_stq2"])]
            e["delta_vs_baseline"] = {
                "stq2": e["stq2"] - base["stq2"],
                "ci95_launch_resampling": [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]],
                "favourable_launches": sum(x < 0 for x in ld), "launches": nl}
    meta = json.loads((res / "metadata.json").read_text())
    out = {"schema": "ntruplus-overview-component-summary/v1", "parameter": args.param,
           "baseline": args.baseline, "launches": nl, "resamples": args.resamples, "seed": args.seed,
           "metadata": meta, "components": comps}
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    for comp, roles in comps.items():
        print(f"{comp:22s} " + "  ".join(
            f"{r}:{e['stq2']:9.1f}" + (f" ({e['delta_vs_baseline']['stq2']:+.1f} "
                                       f"[{e['delta_vs_baseline']['ci95_launch_resampling'][0]:+.1f},"
                                       f"{e['delta_vs_baseline']['ci95_launch_resampling'][1]:+.1f}]"
                                       f" {e['delta_vs_baseline']['favourable_launches']}/{nl})"
                                       if "delta_vs_baseline" in e else "")
            for r, e in roles.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--param", required=True)
    b.add_argument("--campaign-root", type=Path, required=True)
    b.add_argument("--build-dir", type=Path, required=True)
    b.add_argument("--role", action="append", required=True)
    r = sub.add_parser("run")
    r.add_argument("--binary", type=Path, required=True)
    r.add_argument("--result-dir", type=Path, required=True)
    r.add_argument("--launches", type=int, default=15)
    r.add_argument("--cpu", type=int, default=1)
    s = sub.add_parser("summarize")
    s.add_argument("--param", required=True)
    s.add_argument("--result-dir", type=Path, required=True)
    s.add_argument("--baseline", default="official")
    s.add_argument("--output", type=Path, required=True)
    s.add_argument("--resamples", type=int, default=1000)
    s.add_argument("--seed", type=int, default=20260923)
    a = ap.parse_args()
    {"build": build, "run": launch, "summarize": summarize}[a.cmd](a)


if __name__ == "__main__":
    main()
