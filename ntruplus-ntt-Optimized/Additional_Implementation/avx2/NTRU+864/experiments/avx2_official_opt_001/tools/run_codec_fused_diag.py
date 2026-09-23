#!/usr/bin/env python3
"""Same-ELF SUPERCOP-derived component/caller diagnostic of the NTRU+864
layout-fused codec (supercop-derived; NOT Native SUPERCOP KEM).

Builds (unless --skip-build) `make codec-check codec-bench`, then runs N fresh
processes of build/bench_codec_fused pinned to one CPU with ASLR left on (no
setarch -R).  Host controls are only read (governor, no_turbo, ASLR sysctl).
Regions: tobytes/frombytes (Official vs fused) and keypair/encap/decap for
Official (v0), lazy (v1), codec-only (v2) and lazy+codec (v3).

Summary per region and variant: pooled StQ1..3 and quartiles over all
observations; per launch StQ2; per launch delta vs Official (and v3 - v1,
the codec effect on top of the lazy Forward) with median/quartiles over
launches and the count of favourable (negative) launches.

Run it under the shared hygiene wrapper, e.g.
  phase_b_batch.py --result-dir results/codec-fused-diag-TAG --metadata metadata.json -- \
    python3 tools/run_codec_fused_diag.py --experiment . --launches 15 --skip-build --result-dir {RESULT}
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
VARIANTS = {0: ("official", "fused"), 1: ("official", "fused"),
            2: ("official", "lazy", "codec", "lazy_codec"),
            3: ("official", "lazy", "codec", "lazy_codec"),
            4: ("official", "lazy", "codec", "lazy_codec")}


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
    ap.add_argument("--binary", default="build/bench_codec_fused",
                    help="bench ELF relative to the experiment (placement control: "
                         "build/bench_codec_fused_swapped)")
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
        execute(["make", "codec-check"], cwd=root)
        execute(["make", "codec-bench"], cwd=root)
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
        pairs = [(v, 0) for v in range(1, len(names))]
        if len(names) == 4:
            pairs.append((3, 1))   # codec on top of lazy
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
        "asm/ntruplus864_officialopt_codec_fused.s", "asm/ntruplus864_officialopt_ntt_caller_lazy.s",
        "src/kem_lazy.c", "src/kem_codec.c", "src/kem_lazy_codec.c", "upstream/supercop-avx2/kem.c",
        "upstream/supercop-avx2/pack.s", "upstream/supercop-avx2/poly.c",
        "bench/bench_codec_fused.c", "codec.mk", "tools/generate_codec_fused.py")]
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
        "observations_per_variant_per_launch": 256,
        "cpucycles_identity": sorted(identities),
        "compiler": execute(["cc", "--version"]).stdout.splitlines()[0],
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC); see codec.mk bench_codec_fused rule",
        "binary": args.binary,
        "command": ["taskset", "-c", str(args.cpu), str(binary)],
    }
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    brief = {r: {k: round(v["pooled_stq2_delta"], 1) for k, v in e["deltas"].items()}
             for r, e in summary["regions"].items()}
    print(json.dumps({"path": str(result), "pooled_stq2_deltas": brief}, indent=1))


if __name__ == "__main__":
    main()
