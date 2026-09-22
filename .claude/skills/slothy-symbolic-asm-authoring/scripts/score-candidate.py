#!/usr/bin/env python3
"""Score a Slothy candidate and emit reject/investigate/candidate/promote."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from contractlib import load_flat_yaml, status_value, value_bool, value_float


STATUSES = {"reject", "investigate", "candidate", "promote"}
PASS_VALUES = {"pass", "passed", "ok", "true", "yes"}
FAIL_VALUES = {"fail", "failed", "false", "no", "error"}


def is_pass(value: object) -> bool:
    return status_value(value) in PASS_VALUES


def is_fail(value: object) -> bool:
    return status_value(value) in FAIL_VALUES


def pct_delta(baseline: float, candidate: float) -> float:
    if baseline == 0:
        return 0.0 if candidate == 0 else 100.0
    return ((candidate - baseline) / abs(baseline)) * 100.0


def decide(data: dict[str, object]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    input_status = status_value(data.get("candidate.status"))
    if input_status not in STATUSES:
        reasons.append("candidate.status is missing or invalid")

    contract_ok = value_bool(data.get("contract.preserved")) or value_bool(data.get("contract.approved_changes"))
    if not contract_ok:
        reasons.append("contract is not preserved and approved changes are not recorded")

    correctness_keys = ["correctness.oracle", "correctness.tests", "correctness.abi"]
    correctness_fail = any(is_fail(data.get(key)) for key in correctness_keys)
    correctness_pass = all(is_pass(data.get(key)) for key in correctness_keys)
    ct_value = status_value(data.get("correctness.constant_time_review"))
    constant_time_ok = ct_value in PASS_VALUES or ct_value in {"not_applicable", "n/a"}
    if correctness_fail:
        reasons.append("correctness gate failed")
    if not correctness_pass:
        reasons.append("correctness evidence is incomplete")
    if not constant_time_ok:
        reasons.append("constant-time review is incomplete")

    slothy_status = status_value(data.get("slothy.status"))
    baseline_cycles = value_float(data.get("slothy.baseline_expected_cycles"))
    candidate_cycles = value_float(data.get("slothy.candidate_expected_cycles"))
    parity_note = str(data.get("slothy.parity_justification") or "").strip()
    if slothy_status not in PASS_VALUES:
        reasons.append("Slothy result is missing or not pass")
    if candidate_cycles is None:
        reasons.append("candidate Slothy expected cycles are missing")
    cycle_ok = False
    if baseline_cycles is not None and candidate_cycles is not None:
        if candidate_cycles < baseline_cycles:
            cycle_ok = True
        elif candidate_cycles == baseline_cycles and parity_note:
            cycle_ok = True
        else:
            reasons.append("Slothy expected cycles do not improve or justify parity")
    elif candidate_cycles is not None and parity_note:
        cycle_ok = True

    bench_status = status_value(data.get("benchmark.status"))
    baseline_bench = value_float(data.get("benchmark.baseline"))
    candidate_bench = value_float(data.get("benchmark.candidate"))
    lower_is_better = value_bool(data.get("benchmark.lower_is_better"), True)
    threshold = value_float(data.get("benchmark.neutral_threshold_percent"))
    if threshold is None:
        threshold = 1.0
    benchmark_ok = False
    benchmark_regressed = False
    if bench_status in PASS_VALUES and baseline_bench is not None and candidate_bench is not None:
        delta = pct_delta(baseline_bench, candidate_bench)
        if not lower_is_better:
            delta = -delta
        benchmark_ok = delta <= threshold
        benchmark_regressed = delta > threshold
        if benchmark_regressed:
            reasons.append(f"full-path benchmark regressed by {delta:.3f}% beyond {threshold:.3f}% threshold")
    else:
        reasons.append("full-path benchmark evidence is missing")

    if correctness_fail or benchmark_regressed or (not contract_ok and input_status == "reject"):
        return "reject", reasons
    if contract_ok and correctness_pass and constant_time_ok and slothy_status in PASS_VALUES and cycle_ok and benchmark_ok:
        return "promote", reasons
    if contract_ok and correctness_pass and slothy_status in PASS_VALUES and candidate_cycles is not None:
        return "candidate", reasons
    return "investigate", reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_score")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = Path(args.candidate_score)
    if not path.is_file():
        print(f"score-candidate: error: score file not found: {path}", file=sys.stderr)
        return 1

    data = load_flat_yaml(path)
    status, reasons = decide(data)
    result = {"score_file": str(path), "status": status, "reasons": reasons}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"candidate_status: {status}")
        for reason in reasons:
            print(f"- {reason}")

    return 0 if status in {"candidate", "promote"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
