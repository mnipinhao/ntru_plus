#!/usr/bin/env python3
"""Machine-check M5O/M5N dynamic counts and M5M physical allocation."""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
TOP = EXPERIMENTS / "gt_2x9x16_ld3_top_split/gt864_top_split.s"
M5M = EXPERIMENTS / "gt_forward_one_bank_slothy"
SYMBOLIC = M5M / "gt864_forward_one_bank.sym.S"
ALLOCATED = M5M / "slothy-output/gt864_forward_one_bank.n1.alloc.S"

PLACEHOLDER = re.compile(r"[VQ]<([A-Za-z0-9_]+)>")
VECTOR = re.compile(r"\b[vq](\d+)\b", re.IGNORECASE)


def code(raw: str) -> str:
    return raw.split("//", 1)[0].strip()


def is_instruction(line: str) -> bool:
    return bool(line and not line.startswith(".") and not line.endswith(":"))


def instructions(text: str) -> list[str]:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return [line for raw in text.splitlines()
            if is_instruction(line := code(raw))]


def symbolic_stages() -> tuple[list[str], list[str]]:
    stage = "common_modulus"
    stages: list[str] = []
    body: list[str] = []
    transitions = (
        ("x1 = &p8", "tail_gather"),
        ("Branch twist", "tail_twist"),
        ("DIT length 2", "tail_ntt16_length2"),
        ("DIT length 4", "tail_ntt16_length4"),
        ("DIT length 8", "tail_ntt16_length8"),
        ("DIT length 16", "tail_ntt16_length16"),
        ("raw lanes are bit-reverse-3", "tail_canonicalize"),
        ("Main P8 branch twist", "main_branch_twist"),
        ("Main NTT16 DIT length 2", "main_ntt16_length2"),
        ("Main NTT16 DIT length 4", "main_ntt16_length4"),
        ("Main NTT16 DIT length 8", "main_ntt16_length8"),
        ("Main NTT16 DIT length 16", "main_ntt16_length16"),
        ("Delay roots", "delayed_roots"),
        ("Transpose columns 0..7", "transpose_block0"),
        ("Transpose columns 8..15", "transpose_block1"),
        ("f0 has identity twist", "twist_block0"),
        ("Complete M5I NTT9 core", "ntt9_block0"),
        ("Capture the fixed tail", "capture_tail1"),
        ("Twist held rows", "twist_block1"),
        ("Level 1 A", "ntt9_block1"),
    )
    text = SYMBOLIC.read_text(encoding="utf-8")
    region = text.split("gt864_forward_one_bank_slothy_start:", 1)[1]
    region = region.split("gt864_forward_one_bank_slothy_end:", 1)[0]
    for raw in region.splitlines():
        stripped = raw.strip()
        if stripped.startswith("//"):
            comment = stripped[2:].strip()
            for prefix, new_stage in transitions:
                if comment.startswith(prefix):
                    stage = new_stage
                    break
            continue
        line = code(raw)
        if is_instruction(line):
            body.append(line)
            stages.append(stage)
    assert len(body) == 633
    return body, stages


def allocated_instructions() -> list[str]:
    text = ALLOCATED.read_text(encoding="utf-8")
    region = text.split("gt864_forward_one_bank_slothy_start:", 1)[1]
    region = region.split("gt864_forward_one_bank_slothy_end:", 1)[0]
    body = instructions(region)
    assert len(body) == 633
    return body


def vector_tokens_symbolic(line: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"[VQ]<([A-Za-z0-9_]+)>|\bv(\d+)\b", re.IGNORECASE)
    result: list[tuple[str, str]] = []
    for match in pattern.finditer(line):
        if match.group(1) is not None:
            result.append(("symbol", match.group(1)))
        else:
            result.append(("fixed", f"v{int(match.group(2))}"))
    return result


def recover_registers(symbolic: list[str], allocated: list[str],
                      stages: list[str]) -> dict[str, dict[str, object]]:
    recovered: dict[str, dict[str, object]] = {}
    for index, (sym, physical, stage) in enumerate(zip(symbolic, allocated, stages)):
        assert sym.split()[0].lower() == physical.split()[0].lower(), (index, sym, physical)
        sym_tokens = vector_tokens_symbolic(sym)
        physical_tokens = [f"v{int(value)}" for value in VECTOR.findall(physical)]
        assert len(sym_tokens) == len(physical_tokens), (index, sym, physical)
        for (kind, name), register in zip(sym_tokens, physical_tokens):
            if kind == "fixed":
                assert name == register, (index, name, register)
                continue
            entry = recovered.setdefault(name, {
                "register": register,
                "first_instruction": index,
                "last_instruction": index,
                "first_stage": stage,
                "last_stage": stage,
            })
            assert entry["register"] == register, (name, entry["register"], register)
            entry["last_instruction"] = index
            entry["last_stage"] = stage
    return recovered


def top_split_ledger() -> dict[str, object]:
    text = TOP.read_text(encoding="utf-8")
    before, rest = text.split(".Ltop_split_loop:", 1)
    loop, _ = rest.split("    ret", 1)
    pre = instructions(before)
    body = instructions(loop)
    assert len(pre) == 16 and len(body) == 52
    dynamic = len(pre) + 16 * len(body) + 1
    assert dynamic == 849
    return {
        "pre_loop": len(pre),
        "loop_iterations": 16,
        "instructions_per_iteration": len(body),
        "return": 1,
        "dynamic_instructions": dynamic,
        "loop_mnemonics_per_iteration": dict(sorted(collections.Counter(
            line.split()[0].lower() for line in body
        ).items())),
    }


def main() -> None:
    symbolic, stages = symbolic_stages()
    allocated = allocated_instructions()
    registers = recover_registers(symbolic, allocated, stages)
    stage_counts = collections.Counter(stages)
    assert sum(stage_counts.values()) == 633

    expected_groups = {
        "common_modulus": 1,
        "tail": 65,
        "main_branch_twist": 68,
        "main_ntt16": 165,
        "delayed_roots": 1,
        "two_ntt9_blocks": 333,
    }
    actual_groups = {
        "common_modulus": stage_counts["common_modulus"],
        "tail": sum(count for name, count in stage_counts.items()
                    if name.startswith("tail_")),
        "main_branch_twist": stage_counts["main_branch_twist"],
        "main_ntt16": sum(count for name, count in stage_counts.items()
                          if name.startswith("main_ntt16_")),
        "delayed_roots": stage_counts["delayed_roots"],
        "two_ntt9_blocks": sum(stage_counts[name] for name in (
            "transpose_block0", "transpose_block1", "twist_block0",
            "ntt9_block0", "capture_tail1", "twist_block1", "ntt9_block1"
        )),
    }
    assert actual_groups == expected_groups

    helper_per_bank = 633
    banks = 6
    pass2_shell = {
        "public_prologue_epilogue": 6,
        "bank_pointer_table_setup_and_bl": 42,
        "helper_ret": 6,
        "fr0_vector_stores": 108,
    }
    pass2_dynamic = banks * helper_per_bank + sum(pass2_shell.values())
    assert pass2_dynamic == 3960
    wrapper_dynamic = 16
    top = top_split_ledger()
    total = wrapper_dynamic + int(top["dynamic_instructions"]) + pass2_dynamic
    assert total == 4825

    output_registers = {
        f"out{i}": registers[f"out{i}"]["register"] for i in range(18)
    }
    expected_outputs = [
        "v26", "v30", "v7", "v25", "v19", "v21", "v3", "v24", "v22",
        "v23", "v2", "v0", "v31", "v28", "v18", "v5", "v29", "v20",
    ]
    assert list(output_registers.values()) == expected_outputs

    stage_mnemonics: dict[str, dict[str, int]] = {}
    for stage in stage_counts:
        stage_mnemonics[stage] = dict(sorted(collections.Counter(
            line.split()[0].lower() for line, owner in zip(symbolic, stages)
            if owner == stage
        ).items()))

    report = {
        "gate": "M5Q_dynamic_instruction_and_register_allocation",
        "status": "pass",
        "common_harness_instructions_from_m5p": 7,
        "official_kernel_dynamic_instructions": 4028,
        "gt_kernel_dynamic_instructions": total,
        "gt_minus_official": total - 4028,
        "top_split": top,
        "full_wrapper_dynamic_instructions": wrapper_dynamic,
        "pass2": {
            "dynamic_instructions": pass2_dynamic,
            "helper_runs": banks,
            "helper_instructions_per_run": helper_per_bank,
            "helper_dynamic_instructions": banks * helper_per_bank,
            "shell": pass2_shell,
        },
        "one_bank_stage_counts": dict(stage_counts),
        "one_bank_group_counts": actual_groups,
        "one_bank_stage_mnemonics": stage_mnemonics,
        "full_gt_stage_dynamic": {
            "m5o_wrapper": 16,
            "top_split": 849,
            "pass2_shell_control": 54,
            "pass2_fr0_stores": 108,
            "common_modulus": 6,
            "tail_ntt16": 390,
            "main_branch_twist": 408,
            "main_ntt16": 990,
            "delayed_roots": 6,
            "two_oriented_ntt9_blocks": 1998,
        },
        "physical_vector_set": sorted(
            {str(entry["register"]) for entry in registers.values()},
            key=lambda value: int(value[1:])),
        "fixed_vectors": ["v16", "v17"],
        "forbidden_vectors": [f"v{i}" for i in range(8, 16)],
        "symbolic_value_count": len(registers),
        "output_registers": output_registers,
        "symbolic_register_lifetimes": registers,
    }
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(json.dumps(report, indent=2) + "\n",
                                     encoding="utf-8")
    else:
        compact = dict(report)
        compact.pop("symbolic_register_lifetimes")
        print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()
