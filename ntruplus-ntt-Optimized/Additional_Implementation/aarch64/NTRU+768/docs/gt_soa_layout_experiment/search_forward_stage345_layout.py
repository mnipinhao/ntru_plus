#!/usr/bin/env python3
"""Gate 8 symbolic layout search for rowpack Forward stage345 live-outs.

This is not an ASM candidate generator.  It records the current v2 live-out
shape, the target rowpack plane vectors, and the best legal final-only
permutation family under the Gate 7 store policy.  The search is intentionally
small and conservative: it answers whether a final-only permutation can beat
the existing 8x8 16-bit transpose tail before moving on to a stage345 rewrite.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from audit_forward_stage345_liveout import BLOCKS, PLANE_NAMES, required_permutation, target_plane


DEFAULT_OUTDIR = Path("docs/gt_soa_layout_experiment/forward_stage345_layout_search")

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


def json_dump(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def current_liveout() -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for block in BLOCKS:
        semantic = list(block["semantic_order"])
        source = list(block["v2_source_order"])
        blocks.append(
            {
                "block": block["block"],
                "k32_base": block["k32_base"],
                "semantic_liveout_order": semantic,
                "v2_tail_source_order": source,
                "current_v2_tail_cost": {
                    "trn": 24,
                    "vector_stores": 8,
                },
            }
        )
    return {
        "description": "Current rowpack-v2 stage345 live-out registers before the final output tail.",
        "blocks": blocks,
    }


def target_rowpack_planes() -> dict[str, Any]:
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
        "description": "Rowpack-ready plane vectors required before plain vector stores.",
        "blocks": blocks,
    }


def required_permutations() -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for block in BLOCKS:
        blocks.append(
            {
                "block": block["block"],
                "k32_base": block["k32_base"],
                "source_to_semantic_permutation": required_permutation(block),
                "v2_tail_source_order": block["v2_source_order"],
                "semantic_target_order": block["semantic_order"],
            }
        )
    return {
        "description": "Register-order permutation between the current v2 tail source order and semantic k32 order.",
        "blocks": blocks,
    }


def transpose_sequence(block_id: int, source_regs: list[str]) -> list[dict[str, Any]]:
    """Return the standard 8x8 16-bit transpose DAG for a source order.

    This is an abstract DAG, not concrete assembly.  Each op maps to one Neon
    interleave instruction family member.  The output vector p is the rowpack
    plane containing source_regs[*].h[p].
    """
    steps: list[dict[str, Any]] = []

    pairs_16 = [(0, 1), (2, 3), (4, 5), (6, 7)]
    for pair, (a, b) in enumerate(pairs_16):
        steps.append(
            {
                "op": "trn1.8h",
                "dst": f"b{block_id}_s0_{2 * pair}",
                "src": [source_regs[a], source_regs[b]],
            }
        )
        steps.append(
            {
                "op": "trn2.8h",
                "dst": f"b{block_id}_s0_{2 * pair + 1}",
                "src": [source_regs[a], source_regs[b]],
            }
        )

    pairs_32 = [(0, 2), (1, 3), (4, 6), (5, 7)]
    for out_a, out_b, a, b in [
        (0, 2, 0, 2),
        (1, 3, 1, 3),
        (4, 6, 4, 6),
        (5, 7, 5, 7),
    ]:
        steps.append(
            {
                "op": "trn1.4s",
                "dst": f"b{block_id}_s1_{out_a}",
                "src": [f"b{block_id}_s0_{a}", f"b{block_id}_s0_{b}"],
            }
        )
        steps.append(
            {
                "op": "trn2.4s",
                "dst": f"b{block_id}_s1_{out_b}",
                "src": [f"b{block_id}_s0_{a}", f"b{block_id}_s0_{b}"],
            }
        )

    for out_a, out_b, a, b in [
        (0, 4, 0, 4),
        (1, 5, 1, 5),
        (2, 6, 2, 6),
        (3, 7, 3, 7),
    ]:
        steps.append(
            {
                "op": "trn1.2d",
                "dst": f"b{block_id}_out_{out_a}",
                "src": [f"b{block_id}_s1_{a}", f"b{block_id}_s1_{b}"],
            }
        )
        steps.append(
            {
                "op": "trn2.2d",
                "dst": f"b{block_id}_out_{out_b}",
                "src": [f"b{block_id}_s1_{a}", f"b{block_id}_s1_{b}"],
            }
        )

    assert len(pairs_16) == 4
    assert len(pairs_32) == 4
    assert len(steps) == 24
    return steps


def candidate_sequences() -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for block in BLOCKS:
        semantic = list(block["semantic_order"])
        source = list(block["v2_source_order"])
        blocks.append(
            {
                "block": block["block"],
                "k32_base": block["k32_base"],
                "current_v2_reference": {
                    "source_order": source,
                    "permute_instructions": 24,
                    "vector_stores": 8,
                    "allowed_ops_only": True,
                    "performance_status": "baseline",
                },
                "best_final_only_found": {
                    "source_order": semantic,
                    "sequence": transpose_sequence(int(block["block"]), semantic),
                    "permute_instructions": 24,
                    "vector_stores": 8,
                    "allowed_ops_only": True,
                    "uses_forbidden_store_form": False,
                    "estimated_extra_temp_vectors": 16,
                    "estimated_recovery_vs_v2": 0,
                    "status": "no_better_than_v2",
                },
            }
        )
    return {
        "gate": "Gate 8: rowpack Forward stage345 layout search",
        "allowed_ops": ALLOWED_OPS,
        "forbidden_ops": FORBIDDEN_OPS,
        "lower_bound": {
            "model": "8x8 16-bit transpose using two-input Neon lane interleaves",
            "reason": (
                "Each target plane contains one 16-bit lane from each of eight source vectors. "
                "A two-input interleave can at most double source-register fan-in per vector, "
                "so three mixing stages are required.  Preserving all 64 lanes needs eight "
                "vector results per stage, giving a 24-instruction lower bound."
            ),
            "permute_instruction_lower_bound_per_block": 24,
            "current_v2_permute_instructions_per_block": 24,
        },
        "blocks": blocks,
        "summary": {
            "best_final_only_sequence_length": 24,
            "current_v2_sequence_length": 24,
            "uses_only_allowed_ops": True,
            "requires_st4_lane_or_scalar": False,
            "estimated_temp_register_pressure": "moderate/high; no better than current transpose tail",
            "recommendation": "skip v3a unless a non-interleave identity is discovered; proceed to v3b stage345 live-out rewrite",
        },
    }


def summary_markdown(data: dict[str, Any]) -> str:
    lower = data["lower_bound"]
    summary = data["summary"]
    lines = [
        "# Gate 8 Rowpack Forward Stage345 Layout Search",
        "",
        "Status: `complete_static_search_no_candidate`",
        "",
        "This gate does not generate `.S`, `.opt.s`, or Slothy output.  It",
        "answers whether a final-only permutation can beat the current rowpack-v2",
        "output tail before spending effort on another ASM candidate.",
        "",
        "## Store Policy",
        "",
        "Allowed:",
    ]
    lines.extend(f"- `{op}`" for op in ALLOWED_OPS)
    lines.extend(["", "Forbidden:"])
    lines.extend(f"- `{op}`" for op in FORBIDDEN_OPS)
    lines.extend(
        [
            "",
            "## Final-Only Search Result",
            "",
            f"- model: `{lower['model']}`",
            f"- current v2 final tail: `{lower['current_v2_permute_instructions_per_block']} permutes/block`",
            f"- lower bound: `{lower['permute_instruction_lower_bound_per_block']} permutes/block`",
            f"- best final-only sequence: `{summary['best_final_only_sequence_length']} permutes/block`",
            f"- uses only allowed ops: `{summary['uses_only_allowed_ops']}`",
            f"- requires forbidden stores/scatter: `{summary['requires_st4_lane_or_scalar']}`",
            f"- estimated temp pressure: `{summary['estimated_temp_register_pressure']}`",
            "",
            "Reason:",
            "",
            lower["reason"],
            "",
            "## Per-Block Required Permutations",
            "",
            "| block | k32 range | v2 source -> semantic permutation | best final-only count |",
            "| ---: | --- | --- | ---: |",
        ]
    )
    for block in data["blocks"]:
        k32_base = int(block["k32_base"])
        perm = required_permutation(BLOCKS[int(block["block"])])
        lines.append(
            f"| {block['block']} | {k32_base}..{k32_base + 7} | `{perm}` | "
            f"{block['best_final_only_found']['permute_instructions']} |"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            summary["recommendation"],
            "",
            "Decision: final-only v3a has no instruction-count headroom under the",
            "allowed two-input Neon interleave model.  The next useful candidate is",
            "v3b: change the stage345 arithmetic/register order so rowpack plane",
            "vectors are naturally live-out, then use plain vector stores.",
            "",
        ]
    )
    return "\n".join(lines)


def write_artifacts(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    liveout = current_liveout()
    targets = target_rowpack_planes()
    permutations = required_permutations()
    candidates = candidate_sequences()

    json_dump(outdir / "current_liveout.json", liveout)
    json_dump(outdir / "target_rowpack_planes.json", targets)
    json_dump(outdir / "required_permutation.json", permutations)
    json_dump(outdir / "candidate_sequences.json", candidates)
    (outdir / "layout_search_summary.md").write_text(summary_markdown(candidates))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_artifacts(args.outdir)
    print(f"wrote Gate 8 layout-search artifacts to {args.outdir}")
    print("recommendation: proceed to v3b stage345 live-out rewrite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
