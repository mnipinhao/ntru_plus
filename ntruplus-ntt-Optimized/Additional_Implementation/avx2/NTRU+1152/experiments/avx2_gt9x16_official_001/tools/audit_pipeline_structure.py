#!/usr/bin/env python3
"""Compare Official leaf assembly with the linked GT correctness pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

OFFICIAL = {
    "poly_ntt": "forward",
    "poly_basemul": "basemul",
    "poly_basemul_scale": "basemul-scale",
    "poly_baseinv_1": "baseinv",
    "poly_invntt_scale": "inverse",
}
GT = {
    "ntruplus1152_exp001_gt9x16_forward_small": "full-forward-orchestrator",
    "ntruplus1152_exp001_top_split_small": "top-split",
    "ntruplus1152_exp001_top_split_to_gt_adapter": "adapter/pre-twist",
    "ntruplus1152_exp001_gt9x16_shear_stage8": "shear/distance-8",
    "ntruplus1152_exp001_gt9x16_ntt16_finish_row": "NTT16 distances-4/2/1",
    "ntruplus1152_exp001_ntt9_reference": "two-radix3 NTT9",
}
LOOP_CLASSIFICATION = {
    "poly_ntt": "hand-vectorized fixed loops",
    "poly_basemul": "hand-vectorized fixed loops",
    "poly_basemul_scale": "hand-vectorized fixed loops",
    "poly_baseinv_1": "hand-vectorized fixed loops",
    "poly_invntt_scale": "hand-vectorized fixed loops",
    "ntruplus1152_exp001_gt9x16_forward_small": "scalar orchestration around vector helpers and compiler-vectorized scatter",
    "ntruplus1152_exp001_top_split_small": "explicit AVX2 fixed loop",
    "ntruplus1152_exp001_top_split_to_gt_adapter": "mixed compiler-vectorized gather/pre-twist with scalar index control",
    "ntruplus1152_exp001_gt9x16_shear_stage8": "straight-line explicit AVX2",
    "ntruplus1152_exp001_gt9x16_ntt16_finish_row": "straight-line explicit AVX2",
    "ntruplus1152_exp001_ntt9_reference": "scalar source fully vectorized/unrolled by GCC",
}


def disassembly(path: Path) -> str:
    return subprocess.run(["objdump", "-d", "-M", "intel", str(path)], check=True,
                          text=True, stdout=subprocess.PIPE).stdout


def function_lines(text: str, name: str) -> list[str]:
    header = re.search(rf"^[0-9a-f]+ <{re.escape(name)}>:$", text, re.MULTILINE)
    if not header:
        raise SystemExit(f"missing disassembly symbol {name}")
    lines = []
    for line in text[header.end():].splitlines():
        if re.match(r"^[0-9a-f]+ <", line) and not lines:
            continue
        if re.match(r"^\s*[0-9a-f]+:\s+", line):
            lines.append(line)
            if re.search(r"\bret[q]?\b", line):
                break
    if not lines or not re.search(r"\bret[q]?\b", lines[-1]):
        raise SystemExit(f"did not find complete function body for {name}")
    return lines


def instruction_address(line: str) -> int:
    return int(line.split(":", 1)[0].strip(), 16)


def summarize(lines: list[str], role: str, name: str) -> dict:
    calls = []
    back_edges = 0
    for line in lines:
        call = re.search(r"\bcall[q]?\s+[0-9a-fx]+\s+<([^>]+)>", line)
        if call:
            calls.append(call.group(1))
        jump = re.search(r"\bj(?!mp\b)[a-z]+\s+([0-9a-f]+)\s+<", line)
        if jump and int(jump.group(1), 16) < instruction_address(line):
            back_edges += 1
    vector = [line for line in lines if re.search(r"\s+v[a-z0-9]+\s", line)]
    vector_memory = [line for line in vector if "PTR [" in line]
    vector_stores = []
    vector_loads = []
    for line in vector_memory:
        instruction = line.rsplit("\t", 1)[-1].strip()
        operands = instruction.split(None, 1)[1]
        first_operand = operands.split(",", 1)[0]
        (vector_stores if "PTR [" in first_operand else vector_loads).append(line)
    stack_vector = [line for line in vector if re.search(r"\[(?:r|e)(?:sp|bp)[+\-\]]", line)]
    stack_sub = [int(value, 16) for value in re.findall(r"\bsub\s+rsp,0x([0-9a-f]+)", "\n".join(lines))]
    pushes = sum(bool(re.search(r"\bpush\s+r", line)) for line in lines)
    return {
        "role": role,
        "loop_classification": LOOP_CLASSIFICATION[name],
        "static_instruction_count": len(lines),
        "internal_direct_calls": calls,
        "internal_direct_call_count": len(calls),
        "stack_sub_bytes": sum(stack_sub),
        "callee_saved_pushes": pushes,
        "vzeroupper_count": sum("vzeroupper" in line for line in lines),
        "vector_instruction_count": len(vector),
        "vector_memory_instruction_count": len(vector_memory),
        "vector_load_or_memory_operand_count": len(vector_loads),
        "vector_store_instruction_count": len(vector_stores),
        "vector_stack_reference_count": len(stack_vector),
        "conditional_back_edges": back_edges,
        "scalar_integer_multiply_count": sum(
            bool(re.search(r"\bimul\b", line)) for line in lines),
        "ret_count": sum(bool(re.search(r"\bret[q]?\b", line)) for line in lines),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-elf", type=Path, required=True)
    parser.add_argument("--official-object", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", default="cc")
    parser.add_argument("--cflags", required=True)
    args = parser.parse_args()
    report = {
        "compiler": subprocess.run([args.compiler, "--version"], check=True, text=True,
                                   stdout=subprocess.PIPE).stdout.splitlines()[0],
        "candidate_cflags": args.cflags,
        "candidate_elf": str(args.candidate_elf),
        "candidate_elf_sha256": hashlib.sha256(args.candidate_elf.read_bytes()).hexdigest(),
        "official": {},
        "gt_correctness_baseline": {},
        "audit_questions": {
            "vzeroupper_policy": "observe only; do not insert without a measured outer AVX/SSE boundary",
            "target_shape": "one leaf-ish GT arithmetic function with no internal hot-stage calls",
        },
        "gt_dynamic_boundaries_per_forward": {
            "top_split_calls": 1,
            "adapter_calls": 8,
            "shear_distance8_calls": 8,
            "ntt16_finish_row_calls": 72,
            "ntt9_calls": 8,
            "total_hot_helper_calls": 97,
            "estimated_vzeroupper_executions": 98,
            "note": "fixed-count expansion of the linked correctness wrapper; not measured events",
        },
        "gt_materialization_boundaries_per_forward": {
            "adapter_output": "8 x 9 YMM-equivalent R rows",
            "shear_to_ntt16": "72 YMM store/load pairs across eight islands",
            "ntt16_to_ntt9": "72 YMM store/load pairs across eight islands",
            "ntt9_to_official_scatter": "72 YMM-equivalent rows followed by 1152 scalar-position stores",
            "note": "conceptual fixed-layout boundaries; actual linked memory-instruction counts are reported per function",
        },
    }
    candidate_disassembly = disassembly(args.candidate_elf)
    for name, role in GT.items():
        report["gt_correctness_baseline"][name] = summarize(
            function_lines(candidate_disassembly, name), role, name)
    for path in args.official_object:
        body = disassembly(path)
        for name, role in OFFICIAL.items():
            if re.search(rf"^[0-9a-f]+ <{re.escape(name)}>:$", body, re.MULTILINE):
                summary = summarize(function_lines(body, name), role, name)
                summary["object"] = str(path)
                summary["object_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                report["official"][name] = summary
    if set(report["official"]) != set(OFFICIAL):
        raise SystemExit("not all Official pipeline functions were audited")
    for name, summary in report["official"].items():
        if summary["internal_direct_call_count"] or summary["stack_sub_bytes"] or summary["vzeroupper_count"]:
            raise SystemExit(f"Official leaf invariant changed for {name}")
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
