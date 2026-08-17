#!/usr/bin/env python3
"""Exact/static gate for the N32-MR-S3LOCAL mixed-radix proposal."""

import json

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_mr_s3local_gate.json"
OMEGA3 = pow(gt.OMEGA96, 32, gt.Q)
OMEGA3_MONT = gt.centered(OMEGA3 * gt.R)


def dft3(values):
    x0, x1, x2 = values
    p = OMEGA3 * (x1 - x2)
    return [(x0 + x1 + x2) % gt.Q,
            (x0 - x2 + p) % gt.Q,
            (x0 - x1 - p) % gt.Q]


def binomial_ntt32(values, scale):
    """DFT32(diag((s^-3)^m)); output is current bit-reversed Q order."""
    rho = pow(scale, -3, gt.Q)
    data = [x % gt.Q for x in values]
    for stage in range(1, 6):
        distance = 32 >> stage
        for group in range(0, 32, 2 * distance):
            factor = (pow(gt.OMEGA32,
                          gt.forward_power(stage, group), gt.Q)
                      * pow(rho, distance, gt.Q)) % gt.Q
            for lane in range(distance):
                lo = group + lane
                hi = lo + distance
                product = factor * data[hi] % gt.Q
                low = data[lo]
                data[lo] = (low + product) % gt.Q
                data[hi] = (low - product) % gt.Q
    return data


def candidate(values, scale):
    rows = [binomial_ntt32([values[r + 3 * m] for m in range(32)], scale)
            for r in range(3)]
    out = {}
    for physical_q in range(32):
        k32 = gt.bitreverse(physical_q, 5)
        alpha = pow(scale, -1, gt.Q) * pow(gt.OMEGA96, k32, gt.Q) % gt.Q
        column = [rows[0][physical_q],
                  alpha * rows[1][physical_q] % gt.Q,
                  alpha * alpha * rows[2][physical_q] % gt.Q]
        transformed = dft3(column)
        for k3, value in enumerate(transformed):
            out[(k32 + 32 * k3) % 96] = value
    return out


def oracle(values, scale):
    out = {}
    for frequency in range(96):
        root = pow(scale, -1, gt.Q) * pow(
            gt.OMEGA96, frequency, gt.Q) % gt.Q
        out[frequency] = sum(
            value * pow(root, n, gt.Q) for n, value in enumerate(values)
        ) % gt.Q
    return out


def matrix_proof():
    branches = []
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        equal = True
        for basis in range(96):
            vector = [0] * 96
            vector[basis] = 1
            if candidate(vector, scale) != oracle(vector, scale):
                equal = False
                break
        branches.append({"branch": branch, "scale": scale,
                         "all_96_basis_vectors_equal": equal})
    return {
        "integer_coordinate": "n=r+3*m, r in [0,2], m in [0,31]",
        "twist_identity": "s^-n = s^-r * (s^-3)^m (no mod-96 carry)",
        "row_modulus": "z^32-s^-96",
        "rho": [pow(scale, -3, gt.Q) for scale in gt.BRANCH_SCALE],
        "stage_factor": "rho^distance * cyclic_twiddle",
        "radix3_alpha": "s^-1 * omega96^logical_k32",
        "output_frequency": "logical_k32 + 32*k3 mod 96",
        "branches": branches,
        "exact_leaf_matrix_equality": all(
            item["all_96_basis_vectors_equal"] for item in branches),
    }


def range_proof():
    records = []
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        rho = pow(scale, -3, gt.Q)
        bound = 2896
        stages = []
        for stage in range(1, 6):
            distance = 32 >> stage
            factors = []
            for group in range(0, 32, 2 * distance):
                normal = (pow(gt.OMEGA32,
                              gt.forward_power(stage, group), gt.Q)
                          * pow(rho, distance, gt.Q)) % gt.Q
                factors.append(gt.centered(normal * gt.R))
            product = gt.product_bound(bound, factors)
            stages.append({
                "stage": stage, "distance_m": distance,
                "distance_n": 3 * distance,
                "input_abs_bound": bound,
                "identity_factor_count": sum(
                    f == gt.centered(gt.R) for f in factors),
                "product_abs_bound": product,
                "output_abs_bound": bound + product,
            })
            bound += product
        alpha = []
        alpha2 = []
        for physical_q in range(32):
            k32 = gt.bitreverse(physical_q, 5)
            normal = pow(scale, -1, gt.Q) * pow(
                gt.OMEGA96, k32, gt.Q) % gt.Q
            alpha.append(gt.centered(normal * gt.R))
            alpha2.append(gt.centered(normal * normal * gt.R))
        b1 = gt.product_bound(bound, alpha)
        b2 = gt.product_bound(bound, alpha2)
        omega_product = gt.product_bound(b1 + b2, [OMEGA3_MONT])
        outputs = [bound + b1 + b2,
                   bound + b2 + omega_product,
                   bound + b1 + omega_product]
        records.append({
            "branch": branch, "scale": scale, "stages": stages,
            "pre_radix3_abs_bound": bound,
            "alpha_C1_abs_bound": b1,
            "alpha2_C2_abs_bound": b2,
            "omega_difference_abs_bound": omega_product,
            "output_abs_bounds": outputs,
            "max_output_abs_bound": max(outputs),
            "signed_int16_safe": max(outputs) < 32768,
            "within_current_B3_10788_contract": max(outputs) <= 10788,
        })
    return {
        "method": "exhaustive fixed-factor Montgomery bound plus triangle inequality",
        "raw_top_split_abs_bound": 2896,
        "branches": records,
        "all_signed_int16_safe": all(r["signed_int16_safe"] for r in records),
        "all_within_current_B3_contract": all(
            r["within_current_B3_10788_contract"] for r in records),
    }


def route_gate():
    sources = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
    targets = [[0, 3, 6, 9], [1, 4, 7, 10], [2, 5, 8, 11]]
    # A concrete qword-exact AVX2 route.  Each target uses one vpermq per
    # nontrivial source contribution and two qword-granularity vpblendd.
    plans = [
        {"target": targets[0], "selectors": {"A": [0, 3, 0, 0],
                                               "B": "raw",
                                               "C": [0, 0, 0, 1]},
         "source_by_lane": ["A", "A", "B", "C"],
         "permq": 2, "blends": 2},
        {"target": targets[1], "selectors": {"A": [1, 0, 0, 0],
                                               "B": [0, 0, 3, 0],
                                               "C": [0, 0, 0, 2]},
         "source_by_lane": ["A", "B", "B", "C"],
         "permq": 3, "blends": 2},
        {"target": targets[2], "selectors": {"A": [2, 0, 0, 0],
                                               "B": "raw",
                                               "C": [0, 0, 0, 3]},
         "source_by_lane": ["A", "B", "C", "C"],
         "permq": 2, "blends": 2},
    ]
    source_map = dict(zip(("A", "B", "C"), sources))
    for plan in plans:
        routed = []
        for lane, source_name in enumerate(plan["source_by_lane"]):
            selector = plan["selectors"][source_name]
            vector = source_map[source_name]
            routed.append(vector[lane] if selector == "raw"
                          else vector[selector[lane]])
        assert routed == plan["target"]
    assert sum(p["permq"] for p in plans) == 7
    assert sum(p["blends"] for p in plans) == 6
    return {
        "input_qwords": sources,
        "row_major_targets": targets,
        "concrete_route": plans,
        "instructions_per_12Q_block": 13,
        "blocks_full_forward": 2 * 8,
        "route_instructions_full_forward": 13 * 16,
        "current_GT_BLEND3_instructions_full_forward": 96,
        "delta_vs_deleted_GT_BLEND3": 13 * 16 - 96,
        "note": (
            "This is a verified constructive upper bound, not a global lower "
            "bound.  A joint S4/S5/radix3 network must beat it substantially."
        ),
    }


def main():
    proof = matrix_proof()
    ranges = range_proof()
    route = route_gate()
    assert proof["exact_leaf_matrix_equality"]
    assert ranges["all_signed_int16_safe"]
    chains = {
        "qualified_N5": {"twist": 48, "DFT3": 16, "NTT32": 96,
                          "total": 160},
        "N32_MR": {"binomial_NTT32": 120, "twiddled_radix3": 48,
                    "total": 168},
        "delta": 8,
        "instruction_floor_delta": 32,
    }
    result = {
        "schema": "ntruplus768-gt32-n32-mr-s3local-v1",
        "experiment": "GT32-N32-MR-S3LOCAL-001",
        "matrix_proof": proof,
        "range_proof": ranges,
        "Montgomery_chain_accounting": chains,
        "S3_to_S4_row_route": route,
        "stage123_physical_slabs": {
            "distance_n": [48, 24, 12],
            "whole_YMM_edges": True,
            "slab_vectors": ["j+12*t for t=0..7; each vector holds four qwords"],
            "same_cross_register_graph_as_current": True,
        },
        "assembly_emitted": False,
        "decision": "baseline-static-hard-stop-joint-suffix-remains-generator-only",
        "reasons": [
            "known arithmetic floor adds eight full-width Montgomery chains",
            "constructive 12-Q row route costs 208 shuffles versus 96 deleted GT blends",
            "conservative terminal bound 16271 exceeds current B3 input contract 10788",
            "three-row S4/S5 packing must cross blocks to keep Montgomery lanes full",
        ],
        "family_status": (
            "mixed-radix algebra is valid and genuinely new, but S3LOCAL baseline "
            "is not assembly-eligible; only a joint S4/S5/radix3/BM-entry search "
            "that removes the row route and absorbs range repair may continue"
        ),
        "reopen_assembly_only_if": [
            "joint suffix uses fewer than 96 routing shuffles over the full Forward",
            "BM/inverse typed ABI accepts the proved terminal range without a full checkpoint",
            "producer+BM+IDFT3 static saving exceeds the eight-chain arithmetic debt",
            "peak YMM <=16 with no spills",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
