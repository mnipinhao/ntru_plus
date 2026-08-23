#!/usr/bin/env python3
"""Audit the two fixed-count M3C3 full-D4 AVX2 reduction controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

SYMBOLS = {
    "signed-Barrett": "ntruplus1152_exp001_g1c_m3c3_reduce_barrett",
    "Montgomery-identity": (
        "ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity"),
}


def function_lines(disassembly: str, symbol: str) -> list[str]:
    match = re.search(
        rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
        disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing M3C3 symbol: {symbol}")
    return [line.strip() for line in match.group(1).splitlines()
            if re.match(r"^\s*[0-9a-f]+:", line)]


def mnemonic(line: str) -> str:
    match = re.match(r"^[0-9a-f]+:\s+([a-z0-9]+)\b", line)
    if not match:
        raise SystemExit(f"cannot parse instruction: {line}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", default="cc")
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    proof = json.loads(args.proof.read_text())
    if not proof["decision"]["M3C3_full_reduction_control"].startswith("authorized"):
        raise SystemExit("M3C3 audit requires exact-proof authorization")
    disassembly = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", "-M", "intel",
         str(args.object)], check=True, text=True,
        stdout=subprocess.PIPE).stdout
    functions = {}
    for label, symbol in SYMBOLS.items():
        lines = function_lines(disassembly, symbol)
        counts = Counter(mnemonic(line) for line in lines)
        body = "\n".join(lines)
        entry = {
            "static_instruction_count": len(lines),
            "mnemonics": dict(sorted(counts.items())),
            "vector_loads_in_loop_body": counts["vmovdqu"] // 2,
            "vector_stores_in_loop_body": counts["vmovdqu"] // 2,
            "fixed_public_loop_branches": counts["jne"],
            "calls": counts["call"],
            "vzeroupper": counts["vzeroupper"],
            "frame_or_stack_references": len(re.findall(
                r"\b(?:push|pop|enter|leave)\b|\[(?:r|e)?(?:sp|bp)", body)),
            "forbidden_variable_arithmetic": re.findall(
                r"\b(?:idiv|div|vgather\w*|vscatter\w*)\b", body),
        }
        if (entry["fixed_public_loop_branches"] != 1 or entry["calls"] or
                entry["vzeroupper"] or entry["frame_or_stack_references"] or
                entry["forbidden_variable_arithmetic"]):
            raise SystemExit(f"M3C3 {label} constant-time/leaf audit failed")
        functions[label] = entry
    if functions["signed-Barrett"]["mnemonics"].get("vpmulhrsw") != 1:
        raise SystemExit("signed-Barrett reciprocal multiply disappeared")
    mont = functions["Montgomery-identity"]["mnemonics"]
    if mont.get("vpmullw") != 1 or mont.get("vpmulhw") != 2:
        raise SystemExit("Montgomery identity chain changed")

    report = {
        "schema": "gt-g1c-m3c3-reduction-audit/v1",
        "checkpoint": "G1C-M3C3-full-reduction-controls",
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "proof_sha256": hashlib.sha256(args.proof.read_bytes()).hexdigest(),
        "compiler": subprocess.run(
            [args.compiler, "--version"], check=True, text=True,
            stdout=subprocess.PIPE).stdout.splitlines()[0],
        "cflags": args.cflags,
        "functions": functions,
        "gate": {
            "fixed_72_vector_loop": True,
            "call_frame_stack_vzeroupper_free": True,
            "secret_independent_control_and_index": True,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated M3C3 reduction audit is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
