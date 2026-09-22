#!/usr/bin/env python3
"""Hard gate for kernel/baseline/candidate contract files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from contractlib import contains_placeholder, is_missing, load_flat_yaml, status_value


MODES = {
    "new_symbolic_kernel",
    "existing_region_replacement",
    "new_kernel_baseline_then_iterate",
    "oracle_scaffold_only",
    "post_slothy_review",
}

STATUS = {"reject", "investigate", "candidate", "promote"}

REQUIRED_KERNEL_KEYS = [
    "mode",
    "candidate_status",
    "kernel.id",
    "kernel.name",
    "kernel.source",
    "target.arch",
    "target.microarchitecture",
    "slothy.workflow",
    "slothy.allow_spills",
    "region.start_label",
    "region.end_label",
    "region.live_in",
    "region.live_out",
    "abi.inputs",
    "abi.outputs",
    "abi.concrete_gprs_allowed",
    "abi.reserved_registers",
    "instruction_dag.file",
    "layout.input_representation",
    "layout.output_representation",
    "memory_contract.loads",
    "memory_contract.stores",
    "memory_contract.aliasing",
    "memory_contract.alignment",
    "memory_contract.public_offsets_only",
    "constant_contract.constants",
    "constant_contract.modulus",
    "constant_contract.representation",
    "range_contract.input_ranges",
    "range_contract.output_ranges",
    "constant_time_contract.secret_inputs",
    "constant_time_contract.public_inputs",
    "constant_time_contract.no_secret_dependent_branches",
    "constant_time_contract.no_secret_dependent_memory_access",
    "validation.oracle_command",
    "validation.test_command",
    "validation.full_path_benchmark_command",
]

REQUIRED_BASELINE_KEYS = [
    "baseline.id",
    "baseline.source",
    "baseline.extracted_region",
    "baseline.function",
    "baseline.start_label",
    "baseline.end_label",
    "region.instruction_count",
    "region.live_in",
    "region.live_out",
    "abi.inputs",
    "abi.outputs",
    "memory_contract.loads",
    "memory_contract.stores",
    "memory_contract.public_offsets_only",
    "constant_time_contract.no_secret_dependent_branches",
    "constant_time_contract.no_secret_dependent_memory_access",
    "baseline_cost.static_instruction_count",
    "baseline_cost.benchmark_command",
]

REQUIRED_CANDIDATE_KEYS = [
    "candidate.id",
    "candidate.status",
    "candidate.kernel_contract",
    "candidate.symbolic_source",
    "candidate.slothy_driver",
    "contract_preservation.preserved",
    "contract_preservation.approved_changes",
    "region.start_label",
    "region.end_label",
    "region.live_in",
    "region.live_out",
    "abi.inputs",
    "abi.outputs",
    "memory_contract.loads",
    "memory_contract.stores",
    "memory_contract.public_offsets_only",
    "constant_time_contract.no_secret_dependent_branches",
    "constant_time_contract.no_secret_dependent_memory_access",
]


def infer_kind(path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    name = path.name
    if "baseline" in name:
        return "baseline"
    if "candidate" in name:
        return "candidate"
    return "kernel"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract")
    parser.add_argument("--kind", choices=["kernel", "baseline", "candidate"])
    parser.add_argument("--mode", choices=sorted(MODES))
    parser.add_argument("--candidate-source", help="Candidate .S path that this contract permits.")
    parser.add_argument("--allow-placeholders", action="store_true", help="Allow TODO/template placeholder values.")
    args = parser.parse_args()

    path = Path(args.contract)
    if not path.is_file():
        print(f"{path}: error[CONTRACT000]: contract file is required", file=sys.stderr)
        return 1

    data = load_flat_yaml(path)
    kind = infer_kind(path, args.kind)
    required = {
        "kernel": REQUIRED_KERNEL_KEYS,
        "baseline": REQUIRED_BASELINE_KEYS,
        "candidate": REQUIRED_CANDIDATE_KEYS,
    }[kind]

    errors: list[str] = []
    warnings: list[str] = []

    for key in required:
        if key not in data or is_missing(data[key]):
            if args.allow_placeholders:
                continue
            errors.append(f"{path}: error[CONTRACT001]: missing required field: {key}")
        elif not args.allow_placeholders and contains_placeholder(data[key]):
            errors.append(f"{path}: error[CONTRACT002]: placeholder value remains in field: {key}")

    mode = status_value(args.mode or data.get("mode") or data.get("candidate.mode"))
    if kind == "kernel":
        if mode not in MODES:
            errors.append(f"{path}: error[CONTRACT003]: mode must be one of {sorted(MODES)}")
        status = status_value(data.get("candidate_status"))
        if status not in STATUS:
            errors.append(f"{path}: error[CONTRACT004]: candidate_status must be one of {sorted(STATUS)}")
        if mode == "existing_region_replacement":
            baseline = Path(path.parent, "baseline-contract.yml")
            if not baseline.is_file():
                errors.append(f"{path}: error[CONTRACT005]: existing_region_replacement requires baseline-contract.yml before candidate .S generation")
        if mode == "oracle_scaffold_only" and args.candidate_source:
            errors.append(f"{path}: error[CONTRACT006]: oracle_scaffold_only must not generate candidate .S")

    if kind == "candidate":
        status = status_value(data.get("candidate.status"))
        if status not in STATUS:
            errors.append(f"{path}: error[CONTRACT007]: candidate.status must be one of {sorted(STATUS)}")

    if args.candidate_source:
        source = Path(args.candidate_source)
        if source.suffix not in {".S", ".s", ".asm", ".inc"}:
            warnings.append(f"{source}: warning[CONTRACT008]: candidate source has unusual suffix")
        contract_source = data.get("kernel.source") or data.get("candidate.symbolic_source")
        if contract_source and not contains_placeholder(contract_source):
            if Path(str(contract_source)).name != source.name:
                warnings.append(f"{path}: warning[CONTRACT009]: contract source '{contract_source}' differs from candidate '{source}'")

    for warning in warnings:
        print(warning, file=sys.stderr)
    for error in errors:
        print(error, file=sys.stderr)

    if errors:
        print(f"check-kernel-contract: failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"check-kernel-contract: {kind} contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
