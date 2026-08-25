#!/usr/bin/env python3
"""Exhaustively prove the MA3 inv4-to-serializer reduction contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = 1 << 16


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 0x10000 if value & 0x8000 else value


def signed_high(a: int, b: int) -> int:
    return signed16((a * b) >> 16)


def montgomery_const(a: int, factor: int) -> int:
    factor_qinv = signed16(factor * QINV)
    low = signed16(a * factor_qinv)
    return signed16(signed_high(a, factor) - signed_high(low, Q))


def mulhrs(a: int, b: int) -> int:
    value = (a * b + (1 << 14)) >> 15
    return max(-32768, min(32767, value))


def pack_reduce(value: int) -> int:
    quotient = mulhrs(value, 9)
    reduced = signed16(value - signed16(quotient * Q))
    return signed16(reduced + (Q if reduced < 0 else 0))


def centered(value: int) -> int:
    value %= Q
    if value > Q // 2:
        value -= Q
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    schedule_bytes = args.schedule.read_bytes()
    schedule = json.loads(schedule_bytes)
    ranges = schedule["range_proof"]["ma3"]["final_outputs_precenter"]
    inv4 = centered(pow(4, -1, Q) * R)
    proofs = []
    for coefficient, (lower, upper) in enumerate(ranges):
        outputs = [montgomery_const(x, inv4) for x in range(lower, upper + 1)]
        reduced = [pack_reduce(x) for x in outputs]
        if not all(y == x % Q for x, y in zip(outputs, reduced)):
            raise SystemExit(f"pack reduction failed for coefficient {coefficient}")
        if not all(centered(x) == centered(y) for x, y in zip(outputs, reduced)):
            raise SystemExit(f"center equivalence failed for coefficient {coefficient}")
        proofs.append({
            "coefficient": coefficient,
            "pre_inv4_inclusive": [lower, upper],
            "enumerated_inputs": upper - lower + 1,
            "post_inv4_inclusive": [min(outputs), max(outputs)],
            "pack_output_inclusive": [min(reduced), max(reduced)],
            "pack_matches_mod_q_for_every_input": True,
            "explicit_center_before_pack_required": False,
        })

    report = {
        "schema": "gt-f0-ma3-final-range/v1",
        "checkpoint": "MA3-FINAL-RANGE",
        "method": "exhaustive signed-AVX2-instruction model over every integer in each proved input interval",
        "constants": {"q": Q, "qinv": QINV, "r": R, "inv4_montgomery": inv4,
                      "inv4_qinv_signed16": signed16(inv4 * QINV)},
        "proofs": proofs,
        "selected_finalizer": "inv4 Montgomery output directly into MA1_PACK_CHUNK",
        "rejected_redundant_primitive": "MA1_CENTER2 after inv4",
        "static_saving_full_path": {
            "centered_vectors_removed": 72,
            "instructions_removed": 720,
            "note": "four two-vector MA1_CENTER2 expansions per chunk, nine chunks, twenty instructions each"
        },
        "schedule_sha256": hashlib.sha256(schedule_bytes).hexdigest(),
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.write_text(rendered)
    print("MA3-FINAL-RANGE: exhaustive inv4/pack proof passed; explicit final center is redundant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
