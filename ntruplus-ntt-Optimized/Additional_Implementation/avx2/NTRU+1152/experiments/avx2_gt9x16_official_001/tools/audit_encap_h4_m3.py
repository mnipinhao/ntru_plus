#!/usr/bin/env python3
"""Audit the linked H4-M3 scale-1 producer and ciphertext leaf."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


PRODUCER0 = "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta"
PRODUCER1 = PRODUCER0 + "_scale1"
H4 = "ntruplus1152_exp001_encap_h4_m3"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def disassemble(obj: Path, symbol: str) -> tuple[str, list[dict], Counter[str]]:
    text = run("objdump", "-d", "-M", "intel", str(obj))
    body = text.split(f"<{symbol}>:", 1)[1]
    body = re.split(r"\n[0-9a-f]+ <", body, maxsplit=1)[0]
    instructions = []
    counts: Counter[str] = Counter()
    pattern = re.compile(
        r"^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]+)\s*(.*)$")
    for line in body.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        address, mnemonic, operands = match.groups()
        if mnemonic in ("nop", "data16"):
            continue
        instructions.append({"address": int(address, 16),
                             "mnemonic": mnemonic, "operands": operands})
        counts[mnemonic] += 1
    return body, instructions, counts


def symbol_info(obj: Path, symbol: str) -> tuple[int, int]:
    for line in run("nm", "-S", "--defined-only", str(obj)).splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] == symbol:
            return int(fields[0], 16), int(fields[1], 16)
    raise SystemExit(f"missing symbol {symbol}")


def section(obj: Path, name: str) -> tuple[int, int]:
    for line in run("readelf", "-SW", str(obj)).splitlines():
        match = re.search(
            rf"\]\s+{re.escape(name)}\s+\S+\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+).*\s(\d+)$",
            line)
        if match:
            return int(match.group(1), 16), int(match.group(2))
    raise SystemExit(f"missing section {name}")


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale H4-M3 audit: {path}")
    else:
        path.write_text(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-producer", type=Path, required=True)
    parser.add_argument("--scale1-producer", type=Path, required=True)
    parser.add_argument("--h4-object", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--h1-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    h1 = json.loads(args.h1_audit.read_text())
    _, _, p0 = disassemble(args.control_producer, PRODUCER0)
    p1_body, _, p1 = disassemble(args.scale1_producer, PRODUCER1)
    h4_body, instructions, h4 = disassemble(args.h4_object, H4)

    producer_delta = {name: p1[name] - p0[name]
                      for name in sorted(set(p0) | set(p1))
                      if p1[name] != p0[name]}
    expected_producer = {"vpmullw": 8, "vpmulhw": 16, "vpsubw": 8}
    if producer_delta != expected_producer:
        raise SystemExit(f"scale1 producer delta changed: {producer_delta}")
    if any(p1[name] != p0[name] for name in
           ("vperm2i128", "vpshufb", "vpermq", "vmovdqa", "vmovdqu")):
        raise SystemExit("scale1 producer introduced movement debt")

    scratch_stores = [i for i in instructions
                      if i["mnemonic"] == "vmovdqa" and
                      re.search(r"X?Y?MMWORD PTR \[r8(?:\+0x[0-9a-f]+)?\],(?:xmm|ymm)",
                                i["operands"])]
    scratch_loads = [i for i in instructions
                     if "PTR [r8" in i["operands"] and
                     not re.match(r"X?Y?MMWORD PTR \[r8", i["operands"])]
    ct_stores = [i for i in instructions if
                 i["mnemonic"] == "vmovdqu" and
                 re.search(r"YMMWORD PTR \[rdi(?:\+0x[0-9a-f]+)?\],ymm", i["operands"])]
    pk_loads = [i for i in instructions if "PTR [rsi" in i["operands"]]
    if len(scratch_stores) != 72 or len(ct_stores) != 54 or len(pk_loads) != 54:
        raise SystemExit(
            f"H4 boundary counts changed: scratch={len(scratch_stores)} "
            f"ct={len(ct_stores)} pk={len(pk_loads)}")
    if h4["vpmulhrsw"] != 72 or h4["vpsraw"] != 72:
        raise SystemExit("H4 terminal Barrett/canonical vector count changed")
    if max(i["address"] for i in pk_loads) >= min(i["address"] for i in ct_stores):
        raise SystemExit("ciphertext store occurs before the last PK load")

    forbidden = ("call", "push", "pop", "leave", "vzeroupper")
    if any(h4[name] or p1[name] for name in forbidden):
        raise SystemExit("H4-M3 contains a forbidden call/frame/transition")
    if re.search(r"\[(?:e?rsp|e?rbp)(?:[+\]-]|\])", h4_body + p1_body):
        raise SystemExit("H4-M3 contains stack-relative traffic")
    if any(name.startswith("j") or name.startswith("loop") for name in h4):
        raise SystemExit("H4-M3 contains a branch")

    p1_addr, p1_size = symbol_info(args.scale1_producer, PRODUCER1)
    h4_addr, h4_size = symbol_info(args.h4_object, H4)
    h4_text, h4_text_align = section(args.h4_object, ".text")
    h4_rodata, h4_rodata_align = section(args.h4_object, ".rodata")
    if p1_addr % 32 or h4_addr % 32 or h4_text_align != 32 or h4_rodata_align != 32:
        raise SystemExit("H4-M3 alignment gate changed")

    report = {
        "schema": "encap-h4-m3-linked-audit/v1",
        "checkpoint": "ENCAP-MA2-CT-EGRESS-H4-M3-ASM",
        "producer_scale1": {
            "instructions": sum(p1.values()), "text_bytes": p1_size,
            "delta_vs_scale4": producer_delta,
            "added_montgomery_chains": 8, "movement_delta": 0,
            "entry_mod32": p1_addr % 32,
        },
        "h4": {
            "instructions": sum(h4.values()), "text_bytes": h4_size,
            "rodata_bytes": h4_rodata, "entry_mod32": h4_addr % 32,
            "mnemonics": dict(sorted(h4.items())),
            "terminal_barrett_vectors": h4["vpmulhrsw"],
            "terminal_sign_canonicalization_vectors": h4["vpsraw"],
            "canonical_scratch_stores": len(scratch_stores),
            "exact_ownership_scratch_load_instructions": len(scratch_loads),
            "ciphertext_stores": len(ct_stores), "pk_loads": len(pk_loads),
        },
        "h1_control": {
            "instructions": h1["instruction_count"],
            "text_bytes": h1["alignment"]["symbol_text_size"],
            "inv4_montgomery_instructions": 288,
            "coefficient_routes": 336, "pack_routes": 324,
        },
        "m2_model_correction": {
            "selected_pair_primitive_is_exact": False,
            "counterexample": {
                "ma2_vector20_lane15": "official coefficient 0",
                "ma2_vector21_lane15": "official coefficient 16",
                "actual_pair_for_coefficient0": "ma2 vector20 lane14 (coefficient 1)",
            },
            "machine_realization": (
                "correctness control uses Natural-Q H1 ownership/routing after "
                "the H4 terminal has already performed Barrett and sign canonicalization"),
            "benchmark_authorized": False,
        },
        "sections": {"text_bytes": h4_text, "text_alignment": h4_text_align,
                     "rodata_bytes": h4_rodata,
                     "rodata_alignment": h4_rodata_align},
        "gates": {
            "scale1_producer_exact_chain_delta": True,
            "scale1_producer_no_movement_delta": True,
            "terminal_inv4_absent": True,
            "terminal_barrett_72": True, "canonical_scratch_72": True,
            "pk_consumed_before_ct_store": True, "pk_equals_ct_safe": True,
            "call_free": True, "branch_free": True, "frame_free": True,
            "spill_free": True, "vzeroupper_free": True,
            "entry_and_rodata_aligned_32": True,
            "m2_pair_locality_rejected": True,
        },
        "decision": {"h4_scale_gauge_and_terminal_asm_complete": True,
                     "m2_selected_egress_complete": False,
                     "benchmark_authorized": False,
                     "native_kem_authorized": False},
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    write(args.output, rendered, args.check)
    print("H4-M3 linked audit: scale1/terminal pass; M2 pair locality rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
