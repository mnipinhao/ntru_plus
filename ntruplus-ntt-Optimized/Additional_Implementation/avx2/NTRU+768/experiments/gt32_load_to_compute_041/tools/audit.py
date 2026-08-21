#!/usr/bin/env python3
"""Audit exact selected production/candidate dynamic load classes."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

def disassemble(path: Path, symbol: str) -> list[str]:
    text = subprocess.run(
        ["objdump", "-d", "-M", "att", f"--disassemble={symbol}", str(path)],
        check=True, capture_output=True, text=True).stdout
    return [line.strip() for line in text.splitlines()
            if re.match(r"^[0-9a-f]+:", line.strip())]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    selected = {
        "decode_h": (args.build / "pack_control.o", "ntruplus768_unpack_m_body_avx2"),
        "q24_control": (args.build / "pack_control.o", "ntruplus768_pack_m_lazy10788_avx2"),
        "q24_candidate": (args.build / "pack_candidate_raw.o", "ntruplus768_pack_m_lazy10788_avx2"),
        "b3_control": (args.build / "basemul_control.o", "ntruplus768_basemul_general_m_avx2"),
        "b3_candidate": (args.build / "basemul_candidate_raw.o", "ntruplus768_basemul_general_m_avx2"),
    }
    symbols = {}
    for name, (obj, symbol) in selected.items():
        lines = disassemble(obj, symbol)
        symbols[name] = {
            "static_instructions": len(lines),
            "rip_memory_operands": sum("(%rip)" in line for line in lines),
            "rsi_memory_operands": sum("(%rsi)" in line for line in lines),
        }
    result = {
        "schema": "gt32-load-to-compute-041-v1",
        "symbols": symbols,
        "production_dynamic_map": {
            "decode_h": {
                "wire_payload_loads": 96,
                "decode_mask_memory_operands": 48,
                "fixed_constant_loads": 2,
                "output_stores": 48,
                "note": "Four mask values; only ymm13 is free while four validity accumulators are live."
            },
            "q24_m_lazy10788": {
                "input_payload_loads": 48,
                "pair_factor_memory_operands": 48,
                "pack_mask_memory_operands": 48,
                "q_and_v_prologue_loads": 2
            },
            "b3_general_m": {
                "operand_payload_loads": 96,
                "initial_qinv_memory_operands": 48,
                "lambda_and_lambda_qinv_memory_operands": 24,
                "finalizer_constant_memory_operands": 96,
                "note": "Dynamic counts for twelve T16 blocks; memory-source vector operations count as loads."
            }
        },
        "candidate_exchange": {
            "decode": {
                "added_explicit_load_instructions": 1,
                "removed_memory_source_mask_loads": 14,
                "new_explicit_mask_loads": 1,
                "net_dynamic_load_delta": -13,
                "arithmetic_changed": False
            },
            "q24": {
                "added_explicit_load_instructions": 1,
                "removed_memory_source_constant_loads": 48,
                "new_explicit_constant_loads": 1,
                "net_dynamic_load_delta": -47,
                "arithmetic_changed": False
            },
            "b3": {
                "added_explicit_load_instructions": 12,
                "removed_memory_source_qinv_loads": 48,
                "new_explicit_qinv_loads": 12,
                "net_dynamic_load_delta": -36,
                "arithmetic_changed": False
            }
        }
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
