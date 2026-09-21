#!/usr/bin/env python3
"""Linked research-only audit; not a proof of performance or constant time."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

from probe_inverse_ct_gauge import ROOT, compute
from prove_inverse_ct_range import repaired_replay

ELF = ROOT / "build/test_inverse_ct"
SYMBOL = "ntruplus768_officialopt_invntt_ct"


def command(*args):
    return subprocess.check_output(args, text=True)


def main():
    nm = command("nm", "-S", str(ELF))
    match = re.search(rf"^([0-9a-f]+) ([0-9a-f]+) T {SYMBOL}$", nm, re.M)
    if not match:
        raise ValueError("linked CT symbol missing or lacks .size")
    address, size = int(match[1], 16), int(match[2], 16)
    dis = command("objdump", "--disassemble=" + SYMBOL, str(ELF))
    instructions = [line for line in dis.splitlines()
                    if re.match(r"\s*[0-9a-f]+:\s+[0-9a-f]{2}", line)]
    forbidden = {"stack_reference": bool(re.search(r"%rsp|%rbp", dis)),
                 "call": bool(re.search(r"\bcall[q]?\b", dis)),
                 "vzeroupper": "vzeroupper" in dis}
    if address % 32 or any(forbidden.values()):
        raise ValueError(f"linked ABI/structure failed: align={address % 32}, {forbidden}")
    gauge = compute()
    repair = repaired_replay(7644, gauge)
    if not repair["unchanged_tail_uniform_bound"]["all_signed_i16_preoperations_safe"]:
        raise ValueError("range replay failed")
    ct_radix2_mont = sum(s["nonidentity_twiddle_vectors"] for s in gauge["stages"])
    result = {"kind": "linked_research_ct_inverse_not_native_benchmark",
              "elf_sha256": hashlib.sha256(ELF.read_bytes()).hexdigest(),
              "ct_symbol_address": address, "ct_symbol_alignment": address % 32,
              "ct_symbol_text_bytes": size,
              "ct_static_instruction_lines": len(instructions),
              "forbidden": forbidden,
              "ct_added_constant_table_bytes": 5 * 24 * 64 + 48 * 64,
              "official_radix2_gs_montgomery_vectors": 120,
              "ct_radix2_twiddle_montgomery_vectors": ct_radix2_mont,
              "ct_final_gauge_montgomery_vectors": 48,
              "official_standalone_barrett_vectors": 64,
              "ct_standalone_barrett_vectors": repair["total_repaired_vectors"] + 16,
              "range_input_contract_abs": 7644,
              "range_tail": repair["unchanged_tail_uniform_bound"]}
    output = ROOT / "results/officialopt-inverse-ct-linked-20260921.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
