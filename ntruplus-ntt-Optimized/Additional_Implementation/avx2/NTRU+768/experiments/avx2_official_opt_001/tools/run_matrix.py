#!/usr/bin/env python3
"""Run matched O/D/F/S/W component and KEM-caller diagnostics."""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = next(parent for parent in ROOT.parents if (parent / "bench/supercop.lock").exists())
REGIONS = ("forward_r_inplace", "basemul_add", "keygen", "encap", "decap")
VARIANTS = ("O", "D", "F", "S", "W")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stq(samples):
    values = sorted(samples)
    n = len(values)
    return [sum(values[n*(1+2*i)//8:n*(3+2*i)//8]) /
            (n*(3+2*i)//8-n*(1+2*i)//8) for i in range(3)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--launches", type=int, default=3)
    parser.add_argument("--cpu", type=int, default=1)
    args = parser.parse_args()
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=REPO,
                               text=True).strip() != "avx2-official-opt":
        raise SystemExit("wrong branch")
    checks = {f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor":
              "performance", "/sys/devices/system/cpu/intel_pstate/no_turbo": "1"}
    for path, expected in checks.items():
        if Path(path).read_text().strip() != expected:
            raise SystemExit(f"timing host policy failed: {path}")
    if args.launches not in (3, 9):
        raise SystemExit("launches must be 3 or 9")
    result = ROOT / "results" / args.tag
    if result.exists():
        raise SystemExit(f"refusing overwrite: {result}")
    subprocess.run(["make", "check"], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(["make", "build/bench_matrix"], cwd=ROOT, check=True,
                   capture_output=True)
    result.mkdir(parents=True)
    binary = ROOT / "build/bench_matrix"
    by_launch = defaultdict(list)
    all_values = defaultdict(list)
    for launch in range(args.launches):
        proc = subprocess.run(["taskset", "-c", str(args.cpu), str(binary)],
                              text=True, capture_output=True, check=True)
        (result / f"launch-{launch:02d}.out").write_text(proc.stdout)
        (result / f"launch-{launch:02d}.err").write_text(proc.stderr)
        if "preflight=pass" not in proc.stderr:
            raise SystemExit("missing differential preflight")
        for row in csv.reader(line for line in proc.stdout.splitlines()
                              if line[:1].isdigit()):
            region, variant, block, observation, cycles = map(int, row)
            if region >= len(REGIONS) or variant >= len(VARIANTS):
                raise SystemExit("invalid observation label")
            by_launch[launch, region, variant].append(cycles)
            all_values[region, variant].append(cycles)
    summary = {}
    for ri, region in enumerate(REGIONS):
        baseline = stq(all_values[ri, 0])
        candidates = {}
        for vi, variant in enumerate(VARIANTS):
            values = stq(all_values[ri, vi])
            deltas = [stq(by_launch[launch, ri, vi])[1] -
                      stq(by_launch[launch, ri, 0])[1]
                      for launch in range(args.launches)]
            candidates[variant] = dict(stq=values, delta_stq2=values[1]-baseline[1],
                                       launch_deltas=deltas,
                                       favorable_launches=sum(d < 0 for d in deltas))
        summary[region] = candidates
    (result / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    sources = [ROOT / p for p in (
        "bench/bench_matrix.c", "src/kem_reference.c", "src/kem_dup.c",
        "src/kem_fused.c", "src/kem_shared.c", "src/kem_forward.c",
        "asm/ntruplus768_officialopt_dup_basemul.s",
        "asm/ntruplus768_officialopt_basemul_add.s",
        "asm/ntruplus768_officialopt_shared_diag.s",
        "asm/ntruplus768_officialopt_ntt_early_const.s")]
    metadata = dict(benchmark_class="supercop-derived-diagnostic", cpu=args.cpu,
                    launches=args.launches, host=platform.platform(),
                    controls=checks, elf_sha256=sha256(binary),
                    source_sha256={str(p.relative_to(ROOT)): sha256(p) for p in sources},
                    regions=REGIONS, variants=VARIANTS,
                    source_and_elf_placement="same diagnostic ELF",
                    forward_reset="outside timed region; native in-place kernel")
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(json.dumps({"path": str(result), "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
