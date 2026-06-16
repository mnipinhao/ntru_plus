#!/usr/bin/env python3
"""Gate 10 layout search for rowpack Forward v3c stage12+stage345.

This is a feasibility gate, not an ASM candidate generator.  Gate 8 showed
that final-only permutation has no headroom.  Gate 9 step 2 showed that a
stage345-only rewrite cannot escape the current k32-major stage12 scratch
boundary because stage345 arithmetic preserves lane indices.

Gate 10 widens the boundary and asks whether changing the stage12 scratch /
stage345 input contract can reduce the total lane-mixing cost instead of only
moving the same 8x8 transpose earlier.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from audit_forward_stage345_liveout import BLOCKS, PLANE_NAMES, required_permutation, target_plane


OUTDIR = Path("docs/gt_soa_layout_experiment/forward_v3c_stage12_stage345_layout_search")

CURRENT_TAIL_PERMUTES_PER_BLOCK = 24
BLOCKS_PER_NTT32 = 4
CURRENT_SCATTER_CYCLES = 319.328
STORE_READY_CYCLES = 109.359
RECOVERABLE_CYCLES = CURRENT_SCATTER_CYCLES - STORE_READY_CYCLES
CYCLES_PER_PERMUTE = RECOVERABLE_CYCLES / (CURRENT_TAIL_PERMUTES_PER_BLOCK * BLOCKS_PER_NTT32)


ALLOWED_OPS = [
    "trn1",
    "trn2",
    "zip1",
    "zip2",
    "uzp1",
    "uzp2",
    "ext",
    "rev64",
    "mov",
    "orr",
    "plain_vector_store",
]

FORBIDDEN_OPS = [
    "st4",
    "lane_store",
    "scalar_scatter",
    "scalar_GT_to_rowpack_conversion",
]


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


def expected_cycles_saved(total_permutes_per_block: int) -> float:
    saved_permutes = (CURRENT_TAIL_PERMUTES_PER_BLOCK - total_permutes_per_block) * BLOCKS_PER_NTT32
    return round(saved_permutes * CYCLES_PER_PERMUTE, 3)


def gate_status(total_permutes_per_block: int) -> str:
    saved = expected_cycles_saved(total_permutes_per_block)
    if total_permutes_per_block <= CURRENT_TAIL_PERMUTES_PER_BLOCK - 16 or saved >= 200.0:
        return "strong_build_candidate"
    if total_permutes_per_block <= CURRENT_TAIL_PERMUTES_PER_BLOCK - 8 or saved >= 100.0:
        return "build_candidate"
    if total_permutes_per_block < CURRENT_TAIL_PERMUTES_PER_BLOCK:
        return "weak_static_headroom_below_gate"
    if total_permutes_per_block == CURRENT_TAIL_PERMUTES_PER_BLOCK:
        return "no_headroom"
    return "worse_than_current"


def current_stage12_liveout() -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for block in BLOCKS:
        k32_base = int(block["k32_base"])
        blocks.append(
            {
                "block": block["block"],
                "k32_range": f"{k32_base}..{k32_base + 7}",
                "stage12_scratch_contract": "k32-major",
                "scratch_vectors": [
                    {
                        "k32": k32_base + lane,
                        "shape": "fixed k32 with h[0..3]=branch0 lanes and h[4..7]=branch1 lanes",
                    }
                    for lane in range(8)
                ],
                "stage345_liveout_semantic_order": block["semantic_order"],
                "v2_tail_source_order": block["v2_source_order"],
                "source_to_target_lane_permutation": required_permutation(block),
            }
        )
    return {
        "gate": "Gate 10: current stage12 live-out contract",
        "status": "baseline",
        "description": (
            "Current rowpack Forward v2 fixes the layout boundary at stage12: "
            "stage345 receives k32-major scratch vectors.  Because stage345 is "
            "lane-preserving, rowpack plane vectors are only produced by the "
            "final transpose tail."
        ),
        "blocks": blocks,
    }


def stage345_input_contract() -> dict[str, Any]:
    return {
        "gate": "Gate 10: stage345 input contract alternatives",
        "stage345_arithmetic_property": "lane_preserving",
        "lane_preserving_operations": [
            "add/sub",
            "mul/mls/sqrdmulh/sqdmulh",
            "Barrett srshr/mls reduction",
            "lane-broadcast twiddle multiply",
        ],
        "contracts": [
            {
                "name": "A_current_k32_major",
                "stage12_output": "k32-major scratch vectors",
                "stage345_input": "one vector per k32",
                "expected_stage345_behavior": "unchanged lane-preserving arithmetic",
            },
            {
                "name": "B_partial_rowpack_friendly_scratch",
                "stage12_output": "partially grouped vectors before scratch",
                "stage345_input": "mixed contract; some source fan-in paid before stage345",
                "expected_stage345_behavior": "mostly lane-preserving; remaining fan-in still required",
            },
            {
                "name": "C_fully_rowpack_friendly_scratch",
                "stage12_output": "rowpack plane-like vectors",
                "stage345_input": "one vector per branch/lane plane over eight k32 values",
                "expected_stage345_behavior": (
                    "requires stage12 arithmetic topology to be rewritten; a "
                    "layout-only implementation pays a full transpose before scratch"
                ),
            },
        ],
    }


def stage345_output_contract() -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for block in BLOCKS:
        blocks.append(
            {
                "block": block["block"],
                "k32_base": block["k32_base"],
                "target_planes": {
                    PLANE_NAMES[plane]: target_plane(block, plane)
                    for plane in range(len(PLANE_NAMES))
                },
                "store_form": "one plain vector store per target plane",
            }
        )
    return {
        "gate": "Gate 10: stage345 output contract",
        "desired_output_shape": "rowpack plane vectors",
        "allowed_final_store": "plain vector stores only",
        "forbidden_store_forms": FORBIDDEN_OPS,
        "blocks": blocks,
    }


def candidate_contracts() -> list[dict[str, Any]]:
    candidates = [
        {
            "name": "A_current",
            "stage12_extra_permutes_per_block": 0,
            "stage345_extra_permutes_per_block": 0,
            "remaining_final_tail_permutes_per_block": 24,
            "temp_register_pressure": "current",
            "uses_forbidden_store": False,
            "interpretation": "baseline rowpack Forward v2 layout contract",
        },
        {
            "name": "B_partial_rowpack_friendly_scratch",
            "stage12_extra_permutes_per_block": 8,
            "stage345_extra_permutes_per_block": 8,
            "remaining_final_tail_permutes_per_block": 16,
            "temp_register_pressure": "higher than current",
            "uses_forbidden_store": False,
            "interpretation": (
                "A partial scratch grouping pays one mixing stage before the "
                "scratch boundary, but lane-preserving stage345 still needs "
                "two more mixing stages to form rowpack planes."
            ),
        },
        {
            "name": "C_fully_rowpack_friendly_scratch_layout_only",
            "stage12_extra_permutes_per_block": 24,
            "stage345_extra_permutes_per_block": 0,
            "remaining_final_tail_permutes_per_block": 0,
            "temp_register_pressure": "higher than current before accounting scratch stores",
            "uses_forbidden_store": False,
            "interpretation": (
                "If stage12 only changes live-out layout, it pays the full "
                "8x8 mixing network before scratch.  This ties the current "
                "24-permute lower bound before store/load and register pressure."
            ),
        },
    ]

    for candidate in candidates:
        total = (
            int(candidate["stage12_extra_permutes_per_block"])
            + int(candidate["stage345_extra_permutes_per_block"])
            + int(candidate["remaining_final_tail_permutes_per_block"])
        )
        candidate["total_estimated_permutes_per_block"] = total
        candidate["delta_permutes_per_block_vs_current"] = total - CURRENT_TAIL_PERMUTES_PER_BLOCK
        candidate["expected_cycles_saved_per_ntt"] = expected_cycles_saved(total)
        candidate["gate_status"] = gate_status(total)
        candidate["recommendation"] = (
            "build_candidate"
            if candidate["gate_status"] in {"build_candidate", "strong_build_candidate"}
            else "reject_layout_only_candidate"
        )
    return candidates


def candidate_stage12_liveout() -> dict[str, Any]:
    candidates = candidate_contracts()
    return {
        "gate": "Gate 10: v3c stage12+stage345 layout search",
        "status": "complete_static_search_no_asm_candidate",
        "cost_model": {
            "current_tail_permutes_per_block": CURRENT_TAIL_PERMUTES_PER_BLOCK,
            "blocks_per_ntt32": BLOCKS_PER_NTT32,
            "current_scatter_cycles_per_ntt": CURRENT_SCATTER_CYCLES,
            "store_ready_cycles_per_ntt": STORE_READY_CYCLES,
            "recoverable_window_cycles_per_ntt": round(RECOVERABLE_CYCLES, 3),
            "estimated_cycles_per_permute": round(CYCLES_PER_PERMUTE, 3),
        },
        "gate_thresholds": {
            "build_candidate": "total estimated permutes <= current - 8 per block, or expected saving >= 100 cycles/NTT",
            "strong_candidate": "total estimated permutes <= current - 16 per block, or expected saving >= 200 cycles/NTT",
        },
        "candidates": candidates,
        "decision": {
            "build_v3c_layout_only_candidate": False,
            "reason": (
                "No stage12 scratch/live-out contract beats the current "
                "24-permute/block tail under a layout-only cost model.  Partial "
                "scratch grouping is worse, and fully rowpack-friendly scratch "
                "only ties the lower bound by moving the full transpose before "
                "scratch."
            ),
            "still_open": (
                "A larger stage12 arithmetic topology rewrite may still be useful "
                "if it absorbs lane mixing into the butterflies rather than adding "
                "a separate transpose-equivalent network."
            ),
        },
    }


def summary_markdown(candidates: dict[str, Any]) -> str:
    lines = [
        "# Gate 10 Forward v3c Stage12+Stage345 Layout Search",
        "",
        "Status: `complete_static_search_no_asm_candidate`",
        "",
        "This gate does not generate `.S`, `.opt.s`, or Slothy output.  It",
        "widens the search boundary from stage345-only to stage12+stage345 and",
        "checks whether changing the scratch/live-out contract can remove the",
        "rowpack Forward output transpose instead of moving it earlier.",
        "",
        "## Store Policy",
        "",
        "Allowed:",
    ]
    lines.extend(f"- `{op}`" for op in ALLOWED_OPS)
    lines.extend(["", "Forbidden:"])
    lines.extend(f"- `{op}`" for op in FORBIDDEN_OPS)
    cost = candidates["cost_model"]
    lines.extend(
        [
            "",
            "## Cost Model",
            "",
            f"- current tail: `{cost['current_tail_permutes_per_block']} permutes/block`",
            f"- current scatter/transpose-only: `{cost['current_scatter_cycles_per_ntt']} cycles/NTT`",
            f"- store-ready lower bound: `{cost['store_ready_cycles_per_ntt']} cycles/NTT`",
            f"- recoverable window: `{cost['recoverable_window_cycles_per_ntt']} cycles/NTT`",
            f"- estimated cycles per removed permute: `{cost['estimated_cycles_per_permute']}`",
            "",
            "## Contract Comparison",
            "",
            "| candidate | stage12 extra | stage345 extra | final tail | total | expected cycles saved | status |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for candidate in candidates["candidates"]:
        lines.append(
            "| {name} | {s12} | {s345} | {tail} | {total} | {saved} | `{status}` |".format(
                name=candidate["name"],
                s12=candidate["stage12_extra_permutes_per_block"],
                s345=candidate["stage345_extra_permutes_per_block"],
                tail=candidate["remaining_final_tail_permutes_per_block"],
                total=candidate["total_estimated_permutes_per_block"],
                saved=candidate["expected_cycles_saved_per_ntt"],
                status=candidate["gate_status"],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Do not build a v3c candidate that only changes the stage12 scratch",
            "layout.  With the current arithmetic topology, the mismatch is already",
            "fixed at the stage12 scratch boundary: once stage12 emits k32-major",
            "vectors, lane-preserving stage345 arithmetic cannot naturally produce",
            "rowpack plane vectors.  Making scratch more rowpack-friendly by layout",
            "operations alone either worsens total permutation cost or ties the",
            "same 24-permute/block lower bound before accounting for scratch",
            "store/load and register pressure.",
            "",
            "Still open: a larger stage12 arithmetic topology rewrite that absorbs",
            "lane mixing into stage12 butterflies, or an earlier forward-topology",
            "contract change.  That is outside this layout-only Gate 10.",
            "",
        ]
    )
    return "\n".join(lines)


def write_artifacts(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    current = current_stage12_liveout()
    candidates = candidate_stage12_liveout()
    input_contract = stage345_input_contract()
    output_contract = stage345_output_contract()

    write_yml(outdir / "current_stage12_liveout.yml", current)
    write_yml(outdir / "candidate_stage12_liveout.yml", candidates)
    write_yml(outdir / "stage345_input_contract.yml", input_contract)
    write_yml(outdir / "stage345_output_contract.yml", output_contract)
    (outdir / "layout_search_summary.md").write_text(summary_markdown(candidates))


def main() -> int:
    write_artifacts(OUTDIR)
    print(f"wrote Gate 10 v3c layout-search artifacts to {OUTDIR}")
    print("decision: do not build a stage12 scratch-layout-only v3c candidate")
    print("next viable scope: stage12 arithmetic topology rewrite or earlier contract change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
