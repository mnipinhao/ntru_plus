#!/usr/bin/env python3
"""Close the localized D8 repair proof under the signed-i16 register contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
I16 = range(-32768, 32768)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repair-plan", type=Path, required=True)
    parser.add_argument("--m3-oracle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    plan = json.loads(args.repair_plan.read_text())
    m3 = json.loads(args.m3_oracle.read_text())
    if plan["decision"]["M3C2"] != "candidate-selected-proof-open":
        raise SystemExit("M3C2-P requires the proof-open selected repair plan")
    if m3["inverse_order"] != [1, 2, 4, 8]:
        raise SystemExit("M3C2-P requires the fixed inverse16 stage order")

    centered_values = [centered(value) for value in I16]
    centered_min = min(centered_values)
    centered_max = max(centered_values)
    if (centered_min, centered_max) != (-1728, 1728):
        raise SystemExit("centered representative bound changed")
    if any((reduced - value) % Q for value, reduced in zip(I16, centered_values)):
        raise SystemExit("centered reduction lost modular identity")

    actions = {
        "none": {
            "operand_absolute_bounds": [32768, 32768],
            "worst_pre_montgomery_absolute": 65536,
            "witness": {"left": -32768, "right": -32768,
                        "operation": "sum", "value": -65536},
        },
        "reduce_left": {
            "operand_absolute_bounds": [1728, 32768],
            "worst_pre_montgomery_absolute": 34496,
            "witness": {"left_after_repair": -1728, "right": -32768,
                        "operation": "sum", "value": -34496},
        },
        "reduce_right": {
            "operand_absolute_bounds": [32768, 1728],
            "worst_pre_montgomery_absolute": 34496,
            "witness": {"left": -32768, "right_after_repair": -1728,
                        "operation": "sum", "value": -34496},
        },
        "reduce_both": {
            "operand_absolute_bounds": [1728, 1728],
            "worst_pre_montgomery_absolute": 3456,
            "safe_signed_i16": True,
        },
    }
    for name in ("none", "reduce_left", "reduce_right"):
        actions[name]["safe_signed_i16"] = False

    document = {
        "schema": "gt-g1c-m3c2p-localized-exact-proof/v1",
        "checkpoint": "G1C-M3C2-P-localized-D8-proof",
        "proof_scope": {
            "precondition": (
                "both D8 inputs exist as signed-i16 D4 register values"),
            "proved": (
                "which repair actions make both D8 sum and difference fit "
                "signed i16 for every value satisfying that precondition"),
            "not_proved": (
                "producer-correlated D2/D4 safety before the D8 boundary"),
        },
        "lemma": {
            "identity": "max(abs(u+v), abs(u-v)) = abs(u)+abs(v)",
            "centered_mod_q_range_exhaustive_over_65536_i16_inputs": [
                centered_min, centered_max],
            "centered_reduction_preserves_mod_q": True,
            "actions": actions,
        },
        "selected_cover_audit": {
            "corpus_selected_logical_repairs": plan["logical_minimum"]
            ["scalar_reductions_per_inverse16"],
            "corpus_selected_vector_chains": plan["avx2_projection"]
            ["adjacent_row_half_set_cover"]["vector_reduction_chains"],
            "result": "rejected-by-exact-signed-i16-contract",
            "reason": (
                "one-sided repair leaves an operand with absolute bound 32768; "
                "32768+1728=34496 exceeds signed i16. Unrepaired nodes fail "
                "even more directly. Corpus maxima cannot replace this bound."),
        },
        "minimum_proved_cover": {
            "action_per_D8_node": "reduce_both",
            "D8_nodes": 576,
            "D4_values_repaired": 1152,
            "terminal_YMM_vectors_repaired": 72,
            "post_repair_D8_sum_difference_range": [-3456, 3456],
            "minimality": (
                "Under independent signed-i16 D4 operands, none and either "
                "one-sided action have explicit witnesses; both is the only "
                "universally safe action for each node."),
        },
        "decision": {
            "M3C2_P": "complete-selected-cover-rejected",
            "M3C3_full_reduction_control": "authorized-for-isolated-implementation-and-pricing",
            "full_inverse16_assembly": (
                "still blocked by producer-correlated D2/D4 proof and full-caller "
                "correctness"),
        },
        "source_sha256": {"repair_plan": digest(args.repair_plan),
                          "m3_oracle": digest(args.m3_oracle)},
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C-M3C2-P proof is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
