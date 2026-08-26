#!/usr/bin/env python3
"""Audit the linked materialized P2-B producer and MA2-native consumer."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path


WRAPPER = "ntruplus1152_exp001_f0_forward_for_ma2_p2b"
HELPER = "ntruplus1152_exp001_f0_prod2_ma2_p2b_pair"
PREFIX = "ntruplus1152_exp001_f0_prod2_ma2_p2b_"
GENERIC_MA2 = "ntruplus1152_exp001_f0_ma2_full"
NATIVE_MA2 = "ntruplus1152_exp001_f0_ma2_native_full"


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


def symbol_region(insns: list[tuple[int, str, str]], syms: dict,
                  name: str) -> list[tuple[int, str, str]]:
    begin, size, _ = syms[name]
    return [insn for insn in insns if begin <= insn[0] < begin + size]


def marked_region(insns: list[tuple[int, str, str]], syms: dict,
                  name: str) -> list[tuple[int, str, str]]:
    begin = syms[PREFIX + name + "_begin"][0]
    end = syms[PREFIX + name + "_end"][0]
    return [insn for insn in insns if begin <= insn[0] < end]


def opcodes(region: list[tuple[int, str, str]]) -> dict[str, int]:
    return dict(sorted(collections.Counter(x[1] for x in region).items()))


def text_alignment(path: Path, section_name: str) -> int:
    for line in run("readelf", "-SW", str(path)).splitlines():
        if re.search(rf"\]\s+{re.escape(section_name)}\s", line):
            return int(line.split()[-1])
    raise SystemExit(f"cannot read {section_name} alignment")


def rdi_offset(operands: str) -> int | None:
    match = re.search(r"\[rdi(?:\+0x([0-9a-f]+))?\]", operands)
    if not match:
        return None
    return int(match.group(1), 16) if match.group(1) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wrapper-object", type=Path, required=True)
    parser.add_argument("--helper-object", type=Path, required=True)
    parser.add_argument("--ma2-object", type=Path, required=True)
    parser.add_argument("--wrapper-source", type=Path, required=True)
    parser.add_argument("--helper-source", type=Path, required=True)
    parser.add_argument("--ma2-source", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--prod1-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text())
    mapping = json.loads(args.map.read_text())
    prod1 = json.loads(args.prod1_audit.read_text())
    if contract["schema"] != "gt-f0-prod2-ma2-asm/v1":
        raise SystemExit("wrong PROD2 assembly contract")
    if not mapping["decision"]["asm0_authorized"]:
        raise SystemExit("MAP checkpoint does not authorize ASM0")

    wrapper_syms = symbols(args.wrapper_object)
    helper_syms = symbols(args.helper_object)
    ma2_syms = symbols(args.ma2_object)
    helper_insns = instructions(args.helper_object)
    ma2_insns = instructions(args.ma2_object)
    if WRAPPER not in wrapper_syms or HELPER not in helper_syms:
        raise SystemExit("missing PROD2 wrapper/helper symbol")
    if GENERIC_MA2 not in ma2_syms or NATIVE_MA2 not in ma2_syms:
        raise SystemExit("missing generic/native MA2 consumer symbols")

    wrapper_dis = run("objdump", "-dr", "-M", "intel", str(args.wrapper_object))
    helper_dis = run("objdump", "-dr", "-M", "intel", str(args.helper_object))
    ma2_dis = run("objdump", "-dr", "-M", "intel", str(args.ma2_object))
    targets = sorted(set(re.findall(r"R_X86_64_PLT32\s+([^\s-]+)", wrapper_dis)))
    expected_targets = sorted({"ntruplus1152_exp001_top_split_small", HELPER,
                               "__stack_chk_fail"})
    if targets != expected_targets:
        raise SystemExit(f"unexpected PROD2 wrapper targets: {targets}")
    for name, disassembly in (("helper", helper_dis), ("native MA2", ma2_dis)):
        if name == "native MA2":
            region_text = "\n".join(
                f"{address:x}: {opcode} {operands}"
                for address, opcode, operands in symbol_region(ma2_insns, ma2_syms,
                                                               NATIVE_MA2))
        else:
            region_text = disassembly
        if re.search(r"\bcall\b|\bvzeroupper\b", region_text):
            raise SystemExit(f"{name} contains a call or vzeroupper")
        if re.search(r"\b(?:push|pop)\b|\b(?:sub|add)\s+rsp", region_text):
            raise SystemExit(f"{name} has a stack frame")
        if re.search(r"\bvmov[a-z0-9]*\b[^\n]*\[(?:r|e)sp", region_text):
            raise SystemExit(f"{name} has a vector stack access")

    stack = [int(value, 16) for value in
             re.findall(r"sub\s+rsp,0x([0-9a-f]+)", wrapper_dis)]
    if not stack or max(stack) > 2432:
        raise SystemExit(f"PROD2 wrapper frame exceeds 2432 bytes: {stack}")
    helper_address, helper_size, _ = helper_syms[HELPER]
    native_address, native_size, _ = ma2_syms[NATIVE_MA2]
    if helper_address % 32 or native_address % 32:
        raise SystemExit("PROD2 helper or MA2-native consumer is not 32-byte aligned")
    if text_alignment(args.helper_object, ".text") < 32:
        raise SystemExit("PROD2 helper text alignment dropped below 32")
    if text_alignment(args.helper_object, ".rodata") < 32:
        raise SystemExit("PROD2 constant alignment dropped below 32")

    region_names = ("formation_pair0", "formation_pair1", "r2_second", "d1")
    regions = {name: opcodes(marked_region(helper_insns, helper_syms, name))
               for name in region_names}
    control = {name: prod1["helper"]["regions"][name]["opcodes"]
               for name in region_names}
    for name in region_names[:-1]:
        if regions[name] != control[name]:
            raise SystemExit(f"PROD2 changed frozen {name} arithmetic/schedule")
    expected_d1 = dict(control["d1"])
    expected_d1["vperm2i128"] += 18
    if regions["d1"] != expected_d1:
        raise SystemExit("PROD2 D1 differs by more than the 18 P2-B epilogue permutes")

    d1 = marked_region(helper_insns, helper_syms, "d1")
    accesses: dict[int, dict[str, list[int]]] = collections.defaultdict(
        lambda: {"read": [], "write": []})
    for index, (_, opcode, operands) in enumerate(d1):
        if opcode != "vmovdqa":
            continue
        offset = rdi_offset(operands)
        if offset is None:
            continue
        if operands.startswith("ymm"):
            accesses[offset]["read"].append(index)
        elif operands.startswith("YMMWORD PTR [rdi"):
            accesses[offset]["write"].append(index)
    expected_offsets = [row * 128 + stream * 32
                        for row in range(9) for stream in range(2)]
    last_use = []
    for offset in expected_offsets:
        access = accesses[offset]
        if len(access["read"]) != 1 or len(access["write"]) != 1:
            raise SystemExit(f"unexpected D1 access count for slot {offset}: {access}")
        last_read = access["read"][0]
        first_write = access["write"][0]
        if first_write <= last_read:
            raise SystemExit(f"P2-B overwrites slot {offset} before its last read")
        last_use.append({"byte_offset": offset,
                         "last_read_instruction": last_read,
                         "first_write_instruction": first_write,
                         "strictly_after": True})
    unexpected = sorted(set(accesses) - set(expected_offsets))
    if unexpected:
        raise SystemExit(f"unexpected D1 backing slots: {unexpected}")

    generic_region = symbol_region(ma2_insns, ma2_syms, GENERIC_MA2)
    native_region = symbol_region(ma2_insns, ma2_syms, NATIVE_MA2)
    generic_counts = collections.Counter(x[1] for x in generic_region)
    native_counts = collections.Counter(x[1] for x in native_region)
    opcode_delta = {opcode: native_counts[opcode] - generic_counts[opcode]
                    for opcode in set(generic_counts) | set(native_counts)
                    if native_counts[opcode] != generic_counts[opcode]}
    if opcode_delta != {"vmovdqa": -144, "vperm2i128": -144}:
        raise SystemExit(f"MA2-native changed more than input formation: {opcode_delta}")
    native_r_loads = [x for x in native_region
                      if x[1] == "vmovdqa" and "[rsi" in x[2]]
    native_m_loads = [x for x in native_region
                      if x[1] == "vmovdqa" and "[rdx" in x[2]]
    if len(native_r_loads) != 72 or len(native_m_loads) != 72:
        raise SystemExit("MA2-native does not load exactly 72 planes per operand")
    native_branches = [x for x in native_region if x[1].startswith("j")]
    if native_branches:
        raise SystemExit("MA2-native consumer contains a conditional branch")

    report = {
        "schema": "gt-f0-prod2-ma2-audit/v1",
        "checkpoint": "F0-PROD2-MA2-ASM0",
        "wrapper": {
            "symbol": WRAPPER, "stack_reservation_bytes": max(stack),
            "static_call_targets": targets,
            "dynamic_calls_per_forward": {"top_split": 1, "p2b_pair_helper": 4},
        },
        "helper": {
            "symbol": HELPER, "text_bytes": helper_size,
            "entry_mod32": helper_address % 32,
            "entry_mod64": helper_address % 64,
            "calls": 0, "stack_frame_bytes": 0, "vector_spills": 0,
            "vzeroupper": 0, "regions": regions,
            "constant_time_control":
                "only the unchanged fixed public terminal-pair selector branches",
        },
        "arithmetic_identity": {
            "formation_and_r2_opcode_ledgers_equal_p1h": True,
            "d1_delta": {"vperm2i128": 18},
            "new_reductions": 0, "scale_conversions": 0,
        },
        "materialized_boundary": {
            "generic_f0_final_stores": 0,
            "p2b_vperm2i128_per_forward": 72,
            "aligned_plane_stores_per_forward": 72,
            "extra_temporary_bytes": 0,
            "backing_bytes": 2304,
            "last_use_overwrite": last_use,
            "all_18_static_slots_safe": len(last_use) == 18,
        },
        "ma2_native_consumer": {
            "symbol": NATIVE_MA2, "text_bytes": native_size,
            "entry_mod32": native_address % 32,
            "r_plane_loads": len(native_r_loads),
            "m_plane_loads": len(native_m_loads),
            "generic_projection_permutations": 0,
            "conditional_branches": 0,
            "opcode_delta_vs_generic_ma2": opcode_delta,
            "arithmetic_and_serializer_equal": True,
        },
        "decision": {
            "correctness_gate": "enforced-by-test-f0-prod2-ma2-asm0",
            "structural_gate": "passed",
            "producer_boundary_benchmark_authorized": True,
            "kem_benchmark_authorized": False,
        },
        "sha256": {key: hashlib.sha256(path.read_bytes()).hexdigest()
                   for key, path in {
                       "wrapper_object": args.wrapper_object,
                       "helper_object": args.helper_object,
                       "ma2_object": args.ma2_object,
                       "wrapper_source": args.wrapper_source,
                       "helper_source": args.helper_source,
                       "ma2_source": args.ma2_source,
                       "contract": args.contract,
                       "map": args.map,
                       "prod1_audit": args.prod1_audit,
                   }.items()},
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
