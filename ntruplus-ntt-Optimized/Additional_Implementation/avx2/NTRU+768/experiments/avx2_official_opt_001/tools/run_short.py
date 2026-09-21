#!/usr/bin/env python3
"""Run the Official-vs-fused same-ELF SUPERCOP-derived short diagnostic."""

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


def execute(command, **kwargs):
    return subprocess.run(command, text=True, capture_output=True, check=True, **kwargs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stq(values):
    values = sorted(values)
    n = len(values)
    return [sum(values[n * (1 + 2*i)//8:n * (3 + 2*i)//8]) /
            (n * (3 + 2*i)//8 - n * (1 + 2*i)//8) for i in range(3)]


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
    execute(["make", "build/bench_fused"], cwd=ROOT)
    result.mkdir(parents=True)
    binary = ROOT / "build/bench_fused"
    all_rows = []
    identities = []
    for launch in range(args.launches):
        observed = execute(["taskset", "-c", str(args.cpu), str(binary)])
        (result / f"launch-{launch}.out").write_text(observed.stdout)
        (result / f"launch-{launch}.err").write_text(observed.stderr)
        if "preflight=pass" not in observed.stderr:
            raise SystemExit("missing preflight")
        identities.append([line for line in observed.stderr.splitlines()
                           if line.startswith("cpucycles=")])
        for row in csv.reader(line for line in observed.stdout.splitlines()
                              if line[:1].isdigit()):
            region, variant, block, observation, cycles = map(int, row)
            all_rows.append((launch, region, variant, block, observation, cycles))
    samples = defaultdict(list)
    for launch, region, variant, _, _, cycles in all_rows:
        samples[region, variant].append(cycles)
    summary = {}
    for region, name in enumerate(("basemul_plus_add", "complete_encap")):
        official = stq(samples[region, 0])
        fused = stq(samples[region, 1])
        launches = []
        for launch in range(args.launches):
            a = [r[5] for r in all_rows if r[:3] == (launch, region, 0)]
            b = [r[5] for r in all_rows if r[:3] == (launch, region, 1)]
            launches.append(stq(b)[1] - stq(a)[1])
        summary[name] = dict(official_stq=official, fused_stq=fused,
                             fused_minus_official_stq2=fused[1]-official[1],
                             launch_deltas=launches,
                             favorable_launches=sum(x < 0 for x in launches))
    (result / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    sources = [ROOT / p for p in (
        "upstream/supercop-avx2/basemul.s", "upstream/supercop-avx2/kem.c",
        "asm/ntruplus768_officialopt_basemul_add.s", "src/kem_fused.c",
        "src/kem_reference.c", "bench/bench_fused.c")]
    metadata = dict(label="supercop-derived diagnostic, not Native KEM",
                    source_sha256={str(p.relative_to(ROOT)): digest(p) for p in sources},
                    elf_sha256=digest(binary), host=platform.platform(),
                    controls=checks, cpu=args.cpu, launches=args.launches,
                    cpucycles_identity=identities,
                    command=["taskset", "-c", str(args.cpu), str(binary)])
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(dict(path=str(result), summary=summary), indent=2))


if __name__ == "__main__":
    main()
