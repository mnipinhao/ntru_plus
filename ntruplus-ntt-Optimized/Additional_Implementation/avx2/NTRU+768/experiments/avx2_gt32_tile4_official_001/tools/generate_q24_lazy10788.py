#!/usr/bin/env python3
"""Prove the scalar range/scale contract of the lazy10788 Q24 GT-pack."""

import argparse
import json
from pathlib import Path


Q = 3457
BOUND = 10788
V = 9


def rounded_high_word(value: int) -> int:
    """Exact signed vpmulhrsw result; saturation is inactive for this gate."""
    result = (value * V + (1 << 14)) >> 15
    if not -(1 << 15) <= result < (1 << 15):
        raise AssertionError("unexpected vpmulhrsw saturation")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=Path("generated/tile4_q24_lazy10788_gate.json"))
    args = parser.parse_args()

    quotients = []
    centered = []
    canonical = []
    for value in range(-BOUND, BOUND + 1):
        quotient = rounded_high_word(value)
        reduced = value - quotient * Q
        encoded = reduced + (Q if reduced < 0 else 0)
        if not -(1 << 15) <= reduced < (1 << 15):
            raise AssertionError(f"int16 overflow at {value}")
        if not 0 <= encoded < Q:
            raise AssertionError(f"single sign correction fails at {value}")
        if (encoded - value) % Q != 0:
            raise AssertionError(f"congruence fails at {value}")
        quotients.append(quotient)
        centered.append(reduced)
        canonical.append(encoded)

    result = {
        "schema": "ntruplus768-gt32-q24-lazy10788-contract-v1",
        "experiment": "GT32-Q24-LAZY10788-GTPACK-001",
        "contract": {
            "input_layout": "private BM SoA",
            "input_scale_exponent": 0,
            "input_inclusive_range": [-BOUND, BOUND],
            "output": "Official canonical 1152-byte serialization",
            "alias": "input and output disjoint",
            "input_is_nondestructive": True,
        },
        "reducer": {
            "formula": "t=(x*9+16384)>>15; y=x-t*3457",
            "avx2": ["vpmulhrsw v=9", "vpmullw q=3457", "vpsubw"],
            "quotient_range": [min(quotients), max(quotients)],
            "centered_output_range": [min(centered), max(centered)],
            "canonical_output_range": [min(canonical), max(canonical)],
            "single_sign_correction_sufficient": True,
            "signed_int16_safe": True,
            "mod_q_congruence": True,
        },
        "exhaustive_values_checked": 2 * BOUND + 1,
        "assembly_shape": {
            "q24_packets": 48,
            "extra_vector_instructions_per_packet": 3,
            "standalone_canonical_materialization": False,
            "centered_gtpack_symbol_modified": False,
        },
        "decision": "range-and-scale-proof-pass",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
