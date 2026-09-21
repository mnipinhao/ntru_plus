#!/usr/bin/env python3
"""Three-launch same-ELF inverse/Decap diagnostic, not Native SUPERCOP."""

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
REGIONS = ("inverse_only", "inverse_plus_crepmod3", "complete_decap")


def execute(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, check=True, **kwargs)


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
    controls = {
        f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor": "performance",
        "/sys/devices/system/cpu/intel_pstate/no_turbo": "1",
    }
    for path, expected in controls.items():
        if Path(path).read_text().strip() != expected:
            raise SystemExit(f"host timing policy failed: {path}")
    result = ROOT / "results" / args.tag
    if result.exists():
        raise SystemExit(f"refusing overwrite: {result}")
    execute(["make", "check-inverse-ct"], cwd=ROOT)
    execute(["make", "build/bench_inverse_ct"], cwd=ROOT)
    binary = ROOT / "build/bench_inverse_ct"
    result.mkdir(parents=True)
    shutil.copy2(binary, result / "bench_inverse_ct.elf")
    all_rows = []
    identities = []
    for launch in range(args.launches):
        observed = execute(["taskset", "-c", str(args.cpu), str(binary)])
        (result / f"launch-{launch}.out").write_text(observed.stdout)
        (result / f"launch-{launch}.err").write_text(observed.stderr)
        if "preflight=pass" not in observed.stderr:
            raise ValueError("missing untimed correctness preflight")
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
        deltas = []
        for launch in range(args.launches):
            official = [r[5] for r in all_rows if r[:3] == (launch, region, 0)]
            ct = [r[5] for r in all_rows if r[:3] == (launch, region, 1)]
            deltas.append(stq(ct)[1] - stq(official)[1])
        summary[name] = {
            "official_stq": baseline,
            "ct_stq": candidate,
            "ct_minus_official_stq2": candidate[1] - baseline[1],
            "launch_deltas": deltas,
            "favorable_launches": sum(x < 0 for x in deltas),
        }
    sources = [ROOT / name for name in (
        "upstream/supercop-avx2/invntt.s", "upstream/supercop-avx2/kem.c",
        "asm/ntruplus768_officialopt_invntt_ct.s", "src/kem_ct.c",
        "bench/bench_inverse_ct.c", "tools/run_inverse_ct_short.py")]
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources},
        "elf_sha256": digest(binary),
        "saved_elf_sha256": digest(result / "bench_inverse_ct.elf"),
        "host": platform.platform(),
        "compiler": execute(["cc", "--version"]).stdout.splitlines()[0],
        "smt_siblings": Path(f"/sys/devices/system/cpu/cpu{args.cpu}/topology/thread_siblings_list").read_text().strip(),
        "cpu": args.cpu,
        "controls": controls,
        "launches": args.launches,
        "observations_per_variant_region_launch": 8 * 64,
        "cpucycles_identity": identities,
        "compiler_recipe": "Makefile common O3GC; see build rule",
        "placement": "normal, ASLR enabled, one fixed ELF",
        "inverse_input": "16 banks of precomputed canonical-input BaseMulScale output; reset outside timing",
        "decap_input": "16 deterministic valid CT/SK banks; unchanged Official caller except CT inverse",
        "command": ["taskset", "-c", str(args.cpu), str(binary)],
    }
    (result / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"path": str(result), "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
