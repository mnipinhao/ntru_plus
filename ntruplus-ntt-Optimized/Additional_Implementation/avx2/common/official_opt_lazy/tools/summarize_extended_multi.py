#!/usr/bin/env python3
"""Summarise a several-role extended Native run plus its ASLR-on paired runs.

Inputs (all under <experiment>/results):
  native-ext-<role>-b<k>-<tag>/             run_extended_native.py --role ... batches
  paired-aslr-on-<placement>-<ptag>/        run_paired_aslr_on.py (+ summary.json from
                                            scripts/summarize_supercop_paired.py)

Native (measured; independent pools, default SUPERCOP compiler selection):
for every --comparison CAND:BASE, the pooled StQ1/2/3 delta CAND - BASE over
all fresh launches, a 95% CI from resampling launches within each role, the
per-batch StQ2 deltas (batch k of CAND vs batch k of BASE) and their spread,
and the launches of CAND below the median launch of BASE.  This reuses
summarize_extended.native() unchanged, with the role pair as argument.  Also
the compiler SUPERCOP selected and the measure-ELF hash for every role and
batch, and the hygiene record per batch.

Paired (measured; ASLR on only): --paired CAND:BASE=PTAG reads
paired-aslr-on-{normal,reversed}-PTAG with summarize_extended.paired().  In
those manifests the BASE ELF sits in the `official` slot and the CAND ELF in
the `candidate` slot.

Decision rule (2026-09-23 methodology update), applied per comparison with
paired data: robust research win iff (i) the extended Native pooled StQ2
delta < 0 and (ii) the normal-placement ASLR-on paired 95% CI lies below
zero.  Reversed ASLR-on is reported alongside and flagged (not failed) if it
disagrees.  Writes results/extended-multi-summary-<tag>.json.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
from summarize_extended import OPS, native, paired  # noqa: E402
import run_extended_native  # noqa: E402


def compiler_level(compiler: str) -> str:
    return compiler.split()[0].split("_-")[3]


def try_lines(batch: Path, expected: str) -> list:
    """SUPERCOP `try` records of one batch (one per okc compiler line), from its raw data file."""
    out = []
    for line in (batch / "data").read_text(errors="replace").splitlines():
        f = line.split()
        if len(f) > 13 and f[6] == "try":
            out.append({"compiler": compiler_level(f[13]) if len(f) > 13 else None, "result": f[8],
                        "checksum_ok": f[7] == expected})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--param", choices=("768", "864", "1152"), required=True)
    parser.add_argument("--experiment", type=Path)
    parser.add_argument("--results-dir", type=Path, help="default: <experiment>/results")
    parser.add_argument("--order", choices=("alternate", "rotate"), default="alternate",
                        help="round order used by run_extended_native.py")
    parser.add_argument("--tag", required=True, help="native-ext tag")
    parser.add_argument("--roles", required=True,
                        help="comma-separated roles in round-1 order (as run_extended_native.py --role)")
    parser.add_argument("--comparison", action="append", required=True, metavar="CAND:BASE")
    parser.add_argument("--paired", action="append", default=[], metavar="CAND:BASE=PTAG")
    parser.add_argument("--resamples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260923)
    parser.add_argument("--checksums-from", type=Path, default=Path("/home/nuc/src/supercop-pristine-20260831"),
                        help="SUPERCOP tree holding crypto_kem/ntruplus<N>/checksum{small,big} (read only)")
    args = parser.parse_args()
    ck = args.checksums_from / "crypto_kem" / f"ntruplus{args.param}"
    expected = "/".join((ck / f"checksum{k}").read_text().strip() for k in ("small", "big"))
    if (args.experiment is None) == (args.results_dir is None):
        raise SystemExit("give exactly one of --experiment and --results-dir")
    results = (args.results_dir or args.experiment / "results").resolve()
    roles = args.roles.split(",")
    paired_tags = dict(p.split("=", 1) for p in args.paired)

    # Per-role, per-batch identity (compiler pick, ELF, hygiene).
    identity = {}
    for role in roles:
        dirs = sorted(results.glob(f"native-ext-{role}-b*-{args.tag}"),
                      key=lambda d: int(d.name[len(f"native-ext-{role}-b"):].split("-")[0]))
        rows = []
        for d in dirs:
            meta = json.loads((d / "metadata.json").read_text())
            s = json.loads((d / "stq-summary.json").read_text())
            hh = meta["host_hygiene"]
            rows.append({"dir": d.name, "implementation": meta["implementation"],
                         "compiler": s["measure_identity"]["compiler"],
                         "level": compiler_level(s["measure_identity"]["compiler"]),
                         "measure_elf_sha256": meta["measure_elf_sha256"],
                         "measure_source_sha256": meta["measure_source_sha256"],
                         "compiler_policy": meta["compiler_policy"],
                         "compiler_wrapper_sha256": meta.get("compiler_wrapper_sha256"),
                         "launches": meta["fresh_process_launches"],
                         "try": try_lines(d, expected),
                         "hygiene": {"attempt": hh["attempt"], "contaminated": hh["contaminated"],
                                     "earlier_contaminated_attempts": hh["earlier_contaminated_attempts"],
                                     "pre_loadavg1": hh["before"]["loadavg"][0],
                                     "duration_s": hh["duration_s"]}})
        identity[role] = rows
    bad = [(r["dir"], t) for rows in identity.values() for r in rows for t in r["try"]
           if t["result"] != "ok" or not t["checksum_ok"]]
    if bad or any(not r["try"] for rows in identity.values() for r in rows):
        raise SystemExit(f"SUPERCOP try failed or missing: {bad}")
    nb = {len(v) for v in identity.values()}
    if len(nb) != 1 or not nb.pop():
        raise SystemExit(f"unbalanced batches: { {r: len(v) for r, v in identity.items()} }")
    rounds = len(identity[roles[0]])
    round_order = [list(run_extended_native.round_order(roles, k, args.order))
                   for k in range(1, rounds + 1)]

    comparisons = {}
    for i, spec in enumerate(args.comparison):
        cand, base = spec.split(":")
        rng = random.Random(args.seed + i)
        nat = native(results, args.tag, rng, args.resamples, roles=(base, cand))
        for row, order in zip(nat["per_batch"], round_order):
            row["order"] = ",".join(order)
        entry = {"candidate": cand, "baseline": base, "native": nat}
        if spec in paired_tags:
            entry["paired_tag"] = paired_tags[spec]
            entry["paired"] = paired(results, paired_tags[spec], random.Random(args.seed + 100 + i))
            decision = {}
            for op in OPS:
                d = nat["operations"][op]["stq2"]["delta"]
                normal = entry["paired"].get("normal-aslr-on", {}).get("operations", {}).get(op)
                rev = entry["paired"].get("reversed-aslr-on", {}).get("operations", {}).get(op)
                n_ok = normal is not None and normal["ci95"][1] < 0
                e = {"native_pooled_stq2_delta": d, "native_negative": d < 0,
                     "native_ci95": nat["operations"][op]["stq2_delta_ci95_launch_resampling"],
                     "normal_aslr_on_ci95": normal and normal["ci95"],
                     "normal_aslr_on_ci_below_zero": n_ok,
                     "reversed_aslr_on_ci95": rev and rev["ci95"],
                     "verdict": ("robust-research-win" if d < 0 and n_ok else "not-robust")
                     if normal else "no-paired-data"}
                if rev is not None:
                    rev_ok = rev["ci95"][1] < 0
                    e["reversed_aslr_on_ci_below_zero"] = rev_ok
                    e["reversed_flag"] = None if rev_ok == n_ok else "reversed-aslr-on disagrees with normal"
                decision[op] = e
            entry["decision"] = decision
        comparisons[spec] = entry

    policies = sorted({row["compiler_policy"] for rows in identity.values() for row in rows})
    wrappers = sorted({row["compiler_wrapper_sha256"] or "-" for rows in identity.values() for row in rows})
    if len(policies) != 1 or len(wrappers) != 1:
        raise SystemExit(f"mixed compiler policies in one tag: {policies} {wrappers}")
    selection = ("default SUPERCOP compiler selection" if policies[0] == "native-supercop-selection" else
                 f"fixed single-entry okc-amd64 (compiler wrapper sha256 {wrappers[0]}); not the default selection")
    out = {"schema": "ntruplus-caller-lazy-extended-multi/v1", "parameter": args.param,
           "compiler_policy": policies[0], "compiler_wrapper_sha256": None if wrappers[0] == "-" else wrappers[0],
           "tag": args.tag, "seed": args.seed, "roles": roles, "order": args.order,
           "implementations": {r: identity[r][0]["implementation"] for r in roles},
           "round_order": [",".join(o) for o in round_order],
           "methodology": {
               "aslr": "on only (randomize_va_space=2); no ASLR-off setting, no setarch -R",
               "native": f"{selection}, unmodified measure.c, one 9-launch batch "
                         f"per role per round, round order {args.order}, pooled "
                         "per role; independent pools, not paired",
               "paired": "O3GC fixed ELFs, ABBA/BAAB blocks, ASLR on; normal placement primary, "
                         "reversed placement secondary robustness check",
               "references": ["SUPERCOP: normal compile/link, many fresh processes, StQ",
                              "mlkem-native: single process, warm-ups, median; no placement/ASLR control"]},
           "decision_rule": "robust research win iff extended Native pooled StQ2 delta < 0 AND "
                            "normal-placement ASLR-on paired 95% CI below zero; reversed ASLR-on "
                            "reported and flagged (not failed) if it disagrees",
           "supercop_try": {"expected_checksum_small_big": expected,
                            "all_ok": True,
                            "per_batch_compilers": sorted({t["compiler"] for rows in identity.values()
                                                           for r in rows for t in r["try"]})},
           "per_batch_identity": identity, "comparisons": comparisons}
    path = results / f"extended-multi-summary-{args.tag}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {path}")
    for k in range(rounds):
        print(f"round {k + 1} [{','.join(round_order[k])}] " + "  ".join(
            f"{r}:{identity[r][k]['level']}:{identity[r][k]['measure_elf_sha256'][:16]}"
            f" a{identity[r][k]['hygiene']['attempt']} load {identity[r][k]['hygiene']['pre_loadavg1']}"
            f" {identity[r][k]['hygiene']['duration_s']:.1f}s" for r in roles))
    for spec, entry in comparisons.items():
        nat = entry["native"]
        print(f"== {spec}")
        for op in OPS:
            e = nat["operations"][op]
            base = entry["baseline"]
            print(f"{op:15s} {e['stq2'][base]:9.1f} -> {e['stq2'][entry['candidate']]:9.1f}  "
                  + " / ".join(f"{e[q]['delta']:+8.2f}" for q in ("stq1", "stq2", "stq3"))
                  + f" ({e['delta_percent_stq2']:+.2f}%)"
                  f"  CI {[round(x, 1) for x in e['stq2_delta_ci95_launch_resampling']]}"
                  f"  batches {[round(x, 1) for x in e['per_batch_stq2_delta']]}"
                  f" sd {e['per_batch_summary']['sd']:.0f} neg {e['per_batch_summary']['negative_batches']}"
                  f"  below-med {e['candidate_launches_below_official_median']}/{e['launches_per_role']}")
            for s, pe in entry.get("paired", {}).items():
                o = pe["operations"][op]
                print(f"   {s:17s} {o['mean']:+8.2f} {[round(x, 2) for x in o['ci95']]} "
                      f"{o['favourable_blocks']}/{o['blocks']}")
            if "decision" in entry:
                print(f"   -> {entry['decision'][op]['verdict']} flag={entry['decision'][op].get('reversed_flag')}")
        for key, e in nat["derived_by_elf_pair"].items():
            print(f"  elf-pair {key} batches {e['batches']}: " +
                  " ".join(f"{op[:3]} {e[op]['stq2_delta']:+.1f}" for op in OPS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
