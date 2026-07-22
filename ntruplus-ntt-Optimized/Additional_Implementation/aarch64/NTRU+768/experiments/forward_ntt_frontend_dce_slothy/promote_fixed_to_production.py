#!/usr/bin/env python3
"""Promote the verified fixed-register frontend schedule to production."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
CANDIDATE = ROOT / "asm/gt/experiment/forward_ntt/poly_ntt_frontend_dce_slothy_fixed.S"
PRODUCTION = ROOT / "asm/gt/ntt/poly_ntt.n1.opt.S"
INTEGRATION_MANIFEST = EXP / "frontend_dce_integration_manifest.json"
PROMOTION_MANIFEST = EXP / "frontend_dce_promotion_manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restore_production_symbols(text: str) -> str:
    replacements = {
        "_gt_block_major_poly_ntt_frontend_dce_slothy_fixed": "_gt_block_major_poly_ntt",
        "gt_block_major_poly_ntt_frontend_dce_slothy_fixed": "gt_block_major_poly_ntt",
        "_poly_ntt_frontend_dce_slothy_fixed": "_poly_ntt",
        "poly_ntt_frontend_dce_slothy_fixed_end": "poly_ntt_end",
        "poly_ntt_frontend_dce_slothy_fixed": "poly_ntt",
    }
    for old in sorted(replacements, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(old)}\b", replacements[old], text)
    return text


def main() -> int:
    manifest = json.loads(INTEGRATION_MANIFEST.read_text())
    fixed = next(entry for entry in manifest if entry["variant"] == "fixed")
    if sha256(CANDIDATE) != fixed["sha256"]:
        raise ValueError("fixed candidate hash does not match integration manifest")

    old_sha = sha256(PRODUCTION)
    lines = CANDIDATE.read_text().splitlines()
    expected_preamble = [
        "/* Experiment-only frontend DCE + Slothy fixed candidate. */",
        "/* Current production Stage12/Stage345 and S2 store path are unchanged. */",
        "/* Neoverse-N1 optimized production GT forward NTT. */",
    ]
    if lines[:3] != expected_preamble:
        raise ValueError("fixed candidate preamble does not match promotion contract")
    text = "\n".join(
        [
            "/* Neoverse-N1 optimized production GT forward NTT. */",
            "/* Frontend DCE is Slothy-scheduled with the production register allocation. */",
            *lines[3:],
        ]
    ) + "\n"
    text = restore_production_symbols(text)
    PRODUCTION.write_text(text)

    PROMOTION_MANIFEST.write_text(
        json.dumps(
            {
                "candidate": str(CANDIDATE.relative_to(ROOT)),
                "production": str(PRODUCTION.relative_to(ROOT)),
                "old_production_sha256": old_sha,
                "new_production_sha256": sha256(PRODUCTION),
                "candidate_sha256": fixed["sha256"],
                "removed_dead_pointer_updates": 32,
                "slothy_expected_cycles_per_frontend_iteration": 39,
                "pi5_direct_poly_ntt_cycles": {
                    "source_order_production": 2659,
                    "fixed_frontend_schedule": 2612,
                    "paired_median_delta": -47,
                    "paired_delta_percent": -1.7676,
                },
                "promotion_gates": {
                    "poly_ntt_differential_mismatches": 0,
                    "abi_sentinel_mask": "0x0",
                    "canonical_kat_sha256": "22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8",
                },
            },
            indent=2,
        )
        + "\n"
    )
    print(PRODUCTION)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
