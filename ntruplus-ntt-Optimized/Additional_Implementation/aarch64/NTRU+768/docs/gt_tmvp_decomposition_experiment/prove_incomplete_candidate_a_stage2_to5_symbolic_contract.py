#!/usr/bin/env python3
"""Contract probe for Candidate A stage2-to5 symbolic InvNTT32 rowkernel."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1].parent
KERNEL = "ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end"
SOURCE = (
    ROOT
    / "docs/gt_soa_layout_experiment/kernels"
    / f"{KERNEL}.sym.S"
)
DRIVER = (
    ROOT
    / "docs/gt_soa_layout_experiment"
    / f"optimize_{KERNEL}.py"
)
REPORT = (
    ROOT
    / "docs/gt_tmvp_decomposition_experiment"
    / "decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-symbolic-contract.yml"
)
MARKDOWN = REPORT.with_suffix(".md")

START = f"slothy_start_{KERNEL}:"
END = f"slothy_end_{KERNEL}:"
INSTR_RE = re.compile(r"^\s*[A-Za-z][A-Za-z0-9_.]*\b")
PHYS_VEC_RE = re.compile(r"\b[vq](?:[0-9]|[12][0-9]|3[01])(?:\.[0-9]+[bhsdq])?\b")


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].split("@", 1)[0]


def is_instruction(line: str) -> bool:
    stripped = strip_comment(line).strip()
    return bool(stripped and not stripped.startswith(".") and not stripped.endswith(":") and INSTR_RE.match(stripped))


def region_lines(lines: list[str]) -> list[str]:
    try:
        start = lines.index(START)
        end = lines.index(END)
    except ValueError as exc:
        raise SystemExit(f"missing Slothy label: {exc}") from exc
    if not start < end:
        raise SystemExit("Slothy labels are not ordered")
    return lines[start + 1:end]


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing symbolic source: {SOURCE}")
    if not DRIVER.exists():
        raise SystemExit(f"missing Slothy driver: {DRIVER}")

    source_text = SOURCE.read_text()
    driver_text = DRIVER.read_text()
    lines = source_text.splitlines()
    region = region_lines(lines)
    region_code = "\n".join(strip_comment(line) for line in region)
    instruction_count = sum(1 for line in region if is_instruction(line))
    physical_vector_leaks = [
        token
        for line in region
        for token in PHYS_VEC_RE.findall(strip_comment(line))
    ]

    checks = {
        "stage1_instructions_removed": "rev32" not in region_code,
        "stage1_mask_constant_not_loaded": "c_odd" not in region_code,
        "row_input_barrett_removed": "sqdmulh" not in region_code,
        "row_end_barrett_removed": "V<x0_red>" not in region_code and "V<x1_red>" not in region_code,
        "stage2_present": "Stage 2:" in source_text and "V<x0_s2>" in source_text,
        "stage3_present": "Stage 3:" in source_text and "V<x0_s3>" in source_text,
        "stage4_present": "Stage 4:" in source_text and "V<x0_s4>" in source_text,
        "stage5_present": "Stage 5:" in source_text and "V<x0_s5>" in source_text,
        "slothy_region_medium_size": 50 <= instruction_count <= 150,
        "physical_vector_registers_absent": len(physical_vector_leaks) == 0,
        "driver_uses_ra_then_window_workflow": "register_allocate_only" in driver_text and "window_optimize_allocated" in driver_text,
        "driver_does_not_overwrite_symbolic_source": ".alloc.S" in driver_text and ".opt.S" in driver_text,
    }

    status = "pass" if all(checks.values()) else "fail"

    REPORT.write_text(
        "\n".join(
            [
                f"candidate_a_stage2_to5_symbolic_contract_status: {status}",
                "selected_path: incomplete_stage4_candidate_a_tmvp_to_invntt_stage2_to5_symbolic",
                "source_kind: slothy_symbolic_asm",
                f"symbolic_source: {SOURCE.relative_to(ROOT)}",
                f"slothy_driver: {DRIVER.relative_to(ROOT)}",
                f"kernel: {KERNEL}",
                "input_state: invntt_rowkernel_after_stage1_adapter",
                "rowkernel_stage1_skipped: true",
                "row_input_barrett_removed: true",
                "row_end_barrett_removed: true",
                "candidate_rowkernel: symbolic_no_entry_no_end_stage2_to5",
                "slothy_workflow: ra_then_window_opt",
                f"region_instruction_count: {instruction_count}",
                f"physical_vector_leak_count: {len(physical_vector_leaks)}",
                f"stage1_instructions_removed: {str(checks['stage1_instructions_removed']).lower()}",
                f"stage1_mask_constant_not_loaded: {str(checks['stage1_mask_constant_not_loaded']).lower()}",
                f"stage2_present: {str(checks['stage2_present']).lower()}",
                f"stage3_present: {str(checks['stage3_present']).lower()}",
                f"stage4_present: {str(checks['stage4_present']).lower()}",
                f"stage5_present: {str(checks['stage5_present']).lower()}",
                f"driver_uses_ra_then_window_workflow: {str(checks['driver_uses_ra_then_window_workflow']).lower()}",
                "slothy_run_claimed: false",
                "allocated_or_optimized_asm_generated: false",
                "asm_implemented: false",
                "benchmark_or_cycle_claim_made: false",
                "recommended_next_gate: run_slothy_ra_then_window_generate_stage2_to5_asm_then_test",
                "",
            ]
        )
    )

    MARKDOWN.write_text(
        "\n".join(
            [
                "# Candidate A stage2-to5 symbolic contract",
                "",
                f"Status: `{status}`",
                "",
                f"- Source: `{SOURCE.relative_to(ROOT)}`",
                f"- Driver: `{DRIVER.relative_to(ROOT)}`",
                f"- Region instructions: `{instruction_count}`",
                "- Workflow: `ra_then_window_opt`",
                "- This probe does not run Slothy or claim cycles.",
                "",
            ]
        )
    )

    if status != "pass":
        failed = ", ".join(k for k, v in checks.items() if not v)
        raise SystemExit(f"Candidate A stage2-to5 symbolic contract failed: {failed}")

    print(
        "Candidate A stage2-to5 symbolic contract: pass "
        f"instructions={instruction_count}"
    )


if __name__ == "__main__":
    main()
