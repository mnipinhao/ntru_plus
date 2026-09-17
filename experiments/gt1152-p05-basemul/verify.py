"""Differential gate for the NTRU+1152 degree-4 basemul / basemul_add.

Runs the real GT forward, then the C kernel, and compares against the G1
declared oracle under the layout measured in gt1152-p03-gt-layout.  Also
exercises every aliasing pattern the KEM uses or that inverse.h documents.

Correctness only; this host is not Cortex-A76.
"""

import json
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "experiments/gt1152-p01-ring-profile"))

import ntruplus1152 as P  # noqa: E402

Q = P.Q
N = 1152
DEG = 4
PERM = [int(x) for x in (REPO / "experiments/gt1152-p03-gt-layout/perm864.txt"
                         ).read_text().split()]


def slots():
    for top in range(2):
        for row in range(9):
            for halfcol in range(2):
                for lane in range(8):
                    yield top, row, halfcol, lane


def gt_index(top, row, halfcol, component, lane):
    return top * 576 + row * 64 + halfcol * 32 + component * 8 + lane


def to_gt(ref):
    """Permute a reference-order polynomial into the GT layout."""
    out = [0] * N
    for slot_i, (top, row, halfcol, lane) in enumerate(slots()):
        leaf = PERM[slot_i]
        for component in range(DEG):
            out[gt_index(top, row, halfcol, component, lane)] = \
                ref[DEG * leaf + component]
    return out


def run(mode, a, b, c):
    args = ",".join(map(str, a + b + c))
    out = subprocess.run([str(HERE / "harness"), mode, args],
                         capture_output=True, text=True, check=True).stdout
    return [int(x) for x in out.strip().split(",")]


def main():
    random.seed(20260917)
    cases = []
    cases.append(("extremes", [4] * N, [-3] * N, [4] * N))
    cases.append(("zero_b", [random.randint(-1, 1) for _ in range(N)], [0] * N,
                  [random.randint(-1, 1) for _ in range(N)]))
    for k in range(6):
        cases.append((f"ternary{k}",
                      [random.randint(-1, 1) for _ in range(N)],
                      [random.randint(-1, 1) for _ in range(N)],
                      [random.randint(-1, 1) for _ in range(N)]))
    for k in range(6):
        cases.append((f"contract{k}",
                      [random.randint(-3, 4) for _ in range(N)],
                      [random.randint(-3, 4) for _ in range(N)],
                      [random.randint(-3, 4) for _ in range(N)]))

    failures = []
    observed_lo = observed_hi = 0

    for name, a, b, c in cases:
        A, B, C = P.ntt(a), P.ntt(b), P.ntt(c)
        want_mul = to_gt(P.poly_basemul(A, B))
        want_add = to_gt(P.poly_basemul_add(A, B, C))

        for mode, want in (("mul", want_mul), ("add", want_add),
                           ("alias_a", want_mul), ("alias_b", want_mul),
                           ("alias_addc", want_add)):
            got = run(mode, a, b, c)
            observed_lo = min(observed_lo, min(got))
            observed_hi = max(observed_hi, max(got))
            bad = sum(1 for i in range(N) if got[i] % Q != want[i] % Q)
            if bad:
                failures.append({"case": name, "mode": mode, "mismatches": bad})

        # a aliased with itself is a square; the oracle must agree.
        got = run("alias_aa", a, b, c)
        want_sq = to_gt(P.poly_basemul(A, A))
        bad = sum(1 for i in range(N) if got[i] % Q != want_sq[i] % Q)
        if bad:
            failures.append({"case": name, "mode": "alias_aa", "mismatches": bad})

        print(f"  {name:12s} {'ok' if not failures or failures[-1]['case'] != name else 'FAIL'}",
              flush=True)

    analytic = json.loads(
        (REPO / "experiments/gt1152-p02-degree4-bounds/bounds-report.json").read_text())
    barrett_bound = 2343   # bounds_barrett.py, measured GT forward domain
    within = max(abs(observed_lo), observed_hi) <= barrett_bound

    report = {
        "cases": len(cases),
        "modes_per_case": 6,
        "observed_output": {"lo": observed_lo, "hi": observed_hi,
                            "abs_max": max(abs(observed_lo), observed_hi)},
        "barrett_bound_for_measured_forward_domain": barrett_bound,
        "output_within_bound": within,
        "reference_model_bound": analytic["results"]["gt_forward"]["basemul"]["abs_max"],
        "failures": failures,
        "pass": not failures and within,
    }
    (HERE / "verify-report.json").write_text(json.dumps(report, indent=2) + "\n")

    print(f"\nobserved output range [{observed_lo}, {observed_hi}], "
          f"Barrett bound {barrett_bound}: {'within' if within else 'EXCEEDED'}")

    if failures:
        print(f"\nFAIL: {failures[:3]}", file=sys.stderr)
        return 1
    if not within:
        print("\nFAIL: output exceeded the Barrett bound", file=sys.stderr)
        return 1
    print(f"\nPASS: {len(cases)} cases x 6 modes x {N} coefficients "
          f"-> verify-report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
