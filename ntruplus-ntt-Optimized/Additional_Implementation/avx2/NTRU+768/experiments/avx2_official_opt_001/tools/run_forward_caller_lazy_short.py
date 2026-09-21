#!/usr/bin/env python3
"""Same-ELF SUPERCOP-derived short pricing of Official vs caller-lazy Forward."""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = next(p for p in ROOT.parents if (p / "bench/supercop.lock").exists())
REGIONS = ("forward_r", "forward_keygen_f", "keypair", "encap", "decap")


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--launches", type=int, default=3)
    args = parser.parse_args()
    if execute(["git", "branch", "--show-current"], cwd=REPO).stdout.strip() != "avx2-official-opt":
        raise SystemExit("wrong branch")
    checks = {
        f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor": "performance",
        "/sys/devices/system/cpu/intel_pstate/no_turbo": "1",
    }
    for name, expected in checks.items():
        if Path(name).read_text().strip() != expected:
            raise SystemExit(f"host timing preflight failed: {name}")
    result = ROOT / "results" / args.tag
    if result.exists():
        raise SystemExit(f"refusing overwrite: {result}")
    execute(["make", "check"], cwd=ROOT)
    execute(["make", "build/bench_caller_lazy"], cwd=ROOT)
    binary = ROOT / "build/bench_caller_lazy"
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
    sources = [ROOT / name for name in (
        "upstream/supercop-avx2/ntt.s", "upstream/supercop-avx2/kem.c",
        "asm/ntruplus768_officialopt_ntt_caller_lazy.s", "src/kem_lazy.c",
        "bench/bench_caller_lazy.c", "tools/generate_forward_caller_lazy.py")]
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "source_sha256": {str(path.relative_to(ROOT)): digest(path) for path in sources},
        "elf_sha256": digest(binary),
        "host": platform.platform(),
        "cpu": args.cpu,
        "controls": checks,
        "launches": args.launches,
        "cpucycles_identity": identities,
        "compiler_recipe": "Makefile common O3GC; see linked ELF and build rule",
        "primary_placement": "normal; ASLR enabled",
        "command": ["taskset", "-c", str(args.cpu), str(binary)],
    }
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"path": str(result), "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
