#!/usr/bin/env python3
"""Extended Native SUPERCOP run: many 9-launch batches alternating ABBA/BAAB.

Runs --batches rounds; round k runs one Official batch and one candidate
batch, Official first for odd k and candidate first for even k (sequence
A,B,B,A,A,B,...).  With repeated --role NAME=IMPLEMENTATION, round k runs one
batch per role, in the given order for odd k and reversed for even k
(e.g. A,B,C / C,B,A / A,B,C ...).  Each batch is one phase_b_batch.py call (hygiene check,
up to 2 reruns of a contaminated batch) around
scripts/run_supercop_benchmark.py --mode native-kem with DEFAULT SUPERCOP
compiler selection (no --compiler-wrapper), the unmodified measure.c and
--fresh-launches launches pinned to --cpu.  Batches run strictly one after
another.  Result directories:
  results/native-ext-{official,candidate}-b<k>-<tag>/
  results/native-ext-<name>-b<k>-<tag>/  (with --role)
Summarise with summarize_extended.py (two roles) or
summarize_extended_multi.py (several roles).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").is_file())
IMPL = {"official": "avx2", "candidate": "avx2-officialopt-caller-lazy-qual001"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--param", choices=("864", "1152"), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--batches", type=int, default=9)
    parser.add_argument("--fresh-launches", type=int, default=9)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--start", type=int, default=1, help="resume at this round")
    parser.add_argument("--role", action="append", metavar="NAME=IMPLEMENTATION",
                        help="role and SUPERCOP implementation; repeat (default: official, candidate)")
    args = parser.parse_args()
    impl = dict(IMPL)
    if args.role:
        impl = dict(r.split("=", 1) for r in args.role)
        if len(impl) != len(args.role) or len(impl) < 2:
            raise SystemExit("--role needs at least two distinct NAME=IMPLEMENTATION entries")
    results = args.experiment.resolve() / "results"
    for k in range(args.start, args.batches + 1):
        order = tuple(impl) if k % 2 else tuple(reversed(impl))
        for role in order:
            out = results / f"native-ext-{role}-b{k}-{args.tag}"
            if out.exists():
                print(f"skip existing {out.name}", flush=True)
                continue
            cmd = [sys.executable, str(HERE.parent / "phase_b_batch.py"), "--result-dir", str(out),
                   "--metadata", "metadata.json", "--",
                   sys.executable, str(REPO / "scripts/run_supercop_benchmark.py"),
                   "--campaign-root", str(args.campaign_root), "--parameter", args.param,
                   "--implementation", impl[role], "--cpu", str(args.cpu), "--mode", "native-kem",
                   "--fresh-launches", str(args.fresh_launches), "--require-frequency-control",
                   "--result-dir", "{RESULT}"]
            print(f"== round {k} {role}", flush=True)
            code = subprocess.call(cmd)
            if code:
                raise SystemExit(f"batch {out.name} failed ({code})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
