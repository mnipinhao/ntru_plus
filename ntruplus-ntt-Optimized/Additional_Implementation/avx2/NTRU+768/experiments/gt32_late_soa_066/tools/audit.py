#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYMBOLS = (
    "ntruplus768_basemul_scale_m_avx2",
    "ntruplus768_invntt_m_avx2",
    "late066_inverse_prefix_m_to_post_i1_asm",
    "late_soa_full_basemul_i2_fused_asm",
    "gt32_tile4_attr_inverse_i1_cross3_asm",
    "late066_dec_control",
    "late066_dec_candidate",
)


def symbol_rows(binary: Path) -> dict:
    rows = {}
    output = subprocess.check_output(["nm", "-n", "-S", str(binary)], text=True)
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] in SYMBOLS:
            rows[fields[3]] = {
                "address": "0x" + fields[0],
                "size_bytes": int(fields[1], 16),
            }
    return rows


def instruction_count(binary: Path, symbol: str) -> int:
    output = subprocess.check_output(
        ["objdump", "-d", f"--disassemble={symbol}", str(binary)], text=True)
    return sum(bool(re.match(r"\s*[0-9a-f]+:\s", line))
               for line in output.splitlines())


placements = {}
profiles = {
    "attribution_normal": ROOT / "build" / "bench_normal",
    "attribution_reversed": ROOT / "build" / "bench_reversed",
    "primary_normal": ROOT / "build" / "primary_normal",
    "primary_reversed": ROOT / "build" / "primary_reversed",
}
for placement, binary in profiles.items():
    rows = symbol_rows(binary)
    for symbol in rows:
        rows[symbol]["instructions"] = instruction_count(binary, symbol)
    size_output = subprocess.check_output(["size", "-A", str(binary)], text=True)
    sections = {}
    for line in size_output.splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] in (".text", ".rodata", ".data", ".bss"):
            sections[fields[0]] = int(fields[1])
    placements[placement] = {"symbols": rows, "sections": sections}

out = {
    "scope": "GT32-LATE-SOA-066 static geometry",
    "placements": placements,
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "static.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
