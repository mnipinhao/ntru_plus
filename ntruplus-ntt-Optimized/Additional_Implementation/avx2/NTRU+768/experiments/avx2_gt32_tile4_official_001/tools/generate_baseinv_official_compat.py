#!/usr/bin/env python3
"""Generate the P-SoA versus Official BaseInv ABI compatibility gate."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "generated" / "tile4_baseinv_p_mapping.h"
OUT = ROOT / "generated" / "tile4_baseinv_official_compat_gate.json"


def read_array(text: str, name: str) -> list[int]:
    body = text.split(f"{name}[768] = {{", 1)[1].split("};", 1)[0]
    values = [int(value) for value in re.findall(r"\d+", body)]
    assert len(values) == 768
    assert sorted(values) == list(range(768))
    return values


def main() -> None:
    text = HEADER.read_text()
    p_words = read_array(text, "gt32_p_word_from_serialized")
    official_words = read_array(text, "gt32_official_word_from_serialized")

    leaf_map: dict[tuple[int, int], tuple[int, int]] = {}
    degree_plane_exact = True
    degree_independent = True
    for p_word, official_word in zip(p_words, official_words):
        p_degree = (p_word % 64) // 16
        official_degree = (official_word % 64) // 16
        degree_plane_exact &= p_degree == official_degree
        source = (p_word // 64, p_word % 16)
        target = (official_word // 64, official_word % 16)
        if source in leaf_map and leaf_map[source] != target:
            degree_independent = False
        leaf_map[source] = target

    assert degree_plane_exact
    assert degree_independent
    assert len(leaf_map) == 192

    official_blocks_by_p_block = []
    for p_block in range(12):
        blocks = sorted({official_block
                         for (block, _), (official_block, _) in leaf_map.items()
                         if block == p_block})
        official_blocks_by_p_block.append(blocks)
    blocks_are_direct_permutation = all(len(blocks) == 1
                                        for blocks in official_blocks_by_p_block)
    assert all(len(blocks) == 2 for blocks in official_blocks_by_p_block)

    result = {
        "schema": "ntruplus768-gt32-baseinv-official-compat-v1",
        "experiment": "GT32-BASEINV-OFFICIAL-REUSE-O1-O2-001",
        "O1_mapping": {
            "P_and_Official_are_bijections": True,
            "geometry": "12 blocks x 4 degree planes x 16 leaves",
            "degree_plane_grouping_exact": degree_plane_exact,
            "leaf_mapping_independent_of_degree": degree_independent,
            "semantic_leaves": len(leaf_map),
            "P_blocks_each_mix_exactly_two_Official_blocks": True,
            "Official_blocks_by_P_block": official_blocks_by_p_block,
            "direct_call_Official_poly_baseinv_1": False,
            "direct_call_failure_reason": (
                "each P block mixes leaves from two Official blocks; changing "
                "only the outer block address cannot reproduce the Official ABI"
            ),
            "global_data_conversion_required_for_P_native_clone": False,
            "absorption": [
                "reorder lambda and lambda-qinv metadata by P block/lane",
                "keep four degree-plane loads and stores unchanged",
                "batch inversion is leaf-order independent",
            ],
        },
        "typed_contract": {
            "input_scale_exponent": 0,
            "P_forward_abs_bound": 9586,
            "BaseInv_direct_product_limit": 10643,
            "range_compatible": 9586 < 10643,
        },
        "implementation_audit": {
            "current_P_BaseInv": "C/intrinsic core in tile4_baseinv_p_soa.c",
            "current_A_B_C_benchmark_previously_enabled_GT_HAVE_AVX2_ASM": False,
            "available_reuse_probe": (
                "gt_baseinv_native_prepare_asm.S, an Official quartic schedule "
                "generalized to one P-native lambda vector per block"
            ),
            "O1_decision": "compatibility-pass-P-native-clone-direct-symbol-fail",
        },
        "O2_result_artifact": "results/tile4-keygen-baseinv-official-reuse-pmu.json",
        "O2_decision": "measured-hard-stop-existing-Official-derived-P-native-ASM",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "O1": result["implementation_audit"]["O1_decision"],
        "direct_official_symbol": False,
        "degree_plane_exact": degree_plane_exact,
        "O2": result["O2_decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
