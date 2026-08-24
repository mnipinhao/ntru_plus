#!/usr/bin/env python3
"""Audit the executable G1C-M3 C0/C1/C2 full inverse16 leaves."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SYMBOLS = {
    "C0": "ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c0",
    "C1": "ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c1",
    "C2": "ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2",
}


def function_lines(disassembly: str, symbol: str) -> list[str]:
    match = re.search(
        rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
        disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing M3 symbol: {symbol}")
    return [line.strip() for line in match.group(1).splitlines()
            if re.match(r"^\s*[0-9a-f]+:", line)]


def mnemonic(line: str) -> str:
    match = re.match(r"^[0-9a-f]+:\s+([a-z0-9]+)\b", line)
    if not match:
        raise SystemExit(f"cannot parse instruction: {line}")
    return match.group(1)


def audit(lines: list[str]) -> dict:
    names = [mnemonic(line) for line in lines]
    body = "\n".join(lines)
    peak_live = 0
    live: set[int] = set()
    for line in reversed(lines):
        instruction = line.split(":", 1)[1].strip()
        registers = [int(value) for value in re.findall(r"\bymm(\d+)\b", instruction)]
        operands = instruction.split(None, 1)[1] if " " in instruction else ""
        first = operands.split(",", 1)[0].strip()
        defined = int(first[3:]) if re.fullmatch(r"ymm\d+", first) else None
        if defined is not None:
            live.discard(defined)
            registers = registers[1:]
        live.update(registers)
        peak_live = max(peak_live, len(live))
    return {
        "static_instructions": len(lines),
        "output_stores": sum(bool(re.search(
            r"\bvmovdqa\s+YMMWORD PTR \[rdi", line)) for line in lines),
        "output_loads": sum(bool(re.search(
            r"\bvmovdqa\s+ymm\d+,YMMWORD PTR \[rdi", line)) for line in lines),
        "vpshufb": names.count("vpshufb"),
        "vperm2i128": names.count("vperm2i128"),
        "vpblendw": names.count("vpblendw"),
        "vpmullw": names.count("vpmullw"),
        "vpmulhw": names.count("vpmulhw"),
        "vpaddw": names.count("vpaddw"),
        "vpsubw": names.count("vpsubw"),
        "calls": len(re.findall(r"\bcall\b", body)),
        "conditional_branches": len(re.findall(r"\bj(?!mp\b)[a-z]+\b", body)),
        "frame_instructions": len(re.findall(
            r"\b(?:push|pop|enter|leave)\b|\b(?:sub|add)\s+rsp", body)),
        "stack_references": len(re.findall(r"\[(?:r|e)?(?:sp|bp)[^]]*\]", body)),
        "vzeroupper": names.count("vzeroupper"),
        "forbidden_instructions": re.findall(
            r"\b(?:idiv|div|vgather\w*|vscatter\w*)\b", body),
        "backward_dataflow_peak_live_ymm": peak_live,
    }


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
    if proof["proved_conservative_alternative"]["status"] != "range-and-scale-proved":
        raise SystemExit("M3 full assembly requires the D1 identity proof")
    disassembly = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", "-M", "intel", str(args.object)],
        check=True, text=True, stdout=subprocess.PIPE).stdout
    functions = {name: audit(function_lines(disassembly, symbol))
                 for name, symbol in SYMBOLS.items()}
    expected = {
        "C0": {"output_stores": 360, "output_loads": 288},
        "C1": {"output_stores": 288, "output_loads": 216},
        "C2": {"output_stores": 144, "output_loads": 72},
    }
    for name, metrics in functions.items():
        for key, value in expected[name].items():
            if metrics[key] != value:
                raise SystemExit(f"{name} {key}: expected {value}, found {metrics[key]}")
        if any((metrics["calls"], metrics["conditional_branches"],
                metrics["frame_instructions"], metrics["stack_references"],
                metrics["vzeroupper"], metrics["forbidden_instructions"])):
            raise SystemExit(f"{name} leaf/constant-time audit failed")
    if functions["C2"]["backward_dataflow_peak_live_ymm"] > 16:
        raise SystemExit("C2 exceeds the architectural YMM file")

    report = {
        "schema": "gt-g1c-m3-full-inverse16-audit/v1",
        "checkpoint": "G1C-M3-C0-C1-C2-executable-full-path",
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "proof_sha256": hashlib.sha256(args.proof.read_bytes()).hexdigest(),
        "compiler": subprocess.run(
            [args.compiler, "--version"], check=True, text=True,
            stdout=subprocess.PIPE).stdout.splitlines()[0],
        "cflags": args.cflags,
        "functions": functions,
        "attribution": {
            "C1_minus_C0": "BMScale-to-D1 live edge with identical D1 identity repair and materialized D2/D4/D8",
            "C2_minus_C1": "register-persistent D2/D4/D8 after one identical repaired-D1 boundary",
            "C2_minus_C0": "total edge plus persistent credit",
        },
        "internal_alias_contract": "output, a, and b are pairwise non-aliasing",
        "constant_time_static": True,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated M3 full inverse16 audit is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
