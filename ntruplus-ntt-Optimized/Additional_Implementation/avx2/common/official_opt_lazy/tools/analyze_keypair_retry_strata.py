#!/usr/bin/env python3
"""Retry-stratified re-analysis of already collected SUPERCOP keypair timings.

Why not call-index pairing: SUPERCOP's crypto_kem/measure is linked with
fastrandombytes (do-part: measurelibs="$lib/$abi/fastrandombytes.o"), whose
ChaCha20 key is drawn once per process from kernelrandombytes.  The i-th
keypair call therefore gets different coins in every fresh launch, for both
Official and the candidate, so candidate_i - official_i is not a matched
pair.  (knownrandombytes, zero key, is linked only into the try/checksum
binaries.)  This script verifies that empirically: it counts distinct
per-launch retry sequences.

What is observable: measure.c logs keypair_randomcalls per timed call, and
Official/candidate crypto_kem_keypair call randombytes(coins, 32) exactly
once per f attempt and once per g attempt (kem.c / src/kem_lazy.c), so
retries = keypair_randomcalls - 2 and Forward calls = keypair_randomcalls,
exactly, for every observation.  Observations are stratified by retry count
(0, 1, 2, 3+):

* Native (supercop-native-kem raw fresh launches, independent pools): per
  stratum, pooled StQ2 and median per role and candidate-official delta; 95%
  CI by resampling launches within each role (2,000 resamples).
* Fixed-ELF paired (O3GC, 16 ABBA/BAAB blocks per setting): per block and
  stratum, median(candidate) - median(official) over the block's 2+2
  launches; mean/median over blocks, block-bootstrap 95% CI (20,000).

Also reports each launch's retry composition and the share of StQ2's
37.5-62.5% window that the retry mixture places in the r=0 cluster, which
is what makes pooled 1152 Keypair StQ2 sensitive to composition.
Writes results/keypair-retry-strata-<tag>.json.  Derived re-analysis of
existing observations; no new timing.
"""

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
from run_supercop_benchmark import decode_observations, stabilized_quartiles  # noqa: E402

SETTINGS = ("normal-aslr-off", "normal-aslr-on", "reversed-aslr-off", "reversed-aslr-on")
STRATA = ("0", "1", "2", "3+")
RESAMPLES = 20000


def stratum(r: int) -> str:
    return str(r) if r < 3 else "3+"


def load(path: Path):
    text = path.read_text(errors="replace")
    cycles = decode_observations(text, "keypair_cycles")
    calls = decode_observations(text, "keypair_randomcalls")
    if len(cycles) != len(calls) or not cycles:
        raise SystemExit(f"{path}: {len(cycles)} cycles vs {len(calls)} randomcalls")
    if min(calls) < 2:
        raise SystemExit(f"{path}: keypair with fewer than 2 randombytes calls")
    return [(c, n - 2) for c, n in zip(cycles, calls)]


def by_stratum(launches):
    out = {s: [] for s in STRATA}
    for launch in launches:
        for c, r in launch:
            out[stratum(r)].append(c)
    return out


def ci(samples):
    samples = sorted(samples)
    return [samples[int(0.025 * len(samples))], samples[int(0.975 * len(samples)) - 1]]


def native(results: Path, tag: str, rng: random.Random):
    roles = {}
    for role in ("official", "candidate"):
        files = sorted((results / f"native-lazy-qual-{role}-{tag}" / "fresh-launches").glob("launch-*.out"))
        roles[role] = [load(p) for p in files]
    out = {"launches": {r: len(v) for r, v in roles.items()}, "composition": {}, "strata": {},
           "pooled": {}}
    for role, launches in roles.items():
        per_launch = [collections.Counter(stratum(r) for _, r in l) for l in launches]
        pooled = collections.Counter(stratum(r) for l in launches for _, r in l)
        n = sum(pooled.values())
        out["composition"][role] = {
            "pooled": {s: pooled[s] for s in STRATA},
            "pooled_r0_fraction": pooled["0"] / n,
            "per_launch_r0_fraction": [c["0"] / sum(c.values()) for c in per_launch],
            "mean_retries_per_keypair": sum(r for l in launches for _, r in l) / n}
        allc = [c for l in launches for c, _ in l]
        # StQ2 averages the 37.5-62.5% order statistics; which retry strata land there?
        ordered = sorted((c, r) for l in launches for c, r in l)
        window = ordered[(3 * n) // 8:(5 * n) // 8]
        out["pooled"][role] = {"stq2": stabilized_quartiles(allc)[1], "median": statistics.median(allc),
                               "stq2_window_composition": dict(collections.Counter(stratum(r) for _, r in window))}
    out["pooled"]["delta_stq2"] = out["pooled"]["candidate"]["stq2"] - out["pooled"]["official"]["stq2"]
    for s in STRATA:
        o = by_stratum(roles["official"])[s]
        c = by_stratum(roles["candidate"])[s]
        if len(o) < 8 or len(c) < 8:
            continue
        entry = {"n": [len(o), len(c)]}
        for name, fn in (("stq2", lambda v: stabilized_quartiles(v)[1]), ("median", statistics.median)):
            d = fn(c) - fn(o)
            boot = []
            for _ in range(RESAMPLES // 10):  # StQ2 on ~400 values is slow in pure Python
                lo = [rng.choice(roles["official"]) for _ in roles["official"]]
                lc = [rng.choice(roles["candidate"]) for _ in roles["candidate"]]
                bo, bc = by_stratum(lo)[s], by_stratum(lc)[s]
                if len(bo) >= 4 and len(bc) >= 4:
                    boot.append(fn(bc) - fn(bo))
            entry[name] = {"official": fn(o), "candidate": fn(c), "delta": d, "ci95": ci(boot),
                           "resamples": len(boot)}
        out["strata"][s] = entry
    return out


def paired(results: Path, tag: str, rng: random.Random):
    out = {}
    root = results / f"fixed-lazy-paired-{tag}"
    for setting in SETTINGS:
        blocks = collections.defaultdict(lambda: {"official": [], "candidate": []})
        for p in sorted((root / setting).glob("block-*-slot-*-*.out")):
            parts = p.stem.split("-")
            blocks[int(parts[1])][parts[4]].append(load(p))
        entry = {"blocks": len(blocks), "strata": {}}
        for s in STRATA:
            deltas = []
            for b in sorted(blocks):
                o = by_stratum(blocks[b]["official"])[s]
                c = by_stratum(blocks[b]["candidate"])[s]
                if len(o) >= 3 and len(c) >= 3:
                    deltas.append(statistics.median(c) - statistics.median(o))
            if len(deltas) < 8:
                continue
            boot = []
            for _ in range(RESAMPLES):
                sample = [rng.choice(deltas) for _ in deltas]
                boot.append(sum(sample) / len(sample))
            entry["strata"][s] = {"blocks_used": len(deltas), "mean": sum(deltas) / len(deltas),
                                  "median": statistics.median(deltas), "ci95_mean": ci(boot),
                                  "favourable_blocks": sum(d < 0 for d in deltas)}
        out[setting] = entry
    return out


def distinct_sequences(results: Path, tag: str):
    seqs = set()
    files = (sorted(results.glob(f"native-lazy-qual-*-{tag}/fresh-launches/launch-*.out")) +
             sorted(results.glob(f"fixed-lazy-paired-{tag}/*/block-*.out")))
    for p in files:
        seqs.add(tuple(r for _, r in load(p)))
    return {"launch_files": len(files), "distinct_retry_sequences": len(seqs)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--tag", default="20260923")
    parser.add_argument("--seed", type=int, default=20260923)
    args = parser.parse_args()
    results = args.experiment.resolve() / "results"
    rng = random.Random(args.seed)
    out = {"schema": "ntruplus-caller-lazy-keypair-retry-strata/v1",
           "evidence_class": "derived re-analysis of existing supercop-native-kem and fixed-elf-paired raw "
                             "observations; no new timing",
           "call_index_pairing": "impossible: measure links fastrandombytes (per-process kernel-seeded "
                                 "ChaCha20 key), so coins differ per launch",
           "retry_derivation": "retries = keypair_randomcalls - 2 (one randombytes(coins,32) per f/g attempt)",
           "bootstrap_seed": args.seed,
           "sequence_check": distinct_sequences(results, args.tag),
           "native": native(results, args.tag, rng),
           "paired": paired(results, args.tag, rng)}
    path = results / f"keypair-retry-strata-{args.tag}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("sequence_check",)}, indent=1))
    n = out["native"]
    print("native composition r0:", {r: round(v["pooled_r0_fraction"], 4) for r, v in n["composition"].items()},
          "mean retries:", {r: round(v["mean_retries_per_keypair"], 3) for r, v in n["composition"].items()})
    print("native pooled:", n["pooled"])
    for s, e in n["strata"].items():
        print(f" native r={s:2s} n={e['n']} stq2 {e['stq2']['delta']:+8.1f} {e['stq2']['ci95']}  "
              f"median {e['median']['delta']:+8.1f} {e['median']['ci95']}")
    for setting, e in out["paired"].items():
        for s, r in e["strata"].items():
            print(f" {setting:18s} r={s:2s} blocks={r['blocks_used']:2d} mean {r['mean']:+8.1f} "
                  f"CI {[round(x, 1) for x in r['ci95_mean']]} median {r['median']:+8.1f} fav {r['favourable_blocks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
