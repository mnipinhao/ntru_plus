#!/usr/bin/env python3
"""Audit same-binary KEM linkage, symbol layout, and text size."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


SYMBOLS = (
    "bench_crypto_kem_enc_u01v3_prod",
    "bench_crypto_kem_enc_u01v3_candidate",
    "bench_crypto_kem_dec_u01v3_prod",
    "bench_crypto_kem_dec_u01v3_candidate",
    "bench_crypto_kem_enc_u01v3_capture",
    "bench_crypto_kem_dec_u01v3_capture",
    "bench_u01v3_capture_poly_ntt",
    "poly_ntt",
    "poly_ntt_u01v3_g1_r123_s2",
)

FUNCTION_RE = re.compile(r"^([0-9a-fA-F]+)\s+<([^>]+)>:$")
CALL_RE = re.compile(r"^\s*[0-9a-fA-F]+:.*\bbl\s+([0-9a-fA-F]+)\s+<([^>]+)>")


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def read_symbols(binary: Path) -> dict[str, dict[str, int | str]]:
    entries: list[dict[str, int | str]] = []
    for line in run("nm", "-S", "--defined-only", str(binary)).splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        if len(parts) >= 4:
            addr_s, size_s, kind, name = parts[0], parts[1], parts[2], parts[-1]
        else:
            addr_s, kind, name = parts[0], parts[1], parts[-1]
            size_s = "0"
        try:
            address = int(addr_s, 16)
            size = int(size_s, 16)
        except ValueError:
            continue
        entries.append({"name": name, "address": address, "size": size, "kind": kind})

    text_entries = sorted(
        (entry for entry in entries if str(entry["kind"]).lower() == "t"),
        key=lambda entry: int(entry["address"]),
    )
    by_name = {str(entry["name"]): entry for entry in entries}
    result: dict[str, dict[str, int | str]] = {}
    for name in SYMBOLS:
        if name not in by_name:
            raise RuntimeError(f"missing required symbol {name}")
        entry = dict(by_name[name])
        address = int(entry["address"])
        next_addresses = [
            int(other["address"])
            for other in text_entries
            if int(other["address"]) > address
        ]
        entry["span_to_next_text_symbol"] = (
            min(next_addresses) - address if next_addresses else 0
        )
        entry["addr_mod32"] = address & 31
        entry["addr_mod64"] = address & 63
        result[name] = entry
    return result


def disassembly_functions(binary: Path) -> dict[int, dict[str, object]]:
    functions: dict[int, dict[str, object]] = {}
    current: int | None = None
    for line in run("objdump", "-d", str(binary)).splitlines():
        label = FUNCTION_RE.match(line.strip())
        if label:
            current = int(label.group(1), 16)
            functions.setdefault(current, {"name": label.group(2), "calls": []})
            continue
        call = CALL_RE.match(line)
        if current is not None and call:
            calls = functions[current]["calls"]
            assert isinstance(calls, list)
            calls.append((int(call.group(1), 16), call.group(2)))
    return functions


def count_target(calls: list[tuple[int, str]], address: int) -> int:
    return sum(target == address for target, _name in calls)


def count_target_transitive(
    function_address: int,
    address: int,
    functions: dict[int, dict[str, object]],
    depth: int = 4,
    stack: tuple[int, ...] = (),
) -> int:
    if depth < 0 or function_address in stack:
        return 0
    total = 0
    info = functions.get(function_address, {"calls": []})
    calls = info["calls"]
    assert isinstance(calls, list)
    for target, _callee in calls:
        if target == address:
            total += 1
        elif target in functions:
            total += count_target_transitive(
                target, address, functions, depth - 1, (*stack, function_address)
            )
    return total


def binary_text_size(binary: Path) -> int:
    lines = run("size", str(binary)).splitlines()
    return int(lines[-1].split()[0])


def main() -> int:
    if len(sys.argv) not in {2, 3}:
        print(f"usage: {sys.argv[0]} BINARY [OUTPUT_JSON]", file=sys.stderr)
        return 2
    binary = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) == 3 else binary.with_suffix(".layout.json")
    symbols = read_symbols(binary)
    functions = disassembly_functions(binary)
    prod_addr = int(symbols["poly_ntt"]["address"])
    candidate_addr = int(symbols["poly_ntt_u01v3_g1_r123_s2"]["address"])
    capture_addr = int(symbols["bench_u01v3_capture_poly_ntt"]["address"])

    expectations = {
        "bench_crypto_kem_enc_u01v3_prod": (prod_addr, 2),
        "bench_crypto_kem_dec_u01v3_prod": (prod_addr, 2),
        "bench_crypto_kem_enc_u01v3_candidate": (candidate_addr, 2),
        "bench_crypto_kem_dec_u01v3_candidate": (candidate_addr, 2),
        "bench_crypto_kem_enc_u01v3_capture": (capture_addr, 2),
        "bench_crypto_kem_dec_u01v3_capture": (capture_addr, 2),
    }
    linkage: dict[str, object] = {}
    failures: list[str] = []
    for function, (expected_addr, expected_count) in expectations.items():
        function_addr = int(symbols[function]["address"])
        info = functions.get(function_addr, {"calls": []})
        calls = info["calls"]
        assert isinstance(calls, list)
        count = count_target_transitive(function_addr, expected_addr, functions)
        wrong_prod = (
            count_target_transitive(function_addr, prod_addr, functions)
            if expected_addr != prod_addr
            else 0
        )
        wrong_candidate = (
            count_target_transitive(function_addr, candidate_addr, functions)
            if expected_addr != candidate_addr
            else 0
        )
        passed = count == expected_count and wrong_prod == 0 and wrong_candidate == 0
        linkage[function] = {
            "expected_target": expected_addr,
            "expected_resolved_bl_count": expected_count,
            "actual_resolved_bl_count": count,
            "count_includes_compiler_static_helpers": True,
            "wrong_production_calls": wrong_prod,
            "wrong_candidate_calls": wrong_candidate,
            "calls": [{"address": address, "symbol": name} for address, name in calls],
            "pass": passed,
        }
        if not passed:
            failures.append(function)

    candidate_info = functions.get(candidate_addr, {"calls": []})
    candidate_calls = candidate_info["calls"]
    assert isinstance(candidate_calls, list)
    report = {
        "binary": str(binary),
        "binary_text_size": binary_text_size(binary),
        "same_binary": True,
        "measured_poly_ntt_dispatch_branch": False,
        "candidate_poly_ntt_internal_bl_count": len(candidate_calls),
        "symbols": symbols,
        "linkage": linkage,
        "failures": failures,
        "status": "pass" if not failures and not candidate_calls else "fail",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
