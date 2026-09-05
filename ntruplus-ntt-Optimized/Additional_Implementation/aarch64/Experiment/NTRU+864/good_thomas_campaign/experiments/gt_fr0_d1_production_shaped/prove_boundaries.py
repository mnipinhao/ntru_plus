#!/usr/bin/env python3
"""Exhaustively prove the D1-P1 signed-halfword normalization boundary."""

from __future__ import annotations

import json

Q = 3457
RECIPROCAL = 9


def main() -> None:
    residuals: list[int] = []
    nonnegative: list[int] = []
    centered: list[int] = []
    for value in range(-32768, 32768):
        quotient = (value * RECIPROCAL + (1 << 14)) // (1 << 15)
        residual = value - quotient * Q
        canonical = residual + Q if residual < 0 else residual
        centered_value = canonical - Q if canonical > Q // 2 else canonical
        assert -32768 <= quotient * Q <= 32767
        assert -32768 <= residual <= 32767
        assert 0 <= canonical < Q
        assert -(Q // 2) <= centered_value <= Q // 2
        assert (residual - value) % Q == 0
        assert (canonical - value) % Q == 0
        assert (centered_value - value) % Q == 0
        residuals.append(residual)
        nonnegative.append(canonical)
        centered.append(centered_value)
    print(json.dumps({
        "gate": "D1-P1_boundary_normalization",
        "status": "pass",
        "domain": [-32768, 32767],
        "sqrdmulh_reciprocal": RECIPROCAL,
        "residual": [min(residuals), max(residuals)],
        "nonnegative": [min(nonnegative), max(nonnegative)],
        "centered": [min(centered), max(centered)],
        "congruence": True,
        "signed_halfword_safe": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
