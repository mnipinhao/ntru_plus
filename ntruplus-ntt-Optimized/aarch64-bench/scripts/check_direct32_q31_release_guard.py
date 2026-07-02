#!/usr/bin/env python3
"""Release-safety guard for the direct32 Q31 encap-only opt-in."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


GENERIC_SYMBOL = "poly_basemul_add"
Q31_SYMBOL = "poly_basemul_add_encap_direct32_q31_tobytes_contract"
HELPER_SYMBOL = "gt_encap_basemul_add_tobytes_contract"


def run(command: list[str]) -> str:
    return subprocess.check_output(command, text=True)


def parse_nm(nm_output: str) -> dict[str, list[tuple[int, str]]]:
    symbols: dict[str, list[tuple[int, str]]] = {}
    for line in nm_output.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        address_text, kind, name = parts[0], parts[1], parts[2]
        if not re.fullmatch(r"[0-9a-fA-F]+", address_text):
            continue
        symbols.setdefault(name, []).append((int(address_text, 16), kind))
    return symbols


def exact_text_addresses(
    symbols: dict[str, list[tuple[int, str]]], name: str
) -> list[int]:
    return [addr for addr, kind in symbols.get(name, []) if kind.lower() == "t"]


def q31_call_sites(
    objdump_output: str, q31_addrs: set[int]
) -> list[tuple[str, str]]:
    sites: list[tuple[str, str]] = []
    current_function = "<unknown>"
    header_re = re.compile(r"^\s*([0-9a-fA-F]+) <([^>]+)>:")
    call_re = re.compile(r"\bbl\b\s+(?:0x)?([0-9a-fA-F]+)\b")

    for line in objdump_output.splitlines():
        header = header_re.match(line)
        if header:
            current_function = header.group(2)
            continue
        call = call_re.search(line)
        if call and int(call.group(1), 16) in q31_addrs:
            sites.append((current_function, line.strip()))
    return sites


def public_headers_with_q31_symbol(binary: Path) -> list[Path]:
    candidates = [
        Path.cwd() / "ntruplus",
        binary.parent / "ntruplus",
    ]

    headers: list[Path] = []
    seen: set[Path] = set()
    for directory in candidates:
        if not directory.exists():
            continue
        for header in directory.glob("*.h"):
            resolved = header.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            if Q31_SYMBOL in header.read_text(errors="ignore"):
                headers.append(header)
    return headers


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_direct32_q31_release_guard.py <linked-binary>")
        return 2

    binary = Path(sys.argv[1])
    if not binary.exists():
        print(f"error: binary not found: {binary}", file=sys.stderr)
        return 2

    symbols = parse_nm(run(["nm", "-n", str(binary)]))

    generic_addrs = exact_text_addresses(symbols, GENERIC_SYMBOL)
    q31_addrs = exact_text_addresses(symbols, Q31_SYMBOL)
    helper_addrs = [
        addr
        for name, entries in symbols.items()
        if HELPER_SYMBOL in name
        for addr, kind in entries
        if kind.lower() == "t"
    ]

    failures: list[str] = []
    if not generic_addrs:
        failures.append(f"missing generic text symbol {GENERIC_SYMBOL}")
    if not q31_addrs:
        failures.append(f"missing q31 text symbol {Q31_SYMBOL}")
    if not helper_addrs:
        failures.append(f"missing helper text symbol containing {HELPER_SYMBOL}")
    if set(generic_addrs) & set(q31_addrs):
        failures.append("generic poly_basemul_add and q31 symbol share an address")

    objdump_output = run(["objdump", "-d", "--no-show-raw-insn", str(binary)])
    call_sites = q31_call_sites(objdump_output, set(q31_addrs))
    if not call_sites:
        failures.append(f"no call sites to {Q31_SYMBOL} found")

    non_helper_sites = [
        (function, line)
        for function, line in call_sites
        if HELPER_SYMBOL not in function
    ]
    for function, line in non_helper_sites:
        failures.append(f"q31 call outside encap helper: {function}: {line}")

    public_headers = public_headers_with_q31_symbol(binary)
    for header in public_headers:
        failures.append(f"public header exposes q31 symbol: {header}")

    print(f"generic_poly_basemul_add_symbols={len(generic_addrs)}")
    print(f"direct32_q31_symbols={len(q31_addrs)}")
    print(f"encap_helper_symbols={len(helper_addrs)}")
    print(f"direct32_q31_call_sites={len(call_sites)}")
    for function, line in call_sites:
        print(f"direct32_q31_call_site={function}: {line}")

    if failures:
        for failure in failures:
            print(f"release_guard_failure={failure}", file=sys.stderr)
        return 1

    print("generic_poly_basemul_add_overwritten=0")
    print("decap_or_arithmetic_q31_callers=0")
    print(f"public_headers_with_q31_symbol={len(public_headers)}")
    print("release_guard_pass=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
