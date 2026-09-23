#!/usr/bin/env python3
"""SCRATCH decision-gate measurement of a direct 12-bit codec on the Official
NTRU+768 / NTRU+1152 AVX2 8-way layout (supercop-derived component timing,
NOT Native SUPERCOP, no KEM).  Derived from run_freeze2op_diag.py.

Runs N fresh processes of build/bench_codec8_scratch (normal link order) or
--binary build/bench_codec8_scratch_swapped (reversed link order) pinned to
one CPU with ASLR left on (no setarch -R).  Host controls are only read.
Build first with `make codec8-scratch-check codec8-scratch-bench`.
Regions: tobytes (Official, freeze2op, scratch pack, scratch madd) and
frombytes (Official, scratch).

  phase_b_batch.py --result-dir results/codec8-scratch-normal-TAG --metadata metadata.json -- \
    python3 ../../../common/official_opt_lazy/tools/run_codec8_scratch.py --param 768 \
      --experiment . --launches 15 --result-dir {RESULT}
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
REGIONS = ("tobytes", "frombytes")
VARIANTS = {0: ("official", "freeze2op", "scratch_pack", "scratch_madd"), 1: ("official", "scratch")}
PAIRS = {0: [(2, 1), (3, 1), (2, 3)], 1: []}
OBS_PER_LAUNCH = 384   # 12 blocks x 32


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
    ap.add_argument("--param", type=int, choices=(768, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--result-dir", type=Path, required=True)
    ap.add_argument("--cpu", type=int, default=1)
    ap.add_argument("--launches", type=int, default=15)
    ap.add_argument("--binary", default="build/bench_codec8_scratch",
                    help="bench ELF relative to the experiment (placement control: "
                         "build/bench_codec8_scratch_swapped)")
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
    summary = {"class": "scratch component measurement (supercop-derived cpucycles); not Native SUPERCOP",
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
    common = HERE.parents[1]
    sources = [root / p for p in (
        f"asm/ntruplus{n}_officialopt_tobytes_freeze2op.s", "upstream/supercop-avx2/pack.s",
        "upstream/supercop-avx2/consts.c")] + [common / p for p in (
        "bench/bench_codec8_scratch.c", "bench/scratch_codec8.c", "codec8_scratch.mk", "freeze2op.mk",
        "lazy.mk", "tools/run_codec8_scratch.py")]
    metadata = {
        "class": "scratch component measurement (supercop-derived cpucycles); not Native SUPERCOP",
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
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC); see codec8_scratch.mk",
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
