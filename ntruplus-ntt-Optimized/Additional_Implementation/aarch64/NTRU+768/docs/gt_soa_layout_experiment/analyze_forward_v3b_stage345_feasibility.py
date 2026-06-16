#!/usr/bin/env python3
"""Gate 9 step 2 feasibility check for a stage345-only v3b candidate.

The current stage12 -> stage345 boundary stores 32 vectors in k32-major shape:
one vector is a fixed k32 with lanes [branch0 lane0..3, branch1 lane0..3].
Stage345 arithmetic in the existing kernel is lane-preserving.  This checker
records whether a stage345-only rewrite can naturally produce rowpack plane
vectors without reintroducing a full 8x8 lane-mixing network.
"""

from __future__ import annotations

import json
from pathlib import Path


OUTDIR = Path("docs/gt_soa_layout_experiment/forward_v3b_stage345")
SUMMARY = OUTDIR / "feasibility-summary.md"
JSON_OUT = OUTDIR / "feasibility.json"


def build_report() -> dict[str, object]:
    return {
        "gate": "Gate 9 step 2: stage345-only v3b feasibility",
        "status": "blocked_current_stage12_boundary",
        "boundary": {
            "input_shape": "k32-major vectors: q[k32].h[0..7] = branch/lane values",
            "desired_output_shape": "rowpack planes: plane[branch,lane].h[v] = q_out[k32_base+v].h[branch_lane]",
        },
        "lane_preserving_arithmetic": [
            "add/sub preserve lane index",
            "mul/mls/sqrdmulh/sqdmulh preserve lane index",
            "Barrett srshr/mls reduction preserves lane index",
            "broadcast lane constants do not move coefficient lanes",
        ],
        "required_lane_mixing": {
            "reason": (
                "A rowpack plane vector needs one coefficient lane from each of "
                "eight k32-major source/result vectors.  With two-input Neon "
                "interleaves, fan-in can at most double per mixing stage, so "
                "three stages and eight live vector results per stage are needed."
            ),
            "lower_bound_permutes_per_block": 24,
            "matches_gate8_final_only_lower_bound": True,
        },
        "decision": {
            "do_not_author_stage345_only_candidate": True,
            "reason": (
                "Under the existing stage12 boundary, a stage345-only symbolic "
                "candidate cannot make rowpack planes naturally live-out without "
                "introducing a transpose-equivalent lane-mixing network.  That "
                "would only move the 24-permute/block cost rather than remove it."
            ),
            "next_viable_scope": "widen the rewrite to stage12+stage345, or change the stage12 scratch/live-out contract",
        },
    }


def summary_markdown(report: dict[str, object]) -> str:
    required = report["required_lane_mixing"]
    decision = report["decision"]
    return "\n".join(
        [
            "# Gate 9 Step 2 v3b Stage345 Feasibility",
            "",
            f"Status: `{report['status']}`",
            "",
            "## Boundary",
            "",
            f"- input: `{report['boundary']['input_shape']}`",
            f"- desired output: `{report['boundary']['desired_output_shape']}`",
            "",
            "## Lane-Preserving Arithmetic",
            "",
            *[f"- {item}" for item in report["lane_preserving_arithmetic"]],
            "",
            "## Required Lane Mixing",
            "",
            required["reason"],
            "",
            f"- lower bound: `{required['lower_bound_permutes_per_block']} permutes/block`",
            f"- matches Gate 8 final-only lower bound: `{required['matches_gate8_final_only_lower_bound']}`",
            "",
            "## Decision",
            "",
            f"- do not author current-boundary stage345-only candidate: `{decision['do_not_author_stage345_only_candidate']}`",
            f"- reason: {decision['reason']}",
            f"- next viable scope: `{decision['next_viable_scope']}`",
            "",
            "A candidate that starts from the current k32-major stage12 scratch and",
            "ends in rowpack plane vectors must still pay a transpose-equivalent",
            "lane-mixing network somewhere inside stage345.  That is not the v3b",
            "win condition.",
            "",
        ]
    )


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    SUMMARY.write_text(summary_markdown(report))
    print(f"wrote {SUMMARY}")
    print("decision: do not author current-boundary stage345-only v3b candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
