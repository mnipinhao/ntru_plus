#!/usr/bin/env python3
"""Seed-matched paired Keypair diagnostic (Phase-B follow-up, supercop-derived).

Builds `make bench-keypair` (O3GC; normal and swapped KEM link order), then
runs --launches fresh processes pinned to one CPU, alternating the normal and
swapped ELF, each with its own seed.  Every iteration gives Official and the
caller-lazy candidate byte-identical coins (SHAKE256(seed||iteration)) and
times four keypairs in ABBA/BAAB order; the harness traps unless pk/sk and the
randombytes call count match.  Per-iteration paired delta:
  d = (lazy_1 + lazy_2 - official_1 - official_2) / 2
reported (with --summarize, outside the timed batch) overall, per ELF and
per retry stratum (retries = calls - 2), with
two-stage bootstrap 95% CIs (resample launches, then iterations within each
resampled launch).  Host controls are only read.  Not Native SUPERCOP.

  phase_b_batch.py --result-dir results/keypair-seedmatched-20260923 --metadata metadata.json -- \
    python3 run_keypair_seedmatched.py --param 1152 --experiment . --skip-build --result-dir {RESULT}
  python3 run_keypair_seedmatched.py --param 1152 --experiment . \
    --result-dir results/keypair-seedmatched-20260923 --summarize

The summary also carries an estimate (resampling these observations) of the
sampling noise of SUPERCOP-style independently pooled StQ2 comparisons.
"""

import argparse
import csv
import hashlib
import json
import platform
import random
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
COMMON = HERE.parents[1]
BRANCH = "official-opt-lazy-864-1152"
ELFS = ("bench_keypair_seedmatched", "bench_keypair_seedmatched_swapped")
STRATA = ("0", "1", "2", "3", "4+")


def execute(command, **kwargs):
    return subprocess.run(command, text=True, capture_output=True, check=True, **kwargs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stratum(r):
    return str(r) if r < 4 else "4+"


def trimmed_mean(values, frac=0.1):
    v = sorted(values)
    k = int(len(v) * frac)
    v = v[k:len(v) - k] if len(v) > 2 * k else v
    return sum(v) / len(v)


def stats(groups, rng, resamples):
    """groups: list of per-launch lists of deltas.  Two-stage bootstrap."""
    flat = [d for g in groups for d in g]
    groups = [g for g in groups if g]
    fns = {"mean": lambda v: sum(v) / len(v), "median": statistics.median, "trimmed_mean_10": trimmed_mean}
    boot = {k: [] for k in fns}
    for _ in range(resamples):
        sample = []
        for g in (rng.choice(groups) for _ in groups):
            sample.extend(rng.choice(g) for _ in g)
        for k, fn in fns.items():
            boot[k].append(fn(sample))
    out = {"n": len(flat), "launches": len(groups), "favourable_fraction": sum(d < 0 for d in flat) / len(flat)}
    for k, fn in fns.items():
        b = sorted(boot[k])
        out[k] = fn(flat)
        out[k + "_ci95"] = [b[int(0.025 * len(b))], b[int(0.975 * len(b)) - 1]]
    out["favourable_launches"] = sum(statistics.median(g) < 0 for g in groups)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--param", type=int, choices=(864, 1152), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--launches", type=int, default=12)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--warmup", type=int, default=32)
    parser.add_argument("--seed-base", type=int, default=20260923000)
    parser.add_argument("--resamples", type=int, default=1000)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--summarize", action="store_true",
                        help="no timing: (re)write summary.json from an existing result dir")
    args = parser.parse_args()
    root = args.experiment.resolve()
    if args.summarize:
        return summarize(args.result_dir.resolve(), args.resamples)
    if execute(["git", "branch", "--show-current"], cwd=REPO).stdout.strip() != BRANCH:
        raise SystemExit("wrong branch")
    checks = {
        f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor": "performance",
        "/sys/devices/system/cpu/intel_pstate/no_turbo": "1",
    }
    for name, expected in checks.items():
        if Path(name).read_text().strip() != expected:
            raise SystemExit(f"host timing preflight failed: {name}")
    result = args.result_dir.resolve()
    if result.exists():
        raise SystemExit(f"refusing overwrite: {result}")
    if not args.skip_build:
        execute(["make", "check"], cwd=root)
        execute(["make", "bench-keypair"], cwd=root)
    binaries = {name: root / "build" / name for name in ELFS}
    result.mkdir(parents=True)
    identities, launches = set(), []
    for launch in range(args.launches):
        elf = ELFS[launch % 2]
        seed = args.seed_base + launch
        command = ["taskset", "-c", str(args.cpu), str(binaries[elf]), str(seed),
                   str(args.iterations), str(args.warmup)]
        observed = execute(command)
        (result / f"launch-{launch:02d}.out").write_text(observed.stdout)
        (result / f"launch-{launch:02d}.err").write_text(observed.stderr)
        if "seedmatched=pass" not in observed.stderr:
            raise SystemExit("harness did not report seedmatched=pass")
        identities.update(l for l in observed.stderr.splitlines() if l.startswith("cpucycles="))
        launches.append({"launch": launch, "elf": elf, "seed": seed})
    lazy = f"asm/ntruplus{args.param}_officialopt_ntt_caller_lazy.s"
    sources = {str(p.relative_to(REPO)): digest(p) for p in (
        root / "upstream/supercop-avx2/ntt.s", root / "upstream/supercop-avx2/kem.c", root / lazy,
        root / "src/kem_lazy.c", COMMON / "bench/bench_keypair_seedmatched.c", COMMON / "bench/kem_diag.c",
        COMMON / "lazy.mk", HERE)}
    metadata = {
        "class": "supercop-derived diagnostic; not Native SUPERCOP",
        "parameter": str(args.param), "source_sha256": sources,
        "elf_sha256": {e: digest(p) for e, p in binaries.items()},
        "host": platform.platform(), "cpu": args.cpu, "controls": checks,
        "launches": launches, "iterations_per_launch": args.iterations, "warmup_per_launch": args.warmup,
        "cpucycles_identity": sorted(identities),
        "compiler_recipe": "lazy.mk BENCH_CFLAGS (common O3GC)",
        "rng": "per-iteration SHAKE256(seed_le64 || iteration_le64) coin stream, served by memcpy",
        "order": "ABBA on even iterations, BAAB on odd", "aslr": "enabled (default, per process)",
        "bootstrap": {"method": "two-stage (launches, then iterations)", "resamples": args.resamples,
                      "seed": args.seed_base}}
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"timing done: {result} (run --summarize for the analysis)")
    return 0


def summarize(result, resamples):
    metadata = json.loads((result / "metadata.json").read_text())
    rows = []
    for entry in metadata["launches"]:
        launch, elf = entry["launch"], entry["elf"]
        text = (result / f"launch-{launch:02d}.out").read_text()
        for rec in csv.reader(l for l in text.splitlines() if l[:1].isdigit()):
            it, order, retries, o1, l1, l2, o2 = rec
            o1, l1, l2, o2 = map(int, (o1, l1, l2, o2))
            rows.append({"launch": launch, "elf": elf, "retries": int(retries), "order": order,
                         "official": (o1, o2), "lazy": (l1, l2), "delta": (l1 + l2 - o1 - o2) / 2})
    nlaunch = len(metadata["launches"])
    seed = metadata["bootstrap"]["seed"]
    rng = random.Random(seed)

    def grouped(pred):
        return [[r["delta"] for r in rows if r["launch"] == l and pred(r)] for l in range(nlaunch)]

    summary = {"class": "supercop-derived diagnostic (seed-matched paired Keypair); not Native SUPERCOP",
               "delta_definition": "(lazy_1 + lazy_2 - official_1 - official_2) / 2 per iteration, cycles",
               "overall": stats(grouped(lambda r: True), rng, resamples),
               "per_elf": {e: stats(grouped(lambda r, e=e: r["elf"] == e), rng, resamples) for e in ELFS},
               "per_retry_stratum": {}, "composition": {}}
    for s in STRATA:
        g = grouped(lambda r, s=s: stratum(r["retries"]) == s)
        if sum(map(len, g)) >= 50:
            entry = stats(g, rng, resamples)
            entry["official_median_cycles"] = statistics.median(
                c for r in rows if stratum(r["retries"]) == s for c in r["official"])
            summary["per_retry_stratum"][s] = entry
    counts = {s: sum(stratum(r["retries"]) == s for r in rows) for s in STRATA}
    summary["composition"] = {"counts": counts, "mean_retries": sum(r["retries"] for r in rows) / len(rows)}
    # OLS of per-iteration delta on Forward count (= 2 + retries), and on stratum medians
    xs = [2 + r["retries"] for r in rows]
    ys = [r["delta"] for r in rows]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    med = {2 + int(s): summary["per_retry_stratum"][s]["median"] for s in ("0", "1", "2", "3")
           if s in summary["per_retry_stratum"]}
    mxm = sum(med) / len(med)
    mym = sum(med.values()) / len(med)
    slope_m = sum((x - mxm) * (y - mym) for x, y in med.items()) / sum((x - mxm) ** 2 for x in med)
    summary["per_forward_fit"] = {
        "ols_iteration_level": {"slope_per_forward": slope, "intercept": my - slope * mx},
        "ols_on_stratum_medians_r0_to_r3": {"slope_per_forward": slope_m, "intercept": mym - slope_m * mxm}}
    # position check: does the first timed call of a quadruple run slower?
    first = [(r["official"][0] if r["order"] == "ABBA" else r["lazy"][0]) for r in rows]
    second = [(r["lazy"][0] if r["order"] == "ABBA" else r["official"][0]) for r in rows]
    summary["position_check_median_first_minus_second"] = statistics.median(a - b for a, b in zip(first, second))
    # Estimate (not a measurement): how noisy is a SUPERCOP-style comparison of two
    # independently pooled StQ2 values when retry composition is random?  Draw
    # independent pools of n official_1 / lazy_1 observations from these iterations.
    sys.path.insert(0, str(REPO / "scripts"))
    from run_supercop_benchmark import stabilized_quartiles
    off = [r["official"][0] for r in rows]
    laz = [r["lazy"][0] for r in rows]
    sim_rng = random.Random(seed + 1)
    power = {}
    for launches_per_role in (9, 36, 81):
        n = 96 * launches_per_role
        null, alt = [], []
        for _ in range(1000):
            a = stabilized_quartiles(sim_rng.sample(off, n))[1]
            null.append(stabilized_quartiles(sim_rng.sample(off, n))[1] - a)
            alt.append(stabilized_quartiles(sim_rng.sample(laz, n))[1] - a)
        power[str(launches_per_role)] = {
            "observations_per_role": n, "null_delta_sd": statistics.pstdev(null),
            "delta_mean": statistics.mean(alt), "delta_sd": statistics.pstdev(alt),
            "p_delta_positive": sum(x > 0 for x in alt) / len(alt)}
    summary["pooled_stq2_noise_estimate"] = {
        "class": "estimate by resampling these harness observations; not Native",
        "method": "1000 draws of independent pools (96 obs per launch) of official_1 and lazy_1; "
                  "pooled StQ2(lazy) - StQ2(official)", "by_launches_per_role": power}
    summary["summarizer_sha256"] = digest(HERE)  # may differ from metadata's timing-time hash
    (result / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    o = summary["overall"]
    print(json.dumps({"path": str(result), "overall_median": o["median"], "overall_median_ci95": o["median_ci95"],
                      "overall_mean": o["mean"], "overall_mean_ci95": o["mean_ci95"],
                      "per_stratum_median": {s: [round(v["median"], 1), [round(x, 1) for x in v["median_ci95"]]]
                                             for s, v in summary["per_retry_stratum"].items()},
                      "per_forward_fit": summary["per_forward_fit"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
