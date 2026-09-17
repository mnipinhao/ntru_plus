"""Differential gate for the NTRU+1152 eight-bank GT forward.

Checks the built kernel against the G1 declared oracle under the layout
predicted in gt1152-p03-gt-layout, which simultaneously verifies:

  * the transform is correct (values agree mod q with the reference NTT),
  * the predicted 1152 layout formula is the one the kernel actually produces,
  * the GT leaf permutation equals the one measured from NTRU+864.

Correctness only.  This host is Apple silicon; nothing here is a performance
statement about Cortex-A76.
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
    """GT leaf slots in the same order perm864.txt was generated in."""
    for top in range(2):
        for row in range(9):
            for halfcol in range(2):
                for lane in range(8):
                    yield top, row, halfcol, lane


def gt_index(top, row, halfcol, component, lane):
    return top * 576 + row * 64 + halfcol * 32 + component * 8 + lane


def run_kernel(a):
    out = subprocess.run([str(HERE / "harness"), ",".join(map(str, a))],
                         capture_output=True, text=True, check=True).stdout
    return [int(x) for x in out.strip().split(",")]


def main():
    random.seed(20260917)
    cases = []
    # Structured boundary inputs at the edges of the [-3,4] contract.
    cases.append(("all_-3", [-3] * N))
    cases.append(("all_+4", [4] * N))
    cases.append(("zero", [0] * N))
    for i in (0, 1, 575, 576, 1151):
        d = [0] * N
        d[i] = 4
        cases.append((f"delta@{i}", d))
    # Ternary, the domain the KEM actually feeds after poly_triple.
    for k in range(8):
        cases.append((f"ternary{k}", [random.randint(-1, 1) for _ in range(N)]))
    # Full contract range.
    for k in range(8):
        cases.append((f"contract{k}", [random.randint(-3, 4) for _ in range(N)]))

    failures = []
    for name, a in cases:
        gt = run_kernel(a)
        ref = P.ntt(a)
        bad = 0
        for slot_i, (top, row, halfcol, lane) in enumerate(slots()):
            leaf = PERM[slot_i]
            for component in range(DEG):
                got = gt[gt_index(top, row, halfcol, component, lane)] % Q
                want = ref[DEG * leaf + component] % Q
                if got != want:
                    bad += 1
                    if bad == 1:
                        failures.append({
                            "case": name, "slot": slot_i, "leaf": leaf,
                            "component": component, "got": got, "want": want,
                        })
        print(f"  {name:14s} {'ok' if not bad else f'FAIL ({bad} coefficients)'}",
              flush=True)

    report = {
        "cases": len(cases),
        "coefficients_per_case": N,
        "layout": "top*576 + row*64 + halfcol*32 + component*8 + lane",
        "permutation_source": "gt1152-p03-gt-layout/perm864.txt",
        "failures": failures,
        "pass": not failures,
    }
    (HERE / "verify-report.json").write_text(json.dumps(report, indent=2) + "\n")

    if failures:
        print(f"\nFAIL: {len(failures)} cases mismatched", file=sys.stderr)
        for f in failures[:3]:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"\nPASS: {len(cases)} cases x {N} coefficients match the oracle under "
          f"the predicted layout -> verify-report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
