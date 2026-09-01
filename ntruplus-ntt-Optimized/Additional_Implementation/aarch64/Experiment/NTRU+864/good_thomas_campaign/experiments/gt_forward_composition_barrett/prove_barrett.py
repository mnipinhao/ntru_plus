#!/usr/bin/env python3
"""Exhaust Algorithm-10 for every distinct fixed constant used by M5F."""

from __future__ import annotations

import json

from generate_tables import Q, RESIDUES, THETA, pair


def constants() -> set[tuple[int, int]]:
    omega16 = pow(THETA, 54, Q)
    eta = pow(THETA, 96, Q)
    rho = pow(eta, 3, Q)
    values = {1, eta, pow(eta, -1, Q), rho, pow(rho, 2, Q)}
    for residue in RESIDUES:
        values.update(pow(THETA, 9 * residue * t, Q) for t in range(16))
        for column in range(16):
            lam = pow(THETA, residue + 6 * column, Q)
            values.update(pow(lam, s, Q) for s in range(9))
    for length in (2, 4, 8, 16):
        values.update(pow(omega16, j * 16 // length, Q)
                      for j in range(length // 2))
    return {pair(value) for value in values}


checked = 0
maximum = 0
for b, bprime in sorted(constants()):
    for a in range(-32768, 32768):
        quotient = (2 * a * bprime + (1 << 15)) >> 16
        z = a * b - quotient * Q
        assert -32768 <= z <= 32767
        assert (z - a * b) % Q == 0
        maximum = max(maximum, abs(z))
        checked += 1

print(json.dumps({
    "gate": "gt864_forward_algorithm10_exhaustive",
    "status": "pass",
    "distinct_constants": len(constants()),
    "signed_halfword_products": checked,
    "maximum_output_abs": maximum,
    "all_outputs_fit_int16": True,
    "all_outputs_congruent": True,
    "production_linked": False,
}, indent=2, sort_keys=True))
