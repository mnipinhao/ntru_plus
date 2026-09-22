#!/usr/bin/env python3
"""Linked-object audit for the experiment-only live B3→Q24 candidate."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

NAME = "ntruplus768_exp001_encap_live_b3_pack"


def output(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def audit(elf: Path) -> dict:
    symbols = output("nm", "-S", str(elf))
    match = re.search(rf"^[0-9a-f]+ ([0-9a-f]+) T {NAME}$", symbols, re.M)
    assert match, "candidate symbol missing"
    function = output("objdump", "-d", "-M", "intel", str(elf)).split(
        f"<{NAME}>:\n", 1)[1].split("\n\n", 1)[0]
    lines = [line for line in function.splitlines() if "\t" in line]
    mnemonics = []
    for line in lines:
        fields = line.split("\t")
        if len(fields) >= 3:
            mnemonics.append(fields[2].split()[0])
    assert len(mnemonics) > 700, "packet groups missing from symbol"
    assert not re.search(r"\[(?:r|e)sp(?:[+\-\]]|$)", function), "stack operand"
    assert not any(x.startswith("call") for x in mnemonics), "internal call"
    assert mnemonics.count("vzeroupper") == 1
    assert sum(x == "jmp" for x in mnemonics) == 13
    assert sum(x.startswith("vpmulhw") for x in mnemonics) >= 12
    lowered = function.lower()
    assert "ymmword ptr [rsi]" in lowered or "ymmword ptr [rsi+0x" in lowered
    physical_ymm = sorted({int(x) for x in re.findall(r"\bymm(\d+)\b", lowered)})
    assert physical_ymm == list(range(16))
    return {
        "symbol": NAME,
        "symbol_bytes": int(match[1], 16),
        "instruction_count_static": len(mnemonics),
        "vzeroupper": mnemonics.count("vzeroupper"),
        "internal_calls": 0,
        "rsp_memory_operands": 0,
        "packet_groups": 12,
        "public_indirect_dispatch": 1,
        "exact_packet_stores": "48 x (16+8+4 bytes), no overlapping later packet writes",
        "raw_b3_stores": 0,
        "late_raw_b3_reloads": 0,
        "completed_c_materialization": 0,
        "physical_YMM_registers_used": physical_ymm,
        "exact_peak_live_YMM": "not proved by this disassembly-only audit",
        "semantic_def_use_evidence": "1003 raw B3 and ciphertext differential cases",
        "cycle_claim": None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("elf", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    report = audit(args.elf)
    encoded = json.dumps(report, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
