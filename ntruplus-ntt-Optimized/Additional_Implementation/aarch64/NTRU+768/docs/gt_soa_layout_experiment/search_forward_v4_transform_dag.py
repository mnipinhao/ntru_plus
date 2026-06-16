#!/usr/bin/env python3
"""Gate 13 tagged-index transform-DAG search for rowpack Forward v4.

This is a model-only gate.  It emits YAML and Markdown artifacts, but it does
not generate assembly, does not run Slothy, and does not benchmark.  The
purpose is to turn the Gate 12 open research path into explicit transform-DAG
requirements before any Forward v4 ASM work is allowed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


OUTDIR = Path("docs/gt_soa_layout_experiment/forward_v4_transform_dag_search")

NTT32_SIZE = 32
VECTOR_LANES = 8
ROWPACK_PLANES = 8
BLOCKS_PER_NTT32 = 4
STAGE_DISTANCES = [16, 8, 4, 2, 1]
STAGE_NAMES = ["stage1", "stage2", "stage3", "stage4", "stage5"]

CURRENT_TAIL_PERMUTES_PER_BLOCK = 24
PERMUTES_PER_MIXING_LEVEL = 8
HORIZONTAL_PERMUTES_PER_STAGE = 16

CURRENT_SCATTER_CYCLES = 319.328
STORE_READY_CYCLES = 109.359
RECOVERABLE_WINDOW_CYCLES = CURRENT_SCATTER_CYCLES - STORE_READY_CYCLES
CYCLES_PER_PERMUTE = RECOVERABLE_WINDOW_CYCLES / (CURRENT_TAIL_PERMUTES_PER_BLOCK * BLOCKS_PER_NTT32)

MIN_CONTINUE_CYCLES_PER_NTT = 150.0
STRONG_CONTINUE_CYCLES_PER_NTT = 200.0


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def yaml_dump(data: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.append(yaml_dump(value, indent + 2))
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(yaml_dump(item, indent + 2))
            else:
                lines.append(f"{pad}- {yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{pad}{yaml_scalar(data)}"


def write_yml(path: Path, data: Any) -> None:
    path.write_text(yaml_dump(data) + "\n")


def butterfly_pairs(distance: int) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for base in range(0, NTT32_SIZE, 2 * distance):
        for offset in range(distance):
            pairs.append((base + offset, base + offset + distance))
    return pairs


def stage_for_index(stage_idx: int, inputs: list[str]) -> tuple[dict[str, Any], list[str]]:
    distance = STAGE_DISTANCES[stage_idx]
    stage_name = STAGE_NAMES[stage_idx]
    outputs = list(inputs)
    butterflies: list[dict[str, Any]] = []
    for pair_idx, (lo, hi) in enumerate(butterfly_pairs(distance)):
        twiddle = f"zeta_{stage_name}_{pair_idx}"
        lo_in = inputs[lo]
        hi_in = inputs[hi]
        lo_out = f"{stage_name}_y{lo}"
        hi_out = f"{stage_name}_y{hi}"
        butterflies.append(
            {
                "pair": [lo, hi],
                "inputs": [lo_in, hi_in],
                "twiddle": twiddle,
                "outputs": {
                    lo_out: f"{lo_in} + {twiddle}*{hi_in}",
                    hi_out: f"{lo_in} - {twiddle}*{hi_in}",
                },
                "layout_requirement_for_vectorwise_neon": (
                    "inputs must be in corresponding lanes of two vectors, "
                    "or already be lane-local within one vector"
                ),
            }
        )
        outputs[lo] = lo_out
        outputs[hi] = hi_out
    return (
        {
            "stage": stage_name,
            "distance": distance,
            "butterflies": butterflies,
            "stage_boundary": "stage12_scratch" if stage_idx == 1 else "stage345_or_final",
        },
        outputs,
    )


def reference_transform_dag() -> dict[str, Any]:
    inputs = [f"x{i}" for i in range(NTT32_SIZE)]
    stages: list[dict[str, Any]] = []
    live = inputs
    for stage_idx in range(len(STAGE_DISTANCES)):
        stage, live = stage_for_index(stage_idx, live)
        stages.append(stage)

    return {
        "gate": "Gate 13: reference tagged Forward NTT32 transform DAG",
        "status": "model_only",
        "tag_semantics": {
            "input": "x0..x31 are tagged scalar coefficients inside one Good-Thomas NTT32 row",
            "output": "y0..y31 are the current Forward NTT32 row outputs before rowpack output packing",
            "twiddle_labels": "symbolic zeta_stage_pair labels; numeric table remap is a proof obligation",
        },
        "current_stage_split": {
            "stage12": ["stage1", "stage2"],
            "stage345": ["stage3", "stage4", "stage5"],
            "stage12_boundary_layout": "k32-major scratch vectors",
            "stage345_property": "lane-preserving under the current vector-wise Neon topology",
        },
        "stages": stages,
        "final_live_tags": {f"y{i}": live[i] for i in range(NTT32_SIZE)},
    }


def rowpack_output_contract() -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for block in range(BLOCKS_PER_NTT32):
        k32_base = block * VECTOR_LANES
        blocks.append(
            {
                "block": block,
                "k32_range": f"{k32_base}..{k32_base + VECTOR_LANES - 1}",
                "target_planes": [
                    {
                        "plane": plane,
                        "semantic": "branch/lane plane over eight consecutive k32 values",
                        "lanes": [f"y{k32_base + lane}.h[{plane}]" for lane in range(VECTOR_LANES)],
                    }
                    for plane in range(ROWPACK_PLANES)
                ],
                "plain_vector_store_contract": "one store per target plane",
            }
        )
    return {
        "gate": "Gate 13: rowpack output tagged-index contract",
        "status": "model_only",
        "layout": "rowpack plane vectors",
        "blocks": blocks,
    }


def expected_cycles_saved(total_lane_mixing_permutes_per_block: int) -> float:
    saved_permutes = (CURRENT_TAIL_PERMUTES_PER_BLOCK - total_lane_mixing_permutes_per_block) * BLOCKS_PER_NTT32
    return round(saved_permutes * CYCLES_PER_PERMUTE, 3)


def classify_candidate(candidate: dict[str, Any]) -> str:
    saved = candidate["expected_cycles_saved_per_ntt"]
    if saved is None:
        return "unquantified_research"
    if candidate["proof_status"] != "proved":
        if saved >= MIN_CONTINUE_CYCLES_PER_NTT:
            return "blocked_pending_transform_proof"
        if saved > 0:
            return "below_gate_and_unproved"
    if saved >= STRONG_CONTINUE_CYCLES_PER_NTT:
        return "strong_continue"
    if saved >= MIN_CONTINUE_CYCLES_PER_NTT:
        return "continue"
    if saved > 0:
        return "below_continue_gate"
    if saved == 0:
        return "no_headroom"
    return "reject_static_model"


def add_cost_fields(candidates: list[dict[str, Any]]) -> None:
    for candidate in candidates:
        total = candidate.get("total_lane_mixing_permutes_per_block")
        if total is None:
            candidate["expected_cycles_saved_per_ntt"] = None
            candidate["gate_status"] = classify_candidate(candidate)
            continue
        candidate["delta_permutes_per_block_vs_current"] = int(total) - CURRENT_TAIL_PERMUTES_PER_BLOCK
        candidate["expected_cycles_saved_per_ntt"] = expected_cycles_saved(int(total))
        candidate["gate_status"] = classify_candidate(candidate)


def candidate_transform_dags() -> dict[str, Any]:
    candidates: list[dict[str, Any]] = [
        {
            "name": "A_current_ct_stage12_k32_major",
            "description": "Current vector-wise radix-2 CT stage split with final rowpack transpose.",
            "absorbed_lane_mixing_levels": 0,
            "explicit_lane_mixing_levels": 3,
            "horizontal_butterfly_stages": 0,
            "total_lane_mixing_permutes_per_block": 24,
            "proof_status": "proved_by_existing_gates",
            "twiddle_remap": "none",
            "interpretation": "baseline rowpack v2 Forward topology",
        },
        {
            "name": "B_layout_moved_before_stage345",
            "description": "Move the full rowpack 8x8 mixing before stage345, then keep stage345 lane-local only if arithmetic is changed to horizontal lane butterflies.",
            "absorbed_lane_mixing_levels": 0,
            "explicit_lane_mixing_levels": 3,
            "horizontal_butterfly_stages": 3,
            "total_lane_mixing_permutes_per_block": 72,
            "proof_status": "structural_only",
            "twiddle_remap": "required for horizontal stage345",
            "interpretation": "same as Gate 12 pretranspose/horizontal stage345; reject",
        },
        {
            "name": "C_layout_moved_into_stage12_one_level",
            "description": "Move one 8-vector mixing level into stage12 without changing the algebraic transform.",
            "absorbed_lane_mixing_levels": 0,
            "explicit_lane_mixing_levels": 3,
            "horizontal_butterfly_stages": 0,
            "total_lane_mixing_permutes_per_block": 24,
            "proof_status": "structural_only",
            "twiddle_remap": "none if pure layout move",
            "interpretation": "no net lane-mixing reduction",
        },
        {
            "name": "D_six_step_4x8_or_8x4_decomposition",
            "description": "Two-dimensional NTT32 factorization with rowpack-friendly planes and corner turns.",
            "absorbed_lane_mixing_levels": 0,
            "explicit_lane_mixing_levels": 6,
            "horizontal_butterfly_stages": 0,
            "total_lane_mixing_permutes_per_block": 48,
            "proof_status": "requires_twiddle_factorization_proof",
            "twiddle_remap": "required",
            "interpretation": "corner turns alone exceed current lane-mixing cost before arithmetic pressure",
        },
        {
            "name": "E_rowpack_from_entry_horizontal_ntt32",
            "description": "Keep rowpack plane vectors from NTT32 entry and run all five stages horizontally inside lanes.",
            "absorbed_lane_mixing_levels": 0,
            "explicit_lane_mixing_levels": 0,
            "horizontal_butterfly_stages": 5,
            "total_lane_mixing_permutes_per_block": 80,
            "proof_status": "structural_only",
            "twiddle_remap": "required",
            "interpretation": "destroys the current vector-wise butterfly advantage",
        },
        {
            "name": "F_algebraic_absorb_one_mixing_level",
            "description": "Hypothetical transform remap that absorbs one of three rowpack lane-mixing levels into earlier butterflies.",
            "absorbed_lane_mixing_levels": 1,
            "explicit_lane_mixing_levels": 2,
            "horizontal_butterfly_stages": 0,
            "total_lane_mixing_permutes_per_block": 16,
            "proof_status": "not_found_in_bounded_search",
            "twiddle_remap": "required",
            "interpretation": "would save too little to justify ASM even if proved",
        },
        {
            "name": "G_algebraic_absorb_two_mixing_levels",
            "description": "Hypothetical transform remap that absorbs two of three rowpack lane-mixing levels into earlier butterflies.",
            "absorbed_lane_mixing_levels": 2,
            "explicit_lane_mixing_levels": 1,
            "horizontal_butterfly_stages": 0,
            "total_lane_mixing_permutes_per_block": 8,
            "proof_status": "not_found_in_bounded_search",
            "twiddle_remap": "required",
            "interpretation": "near the continue threshold but still below the 150 cycles/NTT gate in this cost model",
        },
        {
            "name": "H_algebraic_absorb_three_mixing_levels",
            "description": "Hypothetical rowpack-native transform DAG that absorbs the full rowpack 8x8 mixing into the Forward arithmetic.",
            "absorbed_lane_mixing_levels": 3,
            "explicit_lane_mixing_levels": 0,
            "horizontal_butterfly_stages": 0,
            "total_lane_mixing_permutes_per_block": 0,
            "proof_status": "not_found_in_bounded_search",
            "twiddle_remap": "required",
            "interpretation": "only class with enough modeled headroom, but no concrete tagged transform was found",
        },
        {
            "name": "I_non_radix2_new_decomposition",
            "description": "Open-ended non-current decomposition that changes root/twiddle assignment before stage12.",
            "absorbed_lane_mixing_levels": None,
            "explicit_lane_mixing_levels": None,
            "horizontal_butterfly_stages": None,
            "total_lane_mixing_permutes_per_block": None,
            "proof_status": "research_only",
            "twiddle_remap": "required",
            "interpretation": "outside bounded search; requires a separate mathematical transform derivation",
        },
    ]
    add_cost_fields(candidates)

    best_proved = max(
        (
            candidate for candidate in candidates
            if candidate["proof_status"] in {"proved", "proved_by_existing_gates"}
            and candidate["expected_cycles_saved_per_ntt"] is not None
        ),
        key=lambda item: item["expected_cycles_saved_per_ntt"],
    )
    best_unproved = max(
        (
            candidate for candidate in candidates
            if candidate["expected_cycles_saved_per_ntt"] is not None
        ),
        key=lambda item: item["expected_cycles_saved_per_ntt"],
    )

    return {
        "gate": "Gate 13: Forward v4 tagged-index transform-DAG search",
        "status": "complete_bounded_search_no_asm_candidate",
        "cost_model": {
            "current_tail_permutes_per_block": CURRENT_TAIL_PERMUTES_PER_BLOCK,
            "blocks_per_ntt32": BLOCKS_PER_NTT32,
            "current_scatter_cycles_per_ntt": CURRENT_SCATTER_CYCLES,
            "store_ready_cycles_per_ntt": STORE_READY_CYCLES,
            "recoverable_window_cycles_per_ntt": round(RECOVERABLE_WINDOW_CYCLES, 3),
            "estimated_cycles_per_removed_permute": round(CYCLES_PER_PERMUTE, 3),
            "minimum_continue_cycles_per_ntt": MIN_CONTINUE_CYCLES_PER_NTT,
            "strong_continue_cycles_per_ntt": STRONG_CONTINUE_CYCLES_PER_NTT,
        },
        "search_constraints": {
            "isa": "AArch64 Neon",
            "vector_lanes": VECTOR_LANES,
            "candidate_must_use": [
                "fixed 128-bit Neon vectors",
                "plain vector stores for rowpack output",
                "public stage/table schedule",
            ],
            "forbidden": [
                "SVE/SVE2/SME",
                "st4 or lane stores as the output fix",
                "scalar scatter",
                "scalar GT-to-rowpack conversion",
                "ASM or Slothy before a proved transform DAG",
            ],
        },
        "candidates": candidates,
        "best_proved_candidate": {
            "name": best_proved["name"],
            "expected_cycles_saved_per_ntt": best_proved["expected_cycles_saved_per_ntt"],
            "gate_status": best_proved["gate_status"],
        },
        "best_unproved_candidate": {
            "name": best_unproved["name"],
            "expected_cycles_saved_per_ntt": best_unproved["expected_cycles_saved_per_ntt"],
            "gate_status": best_unproved["gate_status"],
            "proof_status": best_unproved["proof_status"],
        },
        "decision": {
            "continue_to_forward_v4_asm": False,
            "reason": (
                "The bounded tagged-index search found no proved transform DAG "
                "with at least 150 cycles/NTT expected recovery.  The only modeled "
                "class with strong enough headroom is full algebraic absorption of "
                "all three rowpack mixing levels, and no concrete tagged transform "
                "or twiddle remap was found for it."
            ),
            "next_gate_if_continuing": (
                "derive and test a numeric tagged-index transform oracle for "
                "H_algebraic_absorb_three_mixing_levels using the actual NTRU+768 "
                "Forward NTT tables; still no ASM"
            ),
        },
    }


def twiddle_remap_obligations(candidates: dict[str, Any]) -> dict[str, Any]:
    obligations: list[dict[str, Any]] = []
    for candidate in candidates["candidates"]:
        if candidate["twiddle_remap"] != "required":
            continue
        obligations.append(
            {
                "candidate": candidate["name"],
                "proof_status": candidate["proof_status"],
                "required_before_asm": [
                    "construct numeric tagged-index oracle over q=3457 using current Forward NTT tables",
                    "prove each rowpack-native output tag is congruent to the current NTT32 output tag",
                    "derive lane-specific twiddle table order and signed representatives",
                    "prove changed reduction placement preserves bounded rowpack basemul/add input contract",
                    "prove public memory schedule and table indices remain secret-independent",
                ],
                "continue_gate": (
                    "candidate may proceed only if proof passes and expected saved cycles/NTT "
                    "is at least 150, preferably near 200"
                ),
            }
        )
    return {
        "gate": "Gate 13: Forward v4 twiddle-remap obligations",
        "status": "proof_obligations_only",
        "obligations": obligations,
    }


def transform_dag_report_markdown(
    reference: dict[str, Any],
    rowpack_contract: dict[str, Any],
    candidates: dict[str, Any],
) -> str:
    cost = candidates["cost_model"]
    lines = [
        "# Gate 13 Forward v4 Transform-DAG Search",
        "",
        "Status: `complete_bounded_search_no_asm_candidate`",
        "",
        "This gate is a tagged-index model.  It emits YAML/Markdown only; it",
        "does not generate `.S`, `.opt.s`, Slothy input, or benchmark binaries.",
        "",
        "## Reference DAG",
        "",
        f"- NTT32 size: `{NTT32_SIZE}`",
        f"- stages: `{', '.join(STAGE_NAMES)}`",
        f"- stage distances: `{STAGE_DISTANCES}`",
        f"- current stage12 boundary: `{reference['current_stage_split']['stage12_boundary_layout']}`",
        f"- rowpack output blocks: `{len(rowpack_contract['blocks'])}` blocks of `{VECTOR_LANES}` k32 values",
        "",
        "## Cost Model",
        "",
        f"- current tail: `{cost['current_tail_permutes_per_block']} permutes/block`",
        f"- recoverable window: `{cost['recoverable_window_cycles_per_ntt']} cycles/NTT`",
        f"- continue gate: `>= {cost['minimum_continue_cycles_per_ntt']} cycles/NTT`",
        f"- strong gate: `>= {cost['strong_continue_cycles_per_ntt']} cycles/NTT`",
        "",
        "## Candidate Matrix",
        "",
        "| candidate | total permutes/block | expected saved cycles/NTT | proof | status |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for candidate in candidates["candidates"]:
        total = candidate["total_lane_mixing_permutes_per_block"]
        total_text = "unknown" if total is None else str(total)
        saved = candidate["expected_cycles_saved_per_ntt"]
        saved_text = "unknown" if saved is None else f"{saved:+.3f}"
        lines.append(
            "| {name} | {total} | {saved} | `{proof}` | `{status}` |".format(
                name=candidate["name"],
                total=total_text,
                saved=saved_text,
                proof=candidate["proof_status"],
                status=candidate["gate_status"],
            )
        )

    best_proved = candidates["best_proved_candidate"]
    best_unproved = candidates["best_unproved_candidate"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"Best proved candidate: `{best_proved['name']}` with "
            f"`{best_proved['expected_cycles_saved_per_ntt']}` cycles/NTT expected recovery.",
            "",
            f"Best unproved candidate: `{best_unproved['name']}` with "
            f"`{best_unproved['expected_cycles_saved_per_ntt']}` cycles/NTT expected recovery.",
            "",
            candidates["decision"]["reason"],
            "",
            "Forward v4 ASM remains blocked.  If this line continues, the next",
            "artifact should be a numeric tagged-index transform oracle for",
            "`H_algebraic_absorb_three_mixing_levels` using the actual NTRU+768",
            "Forward NTT tables, not assembly.",
            "",
        ]
    )
    return "\n".join(lines)


def write_artifacts() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    reference = reference_transform_dag()
    rowpack_contract = rowpack_output_contract()
    candidates = candidate_transform_dags()
    obligations = twiddle_remap_obligations(candidates)

    write_yml(OUTDIR / "reference-transform-dag.yml", reference)
    write_yml(OUTDIR / "rowpack-output-tags.yml", rowpack_contract)
    write_yml(OUTDIR / "candidate-transform-dags.yml", candidates)
    write_yml(OUTDIR / "twiddle-remap-obligations.yml", obligations)
    (OUTDIR / "transform-dag-search-report.md").write_text(
        transform_dag_report_markdown(reference, rowpack_contract, candidates)
    )


def main() -> int:
    write_artifacts()
    print(f"wrote Gate 13 transform-DAG search artifacts to {OUTDIR}")
    print("decision: no Forward v4 ASM; no proved transform DAG clears the 150 cycles/NTT gate")
    print("next if continuing: numeric tagged-index oracle for full algebraic absorption")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
