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
    parser.add_argument("--candidate", choices=("ct", "ct-r3", "ct-r3-vs-ct",
                                                "ct-full", "ct-full-vs-ct",
                                                "ct-cohort", "ct-cohort-vs-ct"), default="ct")
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
    suffix = {"ct": "", "ct-r3": "_r3", "ct-r3-vs-ct": "_r3_compare",
              "ct-full": "_full", "ct-full-vs-ct": "_full_compare",
              "ct-cohort": "_cohort", "ct-cohort-vs-ct": "_cohort_compare"}[args.candidate]
    check = ("check-inverse-ct-cohort" if "cohort" in suffix else
             "check-inverse-ct-full" if "full" in suffix else
             "check-inverse-ct-r3" if suffix else "check-inverse-ct")
    execute(["make", check], cwd=ROOT)
    execute(["make", f"build/bench_inverse_ct{suffix}"], cwd=ROOT)
    binary = ROOT / "build" / f"bench_inverse_ct{suffix}"
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
        "asm/ntruplus768_officialopt_invntt_ct.s",
        *(["asm/ntruplus768_officialopt_invntt_ct_r3.s",
           "tools/generate_inverse_ct_r3.py", "tools/prove_inverse_ct_r3_range.py"]
          if "r3" in suffix else []),
        *(["asm/ntruplus768_officialopt_invntt_ct_full.s",
           "tools/generate_inverse_ct_full.py", "tools/prove_inverse_ct_full_range.py"]
          if "full" in suffix else []),
        *(["asm/ntruplus768_officialopt_invntt_ct_cohort.s",
           "tools/generate_inverse_ct_cohort.py", "tools/prove_inverse_ct_full_range.py"]
          if "cohort" in suffix else []),
        "src/kem_ct.c",
        "bench/bench_inverse_ct.c", "tools/run_inverse_ct_short.py")]
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "candidate": args.candidate,
        "baseline": "CT control" if args.candidate.endswith("vs-ct") else "pinned Official",
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
