#!/usr/bin/env python3
"""Seed-matched paired Keypair diagnostic: lazy+freeze2op vs lazy-only
(NTRU+768 / NTRU+1152; supercop-derived, NOT Native SUPERCOP KEM).

Derived from NTRU+864 avx2_official_opt_001/tools/
run_codec_direct_keypair_seedmatched.py.  Uses the shared, unchanged harness
bench/bench_keypair_seedmatched.c (byte-identical SHAKE256 coin streams per
iteration, four keypairs in ABBA/BAAB order, traps unless pk/sk and the
randombytes call count match).  Two ELFs bind its A/B roles to
A = lazy-only KEM, B = lazy+freeze2op KEM:
  kp_lazyfreeze_vs_lazy           A object linked first (normal order)
  kp_lazyfreeze_vs_lazy_swapped   B object linked first (reversed order)
Launches alternate between the two ELFs (fresh process each, distinct seed),
pinned to one CPU with ASLR on.  Per iteration d = (B1 + B2 - A1 - A2) / 2;
reported per ELF and pooled: median and mean of d, per-launch medians,
launches with median d < 0, two-stage bootstrap 95% CI of the mean.
Host controls are only read.  Build first with `make freeze-bench-keypair`.

  phase_b_batch.py --result-dir results/freeze2op-keypair-seedmatched-TAG --metadata metadata.json -- \
    python3 ../../../common/official_opt_lazy/tools/run_freeze2op_keypair_seedmatched.py --param 768 \
      --experiment . --result-dir {RESULT}
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
ELFS = ("kp_lazyfreeze_vs_lazy", "kp_lazyfreeze_vs_lazy_swapped")


def execute(command, **kwargs):
    return subprocess.run(command, text=True, capture_output=True, check=True, **kwargs)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_digest(elf):
    return hashlib.sha256(subprocess.run(
        ["objcopy", "-O", "binary", "--only-section=.text", str(elf), "/dev/stdout"],
        check=True, capture_output=True).stdout).hexdigest()


def bootstrap(launches, reps=2000, seed=2):
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


def describe(launches, retries):
    allv = [x for d in launches for x in d]
    meds = [statistics.median(d) for d in launches]
    return {"iterations": len(allv), "launches": len(launches),
            "median_d": statistics.median(allv), "mean_d": statistics.fmean(allv),
            "mean_ci95_two_stage_bootstrap": bootstrap(launches),
            "launch_median_d": meds, "favourable_launches": sum(m < 0 for m in meds),
            "keypair_retries_total": retries}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--result-dir", type=Path, required=True)
    ap.add_argument("--cpu", type=int, default=1)
    ap.add_argument("--launches-per-elf", type=int, default=9)
    ap.add_argument("--iterations", type=int, default=1000)
    ap.add_argument("--warmup", type=int, default=20)
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
    result.mkdir(parents=True)
    per = {e: [] for e in ELFS}
    retries = {e: 0 for e in ELFS}
    identities = set()
    for launch in range(args.launches_per_elf * len(ELFS)):
        elf = ELFS[launch % len(ELFS)]
        seed = (args.param << 16) + 0xF200 + launch
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
               "parameter": f"NTRU+{args.param}",
               "roles": {"A": "lazy-only KEM (src/kem_lazy.c)", "B": "lazy+freeze2op KEM (src/kem_lazy_freeze2op.c)"},
               "d": "(B1 + B2 - A1 - A2) / 2 cycles per iteration; negative favours lazy+freeze2op",
               "pairings": {e: describe(per[e], retries[e]) for e in ELFS}}
    summary["pooled"] = describe(per[ELFS[0]] + per[ELFS[1]], retries[ELFS[0]] + retries[ELFS[1]])
    (result / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    n = args.param
    common = HERE.parents[1]
    sources = [root / p for p in (f"asm/ntruplus{n}_officialopt_tobytes_freeze2op.s",
                                  f"asm/ntruplus{n}_officialopt_ntt_caller_lazy.s", "src/kem_lazy.c",
                                  "src/kem_lazy_freeze2op.c", "upstream/supercop-avx2/kem.c")]
    sources += [common / "bench/bench_keypair_seedmatched.c", common / "freeze2op.mk"]
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "parameter": str(n),
        "source_sha256": {str(p.resolve().relative_to(REPO)): digest(p) for p in sources},
        "elf_sha256": {e: digest(root / "build" / e) for e in ELFS},
        "elf_text_sha256": {e: text_digest(root / "build" / e) for e in ELFS},
        "host": platform.platform(), "cpu": args.cpu, "controls_read_only": controls,
        "aslr": "on (randomize_va_space=2, no setarch -R)",
        "launches_per_elf": args.launches_per_elf, "iterations": args.iterations,
        "warmup": args.warmup, "cpucycles_identity": sorted(identities),
        "compiler": execute(["cc", "--version"]).stdout.splitlines()[0],
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC); see freeze2op.mk kp_lazyfreeze_* rules",
    }
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({e: {k: v[k] for k in ("median_d", "mean_d", "mean_ci95_two_stage_bootstrap",
                                            "favourable_launches", "launches")}
                      for e, v in list(summary["pairings"].items()) + [("pooled", summary["pooled"])]},
                     indent=1))


if __name__ == "__main__":
    main()
