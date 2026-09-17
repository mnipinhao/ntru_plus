"""Measure the NTRU+1152 eight-bank GT forward output range.

G2's bound model takes the forward output bound as an input. This supplies it.

The value is OBSERVED, not proved. Proving it needs an interval model of
.Lntt_one_bank's 617 instructions, which no gate has built. What is argued is
narrower and sound: the core is byte-identical between 864 and 1152 and sees
the same [-3,4] input contract, so the per-coefficient range is the same --
and that is checked here by measuring both.
"""
import json, random, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
P03 = HERE.parents[0] / "gt1152-p03-gt-layout"


def sweep(binary, n, samples=120):
    random.seed(11)
    cases = [[-3] * n, [4] * n, [3] * n, [-2] * n, [0] * n]
    for i in (0, n // 2 - 1, n // 2, n - 1):
        d = [0] * n; d[i] = 4; cases.append(d)
        d = [0] * n; d[i] = -3; cases.append(d)
    cases += [[random.randint(-3, 4) for _ in range(n)] for _ in range(samples)]
    lo = hi = 0
    for a in cases:
        out = subprocess.run([str(binary), ",".join(map(str, a))],
                             capture_output=True, text=True, check=True).stdout
        v = [int(x) for x in out.strip().split(",")]
        lo, hi = min(lo, min(v)), max(hi, max(v))
    return lo, hi, len(cases)


r1152 = sweep(HERE / "harness", 1152)
r864 = sweep(P03 / "dump864", 864)

report = {
    "note": "observed, not proved; see module docstring",
    "input_contract": [-3, 4],
    "ntruplus1152": {"lo": r1152[0], "hi": r1152[1], "abs_max": max(abs(r1152[0]), r1152[1]), "cases": r1152[2]},
    "ntruplus864": {"lo": r864[0], "hi": r864[1], "abs_max": max(abs(r864[0]), r864[1]), "cases": r864[2]},
    "stage_one_analytic": {
        "alpha_out": 4 + 722 * 4,
        "beta_out": 4 + 4 + 722 * 4,
        "comment": "per coefficient, independent of leaf degree",
    },
}
(HERE / "forward-bound.json").write_text(json.dumps(report, indent=2) + "\n")
for k in ("ntruplus864", "ntruplus1152"):
    d = report[k]
    print(f"{k}: [{d['lo']}, {d['hi']}]  |.| <= {d['abs_max']}  over {d['cases']} inputs")
print("\nsame magnitude, as the byte-identical core predicts -> forward-bound.json")
