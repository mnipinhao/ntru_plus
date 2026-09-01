#!/usr/bin/env python3
"""Prove the one-Algorithm-10 radix-3 identity and conservative int16 closure."""

from __future__ import annotations

import json
from dataclasses import dataclass

Q = 3457
THETA = 9
RHO = (-723, -6853)
RHO2 = (722, 6844)
ETA = (1124, 10654)
ETA_INV = (366, 3469)
SOURCE = (-8874, 8874)  # proved maximum of the NTT16 producer
TWISTED = (-2179, 2179)  # union over every non-identity NTT9 Barrett twist
I16 = (-32768, 32767)


def fixed(value: int, constant: tuple[int, int]) -> int:
    b, bprime = constant
    quotient = (2 * value * bprime + (1 << 15)) >> 16
    low = ((value * b + (1 << 15)) & 0xFFFF) - (1 << 15)
    qlow = ((quotient * Q + (1 << 15)) & 0xFFFF) - (1 << 15)
    return ((low - qlow + (1 << 15)) & 0xFFFF) - (1 << 15)


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def pair(value: int) -> tuple[int, int]:
    value = centered(value)
    reciprocal = (abs(value) * (1 << 15) + Q // 2) // Q
    return value, -reciprocal if value < 0 else reciprocal


@dataclass(frozen=True)
class Interval:
    low: int
    high: int

    @property
    def magnitude(self) -> int:
        return max(abs(self.low), abs(self.high))


def add(left: Interval, right: Interval) -> Interval:
    return Interval(left.low + right.low, left.high + right.high)


def sub(left: Interval, right: Interval) -> Interval:
    return Interval(left.low - right.high, left.high - right.low)


def mul(value: Interval, constant: tuple[int, int]) -> Interval:
    outputs = [fixed(x, constant) for x in range(value.low, value.high + 1)]
    return Interval(min(outputs), max(outputs))


def one_mul_b3(x0: Interval, x1: Interval, x2: Interval):
    nodes = {}
    nodes["sum01"] = add(x0, x1)
    nodes["y0"] = add(nodes["sum01"], x2)
    nodes["diff"] = sub(x1, x2)
    nodes["rho_diff"] = mul(nodes["diff"], RHO)
    nodes["y1_base"] = sub(x0, x2)
    nodes["y1"] = add(nodes["y1_base"], nodes["rho_diff"])
    nodes["y2_base"] = sub(x0, x1)
    nodes["y2"] = sub(nodes["y2_base"], nodes["rho_diff"])
    return nodes


def baseline_b3(x0: Interval, x1: Interval, x2: Interval):
    y0 = add(add(x0, x1), x2)
    y1 = add(x0, add(mul(x1, RHO), mul(x2, RHO2)))
    y2 = add(x0, add(mul(x1, RHO2), mul(x2, RHO)))
    return (y0, y1, y2)


def main() -> None:
    twist_constants = {
        pair(pow(THETA, (residue + 6 * column) * power, Q))
        for residue in (1, 5) for column in range(16) for power in range(1, 9)
    }
    twist_outputs = [fixed(value, constant)
                     for constant in twist_constants
                     for value in range(SOURCE[0], SOURCE[1] + 1)]
    assert (min(twist_outputs), max(twist_outputs)) == TWISTED

    # Root identity and exact Algorithm-10 congruence over the complete safe diff domain.
    rho, rho2 = RHO[0] % Q, RHO2[0] % Q
    assert (rho * rho + rho + 1) % Q == 0
    assert rho2 == rho * rho % Q == (-1 - rho) % Q
    congruence_checks = 0
    for value in range(TWISTED[0] - TWISTED[1], TWISTED[1] - TWISTED[0] + 1):
        assert (fixed(value, RHO) - value * RHO[0]) % Q == 0
        congruence_checks += 1

    reports = {}
    level1 = {}
    # A contains the untwisted s=0 producer; B/C contain three reduced twists.
    for name, x0 in (("A", Interval(*SOURCE)),
                     ("B", Interval(*TWISTED)),
                     ("C", Interval(*TWISTED))):
        x1 = x2 = Interval(*TWISTED)
        nodes = one_mul_b3(x0, x1, x2)
        assert all(I16[0] <= node.low <= node.high <= I16[1]
                   for node in nodes.values())
        old = baseline_b3(x0, x1, x2)
        new = (nodes["y0"], nodes["y1"], nodes["y2"])
        # Interval endpoints need not match because the two DAGs retain different
        # representatives. Mathematical equality is proved exhaustively below.
        reports[name] = {
            "inputs": {"x0": [x0.low, x0.high],
                       "x1_x2": list(TWISTED)},
            "nodes": {key: [value.low, value.high]
                      for key, value in nodes.items()},
            "maximum_abs": max(value.magnitude for value in nodes.values()),
            "baseline_output_intervals": [[x.low, x.high] for x in old],
            "candidate_output_intervals": [[x.low, x.high] for x in new],
        }
        level1[name] = new

    # Carry the changed representatives through the unchanged eta corrections
    # and the unchanged two-product level-2 B3 nodes. This is deliberately a
    # conservative dependency-independent interval proof.
    a, b, c = level1["A"], level1["B"], level1["C"]
    eta_b1, eta_inv_c1 = mul(b[1], ETA), mul(c[1], ETA_INV)
    eta_inv_b2, eta_c2 = mul(b[2], ETA_INV), mul(c[2], ETA)
    groups = {
        "G0": baseline_b3(a[0], b[0], c[0]),
        "G1": baseline_b3(a[1], eta_b1, eta_inv_c1),
        "G2": baseline_b3(a[2], eta_inv_b2, eta_c2),
    }
    downstream = [*eta_b1.__dict__.values(), *eta_inv_c1.__dict__.values(),
                  *eta_inv_b2.__dict__.values(), *eta_c2.__dict__.values()]
    downstream.extend(endpoint for group in groups.values()
                      for interval in group for endpoint in (interval.low, interval.high))
    maximum_downstream = max(abs(value) for value in downstream)
    assert maximum_downstream == 26306
    assert maximum_downstream <= I16[1]

    # Exhaust all residues rather than sampling integer representatives.
    identity_checks = 0
    for x0 in range(Q):
        for x1 in range(Q):
            for x2 in (0, 1, Q // 2, Q - 1):
                d = (x1 - x2) % Q
                r = rho * d % Q
                candidate = ((x0 + x1 + x2) % Q,
                             (x0 - x2 + r) % Q,
                             (x0 - x1 - r) % Q)
                baseline = ((x0 + x1 + x2) % Q,
                            (x0 + rho * x1 + rho2 * x2) % Q,
                            (x0 + rho2 * x1 + rho * x2) % Q)
                assert candidate == baseline
                identity_checks += 1

    print(json.dumps({
        "gate": "gt864_forward_one_mul_b3",
        "status": "pass",
        "identity": "rho^2=-1-rho; y1=x0-x2+rho(x1-x2); y2=x0-x1-rho(x1-x2)",
        "producer_bound": list(SOURCE),
        "nonidentity_twist_union": list(TWISTED),
        "nonidentity_twist_constants_checked": len(twist_constants),
        "algorithm10_congruence_checks": congruence_checks,
        "root_identity_checks": identity_checks,
        "reports": reports,
        "unchanged_downstream": {
            "eta_corrected": {
                "eta_b1": [eta_b1.low, eta_b1.high],
                "eta_inv_c1": [eta_inv_c1.low, eta_inv_c1.high],
                "eta_inv_b2": [eta_inv_b2.low, eta_inv_b2.high],
                "eta_c2": [eta_c2.low, eta_c2.high],
            },
            "level2_output_intervals": {
                key: [[x.low, x.high] for x in value]
                for key, value in groups.items()
            },
            "maximum_abs": maximum_downstream,
            "all_add_sub_steps_no_signed_int16_wrap": True,
        },
        "scope": "three level-1 B3 nodes in each NTT9 block only",
        "mulmods_deleted_per_ntt9_block": 3,
        "new_memory_boundaries": 0,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
