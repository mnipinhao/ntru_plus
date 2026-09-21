#!/usr/bin/env python3
"""Run phase-isolated BaseInv and Decap ingress diagnostics on a pinned P-core."""

import argparse
import csv
import hashlib
import json
import platform
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = next(p for p in ROOT.parents if (p / "bench/supercop.lock").exists())
LABELS = ("baseinv_denominator", "baseinv_batch", "baseinv_apply", "baseinv_full",
          "decap_decode_three", "decap_basemul_scale", "decap_inverse",
          "decap_crepmod3", "decap_scale_inverse",
          "decap_scale_inverse_crep", "decap_full_ingress",
          "decap_decode_c_f", "decap_decode_hinv")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stq(values):
    xs = sorted(values)
    n = len(xs)
    return [sum(xs[n*(1+2*i)//8:n*(3+2*i)//8]) /
            (n*(3+2*i)//8-n*(1+2*i)//8) for i in range(3)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--launches", type=int, choices=(3, 9), default=3)
    parser.add_argument("--cpu", type=int, default=1)
    args = parser.parse_args()
    branch = subprocess.check_output(["git", "branch", "--show-current"],
                                     cwd=REPO, text=True).strip()
    if branch != "avx2-official-opt":
        raise SystemExit(f"wrong branch: {branch}")
    controls = {f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor":
                "performance", "/sys/devices/system/cpu/intel_pstate/no_turbo": "1"}
    for path, expected in controls.items():
        if Path(path).read_text().strip() != expected:
            raise SystemExit(f"timing host policy failed: {path}")
    target = ROOT / "results" / args.tag
    if target.exists():
        raise SystemExit(f"refusing overwrite: {target}")
    subprocess.run(["make", "build/bench_phase_research"], cwd=ROOT,
                   check=True, capture_output=True)
    binary = ROOT / "build/bench_phase_research"
    target.mkdir(parents=True)
    shutil.copy2(binary, target / "bench_phase_research.elf")
    observations = defaultdict(list)
    launches = defaultdict(list)
    for launch in range(args.launches):
        proc = subprocess.run(["taskset", "-c", str(args.cpu), str(binary)],
                              check=True, text=True, capture_output=True)
        (target / f"launch-{launch:02d}.out").write_text(proc.stdout)
        (target / f"launch-{launch:02d}.err").write_text(proc.stderr)
        if "preflight=pass" not in proc.stderr:
            raise SystemExit("missing raw-exact BaseInv preflight")
        for row in csv.reader(line for line in proc.stdout.splitlines()
                              if line[:1].isdigit()):
            region, block, obs, cycles = map(int, row)
            if region >= len(LABELS):
                raise SystemExit("invalid region")
            observations[region].append(cycles)
            launches[region, launch].append(cycles)
    summary = {label: {"stq": stq(observations[i]),
                       "launch_stq2": [stq(launches[i, j])[1]
                                       for j in range(args.launches)]}
               for i, label in enumerate(LABELS)}
    (target / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    sources = ("bench/bench_phase_research.c", "generated/poly_phase_profile.c",
               "upstream/supercop-avx2/poly.c", "tools/generate_phase_profile.py")
    metadata = {"class": "supercop-derived-component; not Native KEM",
                "host": platform.platform(), "cpu": args.cpu, "controls": controls,
                "launches": args.launches, "elf_sha256": sha256(binary),
                "source_sha256": {name: sha256(ROOT / name) for name in sources},
                "preflight": "BaseInv phases raw-exact; valid CT/SK ingress raw-exact",
                "resets": "destructive phase input reset outside timed region",
                "decoder_scope": "three direct poly_frombytes calls on valid inputs; real Decap declassifies the secret-key decode results and short-circuits failures",
                "warning": "isolated phase costs cannot be summed into full caller"}
    (target / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({key: round(value["stq"][1], 2)
                      for key, value in summary.items()}, indent=2))
    print(target)


if __name__ == "__main__":
    main()
