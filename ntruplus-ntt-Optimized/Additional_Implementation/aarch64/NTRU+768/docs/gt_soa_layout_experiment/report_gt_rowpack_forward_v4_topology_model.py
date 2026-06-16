#!/usr/bin/env python3
"""Forward v4 static topology model for rowpack Forward NTT.

This is a model-only gate.  It does not generate assembly, does not run Slothy,
and does not run benchmarks.  The purpose is to decide whether a larger
Forward v4 arithmetic topology rewrite has enough static headroom to justify
authoring a candidate.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


OUTDIR = Path("docs/gt_soa_layout_experiment/forward_v4_topology_model")

CURRENT_TAIL_PERMUTES_PER_BLOCK = 24
BLOCKS_PER_NTT32 = 4
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


def expected_cycles_saved(total_lane_mixing_permutes_per_block: int) -> float:
    saved_permutes = (CURRENT_TAIL_PERMUTES_PER_BLOCK - total_lane_mixing_permutes_per_block) * BLOCKS_PER_NTT32
    return round(saved_permutes * CYCLES_PER_PERMUTE, 3)


def gate_status(candidate: dict[str, Any]) -> str:
    if candidate.get("requires_new_transform_proof"):
        return "research_only_no_static_cycle_claim"
    saved = float(candidate["expected_cycles_saved_per_ntt"])
    total = int(candidate["total_lane_mixing_permutes_per_block"])
    if saved >= STRONG_CONTINUE_CYCLES_PER_NTT or total <= 8:
        return "strong_continue"
    if saved >= MIN_CONTINUE_CYCLES_PER_NTT or total <= 12:
        return "continue"
    if saved > 0:
        return "weak_headroom_below_gate"
    if saved == 0:
        return "no_headroom"
    return "reject_static_model"


def add_derived_fields(candidates: list[dict[str, Any]]) -> None:
    for candidate in candidates:
        if candidate.get("total_lane_mixing_permutes_per_block") is None:
            candidate["expected_cycles_saved_per_ntt"] = None
            candidate["gate_status"] = gate_status(candidate)
            continue
        total = int(candidate["total_lane_mixing_permutes_per_block"])
        candidate["delta_permutes_per_block_vs_current"] = total - CURRENT_TAIL_PERMUTES_PER_BLOCK
        candidate["expected_cycles_saved_per_ntt"] = expected_cycles_saved(total)
        candidate["gate_status"] = gate_status(candidate)


def build_candidates() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = [
        {
            "name": "A_current_v2_k32_major",
            "description": "Current rowpack v2 topology.",
            "stage12_boundary": "k32-major scratch vectors",
            "stage345_arithmetic": "vector-wise, lane-preserving CT butterflies",
            "final_tail": "8x8 transpose to rowpack planes",
            "removed_final_tail_permutes_per_block": 0,
            "added_early_permutes_per_block": 0,
            "added_horizontal_butterfly_permutes_per_block": 0,
            "remaining_tail_permutes_per_block": 24,
            "total_lane_mixing_permutes_per_block": 24,
            "requires_new_transform_proof": False,
            "register_pressure": "known-good",
            "risk": "baseline",
        },
        {
            "name": "B_pretranspose_then_horizontal_stage345",
            "description": (
                "Transpose each 8-k32 block into rowpack plane vectors before stage345, "
                "then run stages 3/4/5 as horizontal lane butterflies inside each plane."
            ),
            "stage12_boundary": "rowpack plane vectors before stage345",
            "stage345_arithmetic": "horizontal lane butterflies for stages 3/4/5",
            "final_tail": "plain vector stores",
            "removed_final_tail_permutes_per_block": 24,
            "added_early_permutes_per_block": 24,
            "added_horizontal_butterfly_permutes_per_block": 48,
            "remaining_tail_permutes_per_block": 0,
            "total_lane_mixing_permutes_per_block": 72,
            "requires_new_transform_proof": False,
            "register_pressure": "high; plane vectors plus partner/merge temporaries",
            "risk": "very high; replaces cheap vector-wise butterflies with horizontal lane work",
            "lower_bound_note": (
                "Each of 8 branch/lane planes needs three horizontal butterfly stages. "
                "At least one partner-align and one merge/select operation per plane "
                "per stage gives a 48-permute lower bound before counting the "
                "pretranspose."
            ),
        },
        {
            "name": "C_absorb_one_mixing_stage_into_stage12",
            "description": (
                "Try to form a partially rowpack-friendly 2-way grouping at the stage12 "
                "boundary, reducing the final transpose by one stage."
            ),
            "stage12_boundary": "2-way grouped scratch",
            "stage345_arithmetic": "mostly vector-wise; remaining fan-in still needed",
            "final_tail": "two remaining transpose stages",
            "removed_final_tail_permutes_per_block": 8,
            "added_early_permutes_per_block": 8,
            "added_horizontal_butterfly_permutes_per_block": 0,
            "remaining_tail_permutes_per_block": 16,
            "total_lane_mixing_permutes_per_block": 24,
            "requires_new_transform_proof": False,
            "register_pressure": "higher than current; no net lane-mixing reduction",
            "risk": "medium; moves one transpose stage into stage12 without reducing total cost",
        },
        {
            "name": "D_absorb_two_mixing_stages_into_stage12",
            "description": (
                "Try to form a 4-way rowpack-friendly grouping at the stage12 boundary, "
                "leaving one final transpose stage."
            ),
            "stage12_boundary": "4-way grouped scratch",
            "stage345_arithmetic": "mixed vector-wise/horizontal shape",
            "final_tail": "one remaining transpose stage",
            "removed_final_tail_permutes_per_block": 16,
            "added_early_permutes_per_block": 16,
            "added_horizontal_butterfly_permutes_per_block": 0,
            "remaining_tail_permutes_per_block": 8,
            "total_lane_mixing_permutes_per_block": 24,
            "requires_new_transform_proof": False,
            "register_pressure": "high; no net lane-mixing reduction before pressure costs",
            "risk": "high; moves two transpose stages into stage12 without reducing total cost",
        },
        {
            "name": "E_rowpack_from_entry_horizontal_ntt32",
            "description": (
                "Keep rowpack plane vectors from the NTT32 entry and run all five "
                "32-point stages horizontally inside lanes."
            ),
            "stage12_boundary": "no k32-major scratch; rowpack plane layout from entry",
            "stage345_arithmetic": "horizontal lane butterflies for stages 1..5",
            "final_tail": "plain vector stores",
            "removed_final_tail_permutes_per_block": 24,
            "added_early_permutes_per_block": 0,
            "added_horizontal_butterfly_permutes_per_block": 80,
            "remaining_tail_permutes_per_block": 0,
            "total_lane_mixing_permutes_per_block": 80,
            "requires_new_transform_proof": False,
            "register_pressure": "very high",
            "risk": "very high; destroys the current vector-wise butterfly advantage",
            "lower_bound_note": (
                "Five horizontal stages times 8 planes times at least two "
                "permute/select operations per stage gives 80 permutes/block."
            ),
        },
        {
            "name": "F_new_forward_decomposition_rowpack_native",
            "description": (
                "Change the mathematical/vectorization decomposition earlier than "
                "stage12 so lane mixing is algebraically absorbed into the transform, "
                "not implemented as an added transpose network."
            ),
            "stage12_boundary": "undefined; not the current stage12/stage345 split",
            "stage345_arithmetic": "new decomposition required",
            "final_tail": "target is plain vector stores",
            "removed_final_tail_permutes_per_block": None,
            "added_early_permutes_per_block": None,
            "added_horizontal_butterfly_permutes_per_block": None,
            "remaining_tail_permutes_per_block": None,
            "total_lane_mixing_permutes_per_block": None,
            "requires_new_transform_proof": True,
            "register_pressure": "unknown",
            "risk": "research; needs tagged-index oracle, twiddle remap, range proof, and micro-DAG before ASM",
            "lower_bound_note": (
                "This is the only class that might beat the 24-permute/block "
                "barrier, but the current evidence does not yet quantify it. "
                "It cannot proceed to ASM until a concrete transform DAG predicts "
                "at least 150 cycles/NTT recoverable."
            ),
        },
    ]
    add_derived_fields(candidates)
    return candidates


def build_report() -> dict[str, Any]:
    candidates = build_candidates()
    return {
        "gate": "Gate 12: Forward v4 topology model",
        "status": "complete_static_model_no_asm_candidate",
        "scope": "Forward v4 rowpack-native arithmetic topology before stage12 scratch",
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
        "constraints": {
            "isa": "AArch64 Neon only",
            "forbidden": [
                "SVE/SVE2/SME",
                "st4 or lane-store output as the fix",
                "scalar scatter",
                "scalar GT-to-rowpack conversion",
                "Slothy or ASM before a concrete passing topology DAG",
            ],
            "must_preserve": [
                "NTRU+768 Forward NTT semantics",
                "twiddle/root order or an explicitly proved remap",
                "bounded output convention consumed by rowpack basemul/add",
                "constant-time public memory schedule",
            ],
        },
        "candidates": candidates,
        "decision": {
            "continue_to_v4_asm": False,
            "reason": (
                "No concrete topology in this model predicts at least 150 cycles/NTT "
                "recoverable.  The concrete variants either tie the 24-permute/block "
                "barrier, move it earlier, or replace it with more horizontal "
                "butterfly permutation work."
            ),
            "only_open_path": (
                "F_new_forward_decomposition_rowpack_native remains research-only. "
                "It needs a tagged-index transform DAG and twiddle/range proof "
                "before it can claim cycle headroom."
            ),
            "next_gate_if_continuing": "build a tagged-index Forward v4 transform-DAG search, not ASM",
        },
    }


def write_yml(path: Path, data: Any) -> None:
    path.write_text(yaml_dump(data) + "\n")


def candidate_matrix(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate": report["gate"],
        "cost_model": report["cost_model"],
        "candidates": [
            {
                "name": candidate["name"],
                "total_lane_mixing_permutes_per_block": candidate["total_lane_mixing_permutes_per_block"],
                "delta_permutes_per_block_vs_current": candidate.get("delta_permutes_per_block_vs_current"),
                "expected_cycles_saved_per_ntt": candidate["expected_cycles_saved_per_ntt"],
                "gate_status": candidate["gate_status"],
                "requires_new_transform_proof": candidate["requires_new_transform_proof"],
                "risk": candidate["risk"],
            }
            for candidate in report["candidates"]
        ],
    }


def topology_report_markdown(report: dict[str, Any]) -> str:
    cost = report["cost_model"]
    lines = [
        "# Gate 12 Forward v4 Topology Model",
        "",
        "Status: `complete_static_model_no_asm_candidate`",
        "",
        "This gate models whether a larger Forward v4 arithmetic topology rewrite",
        "has enough headroom to justify ASM.  It does not generate `.S`, `.opt.s`,",
        "or Slothy artifacts.",
        "",
        "## Cost Model",
        "",
        f"- current rowpack output tail: `{cost['current_tail_permutes_per_block']} permutes/block`",
        f"- current scatter/transpose-only: `{cost['current_scatter_cycles_per_ntt']} cycles/NTT`",
        f"- store-ready lower bound: `{cost['store_ready_cycles_per_ntt']} cycles/NTT`",
        f"- recoverable window: `{cost['recoverable_window_cycles_per_ntt']} cycles/NTT`",
        f"- estimated cycles per removed permute: `{cost['estimated_cycles_per_removed_permute']}`",
        f"- continue gate: `>= {cost['minimum_continue_cycles_per_ntt']} cycles/NTT`",
        f"- strong gate: `>= {cost['strong_continue_cycles_per_ntt']} cycles/NTT`",
        "",
        "## Candidate Matrix",
        "",
        "| candidate | total permutes/block | expected cycles saved/NTT | status | interpretation |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for candidate in report["candidates"]:
        total = candidate["total_lane_mixing_permutes_per_block"]
        total_text = "unknown" if total is None else str(total)
        saved = candidate["expected_cycles_saved_per_ntt"]
        saved_text = "unknown" if saved is None else f"{saved:+.3f}"
        lines.append(
            "| {name} | {total} | {saved} | `{status}` | {desc} |".format(
                name=candidate["name"],
                total=total_text,
                saved=saved_text,
                status=candidate["gate_status"],
                desc=candidate["description"],
            )
        )
    lines.extend(
        [
            "",
            "## Concrete Rejections",
            "",
        ]
    )
    for candidate in report["candidates"]:
        if candidate["name"].startswith("F_"):
            continue
        if candidate["gate_status"] in {"no_headroom", "reject_static_model"}:
            lines.append(
                f"- `{candidate['name']}`: {candidate['risk']}. "
                f"Modeled total lane mixing is `{candidate['total_lane_mixing_permutes_per_block']}` "
                f"permutes/block."
            )
    lines.extend(
        [
            "",
            "## Open Research Path",
            "",
            "`F_new_forward_decomposition_rowpack_native` is the only class left",
            "that could plausibly beat the 24-permute/block barrier, but this",
            "model cannot assign it cycle credit yet.  It changes the transform",
            "decomposition earlier than stage12, so the next artifact must be a",
            "tagged-index transform DAG with twiddle remap and range proof.  ASM",
            "or Slothy remains blocked until that DAG predicts at least",
            "`150 cycles/NTT` recoverable.",
            "",
            "## Decision",
            "",
            report["decision"]["reason"],
            "",
            f"Next gate if continuing: `{report['decision']['next_gate_if_continuing']}`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_yml(OUTDIR / "topology-model.yml", report)
    write_yml(OUTDIR / "candidate-matrix.yml", candidate_matrix(report))
    (OUTDIR / "topology-report.md").write_text(topology_report_markdown(report))
    print(f"wrote {OUTDIR / 'topology-model.yml'}")
    print(f"wrote {OUTDIR / 'candidate-matrix.yml'}")
    print(f"wrote {OUTDIR / 'topology-report.md'}")
    print("decision: no Forward v4 ASM yet; next gate is tagged-index transform-DAG search")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
