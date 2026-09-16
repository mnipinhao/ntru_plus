#!/usr/bin/env python3
"""P51 exact range, representation, and modular-zero-test gate."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q = 3457
RECIP = 9
S = 1 << 15
D1 = (-3023, 3023)
FORWARD_PROOF = ROOT / (
    "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/Experiment/"
    "NTRU+864/good_thomas_campaign/experiments/gt864_p3b40_caller_closure/"
    "build/proof.json")
MAP = ROOT / (
    "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/"
    "gt864_fr0_to_official_map.h")


def sqrdmulh_s16(a: int, b: int) -> int:
    value = (a * b + S // 2) // S
    return max(-32768, min(32767, value))


def residue(x: int) -> int:
    return x - sqrdmulh_s16(x, RECIP) * Q


def parse_map() -> list[int]:
    text = MAP.read_text()
    body = re.search(r"gt864_fr0_for_official\[864\]\s*=\s*\{(.*?)\};",
                     text, re.S)
    if body is None:
        raise RuntimeError("FR0 map declaration not found")
    return [int(x) for x in re.findall(r"\d+", body.group(1))]


def main() -> None:
    source = json.loads(FORWARD_PROOF.read_text())
    record = next(x for x in source["results"]
                  if x["extra"] == ["main.stage1.node0"])
    leaves = [tuple(x) for x in record["forward"]["small"]["leaves"]]
    if len(leaves) != 288:
        raise RuntimeError(f"expected 288 degree-3 leaf intervals, got {len(leaves)}")
    differences = [(lo - D1[1], hi - D1[0]) for lo, hi in leaves]
    if min(lo for lo, _ in differences) < -32768 or max(hi for _, hi in differences) > 32767:
        raise RuntimeError("plain signed-halfword subtraction is not closed")

    all_i16 = range(-32768, 32768)
    residuals = [residue(x) for x in all_i16]
    false = [x for x, r in zip(all_i16, residuals)
             if (r == 0) != (x % Q == 0)]
    if false:
        raise RuntimeError(f"Barrett zero-test counterexample: {false[0]}")
    if any((r - x) % Q for x, r in zip(all_i16, residuals)):
        raise RuntimeError("Barrett residue lost congruence")

    mapping = parse_map()
    if len(mapping) != 864 or sorted(mapping) != list(range(864)):
        raise RuntimeError("FR0-to-Official map is not a permutation")

    result = {
        "experiment": "GT864-P51-TRANSFORM-EQUALITY-20260916",
        "source_forward_proof": str(FORWARD_PROOF.relative_to(ROOT)),
        "leaf_count": len(leaves),
        "coefficient_count": len(leaves) * 3,
        "regenerated_envelope": [min(lo for lo, _ in leaves),
                                 max(hi for _, hi in leaves)],
        "recovered_D1_envelope": list(D1),
        "difference_envelope": [min(lo for lo, _ in differences),
                                max(hi for _, hi in differences)],
        "all_leaf_differences_fit_signed_int16": True,
        "barrett_domain_checked": [-32768, 32767],
        "barrett_residual_envelope": [min(residuals), max(residuals)],
        "barrett_congruence": True,
        "barrett_zero_iff_divisible_by_q": True,
        "fr0_to_official_map_is_permutation": True,
        "fr0_to_official_map_count": len(mapping),
        "wire_injectivity": (
            "canonical residue is unique in [0,3456]; two 12-bit values are "
            "stored losslessly in three bytes; the coordinate map is a permutation"),
        "scale_identity": "both operands are production FR0 R0",
        "decision_equivalence": (
            "P47 canonical wire equality iff every paired FR0 coefficient is "
            "congruent modulo 3457"),
        "decision": "proceed_to_native_assembly",
    }
    (HERE / "proof-report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
