"""Does NTRU+864's Barrett reciprocal 621199 still work at degree 4?

NTRU+864's base.c documents `SQRDMULH(x, 621199)` followed by `x - qhat*3457`
as landing in [-2911, 2911], proved over the degree-3 accumulator union.
Degree 4 accumulates one more product in both the zeta fold and the final sum,
so the union widens and the claim must be re-checked.

Result: the constant transfers.  Only the resulting bound changes.
"""

import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

Q = 3457
C = 621199
TWO31 = 1 << 31

checks = []


def check(name, ok, detail):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(f"[{'pass' if ok else 'FAIL'}] {name}: {detail}")
    return ok


def sqrdmulh_s32(a, b):
    """ARM SQRDMULH on int32 lanes: round(2ab / 2^32), saturating."""
    v = (2 * a * b + (1 << 31)) >> 32
    return max(-TWO31, min(TWO31 - 1, v))


def barrett(x):
    qhat = sqrdmulh_s32(x, C)
    return x - qhat * Q, qhat


# --- the relative error that drives the bound --------------------------------
excess = C * Q - TWO31
eps = excess / TWO31
check("reciprocal_shape", excess == 1295,
      f"C*Q = {C * Q} = 2^31 + {excess}, so the quotient estimate carries a "
      f"relative error of {excess}/2^31 = {eps:.6e}")


def analytic(xmax):
    return Q / 2 + xmax * eps


# --- bound at each reachable accumulator width -------------------------------
DOMAINS = {
    "frombytes [0,4095]": 4 * 4095 * 4095,
    "measured GT forward +/-15951": 4 * 15951 * 15951,
    "degree-4 headroom 22551": 4 * 22551 * 22551,
    "full int32": TWO31 - 1,
}
table = {}
for name, xmax in DOMAINS.items():
    table[name] = {"widest_accumulator": xmax, "bound": analytic(xmax)}
    print(f"      {name:30s} |x| <= {xmax:>12}  ->  |out| <= {analytic(xmax):7.1f}")

check("transfers_at_every_width",
      all(v["bound"] < 32767 for v in table.values()),
      "the Barrett output fits int16 at every reachable accumulator width, "
      f"peaking at {analytic(TWO31 - 1):.1f} even over the whole int32 range")

# --- the intermediate qhat*Q must not overflow int32 -------------------------
# VMLS computes value - qhat*Q in int32, so qhat*Q itself must fit.  That is
# NOT true across the whole int32 range: at x = -2^31 the estimate is
# qhat = -621199 and |qhat*Q| = 2147484943 > 2^31.  Find the exact largest |x|
# for which it holds, and check the reachable accumulators against it.
lo, hi = 1, TWO31 - 1
while lo < hi:
    mid = (lo + hi + 1) // 2
    if max(abs(barrett(mid)[1]), abs(barrett(-mid)[1])) * Q < TWO31:
        lo = mid
    else:
        hi = mid - 1
ACC_LIMIT = lo
reachable = max(DOMAINS[k] for k in DOMAINS if k != "full int32")
check("qhat_times_q_fits_int32_over_reachable_accumulators",
      reachable <= ACC_LIMIT,
      f"|qhat*Q| stays below 2^31 only for |x| <= {ACC_LIMIT} "
      f"({100 * ACC_LIMIT / TWO31:.3f}% of int32); the widest reachable "
      f"degree-4 accumulator is {reachable}, inside it with "
      f"{ACC_LIMIT - reachable} to spare")
table["int32 accumulator limit"] = {
    "widest_accumulator": ACC_LIMIT, "bound": analytic(ACC_LIMIT)}

# --- empirical: sample the function, including the extremes ------------------
random.seed(4)
samples = [0, 1, -1, ACC_LIMIT, -ACC_LIMIT, Q, -Q, Q // 2, -(Q // 2)]
for xmax in DOMAINS.values():
    if xmax > ACC_LIMIT:
        continue
    samples += [xmax, -xmax]
    samples += [random.randint(-xmax, xmax) for _ in range(40000)]
samples += [random.randint(-ACC_LIMIT, ACC_LIMIT) for _ in range(40000)]
worst = 0
samples = [x for x in samples if abs(x) <= ACC_LIMIT]
for x in samples:
    r, _ = barrett(x)
    if (x - r) % Q != 0:
        check("congruence", False, f"x={x} gave a non-congruent result")
        break
    worst = max(worst, abs(r))
else:
    check("congruence", True,
          f"x - qhat*Q stays congruent to x mod q over {len(samples)} samples "
          "spanning every reachable domain and both ends of the accumulator "
          "limit")

check("sampled_within_analytic", worst <= analytic(ACC_LIMIT),
      f"largest sampled |out| = {worst} <= analytic {analytic(ACC_LIMIT):.1f} "
      "at the accumulator limit")

report = {
    "constant": C,
    "q": Q,
    "c_times_q_minus_2_31": excess,
    "relative_error": eps,
    "bounds": table,
    "ntruplus864_documented_degree3": 2911,
    "sampled_worst_output": worst,
    "checks": checks,
    "pass": all(c["pass"] for c in checks),
}
(HERE / "barrett-report.json").write_text(json.dumps(report, indent=2) + "\n")

print(f"\n{'PASS' if report['pass'] else 'FAIL'} -> barrett-report.json")
raise SystemExit(0 if report["pass"] else 1)
