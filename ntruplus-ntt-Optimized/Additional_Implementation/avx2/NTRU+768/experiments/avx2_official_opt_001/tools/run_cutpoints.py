#!/usr/bin/env python3
"""Price matched cumulative Official caller cutpoints, with fresh launches."""

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
LABELS = {
    "keygen": ("sample_f", "forward_f", "baseinv_f", "sample_g", "forward_g",
               "baseinv_g", "first_product_pack_pk", "second_product_pack_sk",
               "hash_f", "clear"),
    "encap": ("decode_pk", "prehash_cbd_r", "forward_r", "serialize_r",
              "hash_g", "sotp_m", "forward_m", "basemul_add", "serialize_c",
              "ss_copy_clear"),
    "decap": ("decode_ct_sk", "basemul_scale", "inverse_crepmod3",
              "message_forward_sub", "recover_basemul", "serialize_recovered_r",
              "hash_g", "sotp_decode", "hash_h", "reencrypt_forward",
              "reencrypt_pack_compare_clear"),
}


def stq(values):
    ordered = sorted(values)
    n = len(ordered)
    return [sum(ordered[n*(1+2*i)//8:n*(3+2*i)//8]) /
            (n*(3+2*i)//8-n*(1+2*i)//8) for i in range(3)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--launches", type=int, default=3)
    args = parser.parse_args()
    if args.launches not in (3, 9):
        raise SystemExit("launches must be 3 or 9")
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=REPO,
                               text=True).strip() != "avx2-official-opt":
        raise SystemExit("wrong branch")
    checks = {f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor":
              "performance", "/sys/devices/system/cpu/intel_pstate/no_turbo": "1"}
    for path, expected in checks.items():
        if Path(path).read_text().strip() != expected:
            raise SystemExit(f"host timing policy failed: {path}")
    result = ROOT / "results" / args.tag
    if result.exists():
        raise SystemExit(f"refusing overwrite: {result}")
    subprocess.run(["make", "build/bench_cutpoints"], cwd=ROOT, check=True,
                   capture_output=True)
    result.mkdir(parents=True)
    binary = ROOT / "build/bench_cutpoints"
    samples = defaultdict(list)
    launch_samples = defaultdict(list)
    retry_counts = []
    names = list(LABELS)
    for launch in range(args.launches):
        proc = subprocess.run(["taskset", "-c", str(args.cpu), str(binary)],
                              text=True, capture_output=True, check=True)
        (result / f"launch-{launch:02d}.out").write_text(proc.stdout)
        (result / f"launch-{launch:02d}.err").write_text(proc.stderr)
        if "preflight=pass" not in proc.stderr:
            raise SystemExit("missing full caller byte preflight")
        retry_counts.append([line for line in proc.stderr.splitlines()
                             if line.startswith("preflight=pass")])
        for row in csv.reader(line for line in proc.stdout.splitlines()
                              if line[:1].isdigit()):
            family, cut, block, obs, cycles = map(int, row)
            key = (names[family], cut)
            if cut >= len(LABELS[names[family]]):
                raise SystemExit("invalid cutpoint")
            samples[key].append(cycles)
            launch_samples[(launch, *key)].append(cycles)
    summary = {}
    for family, stages in LABELS.items():
        result_stages = []
        for index, label in enumerate(stages):
            overall = stq(samples[family, index])
            stage_launches = []
            for launch in range(args.launches):
                current = stq(launch_samples[launch, family, index])[1]
                prior = (stq(launch_samples[launch, family, index-1])[1]
                         if index else 0.0)
                stage_launches.append(current-prior)
            result_stages.append(dict(label=label, cumulative_stq=overall,
                                      incremental_stq2=(overall[1] -
                                                        (stq(samples[family,index-1])[1]
                                                         if index else 0.0)),
                                      incremental_launches=stage_launches))
        summary[family] = result_stages
    (result / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    (result / "metadata.json").write_text(json.dumps(dict(
        benchmark_class="supercop-derived-cumulative-cutpoints",
        contract="prepared valid-input banks; fresh reset from PK/CT or f/g coins per cut; successful keygen path excludes randombytes/retry",
        host=platform.platform(), cpu=args.cpu, controls=checks,
        launches=args.launches, retry_counts=retry_counts,
        elf_sha256=digest(binary), source_sha256=digest(ROOT/"bench/bench_cutpoints.c")
    ), indent=2)+"\n")
    for family, stages in summary.items():
        print(family, [(stage["label"], round(stage["incremental_stq2"], 2))
                       for stage in stages])
    print(result)


if __name__ == "__main__":
    main()
