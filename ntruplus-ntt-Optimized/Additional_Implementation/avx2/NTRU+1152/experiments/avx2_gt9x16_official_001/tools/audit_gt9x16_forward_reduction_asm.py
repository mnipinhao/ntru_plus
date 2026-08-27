#!/usr/bin/env python3
"""Audit the linked T0-beta 72-to-40 Barrett prototype."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_gt9x16_prod3_t0_beta import (
    instructions, ledger, section_alignment, section_size, symbol_address)

CONTROL = "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta"
CANDIDATE = ("ntruplus1152_exp001_gt9x16_prod3_aos_full_"
             "natural_q_t0_beta_lazy_reduce")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--control-object", type=Path, required=True)
    parser.add_argument("--candidate-object", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    proof = json.loads(args.proof.read_text())
    selected = proof["minimum"]["selected"]
    if (selected["mask"] != 79 or selected["kept_registers"] !=
            [7, 8, 15, 10, 13] or
            proof["minimum"]["removed_per_forward"] != 32):
        raise SystemExit("range-proof reduction mask changed")

    control = ledger(instructions(args.elf, CONTROL))
    candidate = ledger(instructions(args.elf, CANDIDATE))
    keys = ("instructions", "barrett", "vpmullw", "vpmulhw", "vpsubw",
            "constant_memory_operands", "routing_total", "data_loads",
            "data_stores")
    delta = {key: candidate[key] - control[key] for key in keys}
    expected = {
        "instructions": -96, "barrett": -32, "vpmullw": -32,
        "vpmulhw": 0, "vpsubw": -32, "constant_memory_operands": -32,
        "routing_total": 0, "data_loads": 0, "data_stores": 0,
    }
    if control["barrett"] != 72 or candidate["barrett"] != 40:
        raise SystemExit("linked Barrett ledger changed")
    if delta != expected:
        raise SystemExit(f"linked machine delta changed: {delta}")
    for item in (control, candidate):
        if any(item[key] for key in ("stack_references", "calls", "branches",
                                     "vzeroupper", "vector_spills")):
            raise SystemExit("prototype lost the frozen leaf ABI")
    if symbol_address(args.elf, CONTROL) % 32 or symbol_address(
            args.elf, CANDIDATE) % 32:
        raise SystemExit("function entry alignment changed")
    if section_alignment(args.candidate_object, ".text") < 32 or \
            section_alignment(args.candidate_object, ".rodata") < 32:
        raise SystemExit("candidate section alignment changed")

    footprint = {
        "control": {"text": section_size(args.control_object, ".text"),
                    "rodata": section_size(args.control_object, ".rodata")},
        "candidate": {"text": section_size(args.candidate_object, ".text"),
                      "rodata": section_size(args.candidate_object, ".rodata")},
    }
    footprint["delta"] = {
        key: footprint["candidate"][key] - footprint["control"][key]
        for key in ("text", "rodata")}
    if footprint["delta"] != {"text": -544, "rodata": 0}:
        raise SystemExit(f"object footprint changed: {footprint['delta']}")

    report = {
        "schema": "gt9x16-forward-reduction-asm-audit/v1",
        "checkpoint": "GT9X16-FORWARD-OPT-V2-LAZY-REDUCTION-ASM",
        "range_proof_mask": selected["mask"],
        "linked_machine": {"control": control, "candidate": candidate,
                           "candidate_minus_control": delta},
        "object_footprint": footprint,
        "gates": {"barrett_72_to_40": True, "canonical_differential": True,
                  "range_bound": 21333, "zero_new_movement": True,
                  "zero_spill_stack_branch_vzeroupper": True,
                  "entry_text_rodata_alignment": 32},
        "authorization": {"short_paired_diagnostic": True,
                          "serious_pricing": False, "promotion": False},
        "sha256": {"elf": sha256(args.elf),
                   "control_object": sha256(args.control_object),
                   "candidate_object": sha256(args.candidate_object),
                   "proof": sha256(args.proof), "source": sha256(args.source)},
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit(f"generated audit is stale: {args.output}")
    else:
        args.output.write_text(text)
    print("Forward lazy-reduction linked audit: Barrett 72->40, -96 "
          "instructions, -544 text bytes, zero movement debt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
