#!/usr/bin/env python3
"""Summarise the extended Native and ASLR-on fixed-ELF paired evidence.

Inputs (all under <experiment>/results):
  native-ext-{official,candidate}-b<k>-<tag>/   run_extended_native.py batches
  paired-aslr-on-{normal,reversed}-<ptag>/      run_paired_aslr_on.py (+ summary.json
                                                from scripts/summarize_supercop_paired.py)

Native (measured; independent pools, default SUPERCOP compiler selection):
pooled StQ1/2/3 over every fresh launch per role and the candidate-official
delta, with a 95% CI from resampling launches within each role; per-batch
StQ2 deltas (batch k Official vs batch k candidate) with their spread; the
compiler SUPERCOP selected and the measure-ELF hash for every batch; host
hygiene per batch.  For Keypair also the retry composition per side
(retries = keypair_randomcalls - 2), the StQ2-window composition and the
retry-stratified StQ2/median deltas (as in analyze_keypair_retry_strata.py).

Paired (measured; ASLR on only): mean delta, block-bootstrap 95% CI and
favourable blocks per placement, copied from summary.json, plus the Keypair
retry-stratified per-block median deltas.

Decision rule (2026-09-23 methodology update): an op is a robust research
win iff (i) the extended Native pooled StQ2 delta < 0 and (ii) the
normal-placement ASLR-on paired 95% CI lies below zero.  The reversed
ASLR-on result is reported alongside and flagged (not failed) if it
disagrees.  Writes results/extended-summary-<tag>.json.
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(HERE.parent))
from run_supercop_benchmark import decode_observations, stabilized_quartiles  # noqa: E402
from analyze_keypair_retry_strata import STRATA, by_stratum, ci, load, stratum  # noqa: E402

OPS = ("keypair_cycles", "enc_cycles", "dec_cycles")
ROLES = ("official", "candidate")


def stq_sorted(s):
    """stabilized_quartiles() of an already sorted list, without the 8x expansion."""
    n = len(s)
    out = []
    for i in range(3):
        lo, hi = (1 + 2 * i) * n, (3 + 2 * i) * n  # indices into the 8x-expanded list
        a, b = lo // 8, (hi - 1) // 8
        if a == b:
            total = s[a] * (hi - lo)
        else:
            total = s[a] * (8 * (a + 1) - lo) + sum(s[a + 1:b]) * 8 + s[b] * (hi - 8 * b)
        out.append(total / (2 * n))
    return out


def stq2(values):
    return stq_sorted(sorted(values))[1]


def batches(results: Path, tag: str, roles=ROLES):
    base, cand = roles
    out = {}
    for role in roles:
        dirs = sorted(results.glob(f"native-ext-{role}-b*-{tag}"),
                      key=lambda d: int(d.name[len(f"native-ext-{role}-b"):].split("-")[0]))
        out[role] = dirs
    if len(out[base]) != len(out[cand]) or not out[base]:
        raise SystemExit(f"unbalanced or missing batches: { {r: len(v) for r, v in out.items()} }")
    return out


def native(results: Path, tag: str, rng: random.Random, resamples: int, roles=ROLES):
    """roles = (baseline, candidate); deltas are candidate - baseline."""
    base, cand = roles
    dirs = batches(results, tag, roles)
    launches = {r: [] for r in roles}   # list of dict op -> values, per launch
    kp = {r: [] for r in roles}         # list of [(cycles, retries)] per launch
    per_batch = []
    for k, (do, dc) in enumerate(zip(dirs[base], dirs[cand]), 1):
        row = {"batch": k, "order": f"{base}-first" if k % 2 else f"{cand}-first"}
        stq = {}
        for role, d in ((base, do), (cand, dc)):
            meta = json.loads((d / "metadata.json").read_text())
            s = json.loads((d / "stq-summary.json").read_text())
            hh = meta["host_hygiene"]
            files = sorted((d / "fresh-launches").glob("launch-*.out"))
            for p in files:
                text = p.read_text(errors="replace")
                launches[role].append({op: decode_observations(text, op) for op in OPS})
                kp[role].append(load(p))
            stq[role] = s["operations"]
            row[role] = {"dir": d.name, "compiler": s["measure_identity"]["compiler"],
                         "compiler_policy": meta["compiler_policy"],
                         "measure_elf_sha256": meta["measure_elf_sha256"],
                         "measure_source_sha256": meta["measure_source_sha256"],
                         "launches": len(files),
                         "hygiene": {"attempt": hh["attempt"], "contaminated": hh["contaminated"],
                                     "earlier_contaminated_attempts": len(hh["earlier_contaminated_attempts"]),
                                     "pre_loadavg1": hh["before"]["loadavg"][0],
                                     "duration_s": hh["duration_s"]}}
        row["stq2_delta"] = {op: stq[cand][op]["stq2"] - stq[base][op]["stq2"] for op in OPS}
        per_batch.append(row)
    out = {"batches": len(per_batch), "launches": {r: len(v) for r, v in launches.items()},
           "per_batch": per_batch, "operations": {}}
    for op in OPS:
        pooled = {r: sorted(v for l in launches[r] for v in l[op]) for r in roles}
        q = {r: stq_sorted(pooled[r]) for r in roles}
        assert abs(q[base][1] - stabilized_quartiles(pooled[base])[1]) < 1e-6
        boot = []
        for _ in range(resamples):
            b = {}
            for r in roles:
                pick = [rng.choice(launches[r]) for _ in launches[r]]
                b[r] = stq2([v for l in pick for v in l[op]])
            boot.append(b[cand] - b[base])
        launch_stq2 = {r: [stq2(l[op]) for l in launches[r]] for r in roles}
        med_o = statistics.median(launch_stq2[base])
        bd = [row["stq2_delta"][op] for row in per_batch]
        out["operations"][op] = {
            "observations": [len(pooled[base]), len(pooled[cand])],
            **{name: {base: q[base][i], cand: q[cand][i],
                      "delta": q[cand][i] - q[base][i]}
               for i, name in enumerate(("stq1", "stq2", "stq3"))},
            "delta_percent_stq2": 100 * (q[cand][1] - q[base][1]) / q[base][1],
            "stq2_delta_ci95_launch_resampling": ci(boot),
            "stq2_delta_bootstrap_sd": statistics.stdev(boot),
            "resamples": resamples,
            "per_batch_stq2_delta": bd,
            "per_batch_summary": {"mean": statistics.mean(bd), "sd": statistics.stdev(bd),
                                  "min": min(bd), "max": max(bd),
                                  "negative_batches": sum(x < 0 for x in bd),
                                  "sd_of_81_launch_pool_from_batch_sd": statistics.stdev(bd) / len(bd) ** 0.5},
            "candidate_launches_below_official_median": sum(v < med_o for v in launch_stq2[cand]),
            "launches_per_role": len(launch_stq2[cand]),
        }
    # Derived: SUPERCOP re-selects the compiler in every batch, so group batches
    # by the (Official ELF, candidate ELF) pair actually measured and pool each group.
    groups = collections.defaultdict(list)
    for i, row in enumerate(per_batch):
        key = " vs ".join(f"{r}:{row[r]['compiler'].split('_-')[3]}:{row[r]['measure_elf_sha256'][:16]}"
                          for r in roles)
        groups[key].append(i)
    per_launch_batch = {r: [i // (len(launches[r]) // len(per_batch)) for i in range(len(launches[r]))]
                        for r in roles}
    out["derived_by_elf_pair"] = {}
    for key, idx in groups.items():
        entry = {"batches": [i + 1 for i in idx]}
        for op in OPS:
            v = {r: [x for l, b in zip(launches[r], per_launch_batch[r]) if b in idx for x in l[op]]
                 for r in roles}
            entry[op] = {"stq2_delta": stq2(v[cand]) - stq2(v[base]),
                         "observations": [len(v[base]), len(v[cand])]}
        out["derived_by_elf_pair"][key] = entry
    out["keypair_retries"] = retries(kp, rng, resamples, roles)
    return out


def retries(kp, rng, resamples, roles=ROLES):
    base, cand = roles
    out = {"composition": {}, "pooled": {}, "strata": {}}
    for role, ls in kp.items():
        pooled = collections.Counter(stratum(r) for l in ls for _, r in l)
        n = sum(pooled.values())
        ordered = sorted((c, r) for l in ls for c, r in l)
        window = ordered[(3 * n) // 8:(5 * n) // 8]
        allc = [c for c, _ in ordered]
        out["composition"][role] = {
            "pooled": {s: pooled[s] for s in STRATA}, "observations": n,
            "pooled_fraction": {s: pooled[s] / n for s in STRATA},
            "mean_retries_per_keypair": sum(r for l in ls for _, r in l) / n,
            "per_batch_r0_fraction": [
                sum(1 for l in ls[i:i + 9] for _, r in l if r == 0) / sum(len(l) for l in ls[i:i + 9])
                for i in range(0, len(ls), 9)]}
        out["pooled"][role] = {"stq2": stq2(allc), "median": statistics.median(allc),
                               "stq2_window_composition": dict(sorted(collections.Counter(
                                   stratum(r) for _, r in window).items()))}
    out["pooled"]["delta_stq2"] = out["pooled"][cand]["stq2"] - out["pooled"][base]["stq2"]
    n_o = out["composition"][base]["observations"]
    d0 = out["composition"][cand]["pooled"]["0"] - out["composition"][base]["pooled"]["0"]
    p = out["composition"][base]["pooled_fraction"]["0"]
    out["r0_count_difference"] = {"candidate_minus_official": d0,
                                  "binomial_sd_of_difference": (2 * n_o * p * (1 - p)) ** 0.5}
    for s in STRATA:
        o, c = by_stratum(kp[base])[s], by_stratum(kp[cand])[s]
        if len(o) < 8 or len(c) < 8:
            continue
        entry = {"n": [len(o), len(c)]}
        for name, fn in (("stq2", stq2), ("median", statistics.median)):
            boot = []
            for _ in range(resamples):
                bo = by_stratum([rng.choice(kp[base]) for _ in kp[base]])[s]
                bc = by_stratum([rng.choice(kp[cand]) for _ in kp[cand]])[s]
                if len(bo) >= 4 and len(bc) >= 4:
                    boot.append(fn(bc) - fn(bo))
            entry[name] = {base: fn(o), cand: fn(c), "delta": fn(c) - fn(o),
                           "ci95": ci(boot), "resamples": len(boot)}
        out["strata"][s] = entry
    return out


def paired(results: Path, ptag: str, rng: random.Random):
    out = {}
    for placement in ("normal", "reversed"):
        root = results / f"paired-aslr-on-{placement}-{ptag}"
        if not (root / "summary.json").is_file():
            continue
        summary = json.loads((root / "summary.json").read_text())
        manifest = json.loads((root / "manifest.json").read_text())
        setting = f"{placement}-aslr-on"
        entry = {"dir": root.name, "blocks": manifest["blocks"],
                 "elf_sha256": {r: manifest["binaries"][placement][r]["sha256"] for r in ROLES},
                 "hygiene": {k: manifest["host_hygiene"][k] for k in
                             ("attempt", "contaminated", "duration_s")} |
                            {"pre_loadavg1": manifest["host_hygiene"]["before"]["loadavg"][0],
                             "earlier_contaminated_attempts":
                                 len(manifest["host_hygiene"]["earlier_contaminated_attempts"])},
                 "operations": {}}
        for r in summary["rows"]:
            if r["setting"] == setting:
                entry["operations"][r["operation"]] = {
                    "mean": r["paired_mean_delta_cycles"], "median": r["paired_median_delta_cycles"],
                    "ci95": [r["bootstrap_ci95_low"], r["bootstrap_ci95_high"]],
                    "favourable_blocks": r["favorable_blocks"], "blocks": r["blocks"]}
        blocks = collections.defaultdict(lambda: {"official": [], "candidate": []})
        for p in sorted((root / setting).glob("block-*-slot-*-*.out")):
            parts = p.stem.split("-")
            blocks[int(parts[1])][parts[4]].append(load(p))
        strata = {}
        for s in STRATA:
            deltas = []
            for b in sorted(blocks):
                o, c = by_stratum(blocks[b]["official"])[s], by_stratum(blocks[b]["candidate"])[s]
                if len(o) >= 3 and len(c) >= 3:
                    deltas.append(statistics.median(c) - statistics.median(o))
            if len(deltas) < 8:
                continue
            boot = []
            for _ in range(20000):
                smp = [rng.choice(deltas) for _ in deltas]
                boot.append(sum(smp) / len(smp))
            strata[s] = {"blocks_used": len(deltas), "mean": statistics.mean(deltas),
                         "median": statistics.median(deltas), "ci95_mean": ci(boot),
                         "favourable_blocks": sum(d < 0 for d in deltas)}
        entry["keypair_retry_strata"] = strata
        out[setting] = entry
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--param", choices=("864", "1152"), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--tag", required=True, help="native-ext tag")
    parser.add_argument("--paired-tag", help="paired-aslr-on tag (default: --tag)")
    parser.add_argument("--resamples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260923)
    args = parser.parse_args()
    results = args.experiment.resolve() / "results"
    rng = random.Random(args.seed)
    nat = native(results, args.tag, rng, args.resamples)
    par = paired(results, args.paired_tag or args.tag, rng)
    decision = {}
    for op in OPS:
        d = nat["operations"][op]["stq2"]["delta"]
        normal = par.get("normal-aslr-on", {}).get("operations", {}).get(op)
        rev = par.get("reversed-aslr-on", {}).get("operations", {}).get(op)
        n_ok = normal is not None and normal["ci95"][1] < 0
        win = d < 0 and n_ok
        entry = {"native_pooled_stq2_delta": d, "native_negative": d < 0,
                 "normal_aslr_on_ci95": normal and normal["ci95"],
                 "normal_aslr_on_ci_below_zero": n_ok,
                 "reversed_aslr_on_ci95": rev and rev["ci95"],
                 "verdict": ("robust-research-win" if win else "not-robust") if normal else "no-paired-data"}
        if rev is not None:
            rev_ok = rev["ci95"][1] < 0
            entry["reversed_aslr_on_ci_below_zero"] = rev_ok
            entry["reversed_flag"] = None if rev_ok == n_ok else "reversed-aslr-on disagrees with normal"
        decision[op] = entry
    out = {"schema": "ntruplus-caller-lazy-extended/v1", "parameter": args.param,
           "tag": args.tag, "paired_tag": args.paired_tag or args.tag, "seed": args.seed,
           "methodology": {
               "aslr": "on only (randomize_va_space=2); no ASLR-off setting, no setarch -R",
               "native": "default SUPERCOP compiler selection, unmodified measure.c, 9-launch batches "
                         "alternating Official/candidate ABBA/BAAB, pooled",
               "paired": "O3GC fixed ELFs (Phase B), ABBA/BAAB blocks; normal placement primary, "
                         "reversed placement secondary robustness check",
               "references": ["SUPERCOP: normal compile/link, many fresh processes, StQ",
                              "mlkem-native: single process, warm-ups, median; no placement/ASLR control"]},
           "decision_rule": "robust research win iff extended Native pooled StQ2 delta < 0 AND "
                            "normal-placement ASLR-on paired 95% CI below zero; reversed ASLR-on "
                            "reported and flagged (not failed) if it disagrees",
           "native": nat, "paired": par, "decision": decision}
    path = results / f"extended-summary-{args.tag}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {path}")
    for op in OPS:
        e = nat["operations"][op]
        print(f"{op:15s} native " + " / ".join(f"{e[q]['delta']:+8.2f}" for q in ("stq1", "stq2", "stq3")) +
              f"  CI {[round(x, 1) for x in e['stq2_delta_ci95_launch_resampling']]}"
              f"  batches {[round(x) for x in e['per_batch_stq2_delta']]} sd {e['per_batch_summary']['sd']:.0f}"
              f"  below-med {e['candidate_launches_below_official_median']}/{e['launches_per_role']}")
        for s, pe in par.items():
            o = pe["operations"][op]
            print(f"   {s:17s} {o['mean']:+8.2f} {[round(x, 2) for x in o['ci95']]} {o['favourable_blocks']}/{o['blocks']}")
        print(f"   -> {decision[op]}")
    for row in nat["per_batch"]:
        print(f"batch {row['batch']} " + " ".join(
            f"{r}:{row[r]['compiler'].split()[0].split('_-')[3]} a{row[r]['hygiene']['attempt']} "
            f"load {row[r]['hygiene']['pre_loadavg1']}" for r in ROLES))
    for key, e in nat["derived_by_elf_pair"].items():
        print(f"elf-pair {key} batches {e['batches']}: " +
              " ".join(f"{op[:3]} {e[op]['stq2_delta']:+.1f}" for op in OPS))
    kr = nat["keypair_retries"]
    print("retry composition:", {r: v["pooled"] for r, v in kr["composition"].items()},
          "window:", {r: kr["pooled"][r]["stq2_window_composition"] for r in ROLES})
    for s, e in kr["strata"].items():
        print(f" native r={s:2s} n={e['n']} stq2 {e['stq2']['delta']:+8.1f} {[round(x, 1) for x in e['stq2']['ci95']]}"
              f"  median {e['median']['delta']:+8.1f} {[round(x, 1) for x in e['median']['ci95']]}")
    for setting, pe in par.items():
        for s, r in pe["keypair_retry_strata"].items():
            print(f" {setting:17s} r={s:2s} mean {r['mean']:+8.1f} {[round(x, 1) for x in r['ci95_mean']]} "
                  f"fav {r['favourable_blocks']}/{r['blocks_used']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
