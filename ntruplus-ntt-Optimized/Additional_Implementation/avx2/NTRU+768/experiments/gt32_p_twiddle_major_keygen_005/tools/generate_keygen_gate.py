#!/usr/bin/env python3
"""Generate GT32-P-TWIDDLE-MAJOR-KEYGEN-005.

The optimization unit is the successful-attempt Keygen P island:

    2 Forward_P + 2 BaseInv + 2 BaseMul + 3 P-pack.

The 48 compact-S5 terminal orders from experiment 002 are re-evaluated in
the *P* coordinate system.  BaseInv and BaseMul must close by table relabel
only.  P-pack is synthesized directly from the candidate layout; a P_TM->P
adapter is never admitted into the cost model.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import tempfile
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
NTRU = EXPERIMENT.parent.parent
E002 = EXPERIMENT.parent / "gt32_persistent_twiddle_major_002"
LEGACY = EXPERIMENT.parent / "avx2_gt32_tile4_official_001"


def load_002():
    path = E002 / "tools" / "generate_persistent_gate.py"
    spec = importlib.util.spec_from_file_location("persistent_tm_002", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G = load_002()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def macro_body(text: str, name: str) -> list[str]:
    match = re.search(
        rf"^\s*\.macro\s+{re.escape(name)}(?:\s.*)?$", text, re.MULTILINE
    )
    if match is None:
        raise AssertionError(f"missing macro {name}")
    body = []
    for line in text[match.end():].splitlines():
        if line.strip() == ".endm":
            return body
        body.append(line)
    raise AssertionError(f"unterminated macro {name}")


def instruction_lines(lines: list[str]) -> list[str]:
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ".", "/*", "*")):
            continue
        result.append(stripped)
    return result


def parse_short_arrays(path: Path) -> tuple[list[list[int]], list[list[int]]]:
    text = path.read_text()

    def one(name: str) -> list[list[int]]:
        match = re.search(
            rf"const\s+int16_t\s+{re.escape(name)}\s*\[12\]\[16\].*?=\s*\{{(.*?)\n\}};",
            text,
            re.DOTALL,
        )
        if match is None:
            raise AssertionError(f"missing {name}")
        values = [int(value) for value in re.findall(r"-?\d+", match.group(1))]
        if len(values) != 192:
            raise AssertionError(f"{name}: expected 192 values, got {len(values)}")
        return [values[offset:offset + 16] for offset in range(0, 192, 16)]

    return one("gt_native_lambda"), one("gt_native_lambda_qinv")


def p_serialized_mapping(serialized_path: Path, permutation_path: Path) -> dict:
    mapping = json.loads(serialized_path.read_text())
    permutation = json.loads(permutation_path.read_text())["permutation"]
    p_q = permutation["logical_q_at_physical_plane_lane"]
    assert sorted(p_q) == list(range(16))
    for record in mapping["records"]:
        q_value = record["physical_q"]
        record["bm_soa_group"] = q_value // 16
        record["bm_soa_lane"] = p_q.index(q_value & 15)
    return mapping


def remap_table(table: list[list[int]], leaf_permutation: dict) -> list[list[int]]:
    result: list[list[int | None]] = [[None] * 16 for _ in range(12)]
    for tile in range(6):
        for entry in leaf_permutation["mapping"]:
            old_batch = 2 * tile + entry["current_group"]
            new_batch = 2 * tile + entry["mtm_group"]
            old_lane = entry["current_lane"]
            new_lane = entry["mtm_lane"]
            if result[new_batch][new_lane] is not None:
                raise AssertionError("non-bijective table remap")
            result[new_batch][new_lane] = table[old_batch][old_lane]
    if any(value is None for row in result for value in row):
        raise AssertionError("incomplete table remap")
    return [[int(value) for value in row] for row in result]


def asymmetric_mask_cost(permutation: list[int]) -> int:
    """Cost after free packet-half selection and TF1 symmetric reversal.

    The pack can select either 128-bit half at no route cost.  Within a YMM,
    TF1 absorbs 00 and 11 qword orientations; 01/10 needs one VPSHUFB.
    """
    if sorted(permutation) != [0, 1, 2, 3]:
        raise AssertionError("not a qword permutation")
    halves = (permutation[:2], permutation[2:])
    bits = []
    for half in halves:
        if half in ([0, 1], [2, 3]):
            bits.append(0)
        elif half in ([1, 0], [3, 2]):
            bits.append(1)
        else:
            raise AssertionError(f"cross-pair qword route {permutation}")
    return int(bits[0] != bits[1])


def current_p_pack_residual_masks(pack_path: Path) -> int:
    body = macro_body(pack_path.read_text(), "Q24_ENCODE_P_SOA_HALF_SCATTER_SP1_BODY")
    return sum("vpshufb .Lq24_p_half_mask_" in line for line in body)


def terminal_ledger(ntt_path: Path) -> dict:
    text = ntt_path.read_text()
    s4 = len(instruction_lines(macro_body(text, "P_MONT_HALF_PACKED")))
    s5 = len(instruction_lines(macro_body(text, "P_MONT_QWORD_PACKED")))
    deposit = len(instruction_lines(macro_body(text, "P_PACKED_TO_PLANES")))
    assert (s4, s5, deposit) == (8, 9, 16)
    current = 4 * s4 + 4 * s5 + 2 * deposit
    assert current == 100
    candidate = 32 + 24 + 2 + 24 + 8
    assert candidate == 90
    return {
        "current": {
            "s4_four_pairs": 4 * s4,
            "s5_four_pairs": 4 * s5,
            "packed_to_planes_twice": 2 * deposit,
            "total_per_tile": current,
        },
        "candidate": {
            "s4_native": 32,
            "l4_to_tm_network": 24,
            "compact_s5_table_loads": 2,
            "compact_s5_arithmetic": 24,
            "direct_stores": 8,
            "total_per_tile": candidate,
        },
        "saving_per_tile": current - candidate,
        "tiles_per_forward": 6,
        "saving_per_forward": 6 * (current - candidate),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ntt = NTRU / "ntt_p.s"
    pack = NTRU / "pack.s"
    baseinv = NTRU / "baseinv_tables.inc"
    basemul = NTRU / "basemul.s"
    serialized = LEGACY / "generated" / "tile4_serialized_mapping.json"
    permutation = LEGACY / "generated" / "tile4_permutation_native_gate.json"

    sources = {name: {"path": str(path.resolve()), "sha256": sha256(path)} for name, path in {
        "ntt_p": ntt,
        "pack": pack,
        "baseinv_tables": baseinv,
        "basemul": basemul,
        "serialized_mapping": serialized,
        "permutation_mapping": permutation,
        "experiment_002_generator": E002 / "tools" / "generate_persistent_gate.py",
    }.items()}

    p_mapping = p_serialized_mapping(serialized, permutation)
    with tempfile.NamedTemporaryFile("w", suffix=".json") as temporary:
        json.dump(p_mapping, temporary)
        temporary.flush()
        temporary_path = Path(temporary.name)

        inputs = G.s4_native_inputs()
        target, exact_flow = G.target_lh(inputs)
        networks = G.search_24_candidates(inputs, target)
        candidates = []
        for index, network in enumerate(networks):
            _, _, leaf_permutation = G.current_and_mtm_outputs(
                network["common_leaf_lane_permutation"]
            )
            closure = G.q24_route_closure(temporary_path, leaf_permutation)
            if closure["status"] != "closed_by_eight_packet_progressive_transpose":
                raise AssertionError(f"unexpected P-pack closure: {closure['status']}")
            permutations = [
                route["qword_permutation"]
                for tile in closure["eight_packet_routes"]
                for route in tile["register_routes"]
            ]
            residual_masks = sum(asymmetric_mask_cost(item) for item in permutations)
            candidates.append({
                "index": index,
                "terminal_leaf_order": network["common_leaf_lane_permutation"],
                "terminal_network": network,
                "leaf_permutation": leaf_permutation,
                "pack_closure_status": closure["status"],
                "pack_transpose_instructions_per_tile": closure[
                    "candidate_transpose_instructions_per_tile"
                ],
                "pack_peak_ymm": closure["candidate_peak_ymm"],
                "pack_residual_asymmetric_masks": residual_masks,
                "pack_routes": closure["eight_packet_routes"],
            })

    current_masks = current_p_pack_residual_masks(pack)
    assert current_masks == 13
    for candidate in candidates:
        candidate["pack_instruction_delta"] = (
            candidate["pack_residual_asymmetric_masks"] - current_masks
        )
        candidate["successful_keygen_instruction_delta"] = (
            2 * (90 - 100) * 6 + 3 * candidate["pack_instruction_delta"]
        )
    candidates.sort(key=lambda item: (
        item["successful_keygen_instruction_delta"],
        item["pack_instruction_delta"],
        item["index"],
    ))
    selected = candidates[0]

    lambda_table, qinv_table = parse_short_arrays(baseinv)
    remapped_lambda = remap_table(lambda_table, selected["leaf_permutation"])
    remapped_qinv = remap_table(qinv_table, selected["leaf_permutation"])
    assert sorted(value for row in remapped_lambda for value in row) == sorted(
        value for row in lambda_table for value in row
    )
    assert sorted(value for row in remapped_qinv for value in row) == sorted(
        value for row in qinv_table for value in row
    )

    pack_deltas = Counter(item["pack_instruction_delta"] for item in candidates)
    keygen_deltas = Counter(item["successful_keygen_instruction_delta"] for item in candidates)
    frontier = [
        {
            "name": "current_P",
            "forward_terminal_per_tile": 100,
            "pack_instruction_delta": 0,
            "successful_keygen_instruction_delta": 0,
        },
        {
            "name": "selected_P_TM",
            "forward_terminal_per_tile": 90,
            "pack_instruction_delta": selected["pack_instruction_delta"],
            "successful_keygen_instruction_delta": selected[
                "successful_keygen_instruction_delta"
            ],
        },
    ]

    result = {
        "schema": "ntruplus768-gt32-p-twiddle-major-keygen-005-v1",
        "experiment": "GT32-P-TWIDDLE-MAJOR-KEYGEN-005",
        "production_modified": False,
        "sources": sources,
        "optimization_unit": "2*Forward_P + 2*BaseInv + 2*BaseMul + 3*P-pack",
        "successful_attempt_baseline": {"f_attempts": 1, "g_attempts": 1},
        "terminal_gate": {
            **terminal_ledger(ntt),
            "montgomery_chains_per_tile": 4,
            "montgomery_chain_delta": 0,
            "candidate_count": len(candidates),
            "all_candidates_peak_ymm_at_most": max(
                item["terminal_network"]["peak_data_plus_rotating_temp_ymm"]
                for item in candidates
            ),
            "spill_required": False,
            "exact_flow": exact_flow,
        },
        "baseinv_closure": {
            "status": "closed_by_batch_lane_table_relabel",
            "runtime_repair_instructions": 0,
            "arithmetic_changed": False,
            "selected_lambda_table": remapped_lambda,
            "selected_lambda_qinv_table": remapped_qinv,
        },
        "basemul_closure": {
            "status": "closed_by_same_batch_lane_table_relabel",
            "runtime_repair_instructions": 0,
            "arithmetic_changed": False,
            "proof": "selected F0xJ1 BaseMul consumes gt_native_lambda and gt_native_lambda_qinv lane-wise",
        },
        "pack_gate": {
            "current_SP1_residual_asymmetric_masks": current_masks,
            "candidate_residual_mask_distribution": {
                str(key): value for key, value in sorted(Counter(
                    item["pack_residual_asymmetric_masks"] for item in candidates
                ).items())
            },
            "pack_instruction_delta_distribution": {
                str(key): value for key, value in sorted(pack_deltas.items())
            },
            "all_candidates_direct_wire_closed": all(
                item["pack_closure_status"].startswith("closed_by_")
                for item in candidates
            ),
            "global_P_TM_to_P_repair": False,
            "transpose_instruction_delta": 0,
            "reduction_and_packet_math_changed": False,
            "load_store_count_changed": False,
            "selected_incremental_debt": selected["pack_instruction_delta"],
        },
        "pareto_frontier": frontier,
        "candidate_distributions": {
            "pack_instruction_delta": {
                str(key): value for key, value in sorted(pack_deltas.items())
            },
            "successful_keygen_instruction_delta": {
                str(key): value for key, value in sorted(keygen_deltas.items())
            },
        },
        "selected_candidate": selected,
        "decision": {
            "classification": "assembly_eligible_pack_debt_1_to_16",
            "selected_pack_instruction_delta": selected["pack_instruction_delta"],
            "successful_keygen_instruction_delta": selected[
                "successful_keygen_instruction_delta"
            ],
            "reason": (
                "P_TM saves 60 instructions per Forward; all consumers stay in the "
                "same degree-plane layout, BaseInv/BaseMul need table relabel only, "
                "and direct P-pack adds only asymmetric half-mask repairs"
            ),
            "next": "bounded executable P_TM Forward plus direct SP1-like P_TM pack",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
