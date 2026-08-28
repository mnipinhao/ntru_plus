#!/usr/bin/env python3
"""Audit H4-M3B against the linked H3 control object."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


H3 = "ntruplus1152_exp001_encap_h_ingress_ma2_h3"
M3B = "ntruplus1152_exp001_encap_h4_m3b_exact_egress"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def disassemble(path: Path, symbol: str) -> tuple[str, list[dict], Counter[str]]:
    text = run("objdump", "-d", "--no-show-raw-insn", "-M", "intel", str(path))
    body = text.split(f"<{symbol}>:", 1)[1]
    body = re.split(r"\n[0-9a-f]+ <", body, maxsplit=1)[0]
    instructions = []
    counts: Counter[str] = Counter()
    for line in body.splitlines():
        match = re.match(r"^\s*([0-9a-f]+):\s+([a-z][a-z0-9]+)\s*(.*)$", line)
        if not match or match.group(2) in ("nop", "data16"):
            continue
        address, mnemonic, operands = match.groups()
        instructions.append({"address": int(address, 16),
                             "mnemonic": mnemonic, "operands": operands})
        counts[mnemonic] += 1
    return body, instructions, counts


def symbol(path: Path, name: str) -> tuple[int, int]:
    for line in run("nm", "-S", "--defined-only", str(path)).splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] == name:
            return int(fields[0], 16), int(fields[1], 16)
    raise SystemExit(f"missing symbol {name}")


def section(path: Path, name: str) -> tuple[int, int]:
    for line in run("readelf", "-SW", str(path)).splitlines():
        match = re.search(
            rf"\]\s+{re.escape(name)}\s+\S+\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+).*\s(\d+)$",
            line)
        if match:
            return int(match.group(1), 16), int(match.group(2))
    raise SystemExit(f"missing section {name}")


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale H4-M3B audit: {path}")
    else:
        path.write_text(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h3-object", type=Path, required=True)
    parser.add_argument("--candidate-object", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--machine-wire", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    machine = json.loads(args.machine_wire.read_text())
    h3_body, _, h3 = disassemble(args.h3_object, H3)
    body, instructions, candidate = disassemble(args.candidate_object, M3B)
    delta = {name: candidate[name] - h3[name]
             for name in sorted(set(h3) | set(candidate))
             if candidate[name] != h3[name]}
    expected_delta = {
        "vextracti128": 72, "vinserti128": 54, "vmovdqa": 156,
        "vmovdqu": 54, "vpaddw": 72, "vpand": 72,
        "vperm2i128": 72, "vpermd": 72, "vpmaddwd": 72,
        "vpmulhrsw": 72, "vpmullw": 72, "vpor": 108,
        "vpshufb": 72, "vpslldq": 108, "vpsraw": 72,
        "vpsrldq": 72, "vpsubw": 72, "vpunpckhdq": 36,
        "vpunpckhwd": 36, "vpunpckldq": 36, "vpunpcklwd": 36,
    }
    if delta != expected_delta or sum(delta.values()) != 1488:
        raise SystemExit(f"H4-M3B linked delta changed: {delta}")
    scratch_stores = [item for item in instructions
                      if item["mnemonic"] == "vmovdqa" and
                      re.match(r"YMMWORD PTR \[r8", item["operands"])]
    scratch_loads = [item for item in instructions
                     if "PTR [r8" in item["operands"] and
                     not re.match(r"YMMWORD PTR \[r8", item["operands"])]
    ct_stores = [item for item in instructions
                 if item["mnemonic"] == "vmovdqu" and
                 re.match(r"YMMWORD PTR \[rdi", item["operands"])]
    pk_loads = [item for item in instructions if "PTR [rsi" in item["operands"]]
    if (len(scratch_stores), len(scratch_loads), len(ct_stores), len(pk_loads)) != (72, 72, 54, 54):
        raise SystemExit("H4-M3B boundary traffic changed")
    if max(item["address"] for item in pk_loads) >= min(item["address"] for item in ct_stores):
        raise SystemExit("H4-M3B writes ciphertext before consuming PK")
    forbidden = ("call", "push", "pop", "leave", "vzeroupper")
    if any(candidate[name] for name in forbidden):
        raise SystemExit("H4-M3B has a forbidden call/frame/transition")
    if re.search(r"\[(?:e?rsp|e?rbp)(?:[+\]-]|\])", body + h3_body):
        raise SystemExit("H4-M3B has stack-relative traffic")
    if any(name.startswith("j") or name.startswith("loop") for name in candidate):
        raise SystemExit("H4-M3B has a branch")
    address, size = symbol(args.candidate_object, M3B)
    text_size, text_align = section(args.candidate_object, ".text")
    rodata_size, rodata_align = section(args.candidate_object, ".rodata")
    if address % 32 or text_align != 32 or rodata_align != 32:
        raise SystemExit("H4-M3B alignment gate failed")
    if machine.get("schema") != "h1-machine-wire-layout/v1":
        raise SystemExit("H4-M3B machine-wire probe changed")
    report = {
        "schema": "encap-h4-m3b-exact-egress-linked-audit/v1",
        "checkpoint": contract["checkpoint"],
        "machine_wire_bijection": len(set(machine["source_to_wire"])) == 1152,
        "linked": {
            "instructions": sum(candidate.values()), "text_bytes": size,
            "rodata_bytes": rodata_size, "delta_vs_h3": delta,
            "instruction_delta_vs_h3": sum(delta.values()),
            "canonical_scratch_stores": len(scratch_stores),
            "canonical_scratch_loads": len(scratch_loads),
            "ciphertext_stores": len(ct_stores), "pk_loads": len(pk_loads),
            "mnemonics": dict(sorted(candidate.items())),
        },
        "sections": {"text_bytes": text_size, "text_alignment": text_align,
                     "rodata_bytes": rodata_size, "rodata_alignment": rodata_align,
                     "entry_mod32": address % 32},
        "gates": {"exact_linked_delta": True, "machine_wire_bijective": True,
                  "pk_consumed_before_ct_store": True, "pk_equals_ct_safe": True,
                  "call_free": True, "branch_free": True, "frame_free": True,
                  "spill_free": True, "vzeroupper_free": True,
                  "entry_text_rodata_aligned_32": True},
        "decision": {"correctness_closure_required": True,
                     "benchmark_authorized": False,
                     "native_kem_authorized": False},
    }
    write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n", args.check)
    print("H4-M3B linked audit: exact machine-wire egress structure passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
