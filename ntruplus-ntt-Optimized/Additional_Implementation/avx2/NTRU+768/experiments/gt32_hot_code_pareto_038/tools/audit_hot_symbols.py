#!/usr/bin/env python3
"""Inventory selected GT32 hot symbols from a fixed production-shaped ELF."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


TARGETS = {
    "frontend": "ntruplus768_ntt_frontend_avx2",
    "ntt_p": "ntruplus768_ntt_p_avx2",
    "ntt_m": "ntruplus768_ntt_m_avx2",
    "decode_m_body": "ntruplus768_unpack_m_body_avx2",
    "pack_m_centered": "ntruplus768_pack_m_centered_avx2",
    "pack_m_lazy10788": "ntruplus768_pack_m_lazy10788_avx2",
    "pack_p": "ntruplus768_pack_p_sp1_lazy10788_avx2",
    "baseinv_leaf": "ntruplus768_baseinv_j1_avx2",
    "baseinv_batch": "ntruplus768_baseinv_batch_tree_avx2",
    "basemul_scale_m": "ntruplus768_basemul_scale_m_avx2",
    "basemul_general_m": "ntruplus768_basemul_general_m_avx2",
    "invntt_m": "ntruplus768_invntt_m_avx2",
    "invntt_tail": "ntruplus768_invntt_tail_avx2",
}

CALL_COUNTS = {
    "frontend": {"keypair": 2, "encap": 2, "decap": 2},
    "ntt_p": {"keypair": 2, "encap": 0, "decap": 0},
    "ntt_m": {"keypair": 0, "encap": 2, "decap": 2},
    "decode_m_body": {"keypair": 0, "encap": 1, "decap": 3},
    "pack_m_centered": {"keypair": 0, "encap": 1, "decap": 1},
    "pack_m_lazy10788": {"keypair": 0, "encap": 1, "decap": 0},
    "pack_p": {"keypair": 3, "encap": 0, "decap": 0},
    "baseinv_leaf": {"keypair": 2, "encap": 0, "decap": 0},
    "baseinv_batch": {"keypair": 2, "encap": 0, "decap": 0},
    "basemul_scale_m": {"keypair": 0, "encap": 0, "decap": 1},
    "basemul_general_m": {"keypair": 0, "encap": 1, "decap": 1},
    "invntt_m": {"keypair": 0, "encap": 0, "decap": 1},
    "invntt_tail": {"keypair": 0, "encap": 0, "decap": 1},
}

SHAPES = {
    "frontend": "compact_U3_loop; freeze_036",
    "ntt_p": "small repeated SIMD loop; freeze",
    "ntt_m": "small repeated SIMD loop; freeze",
    "decode_m_body": "large packet routing body; classify before search",
    "pack_m_centered": "fully expanded packet serializer; Pareto candidate",
    "pack_m_lazy10788": "5120-byte padded fully expanded serializer; Pareto candidate",
    "pack_p": "large P-specific serializer; Keypair Pareto candidate",
    "baseinv_leaf": "compact leaf loop; freeze pending register/DAG change",
    "baseinv_batch": "specialized batch inversion; outside code-shape gate",
    "basemul_scale_m": "compact loop; freeze",
    "basemul_general_m": "compact loop; freeze",
    "invntt_m": "compact inverse core loop; freeze",
    "invntt_tail": "large expanded terminal; Decap Pareto candidate",
}


def symbols(elf: Path) -> dict[str, tuple[int, int]]:
    output = subprocess.check_output(["nm", "-S", "--defined-only", str(elf)], text=True)
    result = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 4 and re.fullmatch(r"[0-9a-fA-F]+", fields[0]):
            result[fields[3]] = (int(fields[0], 16), int(fields[1], 16))
    return result


def instructions(elf: Path) -> list[tuple[int, str, str]]:
    output = subprocess.check_output(["objdump", "-d", "--no-show-raw-insn", str(elf)], text=True)
    result = []
    pattern = re.compile(r"^\s*([0-9a-fA-F]+):\s+([A-Za-z0-9_.]+)\s*(.*)$")
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            result.append((int(match.group(1), 16), match.group(2), match.group(3)))
    return result


def metrics(rows: list[tuple[int, str, str]]) -> dict[str, int]:
    non_nop = [(address, mnemonic, operands) for address, mnemonic, operands in rows
               if not mnemonic.startswith("nop")]
    branches = sum(mnemonic.startswith("j") or mnemonic.startswith("call")
                   or mnemonic.startswith("ret") or mnemonic.startswith("loop")
                   for _, mnemonic, _ in non_nop)
    vector = sum(mnemonic.startswith("v") for _, mnemonic, _ in non_nop)
    memory = 0
    likely_loads = 0
    likely_stores = 0
    for _, mnemonic, operands in non_nop:
        clean = operands.split("#", 1)[0]
        if "(" not in clean or mnemonic.startswith("lea"):
            continue
        memory += 1
        destination = clean.rsplit(",", 1)[-1]
        if "(" in destination:
            likely_stores += 1
        else:
            likely_loads += 1
    return {"static_instructions_excluding_nop": len(non_nop), "static_branches": branches,
            "static_vector_instructions": vector, "memory_operand_instructions": memory,
            "likely_loads": likely_loads, "likely_stores": likely_stores}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    table = symbols(args.elf)
    disassembly = instructions(args.elf)
    payload = {"schema": "gt32-hot-code-pareto-inventory-v1", "elf": str(args.elf.resolve()),
               "symbols": {}}
    for logical, symbol in TARGETS.items():
        if symbol not in table:
            raise SystemExit(f"missing symbol: {symbol}")
        address, size = table[symbol]
        rows = [row for row in disassembly if address <= row[0] < address + size]
        payload["symbols"][logical] = {"symbol": symbol, "address": address,
            "static_bytes": size, **metrics(rows), "calls": CALL_COUNTS[logical],
            "shape": SHAPES[logical]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
