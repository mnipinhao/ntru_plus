"""Degree-4 range and scale bound chain for NTRU+1152.

Every NTRU+864 bound is proved for degree-3 accumulators and does not transfer.
This module derives the degree-4 chain from first principles using exact
interval arithmetic over the reference algorithms, and validates the method by
reproducing NTRU+864's documented bounds with the same code.

What is proved here
-------------------
* the exact reachable interval of every int32 accumulator,
* that no accumulator can overflow int32,
* that every value stored back to int16 fits,
* the output bound of basemul / basemul_add / basemul_rinv / baseinv.

What is NOT proved here
-----------------------
The forward NTT output bound is an input to this module, not an output of it.
G3 owns it: whatever bound the ported eight-bank forward actually achieves must
be fed back here.  Until then the reference bound is used and the NTRU+864 lazy
value is shown alongside for comparison.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "experiments/gt1152-p01-ring-profile"))

import ntruplus1152 as P  # noqa: E402

Q = P.Q
INT32_MIN, INT32_MAX = -(1 << 31), (1 << 31) - 1
INT16_MIN, INT16_MAX = -(1 << 15), (1 << 15) - 1

violations = []


class Iv:
    """A closed integer interval, tracked exactly."""

    __slots__ = ("lo", "hi", "name")

    def __init__(self, lo, hi, name=""):
        assert lo <= hi, (lo, hi)
        self.lo, self.hi, self.name = lo, hi, name

    def __repr__(self):
        return f"[{self.lo}, {self.hi}]"

    @property
    def mag(self):
        return max(abs(self.lo), abs(self.hi))

    def __add__(self, other):
        return Iv(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other):
        return Iv(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other):
        corners = (self.lo * other.lo, self.lo * other.hi,
                   self.hi * other.lo, self.hi * other.hi)
        return Iv(min(corners), max(corners))

    def scale(self, k):
        return Iv(min(self.lo * k, self.hi * k), max(self.lo * k, self.hi * k))


def check_int32(iv, where):
    """Every accumulator is computed in int32 in the C and NEON code."""
    if iv.lo < INT32_MIN or iv.hi > INT32_MAX:
        violations.append({"kind": "int32_overflow", "where": where, "interval": [iv.lo, iv.hi]})
    return iv


def check_int16(iv, where):
    if iv.lo < INT16_MIN or iv.hi > INT16_MAX:
        violations.append({"kind": "int16_overflow", "where": where, "interval": [iv.lo, iv.hi]})
    return iv


def mont(iv, where):
    """Exact output interval of montgomery_reduce.

        t   = (int16_t)a * QINV      -> any value in [-2^15, 2^15-1]
        out = (a - t*Q) >> 16        -> arithmetic (floor) shift

    Taking the worst case over t independently of a is sound and is what the
    NTRU+864 evidence does; it is also tight to within one unit, which the
    self-validation below demonstrates.
    """
    check_int32(iv, where + ":acc")
    lo = (iv.lo - 32767 * Q) >> 16
    hi = (iv.hi + 32768 * Q) >> 16
    out = Iv(lo, hi)
    check_int16(out, where + ":out")
    return out


# --------------------------------------------------------------------------
# Leaf zeta magnitude, taken from the real table rather than assumed
# --------------------------------------------------------------------------
LEAF_ZETAS = [z for i in range(144) for z in (P.ZETAS[144 + i], P.s16(-P.ZETAS[144 + i]))]
ZETA = Iv(min(LEAF_ZETAS), max(LEAF_ZETAS), "leaf zeta")


# --------------------------------------------------------------------------
# Kernel models.  `deg` selects the degree-3 (864) or degree-4 (1152) shape.
# --------------------------------------------------------------------------

def basemul_rinv_model(a, b, deg, tag):
    """Reference basemul steps 1-2: the R^-1 boundary the inverse consumes.

    degree 3:  r0 = a1b2+a2b1        r1 = a2b2
               r0 = r0*z + a0b0      r1 = r1*z + a0b1 + a1b0
                                     r2 =         a0b2 + a1b1 + a2b0
    degree 4:  r0 = a1b3+a2b2+a3b1   r1 = a2b3+a3b2   r2 = a3b3
               r0 = r0*z + a0b0
               r1 = r1*z + a0b1+a1b0
               r2 = r2*z + a0b2+a1b1+a2b0
               r3 =        a0b3+a1b2+a2b1+a3b0
    """
    ab = a * b
    if deg == 3:
        wrap = [ab.scale(2), ab.scale(1)]
        direct = [1, 2, 3]          # terms in r0, r1, r2 after the wrap fold
    else:
        wrap = [ab.scale(3), ab.scale(2), ab.scale(1)]
        direct = [1, 2, 3, 4]

    out = []
    for i, n_direct in enumerate(direct):
        acc = ab.scale(n_direct)
        if i < len(wrap):
            w = mont(check_int32(wrap[i], f"{tag}:wrap{i}"), f"{tag}:wrap{i}")
            acc = acc + (w * ZETA)
        out.append(mont(check_int32(acc, f"{tag}:r{i}"), f"{tag}:r{i}"))
    return out


def basemul_model(a, b, deg, tag):
    """Full reference basemul: the R^-1 stage followed by the RSQ rescale."""
    rinv = basemul_rinv_model(a, b, deg, tag)
    rsq = Iv(P.RSQ, P.RSQ)
    return [mont(check_int32(r * rsq, f"{tag}:rsq{i}"), f"{tag}:rsq{i}")
            for i, r in enumerate(rinv)]


def basemul_add_model(a, b, c, deg, tag):
    """basemul_add folds c*R into the final rescale."""
    rinv = basemul_rinv_model(a, b, deg, tag)
    rsq, rr = Iv(P.RSQ, P.RSQ), Iv(P.R, P.R)
    out = []
    for i, r in enumerate(rinv):
        acc = check_int32((c * rr) + (r * rsq), f"{tag}:add{i}")
        out.append(mont(acc, f"{tag}:add{i}"))
    return out


def baseinv_model(a, tag):
    """Degree-4 quadratic-tower inversion; scale chain R^-1 -> R^-3 -> R^5 -> R^0."""
    aa = a * a
    t0 = mont(check_int32(aa - aa.scale(2), f"{tag}:t0a"), f"{tag}:t0a")
    t1 = mont(check_int32(aa, f"{tag}:t1a"), f"{tag}:t1a")
    t0 = mont(check_int32(aa + (t0 * ZETA), f"{tag}:t0b"), f"{tag}:t0b")
    t1 = mont(check_int32(aa + (t1 * ZETA) - aa.scale(2), f"{tag}:t1b"), f"{tag}:t1b")
    t2 = mont(check_int32(t1 * ZETA, f"{tag}:t2"), f"{tag}:t2")
    t3 = mont(check_int32((t0 * t0) - (t1 * t2), f"{tag}:t3"), f"{tag}:t3")

    num = mont(check_int32((a * t2) + (a * t0), f"{tag}:num"), f"{tag}:num")

    # fqinv is an addition chain of fqmul over already-reduced values; its
    # output is a full field element, so bound it by the centered range.
    t3inv = Iv(-(Q - 1) // 2, (Q - 1) // 2, "fqinv output")
    out = mont(check_int32(num * t3inv, f"{tag}:final"), f"{tag}:final")
    return {"t0": t0, "t1": t1, "t2": t2, "t3": t3, "num": num, "out": out}


# --------------------------------------------------------------------------
# Input domains
# --------------------------------------------------------------------------
FROMBYTES = Iv(0, 4095, "frombytes [0,4095]")
REF_NTT = Iv(-(Q + 1) // 2, (Q + 1) // 2, "reference NTT output")

# Decapsulation computes poly_sub(c, m2) with c straight from poly_frombytes and
# m2 = ntt(crepmod3(...)), then feeds the difference to poly_basemul.  This
# domain was missing from the first version of this model; instrument.py caught
# it by observing a basemul input of 5108, outside every domain listed then.
DECAPS_SUB = FROMBYTES - REF_NTT

# Measured in gt1152-p04-forward-8bank/forward-bound.json by running both GT
# forwards over the [-3,4] input contract: 864 reaches 15951, 1152 reaches
# 14607.  Observed, not proved -- a proof needs an interval model of
# .Lntt_one_bank, which no gate has built.
_fwd = HERE.parent / "gt1152-p04-forward-8bank/forward-bound.json"
if _fwd.is_file():
    _m = json.loads(_fwd.read_text())
    _mag = max(_m["ntruplus1152"]["abs_max"], _m["ntruplus864"]["abs_max"])
else:
    _mag = 15951
GT_FORWARD = Iv(-_mag, _mag, "measured GT forward output")

# Each entry is (a_domain, b_domain); many call sites are asymmetric.
DOMAINS = {
    # The decapsulation first product, and the origin of NTRU+864's 2497.
    "frombytes_x_frombytes": (FROMBYTES, FROMBYTES),
    "reference_ntt": (REF_NTT, REF_NTT),
    # poly_basemul(poly_sub(c, m2), hinv) in crypto_kem_dec.
    "decaps_sub_x_frombytes": (DECAPS_SUB, FROMBYTES),
    # The GT forward's output.  An earlier version of this file used
    # [-4577, 4577] here and labelled it "NTRU+864 lazy forward".  That was
    # wrong: 4577 is the raw ternary-consumer limit in NTRU+864's INVERSE chain
    # (2497/2617/21397/4577), not a forward bound.  G3b measured the real thing
    # by running both kernels -- NTRU+864 reaches 15951 and NTRU+1152 14607 over
    # the [-3,4] input contract.  A conservative int16-safe envelope is used.
    "gt_forward": (GT_FORWARD, GT_FORWARD),
}


def headroom(deg):
    """Largest symmetric input magnitude A for which basemul over [-A,A]^2
    raises no int32 or int16 violation.  Degree 4 accumulates one more product
    than degree 3 in both the zeta fold and the final sum, so its headroom is
    strictly smaller; this quantifies by how much."""
    global violations
    lo, hi = 1, 1 << 15
    while lo < hi:
        mid = (lo + hi + 1) // 2
        saved, violations = violations, []
        iv = Iv(-mid, mid)
        basemul_model(iv, iv, deg, "headroom")
        ok = not violations
        violations = saved
        if ok:
            lo = mid
        else:
            hi = mid - 1
    return lo


def run():
    report = {"q": Q, "leaf_zeta_interval": [ZETA.lo, ZETA.hi], "results": {}}

    print(f"leaf zeta interval over zetas[144..287] and negations: {ZETA}\n")

    # ---- self-validation: reproduce NTRU+864's documented numbers ----------
    d = FROMBYTES
    r864 = basemul_rinv_model(d, d, 3, "864/basemul_rinv")
    got = max(x.mag for x in r864)
    ok = abs(got - 2497) <= 1
    print(f"[{'pass' if ok else 'FAIL'}] self-validation: degree-3 basemul_rinv over "
          f"[0,4095] gives |out| <= {got}; inverse.h documents 2497")
    report["self_validation"] = {
        "documented_864_basemul_rinv": 2497, "model": got, "within_one": ok}

    # ---- the degree-4 chain ----------------------------------------------
    for dom_name, (da, db) in DOMAINS.items():
        entry = {"a_domain": [da.lo, da.hi], "b_domain": [db.lo, db.hi]}
        rinv = basemul_rinv_model(da, db, 4, f"1152/{dom_name}/rinv")
        entry["basemul_rinv"] = {
            "per_coefficient": [[x.lo, x.hi] for x in rinv],
            "abs_max": max(x.mag for x in rinv),
        }
        full = basemul_model(da, db, 4, f"1152/{dom_name}/basemul")
        entry["basemul"] = {
            "per_coefficient": [[x.lo, x.hi] for x in full],
            "abs_max": max(x.mag for x in full),
        }
        addc = basemul_add_model(da, db, REF_NTT, 4, f"1152/{dom_name}/basemul_add")
        entry["basemul_add"] = {
            "per_coefficient": [[x.lo, x.hi] for x in addc],
            "abs_max": max(x.mag for x in addc),
        }
        binv = baseinv_model(da, f"1152/{dom_name}/baseinv")
        entry["baseinv"] = {k: [v.lo, v.hi] for k, v in binv.items()}
        entry["baseinv"]["abs_max_out"] = binv["out"].mag
        report["results"][dom_name] = entry

        print(f"\ninput domain {dom_name}: a={da} b={db}")
        print(f"  basemul_rinv  |out| <= {entry['basemul_rinv']['abs_max']:6d}   "
              f"per-coefficient {entry['basemul_rinv']['per_coefficient']}")
        print(f"  basemul       |out| <= {entry['basemul']['abs_max']:6d}")
        print(f"  basemul_add   |out| <= {entry['basemul_add']['abs_max']:6d}")
        print(f"  baseinv       |out| <= {entry['baseinv']['abs_max_out']:6d}")

    # ---- headroom: how much lazier could the forward get? ------------------
    h3, h4 = headroom(3), headroom(4)
    measured = GT_FORWARD.mag
    report["headroom"] = {
        "degree_3_max_input": h3,
        "degree_4_max_input": h4,
        "measured_gt_forward": measured,
        "degree_4_margin": round(h4 / measured, 3),
    }
    print(f"\nheadroom (largest symmetric input with no int32/int16 violation):")
    print(f"  degree 3: {h3}")
    print(f"  degree 4: {h4}   <- one more product in both the zeta fold and "
          f"the final sum")
    print(f"  measured GT forward output: {measured}, margin {h4 / measured:.2f}x")

    # ---- D7: the basemul_rinv normalization decision ----------------------
    decaps = report["results"]["frombytes_x_frombytes"]["basemul_rinv"]["abs_max"]
    report["d7_basemul_rinv_decision"] = {
        "ntruplus864_inverse_input_contract": 2497,
        "ntruplus1152_basemul_rinv_output": decaps,
        "exceeds_864_contract": decaps > 2497,
        "ratio": round(decaps / 2497, 4),
    }

    report["violations"] = violations
    report["pass"] = not violations and ok
    (HERE / "bounds-report.json").write_text(json.dumps(report, indent=2) + "\n")

    print(f"\nint32 / int16 violations: {len(violations)}")
    for v in violations[:5]:
        print(f"  {v}")

    print(f"\nD7: 1152 basemul_rinv output |out| <= {decaps} versus NTRU+864's "
          f"2497 inverse input contract (ratio {decaps / 2497:.3f})")

    if not report["pass"]:
        print("\nFAIL", file=sys.stderr)
        return 1
    print("\nPASS -> bounds-report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
