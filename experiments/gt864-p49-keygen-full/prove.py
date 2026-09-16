#!/usr/bin/env python3
"""Static feasibility proof for P49's bounded canonical-reduction families."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q = 3457
S = 1 << 15
PROOF = ROOT / ("ntruplus-ntt-Optimized/Additional_Implementation/aarch64/"
                "Experiment/NTRU+864/good_thomas_campaign/experiments/"
                "gt864_p3b40_caller_closure/build/proof.json")


def round_mul(x: int, b: int) -> int:
    return (x * b + (S // 2)) // S


def endpoints(lo: int, hi: int) -> list[int]:
    result: list[int] = []
    for quotient in range(lo // Q, hi // Q + 1):
        result += [max(lo, quotient * Q), min(hi, (quotient + 1) * Q - 1)]
    return sorted(set(result))


def b_bounds(lo: int, hi: int) -> range:
    """All positive b which can possibly span the required quotient delta."""
    delta_x = hi - lo
    delta_q = hi // Q - lo // Q
    # Two nearest-integer errors have magnitude strictly below one in total.
    low = max(1, ((delta_q - 1) * S) // delta_x - 2)
    high = min(32767, ((delta_q + 1) * S) // delta_x + 3)
    return range(low, high + 1)


def shifted_solution(lo: int, hi: int):
    """Find b,c for round((x-c)b/S) == floor(x/q), including i16 shift."""
    pts = endpoints(lo, hi)
    for b in b_bounds(lo, hi):
        c_lo = hi - 32767
        c_hi = lo + 32768
        for x in pts:
            k = x // Q
            # k*S <= (x-c)*b + S/2 <= (k+1)*S-1
            lower_num = (k + 1) * S - 1 - S // 2
            upper_num = k * S - S // 2
            c_lo = max(c_lo, x - lower_num // b)
            c_hi = min(c_hi, x - ((upper_num + b - 1) // b))
        if c_lo <= c_hi:
            for c in range(c_lo, c_hi + 1):
                if all(round_mul(x - c, b) == x // Q for x in pts):
                    return [b, c]
    return None


def biased_solution(lo: int, hi: int):
    pts = endpoints(lo, hi)
    for b in b_bounds(lo, hi):
        for bias in range(-16, 17):
            if all(round_mul(x, b) + bias == x // Q for x in pts):
                return [b, bias]
    return None


def scaled_solution(lo: int, hi: int):
    pts = endpoints(lo, hi)
    for shift in range(1, 12):
        for b in range(1, 32768):
            if all((round_mul(x, b) >> shift) == x // Q for x in pts):
                return [b, shift]
    return None


def main() -> None:
    evidence = json.loads(PROOF.read_text())
    record = next(x for x in evidence["results"]
                  if x["extra"] == ["main.stage1.node0"])
    leaves = [tuple(x) for x in record["forward"]["f"]["leaves"]]
    assert len(leaves) == 288
    current_residual = [x - round_mul(x, 9) * Q
                        for lo, hi in leaves for x in range(lo, hi + 1)]
    result = {
        "experiment": "GT864-P49-KEYGEN-FULL-NORMALIZATION-20260916",
        "source_proof": str(PROOF.relative_to(ROOT)),
        "leaf_count": len(leaves),
        "coefficient_count": len(leaves) * 3,
        "envelope": [min(x[0] for x in leaves), max(x[1] for x in leaves)],
        "leaf_width": [min(hi - lo for lo, hi in leaves),
                       max(hi - lo for lo, hi in leaves)],
        "leaves_inside_small_contract": sum(lo > -Q and hi < Q for lo, hi in leaves),
        "current_b9_residual": [min(current_residual), max(current_residual)],
        "per_leaf_shifted_solutions": [],
        "per_leaf_biased_solutions": [],
    }
    for index, (lo, hi) in enumerate(leaves):
        for key, fn in (("per_leaf_shifted_solutions", shifted_solution),
                        ("per_leaf_biased_solutions", biased_solution)):
            solution = fn(lo, hi)
            if solution is not None:
                result[key].append({"leaf": index, "interval": [lo, hi],
                                    "parameters": solution})
    envelope = tuple(result["envelope"])
    result["uniform_shifted_solution"] = shifted_solution(*envelope)
    result["uniform_biased_solution"] = biased_solution(*envelope)
    result["uniform_scaled_solution"] = scaled_solution(*envelope)
    # One uniform fixed-constant family is required. Per-leaf constants would
    # introduce new table loads and violate this experiment's register/memory
    # hypothesis; the stronger per-leaf checks are retained as diagnostics.
    result["all_leaf_gate"] = any(result[key] is not None for key in
                                  ("uniform_shifted_solution",
                                   "uniform_biased_solution",
                                   "uniform_scaled_solution"))
    result["decision"] = "proceed" if result["all_leaf_gate"] else "reject_before_assembly"
    (HERE / "proof-report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
