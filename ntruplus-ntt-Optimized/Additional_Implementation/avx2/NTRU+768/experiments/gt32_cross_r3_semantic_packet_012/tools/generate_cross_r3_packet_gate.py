#!/usr/bin/env python3
"""Exact first gate for 128-bit cross-R3 semantic packets.

The candidate pairs the two Top objects in the low/high halves while keeping
the R3 row fixed.  This generator proves the packet mapping symbolically,
audits the selected production routing macros, constructs the two natural
two-layer producer/inverse networks, and checks the complete NTT32 closure
condition.  It emits no assembly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
ROOT = EXPERIMENTS.parent
S11 = EXPERIMENTS / "gt32_avx2_packing_superspace_011"
NTT = ROOT / "ntt.s"
NTT_M = ROOT / "ntt_m.s"
INV = ROOT / "invntt.s"
MAPPING = (EXPERIMENTS / "avx2_gt32_tile4_official_001/generated/"
           "gt32_3x32_mapping.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def macro_body(text: str, name: str) -> list[str]:
    match = re.search(rf"^\s*\.macro\s+{re.escape(name)}[^\n]*\n(.*?)^\s*\.endm\s*$",
                      text, re.MULTILINE | re.DOTALL)
    assert match, name
    return [line.strip() for line in match.group(1).splitlines()
            if line.strip() and not line.lstrip().startswith("/*")]


def mnemonic_counts(lines: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in lines:
        if line.startswith((".", "#")):
            continue
        mnemonic = line.split()[0]
        counts[mnemonic] = counts.get(mnemonic, 0) + 1
    return counts


def source_audit() -> dict:
    ntt = NTT.read_text()
    inv = INV.read_text()
    blend = mnemonic_counts(macro_body(ntt, "GT_BLEND3"))
    blend_out = mnemonic_counts(macro_body(inv, "BLEND3_OUT"))
    assert blend == {"vpblendd": 6}
    assert blend_out == {"vpblendd": 6}

    frontend = re.search(
        r"^ntruplus768_ntt_frontend_avx2:(.*?)^\.size ntruplus768_ntt_frontend_avx2",
        ntt, re.MULTILINE | re.DOTALL).group(1)
    iterations = len(re.findall(r"^\s*FRONTEND_WIDE_ITER_[012]\s+", frontend,
                                re.MULTILINE))
    assert iterations == 8
    frontend_blends_per_iteration = 2 * blend["vpblendd"]

    tail8 = macro_body(inv, "TAIL_GROUP_T8")
    assert sum(line.startswith("BLEND3_OUT ") for line in tail8) == 2
    tail = re.search(
        r"^ntruplus768_invntt_tail_avx2:(.*?)^\.size ntruplus768_invntt_tail_avx2",
        inv, re.MULTILINE | re.DOTALL).group(1)
    assert "RUN_8_T8" in tail
    groups = 8
    inverse_blends_per_group = 2 * blend_out["vpblendd"]

    return {
        "sources": [artifact(NTT), artifact(NTT_M), artifact(INV)],
        "GT_BLEND3": {
            "instructions_per_invocation": blend,
            "invocations_per_Forward_iteration": 2,
            "iterations": iterations,
            "vpblendd_per_Forward": frontend_blends_per_iteration * iterations,
        },
        "BLEND3_OUT": {
            "instructions_per_invocation": blend_out,
            "invocations_per_inverse_group": 2,
            "groups": groups,
            "vpblendd_per_Inverse": inverse_blends_per_group * groups,
        },
        "whole_2F_plus_I_R3_routing": {
            "vpblendd": 2 * frontend_blends_per_iteration * iterations
                         + inverse_blends_per_group * groups,
        },
    }


Vector = tuple[str, str, str, str]


def source(name: str, top: str) -> Vector:
    return tuple(f"{top}.{name}.q{q}" for q in range(4))  # type: ignore[return-value]


def gt_blend(x: Vector, y: Vector, z: Vector) -> tuple[Vector, Vector, Vector]:
    return (
        (x[0], y[1], z[2], x[3]),
        (z[0], x[1], y[2], z[3]),
        (y[0], z[1], x[2], y[3]),
    )


def pair_half(a: Vector, b: Vector, half: int) -> Vector:
    assert half in (0, 1)
    offset = 2 * half
    return (a[offset], a[offset + 1], b[offset], b[offset + 1])


def split_packet(low: Vector, high: Vector) -> tuple[Vector, Vector]:
    """Inverse of pair_half for one routed semantic row."""
    a = (low[0], low[1], high[0], high[1])
    b = (low[2], low[3], high[2], high[3])
    return a, b


def blend_odd(base: Vector, odd: Vector) -> Vector:
    return (base[0], odd[1], base[2], odd[3])


def cross_targets(a_rows: tuple[Vector, Vector, Vector],
                  b_rows: tuple[Vector, Vector, Vector]) -> dict[str, Vector]:
    result = {}
    for row in range(3):
        result[f"P{row}L"] = pair_half(a_rows[row], b_rows[row], 0)
        result[f"P{row}H"] = pair_half(a_rows[row], b_rows[row], 1)
    return result


def producer_synthesis() -> dict:
    a = {name: source(name, "A") for name in "xyz"}
    b = {name: source(name, "B") for name in "xyz"}
    routed_a = gt_blend(a["x"], a["y"], a["z"])
    routed_b = gt_blend(b["x"], b["y"], b["z"])
    targets = cross_targets(routed_a, routed_b)

    prepacked = {}
    operations = []
    for name in "xyz":
        for half, suffix in ((0, "L"), (1, "H")):
            key = f"{name.upper()}{suffix}"
            prepacked[key] = pair_half(a[name], b[name], half)
            operations.append({
                "instruction": "vperm2i128",
                "output": key,
                "inputs": [f"A.{name}", f"B.{name}"],
                "semantic": f"pair Top A/B {suffix} halves",
            })

    constructed = {
        "P0L": blend_odd(prepacked["XL"], prepacked["YL"]),
        "P0H": blend_odd(prepacked["ZH"], prepacked["XH"]),
        "P1L": blend_odd(prepacked["ZL"], prepacked["XL"]),
        "P1H": blend_odd(prepacked["YH"], prepacked["ZH"]),
        "P2L": blend_odd(prepacked["YL"], prepacked["ZL"]),
        "P2H": blend_odd(prepacked["XH"], prepacked["YH"]),
    }
    for output, value in constructed.items():
        operations.append({
            "instruction": "vpblendd_or_vshufps",
            "output": output,
            "semantic": "select odd qword from second prepacked source",
        })
        assert value == targets[output]

    route_first_cost = {
        "GT_BLEND3_vpblendd": 12,
        "pair_routed_halves_vperm2i128": 6,
        "total": 18,
    }
    return {
        "target_packets": targets,
        "source_pair_first_exact": True,
        "source_pair_first_operations": operations,
        "source_pair_first_cost": {
            "vperm2i128": 6,
            "qword_mix_vpblendd_or_vshufps": 6,
            "total_routing_instructions": 12,
        },
        "route_first_control": route_first_cost,
        "current_GT_BLEND3_cost": {
            "vpblendd": 12,
            "total_routing_instructions": 12,
        },
        "operation_class_deleted": False,
        "global_minimum_claimed": False,
        "scope_of_exactness": (
            "exact symbolic equality and complete enumeration of the two natural "
            "two-layer normal forms: pair-A/B-halves first or route-R3 first"
        ),
    }


def inverse_synthesis() -> dict:
    # Inputs are the pre-BLEND3 R3 rows, already paired by Top object and half.
    a = {name: source(name, "A") for name in "xyz"}
    b = {name: source(name, "B") for name in "xyz"}
    inputs = {
        f"{name.upper()}{suffix}": pair_half(a[name], b[name], half)
        for name in "xyz" for half, suffix in ((0, "L"), (1, "H"))
    }
    routed_packets = {
        "P0L": blend_odd(inputs["XL"], inputs["YL"]),
        "P0H": blend_odd(inputs["ZH"], inputs["XH"]),
        "P1L": blend_odd(inputs["ZL"], inputs["XL"]),
        "P1H": blend_odd(inputs["YH"], inputs["ZH"]),
        "P2L": blend_odd(inputs["YL"], inputs["ZL"]),
        "P2H": blend_odd(inputs["XH"], inputs["YH"]),
    }
    expected_a = gt_blend(a["x"], a["y"], a["z"])
    expected_b = gt_blend(b["x"], b["y"], b["z"])
    outputs_a = []
    outputs_b = []
    for row in range(3):
        out_a, out_b = split_packet(routed_packets[f"P{row}L"],
                                    routed_packets[f"P{row}H"])
        outputs_a.append(out_a)
        outputs_b.append(out_b)
    assert tuple(outputs_a) == expected_a
    assert tuple(outputs_b) == expected_b
    return {
        "exact_symbolic_equality": True,
        "qword_route_packets": 6,
        "qword_mix_vpblendd_or_vshufps": 6,
        "split_Top_A_B_vperm2i128": 6,
        "total_routing_instructions": 12,
        "current_BLEND3_OUT_routing_instructions": 12,
        "operation_class_deleted": False,
    }


def ntt32_connectivity() -> dict:
    """Prove that separating the original half/leaf bit omits an R2 layer."""
    mapping = json.loads(MAPPING.read_text())
    records = mapping["records"]
    assert len(records) == 96
    for record in records:
        q = record["current_physical_Q"]
        assert record["branch0_tile4_qword"] == q % 4
        assert record["branch1_tile4_qword"] == q % 4
    # A TILE4 qword holds the four quartic degrees.  The 128-bit half holds
    # qwords 0/1 or 2/3, hence its selector is physical Q bit 1.
    missing_bit = 1

    def closure(active_bits: tuple[int, ...]) -> list[set[int]]:
        groups = [{index} for index in range(32)]
        for bit in active_bits:
            updated = []
            for index in range(32):
                partner = index ^ (1 << bit)
                updated.append(groups[index] | groups[partner])
            groups = updated
        return groups

    four = closure(tuple(bit for bit in range(5) if bit != missing_bit))
    five = closure(tuple(range(5)))
    assert all(len(group) == 16 for group in four)
    assert all(len(group) == 32 for group in five)
    return {
        "exact_connectivity": {
            "mapping_artifact": artifact(MAPPING),
            "tile4_qword_formula": "physical_Q mod 4",
            "original_128bit_half_selector": "physical_Q bit 1",
            "missing_NTT32_bit": missing_bit,
            "without_original_half_leaf_bit": 16,
            "with_all_five_NTT32_bits": 32,
            "separate_L_H_streams_are_complete_NTT32": False,
        },
        "state_capacity_for_one_Top_pair": {
            "L_stream_YMM": 8,
            "H_stream_YMM": 8,
            "data_YMM_at_required_join": 16,
            "q_register": 1,
            "minimum_Montgomery_temporary": 1,
            "minimum_live_YMM": 18,
            "architectural_YMM": 16,
        },
        "consequence": (
            "the missing R2 layer requires L/H interaction; a full resident join "
            "does not fit, so an extra cut, replay, or a different packet evolution is mandatory"
        ),
        "simple_complete_consumer_status": "static_hard_stop",
    }


def boundary_accounting() -> dict:
    per_boundary = {"YMM_stores": 48, "YMM_loads": 48,
                    "memory_operations": 96, "bytes": 3072}
    return {
        "current_per_Forward_boundary": per_boundary,
        "cross_packet_per_Forward_boundary_before_R2_join_repair": per_boundary,
        "current_per_inverse_boundary": per_boundary,
        "cross_packet_per_inverse_boundary_before_R2_join_repair": per_boundary,
        "whole_2F_plus_I_current": {"memory_operations": 288, "bytes": 9216},
        "whole_2F_plus_I_candidate_floor": {"memory_operations": 288, "bytes": 9216},
        "packet_major_effect": (
            "turns six distant branch stores into contiguous iteration packets but "
            "does not reduce the 48 values, stores, or loads"
        ),
        "unpriced_nonnegative_debt": "the mandatory R2 L/H join cut or replay",
    }


def build() -> dict:
    current = source_audit()
    assert current["whole_2F_plus_I_R3_routing"]["vpblendd"] == 288
    producer = producer_synthesis()
    inverse = inverse_synthesis()
    connectivity = ntt32_connectivity()
    boundary = boundary_accounting()
    candidate_per_forward = 8 * producer["source_pair_first_cost"]["total_routing_instructions"]
    candidate_inverse = 8 * inverse["total_routing_instructions"]
    assert candidate_per_forward == 96
    assert candidate_inverse == 96
    return {
        "schema": "gt32-cross-r3-semantic-packet-v1",
        "experiment": "GT32-CROSS-R3-SEMANTIC-PACKET-012",
        "production_modified": False,
        "assembly_emitted": False,
        "parent": artifact(S11 / "generated/avx2_packing_superspace_gate.json"),
        "candidate_contract": {
            "lane_width": 16,
            "basis": "coefficient",
            "low128": "Top-A, fixed R3 row and original low half",
            "high128": "Top-B, same R3 row and original low half",
            "companion_packet": "same Top pair and row for the original high half",
            "memory_order": "iteration_then_R3_row_then_LH",
            "BaseMul_in_scope": False,
        },
        "current_source_audit": current,
        "producer_route_synthesis": producer,
        "complete_R2_consumer_gate": connectivity,
        "inverse_join_synthesis": inverse,
        "boundary_memory": boundary,
        "whole_route_accounting": {
            "current_2F_plus_I": {
                "vpblendd": 288,
                "total_R3_routing_instructions": 288,
            },
            "candidate_2F_plus_I_before_R2_join_debt": {
                "vperm2i128": 2 * 8 * 6 + 8 * 6,
                "vpblendd_or_vshufps": 2 * 8 * 6 + 8 * 6,
                "total_R3_routing_instructions": 288,
            },
            "routing_instruction_delta": 0,
            "R2_routing_floor": "unchanged arithmetic topology plus mandatory L/H join debt",
            "physical_operation_classes_eliminated": [],
            "branch_major_scatter_gather": "replaced by packet-major addresses but not fewer memory operations",
        },
        "decision": {
            "status": "static_hard_stop_cross_R3_128bit_half_packet_P0",
            "reason": (
                "the best exact natural producer and inverse networks each replace "
                "twelve qword blends with twelve mixed half/qword routing instructions; "
                "the 2F+I R3 routing total remains 288.  The separated L/H streams "
                "also omit one required NTT32 bit and need an 18-YMM join or another cut"
            ),
            "operation_class_deleted": False,
            "assembly_eligible": False,
            "closed_scope": (
                "coefficient-basis i16 packet ProwL=[A.low|B.low], "
                "ProwH=[A.high|B.high] with persistent Top-A/Top-B half ownership"
            ),
            "not_closed": [
                "cross-R3 qword semantic packets",
                "a half packet whose ownership evolves and deletes the missing-bit join",
                "BaseMul-selected pair packets",
                "streamed evaluation packets",
            ],
            "next": "GT32-CROSS-R3-QWORD-SEMANTIC-PACKET-013",
            "GT_Clean_modified": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
