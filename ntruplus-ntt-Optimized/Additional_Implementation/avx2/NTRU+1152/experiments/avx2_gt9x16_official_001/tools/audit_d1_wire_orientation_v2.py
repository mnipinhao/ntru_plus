#!/usr/bin/env python3
"""Audit the linked-object shape of the D1 wire-orientation prototype."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def output(*command: str) -> str:
    return subprocess.check_output(command, text=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_sizes(path: Path) -> dict[str, int]:
    result = {}
    for line in output("size", "-A", str(path)).splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] in (".text", ".rodata"):
            result[fields[0][1:]] = int(fields[1])
    return result


def machine(path: Path) -> dict:
    disassembly = output("objdump", "-d", "--no-show-raw-insn", "-M", "intel", str(path))
    mnemonics = re.findall(r"^\s*[0-9a-f]+:\s+([a-z0-9]+)", disassembly, re.MULTILINE)
    counts = {name: mnemonics.count(name) for name in set(mnemonics)}
    forbidden = [
        line.strip() for line in disassembly.splitlines()
        if re.search(r"\b(?:rsp|call|vzeroupper|j[a-z]+)\b", line)
    ]
    return {
        "instructions": len(mnemonics),
        "vpshufb": counts.get("vpshufb", 0),
        "vpermq": counts.get("vpermq", 0),
        "vperm2i128": counts.get("vperm2i128", 0),
        "vpmullw": counts.get("vpmullw", 0),
        "vpmulhw": counts.get("vpmulhw", 0),
        "vpmulhrsw": counts.get("vpmulhrsw", 0),
        "vmovdqa": counts.get("vmovdqa", 0),
        "vmovdqu": counts.get("vmovdqu", 0),
        "ret": counts.get("ret", 0),
        "forbidden": forbidden,
        "sections": section_sizes(path),
        "sha256": sha256(path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    control, candidate = machine(args.control), machine(args.candidate)
    invariant_keys = (
        "vpermq", "vperm2i128", "vpmullw", "vpmulhw", "vpmulhrsw",
        "vmovdqa", "vmovdqu", "ret",
    )
    gates = {
        "vpshufb_56_to_48": control["vpshufb"] == 56 and candidate["vpshufb"] == 48,
        "arithmetic_and_movement_unchanged": all(
            control[key] == candidate[key] for key in invariant_keys
        ),
        "no_forbidden_machine_state": not control["forbidden"] and not candidate["forbidden"],
    }
    if not all(gates.values()):
        raise SystemExit(f"D1 v2 linked audit failed: {gates}")
    report = {
        "schema": "d1-wire-orientation-v2-linked-audit/v1",
        "control": control,
        "candidate": candidate,
        "delta": {
            "instructions": candidate["instructions"] - control["instructions"],
            "vpshufb": candidate["vpshufb"] - control["vpshufb"],
            "text": candidate["sections"]["text"] - control["sections"]["text"],
            "rodata": candidate["sections"]["rodata"] - control["sections"]["rodata"],
        },
        "gates": gates,
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit("stale D1 v2 linked audit")
    else:
        args.output.write_text(text)
    print(json.dumps(report["delta"], sort_keys=True))


if __name__ == "__main__":
    main()
