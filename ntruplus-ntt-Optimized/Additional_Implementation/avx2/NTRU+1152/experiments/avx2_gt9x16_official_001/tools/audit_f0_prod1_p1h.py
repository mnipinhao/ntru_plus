#!/usr/bin/env python3
"""Audit F0-PROD1 P1-H wrapper, AVX2 helper, and instruction attribution."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path


WRAPPER = "ntruplus1152_exp001_f0_forward_for_ma2_p1h"
HELPER = "ntruplus1152_exp001_f0_prod1_p1h_pair"
PREFIX = "ntruplus1152_exp001_f0_prod1_p1h_"


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def symbols(path: Path) -> dict[str, tuple[int, int, str]]:
    result = {}
    for line in run("readelf", "-sW", str(path)).splitlines():
        parts = line.split()
        if len(parts) >= 8 and parts[0].rstrip(":").isdigit():
            result[parts[-1]] = (int(parts[1], 16), int(parts[2]), parts[3])
    return result


def instructions(path: Path) -> list[tuple[int, str, str]]:
    result = []
    for line in run("objdump", "-d", "-M", "intel", str(path)).splitlines():
        match = re.match(
            r"\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]+)\s*(.*)",
            line)
        if match:
            result.append((int(match.group(1), 16), match.group(2), match.group(3)))
    return result


def region_counts(insns: list[tuple[int, str, str]], syms: dict, name: str) -> dict:
    begin = syms[PREFIX + name + "_begin"][0]
    end = syms[PREFIX + name + "_end"][0]
    counts = collections.Counter(opcode for address, opcode, _ in insns
                                 if begin <= address < end)
    return {"bytes": end - begin, "instructions": sum(counts.values()),
            "opcodes": dict(sorted(counts.items()))}


def text_alignment(path: Path, section_name: str) -> int:
    for line in run("readelf", "-SW", str(path)).splitlines():
        if re.search(rf"\]\s+{re.escape(section_name)}\s", line):
            return int(line.split()[-1])
    raise SystemExit(f"cannot read {section_name} alignment")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wrapper-object", type=Path, required=True)
    parser.add_argument("--helper-object", type=Path, required=True)
    parser.add_argument("--wrapper-source", type=Path, required=True)
    parser.add_argument("--helper-source", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    schedule = json.loads(args.schedule.read_text())
    wrapper_symbols = symbols(args.wrapper_object)
    helper_symbols = symbols(args.helper_object)
    wrapper_insns = instructions(args.wrapper_object)
    helper_insns = instructions(args.helper_object)
    if WRAPPER not in wrapper_symbols or HELPER not in helper_symbols:
        raise SystemExit("missing P1-H wrapper or helper symbol")

    wrapper_dis = run("objdump", "-dr", "-M", "intel", str(args.wrapper_object))
    helper_dis = run("objdump", "-dr", "-M", "intel", str(args.helper_object))
    wrapper_targets = sorted(set(re.findall(r"R_X86_64_PLT32\s+([^\s-]+)", wrapper_dis)))
    expected_targets = sorted({"ntruplus1152_exp001_top_split_small", HELPER,
                               "__stack_chk_fail"})
    if wrapper_targets != expected_targets:
        raise SystemExit(f"unexpected wrapper targets: {wrapper_targets}")
    if re.search(r"\bcall\b", helper_dis):
        raise SystemExit("P1-H helper contains a call")
    if re.search(r"\bvzeroupper\b", helper_dis):
        raise SystemExit("P1-H helper contains vzeroupper")
    if re.search(r"\b(?:push|pop)\b|\b(?:sub|add)\s+rsp", helper_dis):
        raise SystemExit("P1-H helper has a stack frame")
    if re.search(r"\b(?:vmov|vst)[a-z0-9]*\b[^\n]*\[(?:r|e)sp", helper_dis):
        raise SystemExit("P1-H helper has a vector stack access")
    forbidden = sorted(set(re.findall(r"\b(?:poly_ntt|official_to_f0)\w*", wrapper_dis + helper_dis)))
    if forbidden:
        raise SystemExit(f"Official boundary in P1-H: {forbidden}")

    stack = [int(value, 16) for value in
             re.findall(r"sub\s+rsp,0x([0-9a-f]+)", wrapper_dis)]
    if not stack or max(stack) > 2432:
        raise SystemExit(f"P1-H wrapper frame exceeds 2432 bytes: {stack}")
    wrapper_address, wrapper_size, _ = wrapper_symbols[WRAPPER]
    helper_address, helper_size, _ = helper_symbols[HELPER]
    text_align = text_alignment(args.helper_object, ".text")
    rodata_align = text_alignment(args.helper_object, ".rodata")
    if wrapper_address % 32 or helper_address % 32 or text_align < 32 or rodata_align < 32:
        raise SystemExit("P1-H code/constants are not 32-byte aligned")

    regions = {name: region_counts(helper_insns, helper_symbols, name)
               for name in ("formation_pair0", "formation_pair1", "r2_second", "d1")}
    expected_region_opcodes = {
        "formation_pair0": {"vmovdqa": 63, "vpaddw": 30, "vperm2i128": 18,
                            "vpermq": 54, "vpmulhrsw": 18, "vpmulhw": 48,
                            "vpmullw": 42, "vpshufb": 18, "vpshufd": 36,
                            "vpsubw": 60, "vpunpckhqdq": 9, "vpunpcklqdq": 9},
        "formation_pair1": {"vmovdqa": 63, "vpaddw": 30, "vperm2i128": 18,
                            "vpermq": 54, "vpmulhrsw": 18, "vpmulhw": 48,
                            "vpmullw": 42, "vpshufb": 18, "vpshufd": 36,
                            "vpsubw": 60, "vpunpckhqdq": 9, "vpunpcklqdq": 9},
        "r2_second": {"vmovdqa": 44, "vpaddw": 30, "vpmulhw": 28,
                      "vpmullw": 14, "vpsubw": 32},
        "d1": {"vmovdqa": 46, "vpaddw": 36, "vpblendd": 18,
               "vpblendw": 18, "vperm2i128": 18, "vpmulhw": 72,
               "vpmullw": 36, "vpsllq": 18, "vpsrlq": 18,
               "vpsubw": 72, "vpunpckhqdq": 9, "vpunpcklqdq": 9},
    }
    for name, expected in expected_region_opcodes.items():
        if regions[name]["opcodes"] != expected:
            raise SystemExit(f"P1-H {name} instruction ledger changed")
    if regions["formation_pair0"]["opcodes"] != regions["formation_pair1"]["opcodes"]:
        raise SystemExit("terminal-pair formation paths differ structurally")

    maps = schedule["direct_load_route"]["load_map_count"]
    routing_per_map = schedule["direct_load_route"]["instructions_per_map"]
    report = {
        "checkpoint": "F0-PROD1-ASM-P1-H",
        "wrapper": {
            "symbol": WRAPPER, "text_bytes": wrapper_size,
            "stack_reservation_bytes": max(stack),
            "static_call_targets": wrapper_targets,
            "dynamic_calls_per_forward": {"top_split": 1, "p1h_pair_helper": 4},
            "vzeroupper_static": len(re.findall(r"\bvzeroupper\b", wrapper_dis)),
        },
        "helper": {
            "symbol": HELPER, "text_bytes": helper_size,
            "entry_mod32": helper_address % 32, "entry_mod64": helper_address % 64,
            "text_alignment_bytes": text_align, "rodata_alignment_bytes": rodata_align,
            "calls": 0, "stack_frame_bytes": 0, "vector_stack_accesses": 0,
            "vzeroupper_static": 0, "official_representation_calls": [],
            "constant_time_control": "branches depend only on fixed public terminal-pair selector",
            "regions": regions,
        },
        "dynamic_instruction_attribution_per_forward": {
            "formation": {
                "maps": maps, "aligned_split_loads": maps * 4,
                "routing": {key: maps * value for key, value in routing_per_map.items()
                            if key != "routing_total"},
                "routing_total": maps * routing_per_map["routing_total"],
                "twist_montgomery_chains": maps * 2,
                "twist_montgomery_instructions": maps * 8,
            },
            "r2_first": {"radix3_bodies": 24, "reductions": 72,
                         "transient_f0_stores": 72},
            "r2_second": {"region_executions": 4,
                          "instructions": 4 * regions["r2_second"]["instructions"],
                          "loads_and_stores": 4 * 36},
            "d1": {"region_executions": 4,
                   "instructions": 4 * regions["d1"]["instructions"],
                   "loads_and_stores": 4 * 36},
            "boundary": {"top_split_calls": 1, "helper_calls": 4,
                         "internal_helper_calls": 0, "internal_vzeroupper": 0},
        },
        "removed_staging": {"scalar_gt_adapter_calls": 0,
                            "coefficient_bytes": 0, "pair_input_bytes": 0,
                            "pair_output_bytes": 0},
        "retained": {"top_split_materialization_bytes": 2304,
                     "top_split_arithmetic": "unchanged"},
        "decision": {"structural_gate": "passed",
                     "correctness_gate": "enforced-by-test-f0-prod1-p1h",
                     "producer_benchmark_authorized": True,
                     "kem_benchmark_authorized": False},
        "sha256": {"wrapper_object": hashlib.sha256(args.wrapper_object.read_bytes()).hexdigest(),
                   "helper_object": hashlib.sha256(args.helper_object.read_bytes()).hexdigest(),
                   "wrapper_source": hashlib.sha256(args.wrapper_source.read_bytes()).hexdigest(),
                   "helper_source": hashlib.sha256(args.helper_source.read_bytes()).hexdigest(),
                   "schedule": hashlib.sha256(args.schedule.read_bytes()).hexdigest()},
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
