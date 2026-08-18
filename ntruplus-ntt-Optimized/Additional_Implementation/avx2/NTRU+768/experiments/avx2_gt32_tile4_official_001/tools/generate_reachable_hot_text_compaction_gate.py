#!/usr/bin/env python3
"""Assemble the final reachable-hot-text compaction decision record."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import subprocess
from pathlib import Path


def section_bytes(elf: Path, name: str) -> int:
    text = subprocess.check_output(["readelf", "-SW", str(elf)], text=True)
    for line in text.splitlines():
        fields = line.split()
        if len(fields) >= 7 and fields[1] == name:
            return int(fields[5], 16)
    raise ValueError(name)


def symbol_size(elf: Path, name: str) -> int:
    text = subprocess.check_output(["nm", "-S", str(elf)], text=True)
    for line in text.splitlines():
        if line.endswith(" " + name):
            return int(line.split()[1], 16)
    raise ValueError(name)


def executed_prefix_hash(elf: Path, name: str) -> str:
    text = subprocess.check_output(
        ["objdump", "-d", f"--disassemble={name}", str(elf)], text=True)
    raw = bytearray()
    pattern = re.compile(r"\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s+)+)\s*(\S+)")
    for line in text.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        raw.extend(bytes.fromhex(match.group(1)))
        if match.group(2).startswith("ret"):
            break
    return hashlib.sha256(raw).hexdigest()


def local_medians(local: dict[str, object]) -> dict[str, object]:
    output = {}
    for placement, pdata in local["placements"].items():
        regions = {}
        for region in ("one_q24", "two_q24"):
            regions[region] = {}
            for metric in ("tsc", "core_cycles", "instructions"):
                values = [entry["metrics"][region][metric]["delta"] for entry in pdata["launches"]]
                regions[region][metric] = statistics.median(values)
        output[placement] = regions
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gc-elf", type=Path, required=True)
    parser.add_argument("--c0-elf", type=Path, required=True)
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--supercop", type=Path, required=True)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--call-boundary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    census = json.loads(args.census.read_text())
    supercop = json.loads(args.supercop.read_text())
    local = json.loads(args.local.read_text())
    call_boundary = json.loads(args.call_boundary.read_text())
    symbol = "gt32_q24_encode_soa_lazy10788_asm"
    gc_hash = executed_prefix_hash(args.gc_elf, symbol)
    c0_hash = executed_prefix_hash(args.c0_elf, symbol)
    gc_text = section_bytes(args.gc_elf, ".text")
    c0_text = section_bytes(args.c0_elf, ".text")
    report = {
        "schema": "ntruplus768-gt32-production-reachable-hot-text-compaction-v1",
        "experiment": "PRODUCTION-REACHABLE-HOT-TEXT-COMPACTION-001",
        "phase_a": {
            "encap_reachable_functions": len(census["rows"]),
            "encap_reachable_named_bytes": census["encap_reachable_named_bytes"],
            "linked_text_bytes": census["text_bytes"],
            "only_zero_cost_candidate": symbol,
            "post_ret_padding_bytes": census["zero_cost_trailing_padding_bytes"],
        },
        "phase_b_c0": {
            "gc_text_bytes": gc_text,
            "c0_text_bytes": c0_text,
            "text_delta": c0_text - gc_text,
            "gc_symbol_bytes": symbol_size(args.gc_elf, symbol),
            "c0_symbol_bytes": symbol_size(args.c0_elf, symbol),
            "executed_prefix_sha256": {"Gc": gc_hash, "C0": c0_hash},
            "executed_prefix_identical": gc_hash == c0_hash,
            "kat": "100-of-100-canonical-request-response-byte-exact",
            "formal_supercop": supercop["pooled"],
            "decision": "hard-stop-Encap-regresses-in-all-four-blocks",
        },
        "phase_c_c1": {
            "shape": "six-fixed-route-block-loops-same-transpose-v9-reducer-and-packet-math",
            "symbol_bytes": local["symbol_bytes"],
            "launch_median_deltas": local_medians(local),
            "correctness": local["correctness"],
            "decision": local["decision"],
            "full_supercop_run": False,
            "full_supercop_reason": "predeclared-local-stop-loss-exceeded-by-about-35-core-cycles-per-pack",
        },
        "call_boundary_static": call_boundary,
        "final_decision": {
            "production_baseline": "Gc/H0",
            "promote_c0": False,
            "promote_c1": False,
            "reachable_hot_text_compaction": "closed-for-current-Q24-and-frontend-shapes",
            "frontend_partial_reroll": "not-eligible-without-a-new-schedule-preserving-mechanism",
            "next": "bounded-Decode-debt",
            "reopen_only_if": [
                "at-least-3KiB-live-text-removal-costs-no-more-than-4-core-cycles-per-pack",
                "a-compact-template-preserves-the-qualified-unrolled-schedule-without-scalar-route-dependencies",
                "another-production-change-already-rebuilds-the-image-and-the-dormant-C0-control-is-regated",
            ],
        },
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
