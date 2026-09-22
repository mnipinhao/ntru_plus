#!/usr/bin/env python3
"""Three-launch same-ELF SUPERCOP-derived diagnostic for live B3→Q24."""
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
CLEAN = EXP.parent.parent / "clean/avx2-gt32-clean"
REPO = next(p for p in EXP.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, verify_supercop  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=True)


def stq(values: list[int]) -> list[float]:
    """Pinned SUPERCOP 20260831 include/stq.h, including non-multiple-of-4 n."""
    if not values:
        raise ValueError("stabilized quartiles require observations")
    sorted_values = sorted(x for value in values for x in [value] * 8)
    n = len(values)
    return [sum(sorted_values[i*n:(i+2)*n])/(2*n) for i in (1, 3, 5)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--supercop-root", type=Path, required=True)
    ap.add_argument("--cpu", type=int, default=1)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    if command(["git", "branch", "--show-current"]).stdout.strip() != "avx2-gt-ntt":
        raise SystemExit("wrong branch")
    controls = {
        f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor": "performance",
        "/sys/devices/system/cpu/intel_pstate/no_turbo": "1",
    }
    for path, expected in controls.items():
        if Path(path).read_text().strip() != expected:
            raise SystemExit(f"host timing preflight failed: {path}")
    lock = read_lock(REPO / "bench/supercop.lock")
    verified = verify_supercop(args.supercop_root, lock)
    command([sys.executable, str(EXP / "tools/generate_encap_live_b3_pack.py"), "--check"])
    command(["make", "encap-live-b3-check", "encap-live-b3-kem-check"])
    libs = list((args.supercop_root / "bench").glob("*/lib/nontimecop/amd64/libcpucycles.a"))
    if len(libs) != 1:
        raise SystemExit("expected one built SUPERCOP cpucycles library")
    library = libs[0]
    header = library.parents[3] / "include/nontimecop/amd64"
    sources = [EXP / "bench/bench_encap_live_b3_pack.c",
               EXP / "generated/encap_live_b3_pack.S"]
    sources += [CLEAN / name for name in (
        "baseinv.c", "consts.c", "add.s", "ntt.s", "ntt_m.s",
        "basemul.s", "batch_inverse.s", "pack.s")]
    result = EXP / "results" / args.tag
    if result.exists():
        raise SystemExit(f"refusing overwrite: {result}")
    result.mkdir(parents=True)
    build = [os.environ.get("CC", "cc"), "-O3", "-march=native", "-mtune=native",
             "-mavx2", "-fwrapv", "-fPIC", "-fPIE", "-gdwarf-4",
             "-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections",
             "-I"+str(CLEAN), "-I"+str(header), *map(str, sources),
             str(library), "-o", str(result / "measure")]
    built = command(build)
    (result / "build.log").write_text(built.stdout+built.stderr)
    audit = command([sys.executable, str(EXP / "tools/audit_encap_live_b3_pack.py"),
                     str(result / "measure")])
    (result / "linked-audit.json").write_text(audit.stdout)
    metadata = {
        "label": "supercop-derived diagnostic; not native KEM",
        "lock": lock, "verified_supercop": verified,
        "host": {"cpu": args.cpu, "platform": platform.platform(), "controls": controls,
                 "smt_siblings": Path(f"/sys/devices/system/cpu/cpu{args.cpu}/topology/thread_siblings_list").read_text().strip()},
        "compiler_command": build,
        "source_sha256": {str(p.relative_to(REPO)): sha(p) for p in sources},
        "elf_sha256": sha(result / "measure"),
        "cpucycles_library_sha256": sha(library),
        "regions": ["B3_add_pack", "PK_forward_r_hashbytes_forward_m_B3_add_pack"],
        "variants": ["current_M", "live_B3_Q24"],
    }
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True)+"\n")
    rows: list[tuple[int, int, int, int, int, int]] = []
    for launch in range(3):
        proc = command(["taskset", "-c", str(args.cpu), str(result / "measure")])
        (result / f"launch-{launch}.csv").write_text(proc.stdout)
        (result / f"launch-{launch}.err").write_text(proc.stderr)
        if "preflight=pass" not in proc.stderr:
            raise SystemExit(f"launch {launch} preflight failed")
        for line in proc.stdout.splitlines()[1:]:
            rows.append((launch, *map(int, line.split(","))))
    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for _, region, variant, _, _, cycles in rows:
        groups[region, variant].append(cycles)
    summary = {}
    for region, name in enumerate(metadata["regions"]):
        base, cand = stq(groups[region, 0]), stq(groups[region, 1])
        launches = []
        for launch in range(3):
            each = [[r[5] for r in rows if r[0] == launch and r[1] == region and r[2] == variant]
                    for variant in (0, 1)]
            launches.append(stq(each[1])[1]-stq(each[0])[1])
        summary[name] = {"current_M_stq": base, "live_B3_Q24_stq": cand,
                         "delta_stq2": cand[1]-base[1], "launch_deltas": launches,
                         "favorable_launches": sum(x < 0 for x in launches)}
    (result / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"result": str(result), "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
