#!/usr/bin/env python3
"""Exhaustively prove the selected Q24 v=9 reducer on the current bound."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


Q = 3457
V = 9


def rounded_high_word(value: int) -> int:
    result = (value * V + (1 << 14)) >> 15
    if not -(1 << 15) <= result < (1 << 15):
        raise AssertionError("unexpected vpmulhrsw saturation")
    return result


def generate(pack: Path, bound: int) -> dict[str, object]:
    source = pack.read_text()
    required = [
        "ntruplus768_pack_m_highrange12699_avx2:",
        "jmp ntruplus768_pack_m_lazy10788_avx2",
        "vpmulhrsw %ymm13, \\src, %ymm14",
        "vpmullw %ymm15, %ymm14, %ymm14",
        "vpsubw %ymm14, \\src, \\src",
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise AssertionError(f"selected pack assembly shape changed: {missing}")

    quotients: list[int] = []
    centered: list[int] = []
    canonical: list[int] = []
    for value in range(-bound, bound + 1):
        quotient = rounded_high_word(value)
        reduced = value - quotient * Q
        encoded = reduced + (Q if reduced < 0 else 0)
        if not -(1 << 15) <= reduced < (1 << 15):
            raise AssertionError(f"signed16 reduction overflow at {value}")
        if not 0 <= encoded < Q:
            raise AssertionError(f"single sign correction fails at {value}")
        if encoded != value % Q:
            raise AssertionError(f"canonical residue mismatch at {value}")
        quotients.append(quotient)
        centered.append(reduced)
        canonical.append(encoded)

    # The v=9 quotient happens to cover the complete signed-word domain too.
    full_domain_pass = True
    full_centered_min = 1 << 30
    full_centered_max = -(1 << 30)
    for value in range(-(1 << 15), 1 << 15):
        quotient = rounded_high_word(value)
        reduced = value - quotient * Q
        encoded = reduced + (Q if reduced < 0 else 0)
        full_centered_min = min(full_centered_min, reduced)
        full_centered_max = max(full_centered_max, reduced)
        if not (0 <= encoded < Q and encoded == value % Q):
            full_domain_pass = False
            break

    return {
        "schema": "ntruplus768-gt32-range-contract-audit-032r-v1",
        "experiment": "GT32-RANGE-CONTRACT-AUDIT-032R",
        "selected_symbol": "ntruplus768_pack_m_highrange12699_avx2",
        "selected_body": "ntruplus768_pack_m_lazy10788_avx2",
        "historical_names_are_not_current_bounds": True,
        "current_executable_input_bound": [-bound, bound],
        "reducer": {
            "formula": "t=(x*9+16384)>>15; y=x-t*3457; z=y+(y<0?3457:0)",
            "avx2": ["vpmulhrsw v=9", "vpmullw q=3457", "vpsubw", "sign add q"],
            "quotient_range": [min(quotients), max(quotients)],
            "centered_output_range": [min(centered), max(centered)],
            "canonical_output_range": [min(canonical), max(canonical)],
            "single_sign_correction_sufficient": True,
            "mod_q_congruence": True,
            "signed_int16_safe": True,
        },
        "exhaustive_values_checked": 2 * bound + 1,
        "full_signed_int16_supplement": {
            "values_checked": 1 << 16,
            "pass": full_domain_pass,
            "centered_output_range": [full_centered_min, full_centered_max],
        },
        "executable_packet_differential_required": True,
        "decision": "current-20296-contract-pass",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--bound", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.dumps(generate(args.pack, args.bound), indent=2,
                      sort_keys=True) + "\n"
    if args.check:
        if args.output.read_text() != data:
            raise SystemExit("range audit is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)


if __name__ == "__main__":
    main()
