#!/usr/bin/env python3
"""Same-ELF SUPERCOP-derived diagnostic of the NTRU+768 HT Forward and keygen
R^2 fold (supercop-derived, NOT Native SUPERCOP KEM).

Derived from common/official_opt_keccak/tools/run_keccak_diag.py.  Runs N
fresh processes of build/bench_ht_diag (normal link order) or --binary
build/bench_ht_diag_swapped (reversed link order, placement control) pinned
to one CPU with ASLR left on (no setarch -R).  Host controls are only read.
Build first with `make ht-check ht-bench`.
Regions: forward (lazy vs HT), keygen basemul (Official vs no-R^2 core on the
R-scaled inverse), baseinv (Official vs fold), invntt (Official vs HT inverse);
keypair (seed-matched) / encap / decap for Official, base (lazy+freeze+keccak),
candidate, ht_only, r2fold_only, htinv_only, ht_r2fold.
All deltas are between identical cpucycles() anchors (same null-call overhead).

Summary per region and variant: pooled StQ1..3 and quartiles; per-launch
StQ2; per-launch deltas (every variant vs variant 0, plus every KEM variant
vs base and candidate vs each control) with quartiles over launches and the
count of favourable (negative) launches.

  phase_b_batch.py --result-dir results/ht-diag-normal-TAG --metadata metadata.json -- \\
    python3 ../../../common/official_opt_ht/tools/run_ht_diag.py \\
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
REGIONS = ("forward", "basemul", "baseinv", "invntt", "keypair", "encap", "decap")
KEM = ("official", "base", "candidate", "ht_only", "r2fold_only", "htinv_only", "ht_r2fold")
VARIANTS = {0: ("lazy", "ht"), 1: ("official", "nor2_on_fold_inverse"), 2: ("official", "fold"),
            3: ("official", "ht"), 4: KEM, 5: KEM, 6: KEM}
KEM_PAIRS = [(v, 1) for v in range(2, 7)] + [(2, v) for v in range(3, 7)]
PAIRS = {0: [], 1: [], 2: [], 3: [], 4: KEM_PAIRS, 5: KEM_PAIRS, 6: KEM_PAIRS}
OBS_PER_LAUNCH = 448   # 14 blocks x 32


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
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--result-dir", type=Path, required=True)
    ap.add_argument("--cpu", type=int, default=1)
    ap.add_argument("--launches", type=int, default=31)
    ap.add_argument("--binary", default="build/bench_ht_diag",
                    help="bench ELF relative to the experiment (placement control: "
                         "build/bench_ht_diag_swapped)")
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
               "parameter": "NTRU+768", "binary": args.binary, "regions": {}}
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
    hcommon = HERE.parents[1]
    lcommon = hcommon.parent / "official_opt_lazy"
    kcommon = hcommon.parent / "official_opt_keccak"
    mlk = REPO / "third_party/mlkem-native-fips202-b3ba7b32/mlkem/src/fips202"
    sources = [root / p for p in (
        "src/kem_lazy.c", "src/kem_lazy_freeze2op.c", "src/kem_lazy_freeze2op_keccak.c",
        "src/kem_lazy_r2fold.c", "src/kem_lazy_freeze2op_keccak_ht.c", "src/kem_lazy_r2fold_freeze2op_keccak.c",
        "src/kem_lazy_r2fold_freeze2op_keccak_ht.c", "src/kem_lazy_freeze2op_keccak_htinv.c",
        "src/kem_lazy_r2fold_freeze2op_keccak_ht_htinv.c", "src/ntruplus768_officialopt_baseinv_r2fold.c",
        "asm/ntruplus768_officialopt_invntt_ht.s", "upstream/supercop-avx2/invntt.s",
        "asm/ntruplus768_officialopt_ntt_caller_lazy.s", "asm/ntruplus768_officialopt_ntt_ht.s",
        "asm/ntruplus768_officialopt_basemul_nor2.s", "asm/ntruplus768_officialopt_tobytes_freeze2op.s",
        "upstream/supercop-avx2/kem.c", "upstream/supercop-avx2/poly.c", "upstream/supercop-avx2/basemul.s",
        "upstream/supercop-avx2/ntt.s")] + [hcommon / p for p in ("bench/bench_ht_diag.c", "ht.mk")] + [
        lcommon / "bench/kem_diag.c", lcommon / "lazy.mk", kcommon / "keccak.mk",
        kcommon / "src/symmetric_keccak.c", mlk / "fips202.c", mlk / "keccakf1600.c"]
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "parameter": "768",
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
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC) for all objects (ht.mk ht-bench)",
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
