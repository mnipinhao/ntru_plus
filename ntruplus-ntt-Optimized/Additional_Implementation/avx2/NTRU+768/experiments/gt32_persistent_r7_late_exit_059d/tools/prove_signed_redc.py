#!/usr/bin/env python3
"""Exact interval proof for the signed-low-word REDC32 used by 059D."""

from __future__ import annotations

import json
from pathlib import Path


Q = 3457
QINV = 12929
R = 1 << 16
ACC_BOUND = 36844554
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/signed_redc32_range.json"


def signed16(value: int) -> int:
    value &= 0xffff
    return value - R if value >= R // 2 else value


def redc(value: int) -> int:
    m = signed16(value * QINV)
    numerator = value - m * Q
    assert numerator % R == 0
    return numerator // R


def first_at_or_above(residue: int, lower: int) -> int:
    return lower + ((residue - lower) % R)


def main() -> None:
    minimum = None
    maximum = None
    witnesses = {}
    checked_residues = 0
    for residue in range(R):
        low = first_at_or_above(residue, -ACC_BOUND)
        if low > ACC_BOUND:
            continue
        high = low + ((ACC_BOUND - low) // R) * R
        for label, value in (("minimum", low), ("maximum", high)):
            output = redc(value)
            if minimum is None or output < minimum:
                minimum = output
                witnesses["minimum"] = {"input": value, "output": output,
                                         "endpoint": label}
            if maximum is None or output > maximum:
                maximum = output
                witnesses["maximum"] = {"input": value, "output": output,
                                         "endpoint": label}
        checked_residues += 1
    assert checked_residues == R
    assert minimum is not None and maximum is not None
    assert minimum > -Q and maximum < Q
    report = {
        "schema": "ntruplus768-gt32-059d-signed-redc32-range-v1",
        "q": Q,
        "qinv_mod_2_16": QINV,
        "input_interval": [-ACC_BOUND, ACC_BOUND],
        "signed_m_interval": [-32768, 32767],
        "checked_low_word_residues": checked_residues,
        "exact_output_interval": [minimum, maximum],
        "within_one_q": True,
        "one_sign_correction_is_sufficient": True,
        "witnesses": witnesses,
        "identity": "t=(a-signed16(a*qinv)*q)/2^16 and t=a*2^-16 mod q",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
