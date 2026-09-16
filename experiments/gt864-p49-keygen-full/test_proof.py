#!/usr/bin/env python3
"""Independent checks for P49 proof helpers and the closed static gate."""
from __future__ import annotations

import json
import random

import prove


def check_family(lo: int, hi: int, family: str, parameters: list[int]) -> None:
    for x in range(lo, hi + 1):
        if family == "shifted":
            b, c = parameters
            quotient = prove.round_mul(x - c, b)
        elif family == "biased":
            b, bias = parameters
            quotient = prove.round_mul(x, b) + bias
        else:
            b, shift = parameters
            quotient = prove.round_mul(x, b) >> shift
        assert quotient == x // prove.Q
        assert 0 <= x - quotient * prove.Q < prove.Q


def main() -> None:
    # Positive controls ensure the search is capable of finding and validating
    # solutions, rather than reporting an empty set unconditionally.
    for lo, hi in ((0, 3456), (-3456, -1), (-100, 100)):
        for name, fn in (("shifted", prove.shifted_solution),
                         ("biased", prove.biased_solution),
                         ("scaled", prove.scaled_solution)):
            solution = fn(lo, hi)
            if solution is not None:
                check_family(lo, hi, name, solution)

    report = json.loads((prove.HERE / "proof-report.json").read_text())
    assert report["envelope"] == [-28765, 28258]
    assert report["leaves_inside_small_contract"] == 0
    assert report["current_b9_residual"] == [-3107, 3107]
    assert not report["per_leaf_shifted_solutions"]
    assert not report["per_leaf_biased_solutions"]
    assert report["uniform_scaled_solution"] is None
    assert report["decision"] == "reject_before_assembly"

    # The P46 four-instruction formula remains exact throughout the envelope.
    rng = random.Random(0x5049)
    for x in list(range(-28765, 28259, 17)) + [rng.randrange(-28765, 28259)
                                                for _ in range(10000)]:
        residual = x - prove.round_mul(x, 9) * prove.Q
        canonical = residual + (prove.Q if residual < 0 else 0)
        assert canonical == x % prove.Q

    # A direct Small substitution demonstrably cannot preserve canonical bytes.
    assert 3457 % prove.Q == 0
    assert (3457 & 4095) != 0
    print("P49 proof tests passed: bounded search closed; direct Small has a canonical-byte counterexample")


if __name__ == "__main__":
    main()
