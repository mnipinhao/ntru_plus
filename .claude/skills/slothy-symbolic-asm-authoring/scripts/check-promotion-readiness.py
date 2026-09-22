#!/usr/bin/env python3
"""Hard gate for promotion readiness."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

from contractlib import load_flat_yaml, status_value, value_bool, value_float


PASS_VALUES = {"pass", "passed", "ok", "true", "yes"}


def load_decide():
    script = Path(__file__).with_name("score-candidate.py")
    spec = importlib.util.spec_from_file_location("score_candidate_script", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load scoring script: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decide


def require_file(path_text: str | None, label: str, errors: list[str]) -> None:
    if not path_text:
        errors.append(f"missing {label}")
        return
    if not Path(path_text).is_file():
        errors.append(f"{label} does not exist: {path_text}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-score", required=True)
    parser.add_argument("--kernel-contract", required=True)
    parser.add_argument("--candidate-contract", required=True)
    parser.add_argument("--baseline-contract")
    parser.add_argument("--mode", choices=[
        "new_symbolic_kernel",
        "existing_region_replacement",
        "new_kernel_baseline_then_iterate",
        "post_slothy_review",
    ], default="new_symbolic_kernel")
    parser.add_argument("--slothy-result-json")
    parser.add_argument("--oracle-report")
    parser.add_argument("--benchmark-report")
    args = parser.parse_args()

    errors: list[str] = []
    require_file(args.candidate_score, "candidate score", errors)
    require_file(args.kernel_contract, "kernel contract", errors)
    require_file(args.candidate_contract, "candidate contract", errors)
    if args.mode == "existing_region_replacement":
        require_file(args.baseline_contract, "baseline contract", errors)
    if args.slothy_result_json:
        require_file(args.slothy_result_json, "Slothy result JSON", errors)
    if args.oracle_report:
        require_file(args.oracle_report, "oracle report", errors)
    if args.benchmark_report:
        require_file(args.benchmark_report, "benchmark report", errors)

    if errors:
        for error in errors:
            print(f"check-promotion-readiness: error: {error}", file=sys.stderr)
        return 1

    data = load_flat_yaml(args.candidate_score)
    computed_status, reasons = load_decide()(data)
    recorded_status = status_value(data.get("candidate.status"))
    if recorded_status != "promote" or computed_status != "promote":
        print(f"check-promotion-readiness: error: status must be promote; recorded={recorded_status} computed={computed_status}", file=sys.stderr)
        for reason in reasons:
            print(f"- {reason}", file=sys.stderr)
        return 1

    checks = {
        "contract preserved or approved": value_bool(data.get("contract.preserved")) or value_bool(data.get("contract.approved_changes")),
        "oracle pass": status_value(data.get("correctness.oracle")) in PASS_VALUES,
        "tests pass": status_value(data.get("correctness.tests")) in PASS_VALUES,
        "abi pass": status_value(data.get("correctness.abi")) in PASS_VALUES,
        "slothy pass": status_value(data.get("slothy.status")) in PASS_VALUES,
        "candidate cycles recorded": value_float(data.get("slothy.candidate_expected_cycles")) is not None,
        "benchmark pass": status_value(data.get("benchmark.status")) in PASS_VALUES,
        "benchmark baseline recorded": value_float(data.get("benchmark.baseline")) is not None,
        "benchmark candidate recorded": value_float(data.get("benchmark.candidate")) is not None,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        for name in failed:
            print(f"check-promotion-readiness: error: failed gate: {name}", file=sys.stderr)
        return 1

    print("check-promotion-readiness: promotion gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
