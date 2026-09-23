#!/usr/bin/env python3
"""Same-ELF SUPERCOP-derived component/caller diagnostic of the NTRU+864
exp002 direct codec (supercop-derived; NOT Native SUPERCOP KEM).

Derived from tools/run_codec_fused_diag.py.  Builds (unless --skip-build)
`make direct-check direct-bench`, then runs N fresh processes of
build/bench_codec_direct (or --binary build/bench_codec_direct_swapped, the
reversed-link-order placement control) pinned to one CPU with ASLR left on
(no setarch -R).  Host controls are only read.
Regions: tobytes (Official, exp001 fused, fused_min = exp001 + 2-op freeze,
exp002 direct), frombytes (Official, exp001, exp002) and keypair/encap/decap
for Official, lazy, exp001 (lazy+fused) and exp002 (lazy+direct).

Summary per region and variant: pooled StQ1..3 and quartiles; per launch
StQ2; per-launch deltas (every variant vs Official plus the pairs in PAIRS)
with quartiles over launches and the count of favourable (negative) launches.

Run it under the shared hygiene wrapper, e.g.
  phase_b_batch.py --result-dir results/codec-direct-diag-TAG --metadata metadata.json -- \
    python3 tools/run_codec_direct_diag.py --experiment . --launches 15 --skip-build --result-dir {RESULT}
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
REGIONS = ("tobytes", "frombytes", "keypair", "encap", "decap")
KEM = ("official", "lazy", "exp001", "exp002")
VARIANTS = {0: ("official", "exp001", "fused_min", "exp002"), 1: ("official", "exp001", "exp002"),
            2: KEM, 3: KEM, 4: KEM}
PAIRS = {0: [(2, 1), (3, 1), (3, 2)], 1: [(2, 1)], 2: [(3, 2), (3, 1), (2, 1)],
         3: [(3, 2), (3, 1), (2, 1)], 4: [(3, 2), (3, 1), (2, 1)]}
OBS_PER_LAUNCH = 384   # 12 blocks x 32


def execute(command, **kwargs):
    return subprocess.run(command, text=True, capture_output=True, check=True, **kwargs)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_digest(elf):
    """sha256 of the .text section; the whole-ELF hash changes on every rebuild
    because .strtab records gcc's temporary object names."""
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
    ap.add_argument("--launches", type=int, default=15)
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--binary", default="build/bench_codec_direct",
                    help="bench ELF relative to the experiment (placement control: "
                         "build/bench_codec_direct_swapped)")
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
    if not args.skip_build:
        execute(["make", "direct-check"], cwd=root)
        execute(["make", "direct-bench"], cwd=root)
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
    summary = {"class": "supercop-derived same-ELF diagnostic; not Native SUPERCOP", "regions": {}}
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
        pairs = [(v, 0) for v in range(1, len(names))] + PAIRS[region]
        for a, b in pairs:
            d = [x - y for x, y in zip(launch_stq2[a], launch_stq2[b])]
            entry["deltas"][f"{names[a]}-{names[b]}"] = {
                "pooled_stq2_delta": stq(pooled[region, a])[1] - stq(pooled[region, b])[1],
                "launch_delta_quartiles": quartiles(d),
                "favourable_launches": sum(x < 0 for x in d), "launches": len(d),
                "launch_deltas": d}
        summary["regions"][rname] = entry
    (result / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    sources = [root / p for p in (
        "asm/ntruplus864_officialopt_codec_fused.s", "asm/ntruplus864_officialopt_codec_fused_min.s",
        "asm/ntruplus864_officialopt_codec_direct.s", "asm/ntruplus864_officialopt_ntt_caller_lazy.s",
        "src/kem_lazy.c", "src/kem_lazy_codec.c", "src/kem_lazy_codec_direct.c", "upstream/supercop-avx2/kem.c",
        "upstream/supercop-avx2/pack.s", "upstream/supercop-avx2/poly.c",
        "bench/bench_codec_direct.c", "codec.mk", "codec_direct.mk", "tools/generate_codec_fused.py",
        "tools/generate_codec_direct.py")]
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "parameter": "864",
        "source_sha256": {str(p.relative_to(REPO)): digest(p) for p in sources},
        "elf_sha256": digest(binary),
        "elf_text_sha256": text_digest(binary),  # rebuild-stable (.strtab carries gcc temp names)
        "host": platform.platform(),
        "cpu": args.cpu,
        "controls_read_only": controls,
        "aslr": "on (randomize_va_space=2, no setarch -R)",
        "launches": args.launches,
        "observations_per_variant_per_launch": OBS_PER_LAUNCH,
        "cpucycles_identity": sorted(identities),
        "compiler": execute(["cc", "--version"]).stdout.splitlines()[0],
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC); see codec_direct.mk bench_codec_direct rule",
        "binary": args.binary,
        "command": ["taskset", "-c", str(args.cpu), str(binary)],
    }
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    brief = {r: {k: round(v["pooled_stq2_delta"], 1) for k, v in e["deltas"].items()}
             for r, e in summary["regions"].items()}
    print(json.dumps({"path": str(result), "pooled_stq2_deltas": brief}, indent=1))


if __name__ == "__main__":
    main()
