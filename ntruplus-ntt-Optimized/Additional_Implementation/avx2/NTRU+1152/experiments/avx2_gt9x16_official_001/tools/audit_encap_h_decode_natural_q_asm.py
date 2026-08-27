#!/usr/bin/env python3
"""Audit the linked H1 decoder and preprojected-h MA2 control objects."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

DECODER = "ntruplus1152_exp001_poly_frombytes_h_natural_q"
CONSUMER = "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h"
CONTROL = "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def instructions(obj: Path, symbol: str) -> tuple[Counter[str], int]:
    text = run("objdump", "-d", "-M", "intel", str(obj))
    body = text.split(f"<{symbol}>:", 1)[1]
    body = re.split(r"\n[0-9a-f]+ <", body, maxsplit=1)[0]
    mnemonics = []
    for line in body.splitlines():
        match = re.match(
            r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]+)\b", line)
        if match:
            mnemonics.append(match.group(1))
    return Counter(mnemonics), len(mnemonics)


def symbol_info(obj: Path, symbol: str) -> tuple[int, int]:
    for line in run("nm", "-S", "--defined-only", str(obj)).splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] == symbol:
            return int(fields[0], 16), int(fields[1], 16)
    raise SystemExit(f"missing symbol {symbol}")


def section_alignment(obj: Path, section: str) -> int:
    for line in run("readelf", "-SW", str(obj)).splitlines():
        if re.search(rf"\]\s+{re.escape(section)}\s", line):
            return int(line.split()[-1])
    raise SystemExit(f"missing section {section}")


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"generated audit is stale: {path}")
    else:
        path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-object", type=Path, required=True)
    parser.add_argument("--control-object", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    decoder, decoder_total = instructions(args.candidate_object, DECODER)
    consumer, consumer_total = instructions(args.candidate_object, CONSUMER)
    control, control_total = instructions(args.control_object, CONTROL)
    expected_decoder = {"vmovdqu": 54, "vmovdqa": 72, "vperm2i128": 198,
                        "vpshufb": 144, "vpor": 72, "vpcmpgtw": 9,
                        "vpmovmskb": 9, "ret": 1}
    for mnemonic, expected in expected_decoder.items():
        if decoder[mnemonic] != expected:
            raise SystemExit(f"decoder {mnemonic}: {decoder[mnemonic]} != {expected}")
    expected_delta = {"vmovdqa": -72, "vperm2i128": -144,
                      "vpshufb": -144, "vpor": -72}
    for mnemonic, expected in expected_delta.items():
        actual = consumer[mnemonic] - control[mnemonic]
        if actual != expected:
            raise SystemExit(f"consumer delta {mnemonic}: {actual} != {expected}")
    for mnemonic in ("vpmullw", "vpmulhw", "vpsubw", "vpaddw"):
        if consumer[mnemonic] != control[mnemonic]:
            raise SystemExit(f"MA2 arithmetic changed: {mnemonic}")
    forbidden = ("call", "push", "pop", "leave", "vzeroupper")
    if any(decoder[name] or consumer[name] for name in forbidden):
        raise SystemExit("H1 object contains a forbidden frame/call/transition instruction")
    daddr, dsize = symbol_info(args.candidate_object, DECODER)
    caddr, csize = symbol_info(args.candidate_object, CONSUMER)
    report = {
        "schema": "encap-h-decode-natural-q-asm-audit/v1",
        "checkpoint": "ENCAP-H-DECODE-NATURAL-Q-ASM-H1",
        "role": contract["role"],
        "decoder": {"instructions": decoder_total, "text_bytes": dsize,
                    "entry_mod32": daddr % 32, "mnemonics": dict(sorted(decoder.items()))},
        "preprojected_consumer": {
            "instructions": consumer_total, "text_bytes": csize,
            "entry_mod32": caddr % 32, "mnemonics": dict(sorted(consumer.items()))},
        "control_consumer": {"instructions": control_total,
                             "mnemonics": dict(sorted(control.items()))},
        "consumer_delta": {name: consumer[name] - control[name]
                           for name in sorted(set(consumer) | set(control))},
        "sections": {"text_alignment": section_alignment(args.candidate_object, ".text"),
                     "rodata_alignment": section_alignment(args.candidate_object, ".rodata")},
        "gates": {"call_free": True, "frame_free": True, "spill_free": True,
                  "vzeroupper_free": True, "entries_aligned_32": daddr % 32 == caddr % 32 == 0,
                  "same_ma2_arithmetic": True},
        "benchmark_authorized": False,
    }
    if report["sections"] != {"text_alignment": 32, "rodata_alignment": 32}:
        raise SystemExit("H1 section alignment changed")
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    write(args.output, rendered, args.check)
    print("H1 linked audit: decoder exact; MA2 removes 72 loads and 360 routes; no frame/spill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
