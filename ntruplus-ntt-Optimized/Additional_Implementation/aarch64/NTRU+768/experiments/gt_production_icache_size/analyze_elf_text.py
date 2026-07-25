#!/usr/bin/env python3
"""Write reproducible ELF text/symbol metadata outside the release tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def run(*args: str) -> str:
    return subprocess.run(
        list(args),
        check=True,
        text=True,
        capture_output=True,
    ).stdout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--top", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    elf = args.elf.resolve()
    if not elf.is_file():
        raise SystemExit(f"ELF not found: {elf}")

    size_output = run("size", str(elf))
    size_fields = size_output.splitlines()[-1].split()
    size = {
        "text": int(size_fields[0]),
        "data": int(size_fields[1]),
        "bss": int(size_fields[2]),
        "total": int(size_fields[3]),
    }

    symbols = []
    for line in run("nm", "-S", "-n", "--defined-only", str(elf)).splitlines():
        fields = line.split()
        if len(fields) != 4:
            continue
        address_text, size_text, kind, name = fields
        if kind.lower() != "t":
            continue
        address = int(address_text, 16)
        symbol_size = int(size_text, 16)
        symbols.append(
            {
                "name": name,
                "address": address,
                "size": symbol_size,
                "address_mod32": address % 32,
                "address_mod64": address % 64,
            }
        )
    largest = sorted(symbols, key=lambda item: item["size"], reverse=True)[
        : args.top
    ]

    payload = {
        "elf": str(elf),
        "sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
        "size": size,
        "largest_text_symbols": largest,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "elf_text.json"
    md_path = args.output_dir / "elf_text.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")

    rows = [
        "| {name} | {size} | {mod32} | {mod64} |".format(
            name=item["name"],
            size=item["size"],
            mod32=item["address_mod32"],
            mod64=item["address_mod64"],
        )
        for item in largest
    ]
    md_path.write_text(
        f"""# ELF text report

ELF: `{elf}`

SHA-256: `{payload["sha256"]}`

| Text | Data | BSS | Total |
|---:|---:|---:|---:|
| {size["text"]} | {size["data"]} | {size["bss"]} | {size["total"]} |

## Largest Text Symbols

| Symbol | Bytes | Address mod32 | Address mod64 |
|---|---:|---:|---:|
{chr(10).join(rows)}
""",
        encoding="ascii",
    )
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
