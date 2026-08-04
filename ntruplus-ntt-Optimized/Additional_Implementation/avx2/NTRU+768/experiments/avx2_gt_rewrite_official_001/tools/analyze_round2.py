#!/usr/bin/env python3
"""Compute the Round 2 caller-weighted decomposition and Amdahl gate."""

import argparse
import json
from pathlib import Path


PARITY_CYCLES = 92906.0
PROMOTION_CYCLES = 86530.0
PLAN_PARITY_SAVING = 95420.0
PLAN_PROMOTION_SAVING = 99974.0


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stages", default="results/round2-stage-cycles.json")
    parser.add_argument("--counts", default="results/round2-call-counts.json")
    parser.add_argument("--gt-cycles", type=float, default=186861.520)
    parser.add_argument("--official-cycles", type=float, default=91088.810)
    parser.add_argument("--output", default="results/round2-amdahl.json")
    args = parser.parse_args()

    stage_data = load(args.stages)["stages"]
    stage = {name: value["median_cycles"]
             for name, value in stage_data.items()}
    count = load(args.counts)["triplet"]

    weighted = {
        "forward_frontend": count["ntt"] * stage["forward_frontend"],
        "forward_b1": count["ntt"] * stage["forward_b1"],
        "basemul_bm_a": (count["basemul"] + count["basemul_scale"])
                         * stage["basemul_bm_a"],
        "baseinv": count["baseinv"] * stage["baseinv"],
        "inverse_b1": count["invntt"] * stage["inverse_b1"],
        "inverse_tail": count["invntt"] * stage["inverse_tail"],
        "tobytes": count["tobytes"] * stage["tobytes"],
        "frombytes": count["frombytes"] * stage["frombytes"],
    }
    modeled = sum(weighted.values())
    c32 = weighted["forward_b1"] + weighted["inverse_b1"]
    required_parity = args.gt_cycles - PARITY_CYCLES
    required_promotion = args.gt_cycles - PROMOTION_CYCLES

    projections = {}
    for speedup in (2, 3, 4):
        saving = c32 * (1.0 - 1.0 / speedup)
        projections[f"{speedup}x"] = {
            "saving_cycles": saving,
            "projected_gt_cycles": args.gt_cycles - saving,
        }
    projections["infinite"] = {
        "saving_cycles": c32,
        "projected_gt_cycles": args.gt_cycles - c32,
    }

    theoretical_parity = c32 >= max(required_parity, PLAN_PARITY_SAVING)
    theoretical_promotion = c32 >= max(required_promotion,
                                        PLAN_PROMOTION_SAVING)
    decision = "proceed-paired-assembly" if theoretical_parity else \
        "stop-amdahl-theoretical-gate-failed"
    result = {
        "schema_version": 1,
        "baseline": {
            "official_cycles": args.official_cycles,
            "gt_cycles": args.gt_cycles,
            "research_parity_cycles": PARITY_CYCLES,
            "promotion_cycles": PROMOTION_CYCLES,
        },
        "call_counts": count,
        "stage_median_cycles": stage,
        "caller_weighted_stage_cycles": weighted,
        "modeled_gt_stage_cycles": modeled,
        "unattributed_kem_cycles": args.gt_cycles - modeled,
        "c32_cycles": c32,
        "required_saving": {
            "current_baseline_to_research_parity": required_parity,
            "current_baseline_to_promotion": required_promotion,
            "frozen_plan_parity": PLAN_PARITY_SAVING,
            "frozen_plan_promotion": PLAN_PROMOTION_SAVING,
            "current_baseline_to_official": args.gt_cycles
                                            - args.official_cycles,
        },
        "speedup_projections": projections,
        "optimistic_floor": {
            "cycles": 0.0,
            "reason": "zero is the strongest possible optimistic floor; "
                      "the theoretical infinite-speed gate already fails"
                      if not theoretical_parity else
                      "replace with the static load/uop/dependency floor",
        },
        "gates": {
            "theoretical_research_parity": theoretical_parity,
            "theoretical_promotion": theoretical_promotion,
            "decision": decision,
        },
    }
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n",
                                 encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
