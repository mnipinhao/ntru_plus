#!/usr/bin/env python3
"""Replace one exact `vzeroupper; ret` epilogue without moving any byte."""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess


def output(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def symbol(binary: pathlib.Path, name: str) -> tuple[int, int, str]:
    for line in output("objdump", "-t", str(binary)).splitlines():
        fields = line.split()
        if len(fields) >= 6 and fields[-1] == name and fields[2] == "F":
            return int(fields[0], 16), int(fields[-2], 16), fields[-3]
    raise SystemExit(f"symbol not found: {name}")


def section(binary: pathlib.Path, wanted: str) -> tuple[int, int]:
    pattern = re.compile(
        r"^\s*\d+\s+(\S+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+"
        r"[0-9a-fA-F]+\s+([0-9a-fA-F]+)"
    )
    for line in output("objdump", "-h", str(binary)).splitlines():
        match = pattern.match(line)
        if match and match.group(1) == wanted:
            return int(match.group(2), 16), int(match.group(3), 16)
    raise SystemExit(f"section not found: {wanted}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("symbol")
    parser.add_argument(
        "--mode", choices=("early-ret", "nop-ret"), default="early-ret"
    )
    args = parser.parse_args()

    address, size, section_name = symbol(args.input, args.symbol)
    section_address, section_offset = section(args.input, section_name)
    epilogue_offset = section_offset + address - section_address + size - 4
    image = bytearray(args.input.read_bytes())
    old = bytes(image[epilogue_offset : epilogue_offset + 4])
    if old != bytes.fromhex("c5f877c3"):
        raise SystemExit(
            f"unexpected epilogue for {args.symbol}: {old.hex()} at {epilogue_offset:#x}"
        )
    if args.mode == "early-ret":
        # ret; 3-byte NOP. Padding remains inside the symbol but is unreachable.
        replacement = bytes.fromhex("c30f1f00")
    else:
        # One 3-byte NOP; ret remains at its original address. This distinguishes
        # vzeroupper semantics from the three-byte earlier return site.
        replacement = bytes.fromhex("0f1f00c3")
    image[epilogue_offset : epilogue_offset + 4] = replacement
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(image)
    shutil.copymode(args.input, args.output)
    print(
        f"patched {args.symbol}: address={address:#x} size={size} "
        f"file_offset={epilogue_offset:#x} mode={args.mode}"
    )


if __name__ == "__main__":
    main()
