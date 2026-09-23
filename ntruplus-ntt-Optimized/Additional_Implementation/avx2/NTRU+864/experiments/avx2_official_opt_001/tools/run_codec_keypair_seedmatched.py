#!/usr/bin/env python3
"""Seed-matched paired Keypair diagnostic for the NTRU+864 fused codec
(supercop-derived; NOT Native SUPERCOP KEM).

Uses the shared, unchanged harness common/official_opt_lazy/bench/
bench_keypair_seedmatched.c (byte-identical SHAKE256 coin streams per
iteration, four keypairs in ABBA/BAAB order, traps unless pk/sk and the
randombytes call count match).  Three ELFs bind its A/B roles to:
  kp_lazycodec_vs_official  A = Official        B = lazy+codec
  kp_lazycodec_vs_lazy      A = lazy            B = lazy+codec  (codec effect on lazy)
  kp_codec_vs_official      A = Official        B = codec-only
Launches rotate over the three ELFs (fresh process each, distinct seed),
pinned to one CPU with ASLR on.  Per iteration d = (B1 + B2 - A1 - A2) / 2;
reported per pairing: median and mean of d, per-launch medians, launches with
median d < 0, and a two-stage bootstrap 95% CI of the mean (launches, then
iterations).  Host controls are only read.

  phase_b_batch.py --result-dir results/codec-keypair-seedmatched-TAG --metadata metadata.json -- \
    python3 tools/run_codec_keypair_seedmatched.py --experiment . --skip-build --result-dir {RESULT}
"""

import argparse
import hashlib
import json
import platform
import random
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
BRANCH = "official-opt-lazy-864-1152"
ELFS = ("kp_lazycodec_vs_official", "kp_lazycodec_vs_lazy", "kp_codec_vs_official")


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


def bootstrap(launches, reps=2000, seed=864):
    rng = random.Random(seed)
    means = []
    for _ in range(reps):
        pick = [launches[rng.randrange(len(launches))] for _ in launches]
        vals = []
        for d in pick:
            vals.extend(d[rng.randrange(len(d))] for _ in d)
        means.append(statistics.fmean(vals))
    means.sort()
    return [means[int(0.025 * reps)], means[int(0.975 * reps) - 1]]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--result-dir", type=Path, required=True)
    ap.add_argument("--cpu", type=int, default=1)
    ap.add_argument("--launches-per-elf", type=int, default=9)
    ap.add_argument("--iterations", type=int, default=1000)
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--skip-build", action="store_true")
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
        execute(["make", "codec-bench-keypair"], cwd=root)
    result.mkdir(parents=True)
    per = {e: [] for e in ELFS}
    retries = {e: 0 for e in ELFS}
    identities = set()
    for launch in range(args.launches_per_elf * len(ELFS)):
        elf = ELFS[launch % len(ELFS)]
        seed = 0x8640000 + launch
        observed = execute(["taskset", "-c", str(args.cpu), str(root / "build" / elf), str(seed),
                            str(args.iterations), str(args.warmup)])
        (result / f"launch-{launch}-{elf}.out").write_text(observed.stdout)
        (result / f"launch-{launch}-{elf}.err").write_text(observed.stderr)
        if "seedmatched=pass" not in observed.stderr:
            raise ValueError("harness did not pass")
        identities.update(l for l in observed.stderr.splitlines() if l.startswith("cpucycles="))
        d = []
        for line in observed.stdout.splitlines():
            if not line[:1].isdigit():
                continue
            f = line.split(",")
            retries[elf] += int(f[2])
            d.append((int(f[4]) + int(f[5]) - int(f[3]) - int(f[6])) / 2)
        per[elf].append(d)
    summary = {"class": "supercop-derived seed-matched paired Keypair diagnostic; not Native SUPERCOP",
               "roles": {"kp_lazycodec_vs_official": ["official", "lazy_codec"],
                         "kp_lazycodec_vs_lazy": ["lazy", "lazy_codec"],
                         "kp_codec_vs_official": ["official", "codec"]},
               "pairings": {}}
    for elf, launches in per.items():
        allv = [x for d in launches for x in d]
        meds = [statistics.median(d) for d in launches]
        summary["pairings"][elf] = {
            "iterations": len(allv), "launches": len(launches),
            "median_d": statistics.median(allv), "mean_d": statistics.fmean(allv),
            "mean_ci95_two_stage_bootstrap": bootstrap(launches),
            "launch_median_d": meds, "favourable_launches": sum(m < 0 for m in meds),
            "keypair_retries_total": retries[elf]}
    (result / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    sources = [root / p for p in ("asm/ntruplus864_officialopt_codec_fused.s",
                                  "asm/ntruplus864_officialopt_ntt_caller_lazy.s", "src/kem_lazy.c",
                                  "src/kem_codec.c", "src/kem_lazy_codec.c",
                                  "upstream/supercop-avx2/kem.c", "codec.mk")]
    sources.append(REPO / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/"
                   "official_opt_lazy/bench/bench_keypair_seedmatched.c")
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "parameter": "864",
        "source_sha256": {str(p.relative_to(REPO)): digest(p) for p in sources},
        "elf_sha256": {e: digest(root / "build" / e) for e in ELFS},
        "elf_text_sha256": {e: text_digest(root / "build" / e) for e in ELFS},
        "host": platform.platform(), "cpu": args.cpu, "controls_read_only": controls,
        "aslr": "on (randomize_va_space=2, no setarch -R)",
        "launches_per_elf": args.launches_per_elf, "iterations": args.iterations,
        "warmup": args.warmup, "cpucycles_identity": sorted(identities),
        "compiler": execute(["cc", "--version"]).stdout.splitlines()[0],
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC); see codec.mk kp_* rules",
    }
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({e: {k: v[k] for k in ("median_d", "mean_d", "mean_ci95_two_stage_bootstrap",
                                            "favourable_launches", "launches")}
                      for e, v in summary["pairings"].items()}, indent=1))


if __name__ == "__main__":
    main()
