#!/usr/bin/env python3
"""Linked CT level-0 co-design audit; counts are structural, not timing."""

import argparse
import hashlib
import json
import re
import subprocess

from generate_inverse_ct_full import ROOT
from prove_inverse_ct_full_range import prove


def command(*argv):
    return subprocess.check_output(argv, text=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("full", "cohort"), required=True)
    args = parser.parse_args()
    name = f"ntruplus768_officialopt_invntt_ct_{args.variant}"
    elf = ROOT / "build" / f"test_inverse_ct_{args.variant}"
    source = ROOT / "asm" / (name + ".s")
    nm = command("nm", "-S", str(elf))
    match = re.search(rf"^([0-9a-f]+) ([0-9a-f]+) T {name}$", nm, re.M)
    if not match:
        raise ValueError("candidate symbol missing")
    addr, size = int(match[1], 16), int(match[2], 16)
    dis = command("objdump", "--disassemble=" + name, str(elf))
    forbidden = {"stack_reference": bool(re.search(r"%rsp|%rbp", dis)),
                 "call": bool(re.search(r"\bcall[q]?\b", dis)),
                 "vzeroupper": "vzeroupper" in dis}
    insns = [line for line in dis.splitlines()
             if re.match(r"\s*[0-9a-f]+:\s+[0-9a-f]{2}", line)]
    if addr % 32 or any(forbidden.values()):
        raise ValueError(f"linked ABI failed: {forbidden}")
    # The stage-1 pair alignment uses 2 multiplies for eight triples and
    # 3 multiplies for the paired eight: 40, genuinely eight fewer than
    # the CT control's 48 independent gauge restorations.
    table_bytes = 5 * 24 * 64 + 40 * 64 + (16 if args.variant == "cohort" else 48) * 64
    result = {"kind": "research_CT_level0_linked_not_native",
              "variant": args.variant,
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
              "symbol_address": addr, "symbol_alignment": addr % 32,
              "symbol_text_bytes": size, "static_instruction_rows": len(insns),
              "forbidden": forbidden,
              "ct_radix2_twiddle_montgomery_vectors": 78,
              "additional_pair_gauge_montgomery_vectors": 40,
              "ct_radix2_plus_gauge_montgomery_vectors": 118,
              "ct_control_radix2_plus_gauge_montgomery_vectors": 126,
              "standalone_barrett_vectors": 40,
              "added_constant_table_bytes": table_bytes,
              "range_max_signed_preoperation": prove()["max_signed_preoperation"]}
    out = ROOT / "results" / f"officialopt-inverse-ct-{args.variant}-linked-20260921.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
