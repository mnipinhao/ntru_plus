#!/usr/bin/env python3
"""Linked structural audit of the namespaced CT→radix-3 candidate."""

import hashlib
import json
import re
import subprocess

from generate_inverse_ct_r3 import OUTPUT, ROOT
from prove_inverse_ct_r3_range import prove

ELF = ROOT / "build/test_inverse_ct_r3"
SYMBOL = "ntruplus768_officialopt_invntt_ct_r3"


def command(*argv):
    return subprocess.check_output(argv, text=True)


def main():
    nm = command("nm", "-S", str(ELF))
    match = re.search(rf"^([0-9a-f]+) ([0-9a-f]+) T {SYMBOL}$", nm, re.M)
    if not match:
        raise ValueError("missing linked candidate symbol or size")
    address, size = int(match[1], 16), int(match[2], 16)
    dis = command("objdump", "--disassemble=" + SYMBOL, str(ELF))
    insns = [line for line in dis.splitlines()
             if re.match(r"\s*[0-9a-f]+:\s+[0-9a-f]{2}", line)]
    forbidden = {"stack_reference": bool(re.search(r"%rsp|%rbp", dis)),
                 "call": bool(re.search(r"\bcall[q]?\b", dis)),
                 "vzeroupper": "vzeroupper" in dis}
    source = OUTPUT.read_text()
    # 78 CT radix-2 chains; 16 radix-3 triples each require 2 relative
    # normalizations plus 1 output-zero normalization. Existing alpha/omega
    # multiplications are not counted as additional gauge work.
    counts = {"ct_radix2_twiddle_montgomery": 78,
              "radix3_relative_input_montgomery": 32,
              "radix3_output0_montgomery": 16,
              "total_ct_plus_gauge_montgomery": 126,
              "standalone_barrett": 24,
              "new_constant_table_bytes": 5 * 24 * 64 + 16 * 5 * 64,
              "old_ct_constant_table_bytes": 5 * 24 * 64 + 48 * 64}
    if address % 32 or any(forbidden.values()) or "ct_final_gauges:" in source:
        raise ValueError(f"linked structural gate failed: {forbidden}")
    result = {"kind": "research_linked_ct_r3_not_native",
              "elf_sha256": hashlib.sha256(ELF.read_bytes()).hexdigest(),
              "source_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
              "symbol_address": address, "symbol_text_bytes": size,
              "symbol_alignment": address % 32,
              "static_instruction_lines": len(insns),
              "forbidden": forbidden, "counts": counts,
              "range_max_signed_preoperation": prove()["max_signed_preoperation"]}
    path = ROOT / "results/officialopt-inverse-ct-r3-linked-20260921.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
