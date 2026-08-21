#!/usr/bin/env python3
"""Audit where diag(1,s,s^2,s^3) can reuse an existing operation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = ROOT / "generated/d4_fixed_modulus_norm.json"
FORWARD = REPO / "experiments/avx2_gt32_tile4_official_001/src/tile4_asm.S"
Q24 = REPO / "experiments/avx2_gt32_tile4_official_001/src/tile4_q24_codec_asm.S"
OUT = ROOT / "generated/d4_norm_absorption_matrix.json"


def row(boundary: str, degree: int, standalone: int, existing: str,
        direct: str, mechanism: str, verdict: str) -> dict:
    return {
        "boundary": boundary,
        "degree": degree,
        "factor": f"s^{degree}" if boundary == "Forward" else f"s^-{degree}",
        "standalone_full_width_chains": standalone,
        "existing_operation": existing,
        "can_fuse_into_existing_operation": direct,
        "required_mechanism": mechanism,
        "current_verdict": verdict,
    }


def main() -> None:
    base = json.loads(BASE.read_text())
    forward_text = FORWARD.read_text()
    q24_text = Q24.read_text()
    assert "MONT_CROSS4" in forward_text
    assert "vpmulhrsw" in q24_text and "vpmaddwd" in q24_text

    rows = []
    for degree in (1, 2, 3):
        rows.append(row(
            "Forward", degree, 12,
            "frontend twist and NTT32 high-arm Montgomery chains",
            "not in the current schedule",
            "conjugate the full transform constants/physical trajectory so every low and high output receives the degree diagonal",
            "open topology gate; changing only terminal constants is insufficient because low arms bypass the multiply",
        ))
    for degree in (1, 2, 3):
        rows.append(row(
            "Q24 inverse", degree, 12,
            "v=9 quotient estimate, multiply-by-q correction, sign fix, pair pack",
            "no direct constant-table fusion",
            "joint wide constant multiply + modular reduction + packet formation, or consume already-normalized late K output",
            "open wide-exit gate; Q24 has reduction multiplies but no existing arbitrary-constant Montgomery chain",
        ))

    matrix = {
        "Forward": {str(d): rows[d - 1] for d in (1, 2, 3)},
        "Q24_inverse": {str(d): rows[d + 2] for d in (1, 2, 3)},
    }
    standalone_forward = sum(matrix["Forward"][str(d)]["standalone_full_width_chains"]
                             for d in (1, 2, 3))
    standalone_q24 = sum(matrix["Q24_inverse"][str(d)]["standalone_full_width_chains"]
                         for d in (1, 2, 3))
    report = {
        "schema": "ntruplus768-gt32-d4-norm-absorption-matrix-v1",
        "experiment": "GT32-D4-NORM-ABSORPTION-MATRIX-C",
        "status": "research-open-no-free-absorption-proved",
        "production_modified": False,
        "source_hashes": {
            BASE.name: hashlib.sha256(BASE.read_bytes()).hexdigest(),
            FORWARD.name: hashlib.sha256(FORWARD.read_bytes()).hexdigest(),
            Q24.name: hashlib.sha256(Q24.read_bytes()).hexdigest(),
        },
        "matrix": matrix,
        "standalone_accounting": {
            "Forward_per_polynomial": standalone_forward,
            "two_Forward": 2 * standalone_forward,
            "Q24_per_polynomial": standalone_q24,
            "two_Q24": 2 * standalone_q24,
            "B3_credit": -36,
            "net_if_nothing_absorbs": 2 * standalone_forward + 2 * standalone_q24 - 36,
        },
        "direct_answers": {
            "Forward_degree1": "not free in current schedule",
            "Forward_degree2": "not free in current schedule",
            "Forward_degree3": "not free in current schedule",
            "Q24_inverse_degree1": "not a direct reuse of v=9/q operations",
            "Q24_inverse_degree2": "not a direct reuse of v=9/q operations",
            "Q24_inverse_degree3": "not a direct reuse of v=9/q operations",
        },
        "important_distinction": {
            "closed": "simple constant relabeling of the current terminal or Q24 reducer does not absorb the diagonal",
            "open": [
                "full Forward conjugation with a new physical trajectory",
                "wide inverse-diagonal plus Q24 REDC/pack exit",
                "asymmetric raw-h times normalized-r tensor",
                "059C late K exit where normalization is folded into the interpolation constants",
            ],
        },
        "decision": {
            "production": False,
            "continue": True,
            "priority": [
                "benchmark pooled ninth-product first",
                "lower Q24 inverse diagonal as one wide exit",
                "only then attempt full Forward conjugation",
            ],
            "reason": "the matrix finds no free current-operation absorption, but two joint-operation mechanisms remain algebraically distinct and untested",
        },
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "standalone_two_forward": 2 * standalone_forward,
        "standalone_two_q24": 2 * standalone_q24,
        "B3_credit": -36,
        "free_absorptions_proved": 0,
        "decision": report["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
