#!/usr/bin/env python3
"""Release-safety guard for production SAMPLE-DAG + HIERK8 tree promotion."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


SAMPLE_SYMBOLS = (
    "poly_ntt_mul3",
    "poly_ntt_mul3_add1",
)
SAMPLE_HELPERS = (
    "gt_keygen_ntt_mul3",
    "gt_keygen_ntt_mul3_add1",
)
GENERIC_NTT = "poly_ntt"
GENERIC_BASEINV = "poly_baseinv_scaled_r"
EXPERIMENT_TREE_SYMBOL = "poly_baseinv_scaled_r_hier_k8_tree_candidate"


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


def marker_present(symbols: dict[str, list[tuple[int, str]]], marker: str) -> bool:
    return any(name == marker for name in symbols)


def call_sites(objdump_output: str, addrs: set[int]) -> list[tuple[str, str]]:
    sites: list[tuple[str, str]] = []
    current_function = "<unknown>"
    header_re = re.compile(r"^\s*([0-9a-fA-F]+) <([^>]+)>:")
    call_re = re.compile(r"\b(?:b|bl)\b\s+(?:0x)?([0-9a-fA-F]+)\b")

    for line in objdump_output.splitlines():
        header = header_re.match(line)
        if header:
            current_function = header.group(2)
            continue
        call = call_re.search(line)
        if call and int(call.group(1), 16) in addrs:
            sites.append((current_function, line.strip()))
    return sites


def public_headers_with_internal_symbols(binary: Path) -> list[tuple[Path, str]]:
    candidates = [
        Path.cwd() / "ntruplus",
        binary.parent / "ntruplus",
    ]

    hits: list[tuple[Path, str]] = []
    seen: set[Path] = set()
    needles = list(SAMPLE_SYMBOLS) + [EXPERIMENT_TREE_SYMBOL]
    for directory in candidates:
        if not directory.exists():
            continue
        for header in directory.glob("*.h"):
            resolved = header.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            text = header.read_text(errors="ignore")
            for needle in needles:
                if needle in text:
                    hits.append((header, needle))
    return hits


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: check_gt_sample_hierk8_release_guard.py "
            "[--expect-default|--expect-sample-disabled|--expect-hier-disabled] "
            "<linked-binary>"
        )
        return 2

    mode = sys.argv[1]
    binary = Path(sys.argv[2])
    if mode not in (
        "--expect-default",
        "--expect-sample-disabled",
        "--expect-hier-disabled",
    ):
        print(f"error: unknown mode {mode}", file=sys.stderr)
        return 2
    if not binary.exists():
        print(f"error: binary not found: {binary}", file=sys.stderr)
        return 2

    expect_sample = mode != "--expect-sample-disabled"
    expect_hier_tree = mode != "--expect-hier-disabled"

    symbols = parse_nm(run(["nm", "-n", str(binary)]))
    objdump_output = run(["objdump", "-d", "--no-show-raw-insn", str(binary)])

    failures: list[str] = []

    generic_ntt = exact_text_addresses(symbols, GENERIC_NTT)
    generic_baseinv = exact_text_addresses(symbols, GENERIC_BASEINV)
    if len(generic_ntt) != 1:
        failures.append(f"expected one generic {GENERIC_NTT} symbol, found {len(generic_ntt)}")
    if len(generic_baseinv) != 1:
        failures.append(
            f"expected one generic {GENERIC_BASEINV} symbol, found {len(generic_baseinv)}"
        )

    sample_addrs: set[int] = set()
    sample_symbol_counts: dict[str, int] = {}
    for symbol in SAMPLE_SYMBOLS:
        addrs = exact_text_addresses(symbols, symbol)
        sample_symbol_counts[symbol] = len(addrs)
        sample_addrs.update(addrs)
        if expect_sample and len(addrs) != 1:
            failures.append(f"expected one {symbol} text symbol, found {len(addrs)}")

    sites = call_sites(objdump_output, sample_addrs)
    if expect_sample and len(sites) != 2:
        failures.append(f"expected two SAMPLE-DAG call sites, found {len(sites)}")
    if not expect_sample and sites:
        failures.append(f"SAMPLE-DAG call sites present with sample kill switch: {sites}")

    for function, line in sites:
        if not any(helper in function for helper in SAMPLE_HELPERS):
            failures.append(f"SAMPLE-DAG call outside keygen helper: {function}: {line}")

    sample_enabled_marker = marker_present(
        symbols, "gt_release_guard_sample_dag_enabled"
    )
    sample_disabled_marker = marker_present(
        symbols, "gt_release_guard_sample_dag_disabled"
    )
    hier_enabled_marker = marker_present(
        symbols, "gt_release_guard_hierk8_tree_enabled"
    )
    hier_disabled_marker = marker_present(
        symbols, "gt_release_guard_hierk8_tree_disabled"
    )
    if expect_sample and not sample_enabled_marker:
        failures.append("missing gt_release_guard_sample_dag_enabled marker")
    if not expect_sample and not sample_disabled_marker:
        failures.append("missing gt_release_guard_sample_dag_disabled marker")
    if expect_hier_tree and not hier_enabled_marker:
        failures.append("missing gt_release_guard_hierk8_tree_enabled marker")
    if not expect_hier_tree and not hier_disabled_marker:
        failures.append("missing gt_release_guard_hierk8_tree_disabled marker")

    experiment_tree_present = any(
        name == EXPERIMENT_TREE_SYMBOL for name in symbols
    )
    if experiment_tree_present:
        failures.append(
            f"experiment-only tree symbol linked into production guard: {EXPERIMENT_TREE_SYMBOL}"
        )

    header_hits = public_headers_with_internal_symbols(binary)
    for header, needle in header_hits:
        failures.append(f"public header exposes internal symbol {needle}: {header}")

    print(f"sample_hierk8_guard_mode={mode.removeprefix('--expect-')}")
    print(f"generic_poly_ntt_symbols={len(generic_ntt)}")
    print(f"generic_poly_baseinv_scaled_r_symbols={len(generic_baseinv)}")
    for symbol, count in sample_symbol_counts.items():
        print(f"{symbol}_symbols={count}")
    print(f"sample_dag_call_sites={len(sites)}")
    for function, line in sites:
        print(f"sample_dag_call_site={function}: {line}")
    print(f"sample_dag_marker_enabled={int(sample_enabled_marker)}")
    print(f"sample_dag_marker_disabled={int(sample_disabled_marker)}")
    print(f"hierk8_tree_marker_enabled={int(hier_enabled_marker)}")
    print(f"hierk8_tree_marker_disabled={int(hier_disabled_marker)}")
    print(f"experiment_tree_symbol_present={int(experiment_tree_present)}")
    print(f"public_headers_with_internal_symbols={len(header_hits)}")

    if failures:
        for failure in failures:
            print(f"release_guard_failure={failure}", file=sys.stderr)
        return 1

    print("generic_poly_ntt_overwritten=0")
    print("generic_poly_baseinv_scaled_r_overwritten=0")
    print("sample_dag_callers_keygen_only=1")
    print("production_default_kill_switches_checked=1")
    print("release_guard_pass=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
