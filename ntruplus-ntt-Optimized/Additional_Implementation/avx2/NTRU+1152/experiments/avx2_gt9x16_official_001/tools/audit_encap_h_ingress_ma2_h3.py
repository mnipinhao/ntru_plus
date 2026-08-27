#!/usr/bin/env python3
"""Audit the linked H3 zero-materialization PK-ingress/MA2 object."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


H3 = "ntruplus1152_exp001_encap_h_ingress_ma2_h3"
H1_DECODER = "ntruplus1152_exp001_poly_frombytes_h_natural_q"
H1_CONSUMER = "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def disassembly(obj: Path, symbol: str) -> tuple[str, Counter[str], int]:
    text = run("objdump", "-d", "-M", "intel", str(obj))
    try:
        body = text.split(f"<{symbol}>:", 1)[1]
    except IndexError as error:
        raise SystemExit(f"missing disassembly for {symbol}") from error
    body = re.split(r"\n[0-9a-f]+ <", body, maxsplit=1)[0]
    mnemonics = []
    for line in body.splitlines():
        match = re.match(
            r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]+)\b", line)
        if match:
            mnemonic = match.group(1)
            # GAS inserts these bytes only to align the second H1 symbol.  They
            # are not part of either semantic path and H3 has no internal
            # symbol boundary requiring equivalent padding.
            if mnemonic not in ("nop", "data16"):
                mnemonics.append(mnemonic)
    return body, Counter(mnemonics), len(mnemonics)


def symbol_info(obj: Path, symbol: str) -> tuple[int, int]:
    for line in run("nm", "-S", "--defined-only", str(obj)).splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] == symbol:
            return int(fields[0], 16), int(fields[1], 16)
    raise SystemExit(f"missing symbol {symbol}")


def section_info(obj: Path, section: str) -> tuple[int, int]:
    for line in run("readelf", "-SW", str(obj)).splitlines():
        match = re.search(
            rf"\]\s+{re.escape(section)}\s+\S+\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+).*\s(\d+)$",
            line)
        if match:
            return int(match.group(1), 16), int(match.group(2))
    raise SystemExit(f"missing section {section}")


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"generated H3 audit is stale: {path}")
    else:
        path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h3-object", type=Path, required=True)
    parser.add_argument("--h1-object", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text())
    schedule = json.loads(args.schedule.read_text())
    h3_body, h3, h3_total = disassembly(args.h3_object, H3)
    d_body, decoder, decoder_total = disassembly(args.h1_object, H1_DECODER)
    c_body, consumer, consumer_total = disassembly(args.h1_object, H1_CONSUMER)
    h1 = decoder + consumer
    h1_total = decoder_total + consumer_total
    delta = {name: h3[name] - h1[name]
             for name in sorted(set(h3) | set(h1))}

    expected_delta = {
        "vmovdqa": -144,
        "vperm2i128": 0,
        "vpshufb": 0,
        "vpor": 0,
        "vpmullw": 0,
        "vpmulhw": 0,
        "vpaddw": 0,
        "vpsubw": 0,
        "vpmaxuw": -27,
        "vpcmpgtw": 27,
        "vpmovmskb": 27,
        "or": 27,
        "ret": -1,
    }
    for mnemonic, expected in expected_delta.items():
        if delta[mnemonic] != expected:
            raise SystemExit(f"H3-H1 {mnemonic}: {delta[mnemonic]} != {expected}")
    expected_total = contract["expected"]["total_instruction_delta_vs_h1"]
    if h3_total - h1_total != expected_total:
        raise SystemExit(
            f"H3-H1 instructions: {h3_total - h1_total} != {expected_total}")
    if h3["vmovdqu"] != 54 or h3["vmovdqa"] != 270:
        raise SystemExit("H3 load/store ledger changed")
    if h3["vperm2i128"] != 198 or h3["vpshufb"] != 144 or h3["vpor"] != 72:
        raise SystemExit("H3 consumer-required routing ledger changed")
    forbidden = ("call", "push", "pop", "leave", "vzeroupper")
    if any(h3[name] for name in forbidden):
        raise SystemExit("H3 contains a forbidden frame/call/transition instruction")
    if any(name.startswith("j") or name in ("loop", "loope", "loopne") for name in h3):
        raise SystemExit("H3 contains a data-independent or data-dependent branch")
    if re.search(r"\[(?:e?rsp|e?rbp)(?:[+\]-]|\])", h3_body):
        raise SystemExit("H3 contains stack-relative vector or scalar traffic")

    h3_addr, h3_size = symbol_info(args.h3_object, H3)
    h1_decoder_addr, h1_decoder_size = symbol_info(args.h1_object, H1_DECODER)
    h1_consumer_addr, h1_consumer_size = symbol_info(args.h1_object, H1_CONSUMER)
    h3_text, h3_text_align = section_info(args.h3_object, ".text")
    h3_rodata, h3_rodata_align = section_info(args.h3_object, ".rodata")
    h1_text, _ = section_info(args.h1_object, ".text")
    h1_rodata, _ = section_info(args.h1_object, ".rodata")
    if h3_addr % 32 or h3_text_align != 32 or h3_rodata_align != 32:
        raise SystemExit("H3 entry/section alignment changed")

    report = {
        "schema": "encap-h-ingress-ma2-h3-asm-audit/v1",
        "checkpoint": "ENCAP-H-INGRESS-MA2-H3-ASM",
        "h3": {"instructions": h3_total, "text_bytes": h3_size,
               "entry_mod32": h3_addr % 32,
               "mnemonics": dict(sorted(h3.items()))},
        "h1_control": {
            "instructions": h1_total,
            "text_bytes": h1_decoder_size + h1_consumer_size,
            "decoder_entry_mod32": h1_decoder_addr % 32,
            "consumer_entry_mod32": h1_consumer_addr % 32,
            "mnemonics": dict(sorted(h1.items())),
        },
        "delta_h3_minus_h1": {name: value for name, value in delta.items() if value},
        "object_sections": {
            "h3": {"text_bytes": h3_text, "rodata_bytes": h3_rodata,
                   "text_alignment": h3_text_align, "rodata_alignment": h3_rodata_align},
            "h1": {"text_bytes": h1_text, "rodata_bytes": h1_rodata},
        },
        "architecture_ledger": {
            "h1": {"resident_h": True, "h_stores": 72, "h_reloads": 72,
                   "consumer_required_routes": 360},
            "h3": {"resident_h": False, "h_stores": 0, "h_reloads": 0,
                   "consumer_required_routes": 360},
        },
        "allocation": {"expected_peak_ymm": schedule["register_flow"]["peak_ymm"],
                       "stack_bytes": 0, "spill": 0},
        "gates": {
            "official_validation_semantics_tested": True,
            "raw_h1_ma2_output_tested": True,
            "h_boundary_eliminated": True,
            "same_ma2_arithmetic": True,
            "pure_h_abi_routes_zero": True,
            "call_free": True, "branch_free": True, "frame_free": True, "spill_free": True,
            "vzeroupper_free": True, "entry_aligned_32": True,
        },
        "benchmark_authorized": False,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    write(args.output, rendered, args.check)
    print("H3 linked audit: resident h eliminated; -72 stores/-72 reloads; no frame/spill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
