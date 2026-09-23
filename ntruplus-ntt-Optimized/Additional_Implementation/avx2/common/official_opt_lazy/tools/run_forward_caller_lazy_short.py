#!/usr/bin/env python3
"""Same-ELF SUPERCOP-derived pricing of Official vs caller-lazy Forward (864/1152).

Port of NTRU+768 avx2_official_opt_001/tools/run_forward_caller_lazy_short.py.
Builds `make bench` (common O3GC recipe) after the Phase-A `make check`, then
runs N fresh processes pinned to one CPU.  Each process times five regions
(r Forward, Keygen f Forward, full Keygen, full Encap, full Decap) for both
variants in alternating ABAB/BABA blocks.  Host controls are only read.
This is a complete-caller diagnostic, not Native SUPERCOP KEM.

Run it under phase_b_batch.py so that host hygiene is recorded, e.g.
  phase_b_batch.py --result-dir results/officialopt-forward-caller-lazy-serious-20260923 \
    --metadata metadata.json -- python3 run_forward_caller_lazy_short.py \
    --param 864 --experiment . --launches 9 --result-dir {RESULT}
"""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
COMMON = HERE.parents[1]
REGIONS = ("forward_r", "forward_keygen_f", "keypair", "encap", "decap")
BRANCH = "official-opt-lazy-864-1152"


def execute(command, **kwargs):
    return subprocess.run(command, text=True, capture_output=True, check=True, **kwargs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stq(values):
    values = sorted(values)
    n = len(values)
    return [sum(values[n * (1 + 2 * i) // 8:n * (3 + 2 * i) // 8]) /
            (n * (3 + 2 * i) // 8 - n * (1 + 2 * i) // 8) for i in range(3)]


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--param", type=int, choices=(864, 1152), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--skip-build", action="store_true",
                        help="use an already built build/bench_caller_lazy (still hashed)")
    args = parser.parse_args()
    root = args.experiment.resolve()
    if execute(["git", "branch", "--show-current"], cwd=REPO).stdout.strip() != BRANCH:
        raise SystemExit("wrong branch")
    checks = {
        f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor": "performance",
        "/sys/devices/system/cpu/intel_pstate/no_turbo": "1",
    }
    for name, expected in checks.items():
        if Path(name).read_text().strip() != expected:
            raise SystemExit(f"host timing preflight failed: {name}")
    result = args.result_dir.resolve()
    if result.exists():
        raise SystemExit(f"refusing overwrite: {result}")
    if not args.skip_build:
        execute(["make", "check"], cwd=root)
        execute(["make", "bench"], cwd=root)
    binary = root / "build/bench_caller_lazy"
    result.mkdir(parents=True)
    all_rows = []
    identities = []
    for launch in range(args.launches):
        observed = execute(["taskset", "-c", str(args.cpu), str(binary)])
        (result / f"launch-{launch}.out").write_text(observed.stdout)
        (result / f"launch-{launch}.err").write_text(observed.stderr)
        if "preflight=pass" not in observed.stderr:
            raise ValueError("missing benchmark preflight")
        identities.extend(line for line in observed.stderr.splitlines()
                          if line.startswith("cpucycles="))
        for row in csv.reader(line for line in observed.stdout.splitlines()
                              if line[:1].isdigit()):
            region, variant, block, observation, cycles = map(int, row)
            all_rows.append((launch, region, variant, block, observation, cycles))
    samples = defaultdict(list)
    for launch, region, variant, _, _, cycles in all_rows:
        samples[region, variant].append(cycles)
    summary = {}
    for region, name in enumerate(REGIONS):
        baseline = stq(samples[region, 0])
        candidate = stq(samples[region, 1])
        launch_deltas = []
        for launch in range(args.launches):
            a = [row[5] for row in all_rows if row[:3] == (launch, region, 0)]
            b = [row[5] for row in all_rows if row[:3] == (launch, region, 1)]
            launch_deltas.append(stq(b)[1] - stq(a)[1])
        summary[name] = {
            "official_stq": baseline,
            "caller_lazy_stq": candidate,
            "caller_lazy_minus_official_stq2": candidate[1] - baseline[1],
            "launch_deltas": launch_deltas,
            "favorable_launches": sum(delta < 0 for delta in launch_deltas),
        }
    (result / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    lazy = f"asm/ntruplus{args.param}_officialopt_ntt_caller_lazy.s"
    sources = {str(path.relative_to(REPO)): digest(path) for path in (
        root / "upstream/supercop-avx2/ntt.s", root / "upstream/supercop-avx2/kem.c",
        root / lazy, root / "src/kem_lazy.c",
        COMMON / "bench/bench_caller_lazy.c", COMMON / "bench/kem_diag.c",
        COMMON / "lazy.mk", COMMON / "tools/generate_forward_caller_lazy.py")}
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "parameter": str(args.param),
        "source_sha256": sources,
        "elf_sha256": digest(binary),
        "host": platform.platform(),
        "cpu": args.cpu,
        "controls": checks,
        "launches": args.launches,
        "cpucycles_identity": sorted(set(identities)),
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC); see linked ELF and build rule",
        "primary_placement": "normal; ASLR enabled",
        "command": ["taskset", "-c", str(args.cpu), str(binary)],
    }
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"path": str(result), "summary": {
        k: v["caller_lazy_minus_official_stq2"] for k, v in summary.items()}}, indent=2))


if __name__ == "__main__":
    main()
