#!/usr/bin/env python3
"""Coverage-corrected gate for alternative GT32 AVX2 physical bases.

This gate does not optimize a terminal adapter.  It first records which part
of the proposed global-basis space was already implemented by
GT32-GLOBAL-PHYSICAL-LAYOUT-001, then isolates the genuinely open mechanisms:
lane-local Stockham/Pease scheduling, a hybrid-native BaseMul, and plane-major
radix-4.  Q24 is deliberately outside this phase.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
NTRU = EXPERIMENT.parent.parent
LEGACY = EXPERIMENT.parent / "avx2_gt32_tile4_official_001"

AXES = ("p0", "p1", "k0", "k1", "k2", "k3", "k4")
PHYSICAL = (
    "lane_bit0", "lane_bit1", "lane_bit2", "lane_bit3",
    "ymm_bit0", "ymm_bit1", "ymm_bit2",
)
FORWARD_AXES = ("k4", "k3", "k2", "k1", "k0")

# Tuple positions are physical positions low-to-high: four word-lane bits,
# followed by three YMM-selector bits.  Register-selector order is metadata.
BASES = {
    "current_like": ("p0", "p1", "k0", "k1", "k2", "k3", "k4"),
    "hybrid_one_plane_bit": ("p0", "k0", "k1", "k2", "p1", "k3", "k4"),
    "full_plane_major": ("k0", "k1", "k2", "k3", "k4", "p0", "p1"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_bijection(layout: tuple[str, ...]) -> list[int]:
    result = []
    for semantic in range(128):
        bits = {axis: (semantic >> index) & 1
                for index, axis in enumerate(AXES)}
        result.append(sum(bits[axis] << position
                          for position, axis in enumerate(layout)))
    assert sorted(result) == list(range(128))
    return result


def basis_record(layout: tuple[str, ...]) -> dict[str, object]:
    stages = []
    for number, axis in enumerate(FORWARD_AXES, 1):
        position = layout.index(axis)
        stages.append({
            "stage": number,
            "logical_axis": axis,
            "physical_position": PHYSICAL[position],
            "shape": "cross_YMM" if position >= 4 else "lane_local",
        })
    return {
        "layout_low_to_high": list(layout),
        "lane_axes": list(layout[:4]),
        "YMM_selector_axes": list(layout[4:]),
        "exact_128_word_bijection_sha256": hashlib.sha256(
            json.dumps(exact_bijection(layout), separators=(",", ":")).encode()
        ).hexdigest(),
        "forward_stage_placement": stages,
        "cross_YMM_stages": sum(stage["shape"] == "cross_YMM"
                                for stage in stages),
        "lane_local_stages": sum(stage["shape"] == "lane_local"
                                 for stage in stages),
        "quartic_plane_location": {
            axis: PHYSICAL[layout.index(axis)] for axis in ("p0", "p1")
        },
        "plane_major_B3_loads_are_native": all(
            layout.index(axis) >= 4 for axis in ("p0", "p1")
        ),
    }


def label_values(text: str, label: str) -> list[int]:
    match = re.search(
        rf"^{re.escape(label)}:\s*(.*?)(?=^\s*\.section|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing {label}")
    values = [int(value) for value in re.findall(
        r"\.short\s+([^\n]+)", match.group(1)
    ) for value in re.findall(r"-?\d+", value)]
    assert len(values) == 64, (label, len(values))
    return values


def dormant_twiddle_oracle(invntt: Path) -> dict[str, object]:
    text = invntt.read_text()
    stages = {}
    total_vectors = 0
    total_unique = 0
    for stage in range(2, 6):
        stage_record = {}
        for kind in ("qinv", "factor"):
            label = f".Lgp_forward_s{stage}_{kind}"
            values = label_values(text, label)
            vectors = [values[offset:offset + 16]
                       for offset in range(0, 64, 16)]
            unique = []
            for vector in vectors:
                if vector not in unique:
                    unique.append(vector)
            assert len(unique) == 2
            stage_record[kind] = {
                "vectors_in_table": 4,
                "unique_vectors": len(unique),
                "duplicate_map": [unique.index(vector) for vector in vectors],
                "unique_values": unique,
            }
            total_vectors += len(vectors)
            total_unique += len(unique)
        stages[f"S{stage}"] = stage_record
    assert total_vectors == 32 and total_unique == 16
    return {
        "source": "invntt.s dormant gp_forward_s2..s5 tables",
        "stages": stages,
        "current_memory_operand_equivalent_vectors_per_tile": total_vectors,
        "plane_major_register_reuse_vector_loads_per_tile": total_unique,
        "potential_vector_load_reduction_per_tile": total_vectors - total_unique,
        "claim_scope": "constant delivery only; not yet a cycle or full-stage proof",
    }


def old_gate_audit(generator: Path, result_path: Path) -> dict[str, object]:
    text = generator.read_text()
    result = json.loads(result_path.read_text())
    assert "len(states) == 5040" in text
    assert '"pair-packed-lane-local-butterfly"' in text
    assert '"kernel": "current-private-SoA-B3"' in text
    assert "memory_uops=0" in text
    assert result["assembly_eligible"] is True
    serious_path = LEGACY / "results" / "tile4-global-physical-whole-serious.json"
    serious = json.loads(serious_path.read_text())
    measurements = {}
    for placement, record in serious["placements"].items():
        summary = record["launch_median_summary"]
        measurements[placement] = {
            "TSC_delta": summary["tsc"]["median"],
            "core_cycle_delta": summary["core_cycles"]["median"],
            "instruction_delta": summary["instructions"]["median"],
        }
    return {
        "already_covered": {
            "all_5040_bit_permutation_states_between_radix2_stages": True,
            "reverse_inverse_progressive_forward": True,
            "zero_repair_current_private_SoA_B3": True,
            "explicit_progressive_inverse": True,
            "exact_matrix_proof_and_executable_assembly": True,
            "100k_serious_private_polymul": measurements,
        },
        "not_covered_by_old_cost_model": {
            "persistent_full_plane_in_YMM_Stockham": True,
            "fused_stage_transition_instead_of_fixed_16_shuffle_lane_stage": True,
            "twiddle_constant_load_uops_and_register_reuse": True,
            "hybrid_native_BaseMul_arithmetic": True,
            "radix4_N32_equals_2x4x4": True,
        },
        "important_correction": (
            "reverse-Inverse progressive Forward is not new: it was generated, "
            "implemented, and serious-qualified as a private polynomial primitive"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    invntt = NTRU / "invntt.s"
    basemul = NTRU / "basemul.s"
    ntt = NTRU / "ntt.s"
    old_generator = LEGACY / "tools" / "generate_gt32_global_physical_layout_gate.py"
    old_result = LEGACY / "generated" / "tile4_global_physical_layout_gate.json"
    old_serious = LEGACY / "results" / "tile4-global-physical-whole-serious.json"

    basis = {name: basis_record(layout) for name, layout in BASES.items()}
    assert basis["current_like"]["cross_YMM_stages"] == 3
    assert basis["hybrid_one_plane_bit"]["cross_YMM_stages"] == 2
    assert basis["full_plane_major"]["cross_YMM_stages"] == 1
    assert basis["full_plane_major"]["plane_major_B3_loads_are_native"]

    result = {
        "schema": "ntruplus768-gt32-plane-major-n32-architecture-006-v1",
        "experiment": "GT32-PLANE-MAJOR-N32-ARCHITECTURE-006",
        "production_modified": False,
        "question": (
            "Can a basis chosen before S1 lower Forward+BaseMul+Inverse cost "
            "through lane-local Stockham, hybrid-native arithmetic, or radix-4?"
        ),
        "sources": {
            name: {"path": str(path.resolve()), "sha256": sha256(path)}
            for name, path in {
                "ntt": ntt,
                "invntt": invntt,
                "basemul": basemul,
                "old_global_generator": old_generator,
                "old_global_result": old_result,
                "old_global_serious": old_serious,
            }.items()
        },
        "coordinate_model": {
            "semantic_axes": list(AXES),
            "physical_positions": list(PHYSICAL),
            "words_per_tile": 128,
            "YMM_per_tile": 8,
            "basis_bijections_exact": True,
            "basis": basis,
        },
        "twiddle_oracle": dormant_twiddle_oracle(invntt),
        "prior_coverage_audit": old_gate_audit(old_generator, old_result),
        "transform_island_budget": {
            "current_packed_plane_routing_per_tile": {
                "forward_terminal": 24,
                "inverse_ingress": 24,
                "total": 48,
            },
            "six_tile_total_per_polymul": 288,
            "interpretation": (
                "available architecture budget, not an assumed saving; the old "
                "progressive implementation already captured part of it"
            ),
        },
        "open_families": {
            "F0_reverse_inverse_progressive": {
                "status": "already_serious_qualified_do_not_duplicate",
            },
            "F1_full_plane_stockham": {
                "status": "active_next",
                "required_proof": (
                    "exact executable q3..q0 lane-partner circuits whose output "
                    "layout is the next stage input, including twiddle registers"
                ),
            },
            "F2_hybrid_native": {
                "status": "active_after_shared_lane_stage_library",
                "required_proof": (
                    "hybrid-native quartic BM and inverse without conversion to M"
                ),
            },
            "F3_plane_major_radix4": {
                "status": "active_after_radix2_lane_oracle",
                "required_proof": (
                    "exact N32=2x4x4 matrix and fewer shuffle/dependency layers"
                ),
            },
        },
        "next_executable_gate": {
            "name": "GT32-PLANE-N16-STOCKHAM-STAGES-007",
            "scope": "one plane-major tile, q4 cross-YMM plus q3..q0 lane stages",
            "compare": [
                "persistent plane-major radix-2 Stockham",
                "old progressive selected circuit",
                "current pair-packed local-stage control",
            ],
            "must_measure": [
                "retired instructions", "estimated and PMU core cycles",
                "shuffle uops", "constant loads", "peak YMM", "critical depth",
            ],
            "hard_requirements": [
                "exact 128-basis matrix equality",
                "no spill",
                "peak YMM <= 16 including q/twiddle/temp",
                "no new Montgomery chain or checkpoint",
                "no canonical-layout repair between lane stages",
            ],
        },
        "decision": "continue_to_exact_lane_stage_synthesis_not_whole_ASM",
        "Q24_policy": "deferred_until_transform_domain_architecture_is_executable",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
