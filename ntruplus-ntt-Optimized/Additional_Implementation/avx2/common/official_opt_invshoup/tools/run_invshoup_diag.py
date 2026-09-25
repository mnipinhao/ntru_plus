#!/usr/bin/env python3
"""Same-ELF SUPERCOP-derived diagnostic of the NTRU+768 / 864 / 1152 fused inverse and Shoup
BaseMul on the current best (supercop-derived, NOT Native SUPERCOP KEM).

Derived from common/official_opt_ht/tools/run_ht_diag.py (same launch, host-control and summary
logic).  Runs N fresh processes of build/bench_invshoup_diag (normal link order) or --binary
build/bench_invshoup_diag_swapped (reversed link order, placement control) pinned to one CPU with
ASLR left on (no setarch -R).  Host controls are only read.  Build first with
`make invshoup-check invshoup-bench`.
Regions: inverse (current best vs fused invntt_crep), bm_encap / bm_decap (Official poly_basemul vs
Shoup on the real Encap / second-Decap operands), keypair (seed-matched) / encap / decap for the
five KEM variants of bench_invshoup_diag.c; 20 blocks x 32 observations per variant per launch.
All deltas are between identical cpucycles() anchors (same null-call overhead).

  phase_b_batch.py --result-dir results/invshoup-diag-normal-TAG --metadata metadata.json -- \\
    python3 ../../../common/official_opt_invshoup/tools/run_invshoup_diag.py --param N \\
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
REGIONS = ("inverse", "bm_encap", "bm_decap", "keypair", "encap", "decap")
KEM = {768: ("official", "base", "shoup", "invcrep_only", "invcrep_shoup"),
       864: ("official", "base", "candidate", "invd_only", "shoup_only"),
       1152: ("official", "base", "candidate", "invd_only", "shoup_only")}
KEM_PAIRS = [(v, 1) for v in range(2, 5)] + [(2, v) for v in range(3, 5)]
OBS_PER_LAUNCH = 640   # 20 blocks x 32
STEM = {768: "freeze2op", 864: "codec_direct", 1152: "freeze2op"}


def sources(n):
    s, p = STEM[n], f"ntruplus{n}_officialopt"
    ht = f"src/kem_lazy_r2fold_{s}_keccak_ht" + ("_htinv" if n == 768 else "") + ".c"
    files = ["src/kem_lazy.c", "src/kem_lazy_r2fold.c", ht, f"src/kem_lazy_r2fold_{s}_keccak_ht.c",
             f"src/kem_lazy_r2fold_{s}_keccak.c", f"src/{p}_baseinv_r2fold.c",
             f"asm/{p}_ntt_caller_lazy.s", f"asm/{p}_ntt_ht.s", f"asm/{p}_basemul_nor2.s",
             f"asm/{p}_invntt_crep.s", f"asm/{p}_basemul_shoup.s", f"src/{p}_basemul_shoup.c",
             "asm/" + (f"{p}_codec_direct.s" if n == 864 else f"{p}_tobytes_freeze2op.s")]
    if n == 768:
        files.append(f"asm/{p}_invntt_ht.s")
    for v in ("invcrep", "shoup", "invcrep_shoup"):
        files += [f"src/kem_lazy_r2fold_{v}.c", f"src/kem_lazy_r2fold_{v}_{s}_keccak.c",
                  f"src/kem_lazy_r2fold_{v}_{s}_keccak_ht.c"]
    if n == 768:
        files.append(f"src/kem_lazy_r2fold_shoup_{s}_keccak_ht_htinv.c")
    return list(dict.fromkeys(files))


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
    ap.add_argument("--binary", default="build/bench_invshoup_diag",
                    help="bench ELF relative to the experiment (placement control: "
                         "build/bench_invshoup_diag_swapped)")
    args = ap.parse_args()
    kem = KEM[args.param]
    VARIANTS = {0: ("current_best", "invntt_crep"), 1: ("official", "shoup"), 2: ("official", "shoup"),
                3: kem, 4: kem, 5: kem}
    PAIRS = {0: [], 1: [], 2: [], 3: KEM_PAIRS, 4: KEM_PAIRS, 5: KEM_PAIRS}
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
    common = HERE.parents[2]
    mlk = REPO / "third_party/mlkem-native-fips202-b3ba7b32/mlkem/src/fips202"
    srcs = [root / p for p in sources(args.param) + [
        "upstream/supercop-avx2/kem.c", "upstream/supercop-avx2/poly.c", "upstream/supercop-avx2/basemul.s",
        "upstream/supercop-avx2/invntt.s", "upstream/supercop-avx2/crepmod3.s", "upstream/supercop-avx2/ntt.s"]] + [
        common / p for p in ("official_opt_invshoup/bench/bench_invshoup_diag.c", "official_opt_invshoup/invshoup.mk",
                             "official_opt_ht/ht.mk", "official_opt_lazy/bench/kem_diag.c",
                             "official_opt_lazy/lazy.mk", "official_opt_keccak/keccak.mk",
                             "official_opt_keccak/src/symmetric_keccak.c")] + [mlk / "fips202.c", mlk / "keccakf1600.c"]
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "parameter": str(args.param),
        "source_sha256": {str(p.resolve().relative_to(REPO)): digest(p) for p in srcs},
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
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC) for all objects (invshoup.mk invshoup-bench)",
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
