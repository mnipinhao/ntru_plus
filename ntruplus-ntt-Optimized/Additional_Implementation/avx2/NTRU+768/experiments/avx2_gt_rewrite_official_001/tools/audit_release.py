#!/usr/bin/env python3
"""Mechanical release-object checks for the AVX2 GT experiment.

This deliberately separates things objdump can establish from the constant-
time properties that still require source review.  A clean result is necessary
for promotion, but is not by itself a constant-time proof.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


OBJECT_NAMES = (
    "gt_backend.o",
    "gt_forward_avx2.o",
    "gt_inverse_avx2.o",
    "gt_basemul_avx2.o",
    "gt_baseinv_avx2.o",
    "gt_generated_tables.o",
)


def command(*args: str) -> str:
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def function_body(disassembly: str, name: str) -> str:
    match = re.search(
        rf"^[0-9a-f]+ <{re.escape(name)}>:\n(.*?)(?=^[0-9a-f]+ <|\Z)",
        disassembly,
        re.MULTILINE | re.DOTALL,
    )
    return "" if match is None else match.group(1)


def section_sizes(path: Path) -> tuple[int, int]:
    output = command("size", "-A", str(path))
    text = 0
    tables = 0
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 2 or not fields[1].isdigit():
            continue
        if fields[0] == ".text":
            text += int(fields[1])
        elif fields[0].startswith(".rodata"):
            tables += int(fields[1])
    return text, tables


def symbol_sizes(path: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    output = command("nm", "-a", "-S", "--size-sort", str(path))
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 4:
            try:
                result[fields[3]] = int(fields[1], 16)
            except ValueError:
                pass
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", default="build")
    args = parser.parse_args()
    build = Path(args.build_dir)
    objects = [build / name for name in OBJECT_NAMES]
    missing = [str(path) for path in objects if not path.is_file()]
    if missing:
        raise SystemExit("missing release objects: " + ", ".join(missing))

    symbol_failures: list[str] = []
    evex_findings: list[str] = []
    forbidden_register_findings: list[str] = []
    instruction_count = 0
    text_bytes = 0
    table_bytes = 0
    disassemblies: dict[str, str] = {}

    for path in objects:
        symbols = command("nm", "-g", "--defined-only", str(path))
        for line in symbols.splitlines():
            fields = line.split()
            if fields and not fields[-1].startswith("gt_"):
                symbol_failures.append(f"{path.name}:{fields[-1]}")

        disassembly = command("objdump", "-d", "-M", "intel", str(path))
        disassemblies[path.name] = disassembly
        for line in disassembly.splitlines():
            if re.match(r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+", line):
                instruction_count += 1
            if re.match(r"^\s*[0-9a-f]+:\s+62\s", line):
                evex_findings.append(f"{path.name}:{line.strip()}")
            if re.search(r"\b(?:zmm\d+|k[0-7])\b|\{k[0-7]\}", line):
                forbidden_register_findings.append(f"{path.name}:{line.strip()}")

        object_text, object_tables = section_sizes(path)
        text_bytes += object_text
        table_bytes += object_tables

    basemul_leaf = function_body(disassemblies["gt_basemul_avx2.o"],
                                 "basemul4")
    basemul_leaf_stack_access = bool(re.search(r"\[(?:e|r)sp", basemul_leaf))

    stack_frames: dict[str, int] = {}
    for name, disassembly in disassemblies.items():
        frames = [int(value, 16) for value in
                  re.findall(r"\bsub\s+rsp,0x([0-9a-f]+)", disassembly)]
        stack_frames[name] = max(frames, default=0)

    forward_sizes = symbol_sizes(build / "gt_forward_avx2.o")
    cyclic16_bytes = forward_sizes.get("cyclic16", 0)
    b1_code_bytes = (cyclic16_bytes
                     + forward_sizes.get("ntt32_b_rows.constprop.1", 0)
                     + forward_sizes.get("gt_avx2_ntt32_b1_rows", 0))
    b2_code_bytes = (cyclic16_bytes
                     + forward_sizes.get("ntt32_b_rows.constprop.0", 0)
                     + forward_sizes.get("gt_avx2_ntt32_b2_rows", 0))
    basemul_sizes = symbol_sizes(build / "gt_basemul_avx2.o")
    bm_a_code_bytes = (basemul_sizes.get("basemul4", 0)
                       + basemul_sizes.get("gt_poly_basemul", 0))
    bm_b_code_bytes = (basemul_sizes.get("basemul4_bm_b", 0)
                       + basemul_sizes.get("gt_poly_basemul_bm_b", 0))

    baseinv_source = Path("src/gt_baseinv_avx2.c").read_text()
    baseinv_early_exit = "if (batch_inverse" in baseinv_source
    mandatory_pass = (not symbol_failures and not evex_findings
                      and not forbidden_register_findings
                      and not basemul_leaf_stack_access
                      and not baseinv_early_exit)
    report = {
        "schema_version": 1,
        "scope": "release GT backend objects",
        "symbols": {
            "status": "pass" if not symbol_failures else "fail",
            "required_prefix": "gt_",
            "unexpected": symbol_failures,
        },
        "isa": {
            "status": "pass" if not evex_findings
                      and not forbidden_register_findings else "fail",
            "policy": "AVX2-only; no EVEX, zmm, or opmask registers",
            "evex_findings": evex_findings,
            "forbidden_register_findings": forbidden_register_findings,
        },
        "stack": {
            "status": "pass" if not basemul_leaf_stack_access else "fail",
            "basemul4_leaf_stack_access": basemul_leaf_stack_access,
            "largest_static_frame_bytes_by_object": stack_frames,
            "note": "Forward/inverse/baseinv frames contain explicit fixed-size row or batch workspaces; only the BM-A leaf has a no-spill gate.",
        },
        "constant_time_review": {
            "status": "pass" if not baseinv_early_exit else "fail",
            "baseinv_failure_early_exit": baseinv_early_exit,
            "secret_kernels": [
                "gt_poly_ntt", "gt_poly_basemul", "gt_poly_basemul_scale",
                "gt_poly_baseinv", "gt_poly_invntt_scale",
            ],
            "public_input_exception": "gt_poly_frombytes rejection may branch on public wire input",
            "finding": "Fixed loop bounds and coefficient-independent addresses verified by source review; disassembly scan is not a formal constant-time proof.",
        },
        "footprint": {
            "text_bytes": text_bytes,
            "table_bytes": table_bytes,
            "static_instruction_count": instruction_count,
            "n32_candidates": {
                "B1": {"code_bytes": b1_code_bytes, "table_bytes": 64},
                "B2": {"code_bytes": b2_code_bytes, "table_bytes": 64},
            },
            "basemul_candidates": {
                "BM-A": {"code_bytes": bm_a_code_bytes,
                         "table_bytes": 384},
                "BM-B": {"code_bytes": bm_b_code_bytes,
                         "table_bytes": 384},
            },
        },
        "mandatory_mechanical_gate": "pass" if mandatory_pass else "fail",
        "promotion_ready": False,
        "promotion_blocker": "full-caller performance gate is evaluated separately",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if mandatory_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
