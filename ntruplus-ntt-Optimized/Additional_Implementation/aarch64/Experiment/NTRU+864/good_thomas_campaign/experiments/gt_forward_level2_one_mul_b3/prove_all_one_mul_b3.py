#!/usr/bin/env python3
"""Machine-check M5R-D level-2 one-product B3 ranges and residues."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROOF = ROOT.parent / "gt_forward_one_mul_b3/prove_one_mul_b3.py"
SPEC = importlib.util.spec_from_file_location("m5rc_proof", PROOF)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules["m5rc_proof"] = M
SPEC.loader.exec_module(M)


def interval(low: int, high: int):
    return M.Interval(low, high)


def main() -> None:
    rho = M.RHO[0] % M.Q
    rho2 = M.RHO2[0] % M.Q
    assert rho2 == rho * rho % M.Q == (-1 - rho) % M.Q

    # Exact accepted M5R-C level-1 bounds from its synchronized proof.
    a = (interval(-13232, 13232), interval(-12833, 12833), interval(-12833, 12833))
    b = (interval(-6537, 6537), interval(-6138, 6138), interval(-6138, 6138))
    c = b
    eta_b1 = M.mul(b[1], M.ETA)
    eta_inv_c1 = M.mul(c[1], M.ETA_INV)
    eta_inv_b2 = M.mul(b[2], M.ETA_INV)
    eta_c2 = M.mul(c[2], M.ETA)
    inputs = {
        "G0": (a[0], b[0], c[0]),
        "G1": (a[1], eta_b1, eta_inv_c1),
        "G2": (a[2], eta_inv_b2, eta_c2),
    }

    reports = {}
    global_max = 0
    widest_diff = 0
    for name, values in inputs.items():
        nodes = M.one_mul_b3(*values)
        baseline = M.baseline_b3(*values)
        candidate = (nodes["y0"], nodes["y1"], nodes["y2"])
        maximum = max(node.magnitude for node in nodes.values())
        global_max = max(global_max, maximum)
        widest_diff = max(widest_diff, nodes["diff"].magnitude)
        assert all(-32768 <= node.low <= node.high <= 32767
                   for node in nodes.values())
        reports[name] = {
            "inputs": [[x.low, x.high] for x in values],
            "nodes": {key: [value.low, value.high]
                      for key, value in nodes.items()},
            "baseline_output_intervals": [[x.low, x.high] for x in baseline],
            "candidate_output_intervals": [[x.low, x.high] for x in candidate],
            "maximum_abs": maximum,
        }
    assert global_max == 26306
    assert widest_diff == 13074

    congruence_checks = 0
    for value in range(-widest_diff, widest_diff + 1):
        assert (M.fixed(value, M.RHO) - value * M.RHO[0]) % M.Q == 0
        congruence_checks += 1

    # Exhaust the finite field for the shared difference variable and public
    # basis representatives.  This checks both output formulas, not intervals.
    identity_checks = 0
    for x0 in range(M.Q):
        for d in range(M.Q):
            for x2 in (0, 1, M.Q // 2, M.Q - 1):
                x1 = (d + x2) % M.Q
                r = rho * d % M.Q
                new = ((x0 + x1 + x2) % M.Q,
                       (x0 - x2 + r) % M.Q,
                       (x0 - x1 - r) % M.Q)
                old = ((x0 + x1 + x2) % M.Q,
                       (x0 + rho * x1 + rho2 * x2) % M.Q,
                       (x0 + rho2 * x1 + rho * x2) % M.Q)
                assert new == old
                identity_checks += 1

    print(json.dumps({
        "gate": "gt864_forward_level2_one_mul_b3",
        "status": "pass",
        "identity": "rho^2=-1-rho",
        "reports": reports,
        "widest_level2_difference": widest_diff,
        "maximum_abs_all_new_level2_nodes": global_max,
        "algorithm10_congruence_checks": congruence_checks,
        "field_identity_checks": identity_checks,
        "additional_mulmods_deleted_per_ntt9_block": 3,
        "new_memory_boundaries": 0,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
