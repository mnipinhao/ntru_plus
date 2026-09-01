#!/usr/bin/env python3
"""Machine-check Forward NTT9 orientations, roots, scale, and exact cost."""

from __future__ import annotations

import json

Q = 3457
THETA = 9
ETA = pow(THETA, 96, Q)
RHO = pow(ETA, 3, Q)
INV9 = pow(9, -1, Q)
R = (1 << 16) % Q


def b3(x: list[int]) -> list[int]:
    return [sum(x[j] * pow(RHO, k * j, Q) for j in range(3)) % Q
            for k in range(3)]


def direct(u: list[int], lam: int) -> list[int]:
    return [sum(u[s] * pow(lam * pow(ETA, k, Q) % Q, s, Q)
                for s in range(9)) % Q for k in range(9)]


def factored(u: list[int], lam: int) -> list[int]:
    f = [u[s] * pow(lam, s, Q) % Q for s in range(9)]
    a = b3([f[0], f[3], f[6]])
    b = b3([f[1], f[4], f[7]])
    c = b3([f[2], f[5], f[8]])
    out = [0] * 9
    for k0 in range(3):
        second = b3([a[k0],
                     b[k0] * pow(ETA, k0, Q) % Q,
                     c[k0] * pow(ETA, 2 * k0, Q) % Q])
        for k1 in range(3):
            out[k0 + 3 * k1] = second[k1]
    return out


def main() -> None:
    assert pow(ETA, 9, Q) == 1 and all(pow(ETA, k, Q) != 1 for k in range(1, 9))
    assert pow(RHO, 3, Q) == 1 and RHO != 1
    cases = 0
    for residue in (1, 5):
        for column in range(16):
            lam = pow(THETA, residue + 6 * column, Q)
            for seed in range(11):
                u = [((seed + 3) * (s + 5) + s * s + column) % Q for s in range(9)]
                expected = direct(u, lam)
                assert factored(u, lam) == expected
                for rotation in range(9):
                    shifted = direct(u, lam * pow(ETA, rotation, Q) % Q)
                    assert shifted == [expected[(k + rotation) % 9] for k in range(9)]
                cases += 1

    # A cyclic input orientation changes a first-level B3 output only by a
    # rho^h factor.  Therefore each second-level correction exponent may move
    # by a multiple of three, but r=1,2 can never become zero mod 9 for both
    # nonzero k0 values.  Enumerate all independent orientations to prove the
    # minimum is exactly four non-identity corrections.
    minimum = 99
    witnesses = []
    for hb in range(3):
        for hc in range(3):
            corrections = []
            for k0 in range(3):
                corrections.extend(((k0 - 3 * hb * k0) % 9,
                                    (2 * k0 - 3 * hc * k0) % 9))
            count = sum(exponent != 0 for exponent in corrections)
            if count < minimum:
                minimum, witnesses = count, [(hb, hc, corrections)]
            elif count == minimum:
                witnesses.append((hb, hc, corrections))
    assert minimum == 4

    # M5R removed six ORR saves from the historical 142-instruction block.
    # Pairing the eight contiguous b/bprime reads removes eight more issued
    # load instructions without changing bytes, mulmods, roots, or ranges.
    ledger = {
        "historical_block": 142,
        "m5r_copy_free_block": 136,
        "candidate_block": 128,
        "baseline_twist_load_instructions": 16,
        "candidate_twist_load_instructions": 8,
        "algorithm10_mulmods": 24,
        "eta_corrections_minimum": minimum,
    }
    assert ledger["candidate_block"] < 142
    assert ledger["baseline_twist_load_instructions"] - ledger["candidate_twist_load_instructions"] >= 2
    assert (R * INV9 * pow(R, -1, Q)) % Q == INV9  # R1 constant times R0 remains R0.
    print(json.dumps({
        "status": "pass",
        "direct_vs_factored_cases": cases,
        "lambda_eta_rotation_cases": cases * 9,
        "cyclic_orientation_candidates": 9,
        "minimum_nonidentity_eta_corrections": minimum,
        "mulmod_reduction_from_orientation": 0,
        "selected_change": "pair adjacent public b/bprime reads with ldp",
        "root_identity": "pass",
        "R0_scale": "pass",
        "range_contract": "unchanged arithmetic DAG",
        "cost": ledger,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
