#!/usr/bin/env python3
"""Same-ELF SUPERCOP-derived diagnostic of the mlkem-native x1 Keccak backend
(NTRU+768 / 864 / 1152; supercop-derived, NOT Native SUPERCOP KEM).

Derived from common/official_opt_lazy/tools/run_freeze2op_diag.py.  Runs N
fresh processes of build/bench_keccak_diag (normal link order) or --binary
build/bench_keccak_diag_swapped (reversed link order, placement control)
pinned to one CPU with ASLR left on (no setarch -R).  Host controls are only
read.  Build first with `make keccak-check keccak-bench`.
Regions: x1 permute and hash_f/g/h for Official, mlkem-native -O3 and
mlkem-native -O2; keypair (seed-matched) / encap / decap for Official, base
candidate, base + keccak (candidate) and keccak only (control).

Summary per region and variant: pooled StQ1..3 and quartiles; per-launch
StQ2; per-launch deltas (every variant vs Official, plus mlkem_o2-mlkem_o3
for the hash regions and base_keccak-base for the KEM regions) with quartiles
over launches and the count of favourable (negative) launches.

  phase_b_batch.py --result-dir results/keccak-diag-normal-TAG --metadata metadata.json -- \\
    python3 ../../../common/official_opt_keccak/tools/run_keccak_diag.py --param 768 \\
      --experiment . --launches 31 --result-dir {RESULT}
"""

import argparse
import csv
import hashlib
import json
import platform
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
BRANCH = "official-opt-lazy-864-1152"
REGIONS = ("permute", "hash_f", "hash_g", "hash_h", "keypair", "encap", "decap")
HASH = ("official", "mlkem_o3", "mlkem_o2")
KEM = ("official", "base", "base_keccak", "keccak_only")
VARIANTS = {0: HASH, 1: HASH, 2: HASH, 3: HASH, 4: KEM, 5: KEM, 6: KEM}
PAIRS = {r: [(2, 1)] for r in range(7)}   # hash: o2-o3; KEM: base_keccak-base
OBS_PER_LAUNCH = 384   # 12 blocks x 32
BASES = {768: ("kem_lazy_freeze2op", ["asm/ntruplus768_officialopt_ntt_caller_lazy.s",
                                      "asm/ntruplus768_officialopt_tobytes_freeze2op.s"]),
         864: ("kem_lazy_codec_direct", ["asm/ntruplus864_officialopt_ntt_caller_lazy.s",
                                         "asm/ntruplus864_officialopt_codec_direct.s"]),
         1152: ("kem_lazy_freeze2op", ["asm/ntruplus1152_officialopt_ntt_caller_lazy.s",
                                       "asm/ntruplus1152_officialopt_tobytes_freeze2op.s"])}


def execute(command, **kwargs):
    return subprocess.run(command, text=True, capture_output=True, check=True, **kwargs)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_digest(elf):
    """sha256 of .text (rebuild-stable; .strtab carries gcc temp names)."""
    return hashlib.sha256(subprocess.run(
        ["objcopy", "-O", "binary", "--only-section=.text", str(elf), "/dev/stdout"],
        check=True, capture_output=True).stdout).hexdigest()


def stq(values):
    values = sorted(values)
    n = len(values)
    return [sum(values[n * (1 + 2 * i) // 8:n * (3 + 2 * i) // 8]) /
            (n * (3 + 2 * i) // 8 - n * (1 + 2 * i) // 8) for i in range(3)]


def quartiles(values):
    q = statistics.quantiles(values, n=4, method="inclusive")
    return {"q1": q[0], "median": q[1], "q3": q[2]}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--result-dir", type=Path, required=True)
    ap.add_argument("--cpu", type=int, default=1)
    ap.add_argument("--launches", type=int, default=31)
    ap.add_argument("--binary", default="build/bench_keccak_diag",
                    help="bench ELF relative to the experiment (placement control: "
                         "build/bench_keccak_diag_swapped)")
    args = ap.parse_args()
    root = args.experiment.resolve()
    if execute(["git", "branch", "--show-current"], cwd=REPO).stdout.strip() != BRANCH:
        raise SystemExit("wrong branch")
    controls = {
        f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor": "performance",
        "/sys/devices/system/cpu/intel_pstate/no_turbo": "1",
        "/proc/sys/kernel/randomize_va_space": "2",
    }
    for name, expected in controls.items():
        if Path(name).read_text().strip() != expected:
            raise SystemExit(f"host timing preflight failed: {name}")
    result = args.result_dir.resolve()
    if result.exists():
        raise SystemExit(f"refusing overwrite: {result}")
    binary = root / args.binary
    result.mkdir(parents=True)
    rows, identities = [], set()
    for launch in range(args.launches):
        observed = execute(["taskset", "-c", str(args.cpu), str(binary)])
        (result / f"launch-{launch}.out").write_text(observed.stdout)
        (result / f"launch-{launch}.err").write_text(observed.stderr)
        if "preflight=pass" not in observed.stderr:
            raise ValueError("missing benchmark preflight")
        identities.update(l for l in observed.stderr.splitlines() if l.startswith("cpucycles="))
        for row in csv.reader(l for l in observed.stdout.splitlines() if l[:1].isdigit()):
            region, variant, _, _, cycles = map(int, row)
            rows.append((launch, region, variant, cycles))
    pooled = defaultdict(list)
    per_launch = defaultdict(list)
    for launch, region, variant, cycles in rows:
        pooled[region, variant].append(cycles)
        per_launch[launch, region, variant].append(cycles)
    summary = {"class": "supercop-derived same-ELF diagnostic; not Native SUPERCOP",
               "parameter": f"NTRU+{args.param}", "binary": args.binary, "regions": {}}
    for region, rname in enumerate(REGIONS):
        names = VARIANTS[region]
        launch_stq2 = {v: [stq(per_launch[l, region, v])[1] for l in range(args.launches)]
                       for v in range(len(names))}
        entry = {"variants": {}, "deltas": {}}
        for v, vname in enumerate(names):
            entry["variants"][vname] = {"pooled_stq": stq(pooled[region, v]),
                                        "pooled_quartiles": quartiles(pooled[region, v]),
                                        "launch_stq2": launch_stq2[v],
                                        "launch_stq2_median": statistics.median(launch_stq2[v])}
        for a, b in [(v, 0) for v in range(1, len(names))] + PAIRS[region]:
            d = [x - y for x, y in zip(launch_stq2[a], launch_stq2[b])]
            entry["deltas"][f"{names[a]}-{names[b]}"] = {
                "pooled_stq2_delta": stq(pooled[region, a])[1] - stq(pooled[region, b])[1],
                "launch_delta_quartiles": quartiles(d),
                "favourable_launches": sum(x < 0 for x in d), "launches": len(d),
                "launch_deltas": d}
        summary["regions"][rname] = entry
    (result / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    n = args.param
    kcommon = HERE.parents[1]
    lcommon = kcommon.parent / "official_opt_lazy"
    base, base_asm = BASES[n]
    mlk = REPO / "third_party/mlkem-native-fips202-b3ba7b32/mlkem/src/fips202"
    sources = [root / p for p in (
        f"src/{base}.c", f"src/{base}_keccak.c", "src/kem_keccak.c", "src/kem_lazy.c",
        "upstream/supercop-avx2/kem.c", "upstream/supercop-avx2/symmetric.c", "upstream/supercop-avx2/fips202.c",
        "upstream/supercop-avx2/KeccakP-1600-AVX2.s", *base_asm)] + [kcommon / p for p in (
        "bench/bench_keccak_diag.c", "keccak.mk", "src/fips202_mlkem.h", "src/keccak_names.h",
        "src/symmetric_keccak.c", "config/mlkem_native_config.h", "tools/generate_keccak_overlays.py")] + [
        lcommon / "bench/kem_diag.c", lcommon / "lazy.mk", mlk / "fips202.c", mlk / "keccakf1600.c"]
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "parameter": str(n),
        "source_sha256": {str(p.resolve().relative_to(REPO)): digest(p) for p in sources},
        "elf_sha256": digest(binary),
        "elf_text_sha256": text_digest(binary),
        "host": platform.platform(),
        "cpu": args.cpu,
        "controls_read_only": controls,
        "aslr": "on (randomize_va_space=2, no setarch -R)",
        "launches": args.launches,
        "observations_per_variant_per_launch": OBS_PER_LAUNCH,
        "cpucycles_identity": sorted(identities),
        "compiler": execute(["cc", "--version"]).stdout.splitlines()[0],
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC) for all objects; the mlkem_o2 variant is a "
                           "second copy of mlk fips202.c/keccakf1600.c/symmetric_keccak.c built with the same "
                           "flags but -O2 (keccak.mk KBENCH_O2)",
        "binary": args.binary,
        "link_order": "reversed" if "swapped" in args.binary else "normal",
        "command": ["taskset", "-c", str(args.cpu), str(binary)],
    }
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    brief = {r: {k: round(v["pooled_stq2_delta"], 1) for k, v in e["deltas"].items()}
             for r, e in summary["regions"].items()}
    print(json.dumps({"path": str(result), "pooled_stq2_deltas": brief}, indent=1))


if __name__ == "__main__":
    main()
