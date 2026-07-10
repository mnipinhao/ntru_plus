#!/usr/bin/env python3
"""Conservative reachable-bound model for inverse NTT32 twiddle=1 sites."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
Q = 3457
CENTER = (Q - 1) // 2
LENGTHS = (2, 4, 8, 16, 32)


def model(delete_identity_lengths: set[int]) -> dict[str, object]:
    bounds = [CENTER] * 32
    stages: list[dict[str, object]] = []
    safe = True
    for length in LENGTHS:
        half = length // 2
        next_bounds = list(bounds)
        sites = 0
        for start in range(0, 32, length):
            for lane in range(half):
                lo = bounds[start + lane]
                hi = bounds[start + lane + half]
                identity = lane == 0
                delete = identity and length in delete_identity_lengths
                product = hi if delete else CENTER
                out = lo + product
                next_bounds[start + lane] = out
                next_bounds[start + lane + half] = out
                sites += int(delete)
                safe &= out <= 32767
        bounds = next_bounds
        stages.append(
            {
                "length": length,
                "deleted_identity_sites": sites,
                "max_abs_after_stage": max(bounds),
                "int16_safe": max(bounds) <= 32767,
            }
        )
    return {
        "deleted_identity_lengths": sorted(delete_identity_lengths),
        "stages": stages,
        "final_max_abs_before_row_end_reduction": max(bounds),
        "int16_safe": safe,
    }


def main() -> int:
    candidates = {
        "stage123_only": model({2, 4, 8}),
        "through_len16": model({2, 4, 8, 16}),
        "all_identity_sites": model({2, 4, 8, 16, 32}),
    }
    report = {
        "input_contract": [-CENTER, CENTER],
        "assumption": (
            "Every retained modular multiply returns a centered residue with "
            f"absolute value <= {CENTER}; add/sub use signed int16 lanes."
        ),
        "candidates": candidates,
        "selected": "through_len16",
        "selected_reason": (
            "Stage123 plus len16 reaches max abs 29376 after the retained "
            "len32 stage and before row-end reduction."
        ),
        "rejected": {
            "all_identity_sites": (
                "The DC path reaches absolute bound 55296 before final row "
                "reduction, exceeding signed int16."
            )
        },
        "instruction_delta_selected": {
            "identity_fqmul_sites_per_row": 30,
            "rows": 3,
            "instructions_per_fqmul": 3,
            "dynamic_vector_instructions_removed": 270,
        },
    }
    (ROOT / "twiddle1_range_proof.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# InvNTT twiddle=1 range proof",
        "",
        f"Input contract: centered coefficients in `[-{CENTER}, {CENTER}]`.",
        "",
        "| candidate | max abs | int16 safe | decision |",
        "|---|---:|---|---|",
    ]
    for name, item in candidates.items():
        decision = "selected" if name == "through_len16" else (
            "proof-only" if item["int16_safe"] else "rejected"
        )
        lines.append(
            f"| `{name}` | {item['final_max_abs_before_row_end_reduction']} | "
            f"{'yes' if item['int16_safe'] else 'no'} | {decision} |"
        )
    lines.extend(
        [
            "",
            "The selected candidate removes 30 identity modular multiplies per row,",
            "or 270 dynamic vector instructions across three rows. The len32 stage",
            "and row-end Barrett reductions remain unchanged.",
            "",
            "Deleting every identity multiply is unsafe under this contract: the",
            "DC path reaches 55296 before the final row reduction.",
        ]
    )
    (ROOT / "twiddle1_range_proof.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print("invntt_twiddle1_stage123_max_abs=13824")
    print("invntt_twiddle1_all_max_abs=55296")
    print("invntt_twiddle1_selected_removed_instructions=270")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
