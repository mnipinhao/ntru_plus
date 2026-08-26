#!/usr/bin/env python3
"""Audit PROD3 FULL and compare its linked dynamic path with G0/P2-B."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


CANDIDATE = "ntruplus1152_exp001_gt9x16_prod3_aos_full"
CONTROL = "ntruplus1152_exp001_f0_prod2_ma2_p2b_pair"
CONTROL_MARKER = "ntruplus1152_exp001_f0_prod2_ma2_p2b"
ROUTING = (
    "vperm2i128", "vpunpcklwd", "vpunpckhwd", "vpunpckldq",
    "vpunpckhdq", "vpunpcklqdq", "vpunpckhqdq", "vpermq", "vpshufb",
    "vpblendd", "vpblendw", "vpsllq", "vpsrlq",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args: str) -> str:
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def symbols(path: Path) -> dict[str, tuple[int, int]]:
    result = {}
    for line in command("nm", "-S", str(path)).splitlines():
        match = re.match(
            r"^([0-9a-f]+)(?:\s+([0-9a-f]+))?\s+[Tt]\s+(\S+)$", line)
        if match:
            result[match.group(3)] = (int(match.group(1), 16),
                                      int(match.group(2), 16)
                                      if match.group(2) else 0)
    return result


def instructions(path: Path) -> list[tuple[int, str]]:
    result = []
    for line in command("objdump", "-d", "-M", "intel", str(path)).splitlines():
        match = re.match(r"^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*(.*)$", line)
        if match:
            result.append((int(match.group(1), 16), match.group(2)))
    return result


def region(code: list[tuple[int, str]], begin: int, end: int) -> list[str]:
    return [text for address, text in code if begin <= address < end]


def count(lines: list[str], opcode: str) -> int:
    return sum(bool(re.search(rf"\b{opcode}\b", line)) for line in lines)


def ledger(lines: list[str], data_bases: tuple[str, ...]) -> dict:
    routing = {opcode: count(lines, opcode) for opcode in ROUTING}
    data_loads = data_stores = 0
    for line in lines:
        if not re.search(r"\bvmovdq[au]\b", line):
            continue
        if not any(f"[{base}" in line for base in data_bases):
            continue
        if re.search(r"vmovdq[au]\s+YMMWORD PTR", line):
            data_stores += 1
        else:
            data_loads += 1
    return {
        "data_loads": data_loads,
        "data_stores": data_stores,
        "constant_memory_operands": sum("[rip" in line or "[rdx" in line
                                        for line in lines),
        "routing": routing,
        "routing_total": sum(routing.values()),
        "vpmullw": count(lines, "vpmullw"),
        "vpmulhw": count(lines, "vpmulhw"),
        "vpmulhrsw": count(lines, "vpmulhrsw"),
        "calls": count(lines, "call"),
        "conditional_branches": sum(bool(re.search(r"\bj(?!mp\b)[a-z]+\b", x))
                                    for x in lines),
        "stack_references": sum(bool(re.search(r"\[(?:r|e)?(?:sp|bp)[^]]*\]", x))
                                for x in lines),
        "frame_instructions": sum(bool(re.search(
            r"\b(?:push|pop|enter|leave)\b|\b(?:sub|add)\s+rsp", x))
                                  for x in lines),
        "vzeroupper": count(lines, "vzeroupper"),
    }


def add_ledgers(parts: list[tuple[int, dict]]) -> dict:
    result = {}
    for multiplier, part in parts:
        for key, value in part.items():
            if isinstance(value, dict):
                target = result.setdefault(key, {})
                for subkey, subvalue in value.items():
                    target[subkey] = target.get(subkey, 0) + multiplier * subvalue
            else:
                result[key] = result.get(key, 0) + multiplier * value
    return result


def verify_candidate_events(lines: list[str]) -> None:
    events = []
    for line in lines:
        if "vmovdqu" not in line or "[rdi" not in line:
            continue
        match = re.search(r"\[rdi(?:\+0x([0-9a-f]+))?\]", line)
        if not match:
            raise SystemExit(f"cannot decode full backing access: {line}")
        events.append(("store" if "vmovdqu YMMWORD PTR" in line else "load",
                       int(match.group(1), 16) if match.group(1) else 0))
    if len(events) != 288:
        raise SystemExit(f"expected 288 full backing events, found {len(events)}")
    for branch in range(2):
        base = 1152 * branch
        branch_events = events[144 * branch:144 * (branch + 1)]
        for block in range(4):
            group = branch_events[18 * block:18 * (block + 1)]
            expected = {base + 128 * row + 32 * block for row in range(9)}
            if ({offset for op, offset in group[:9]} != expected or
                    {offset for op, offset in group[9:]} != expected or
                    any(op != "load" for op, _ in group[:9]) or
                    any(op != "store" for op, _ in group[9:])):
                raise SystemExit(f"branch {branch} pass-A overwrite gate failed")
        for row in range(9):
            group = branch_events[72 + 8 * row:72 + 8 * (row + 1)]
            expected = [base + 128 * row + 32 * index for index in range(4)]
            if ([offset for op, offset in group[:4]] != expected or
                    [offset for op, offset in group[4:]] != expected or
                    any(op != "load" for op, _ in group[:4]) or
                    any(op != "store" for op, _ in group[4:])):
                raise SystemExit(f"branch {branch} pass-B overwrite gate failed")


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"generated audit is stale: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-object", type=Path, required=True)
    parser.add_argument("--control-object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    proof = json.loads(args.proof.read_text(encoding="utf-8"))
    candidate_symbols = symbols(args.candidate_object)
    control_symbols = symbols(args.control_object)
    candidate_code = instructions(args.candidate_object)
    control_code = instructions(args.control_object)
    candidate_begin, candidate_size = candidate_symbols[CANDIDATE]
    candidate_lines = region(candidate_code, candidate_begin,
                             candidate_begin + candidate_size)
    verify_candidate_events(candidate_lines)
    candidate = ledger(candidate_lines, ("rdi",))

    control_begin, control_size = control_symbols[CONTROL]
    pair0_begin = control_symbols[CONTROL_MARKER + "_formation_pair0_begin"][0]
    pair0_end = control_symbols[CONTROL_MARKER + "_formation_pair0_end"][0]
    pair1_begin = control_symbols[CONTROL_MARKER + "_formation_pair1_begin"][0]
    pair1_end = control_symbols[CONTROL_MARKER + "_formation_pair1_end"][0]
    common_begin = control_symbols[CONTROL_MARKER + "_r2_second_begin"][0]
    prologue = ledger(region(control_code, control_begin, pair0_begin),
                      ("rdi", "rsi"))
    formation0 = ledger(region(control_code, pair0_begin, pair0_end),
                        ("rdi", "rsi"))
    formation1 = ledger(region(control_code, pair1_begin, pair1_end),
                        ("rdi", "rsi"))
    common = ledger(region(control_code, common_begin,
                           control_begin + control_size), ("rdi", "rsi"))
    control = add_ledgers([(4, prologue), (2, formation0), (2, formation1),
                           (4, common)])

    expected_candidate = proof["full"]
    if (candidate["data_loads"] != expected_candidate["data_loads"] or
            candidate["data_stores"] != expected_candidate["data_stores"] or
            candidate["routing_total"] != expected_candidate["routing"] or
            candidate["vpmullw"] != 368 or candidate["vpmulhw"] != 592 or
            candidate["vpmulhrsw"] != 72):
        raise SystemExit(f"candidate linked ledger changed: {candidate}")
    if control["routing_total"] != 936:
        raise SystemExit(f"G0/P2-B linked routing changed: {control['routing_total']}")
    if any(candidate[key] for key in ("calls", "conditional_branches",
                                      "stack_references", "frame_instructions",
                                      "vzeroupper")):
        raise SystemExit("FULL is not frame-free, spill-free fixed-control AVX2")

    used = sorted({int(value) for line in candidate_lines
                   for value in re.findall(r"\bymm(\d+)\b", line)})
    if used != list(range(16)):
        raise SystemExit(f"unexpected candidate register file: {used}")
    if candidate_begin % 32:
        raise SystemExit("FULL entry lost 32-byte alignment")
    source_text = args.source.read_text(encoding="utf-8")
    if ".align" in source_text or source_text.count(".p2align 5") < 2:
        raise SystemExit("ambiguous or missing function alignment")

    report = {
        "schema": "gt9x16-prod3-aos-full-audit/v1",
        "checkpoint": "GT9X16-PROD3-AOS-FULL",
        "comparison_scope": "post-top-split through exact 2304-byte MA2 input ABI",
        "linked_machine_counts": {
            "g0_p2b_four_dynamic_pair_calls": {**control,
                                                "text_bytes": control_size,
                                                "montgomery_chains": 296,
                                                "barrett_vectors": 72,
                                                "peak_live_ymm": 16,
                                                "vector_spills": 0},
            "prod3_persistent_aos_full": {**candidate,
                                          "text_bytes": candidate_size,
                                          "montgomery_chains": 296,
                                          "barrett_vectors": 72,
                                          "peak_live_ymm": 16,
                                          "vector_spills": 0},
            "candidate_minus_control": {
                "data_loads": candidate["data_loads"] - control["data_loads"],
                "data_stores": candidate["data_stores"] - control["data_stores"],
                "constant_memory_operands": (candidate["constant_memory_operands"] -
                                             control["constant_memory_operands"]),
                "routing": candidate["routing_total"] - control["routing_total"],
                "montgomery_chains": 0,
                "barrett_vectors": 0,
                "text_bytes": candidate_size - control_size,
            },
        },
        "routing_attribution": {
            "control": 936,
            "candidate": 576,
            "delta": -360,
            "candidate_decomposition": proof["full"]["routing_decomposition"],
        },
        "overwrite": {
            "both_branches_load_before_overwrite": True,
            "in_place_2304_bytes": True,
            "extra_array_bytes": 0,
        },
        "alignment": {
            "function_entry_bytes": 32,
            "caller_pointer_alignment_required": False,
            "data_memory_opcode": "vmovdqu",
        },
        "authorization": {
            "correctness_and_structural_gate": "passed",
            "benchmark": False,
            "native_kem": False,
        },
        "sha256": {
            "candidate_object": sha256(args.candidate_object),
            "control_object": sha256(args.control_object),
            "source": sha256(args.source),
            "proof": sha256(args.proof),
        },
    }
    write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n",
          args.check)
    print("GT9X16-PROD3-AOS-FULL linked comparison audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
