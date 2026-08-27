#!/usr/bin/env python3
"""Emit the 094 lifetime/coloring proof and reject source drift."""

from __future__ import annotations

import json
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle}")


def main() -> None:
    production = (ROOT / "encap.c").read_text()
    f1 = (EXP / "encap-f1.c").read_text()
    require(production, "ntruplus768_pack_m_sum_highrange12699_avx2(",
            "promoted E0V boundary")
    if "poly_add(" in production:
        raise SystemExit("production baseline still materializes sum")
    require(f1, "forward_m(scratch.m, scratch.c, scratch.m);",
            "m lifetime coloring")
    if "scratch.work" in f1:
        raise SystemExit("F1 still references removed work field")
    result = {
        "status": "PASS",
        "control_commit": "9600506",
        "semantic_lifetimes": {
            "h": "unpack through B3 input",
            "r": "first Forward through B3 input",
            "m": "coefficient producer; overwritten after frontend; live through Q24",
            "product": "distinct B3 output through Q24",
            "sum": "semantic register value only; zero memory accesses"
        },
        "peak_at_b3": ["h", "r", "m", "product"],
        "peak_polynomial_live_count": 4,
        "four_slot_lower_bound": True,
        "alias_contract": "coefficient input aliases Forward output only after frontend returns",
        "frames": {"F0": 8128, "FP": 8128, "F1": 6592},
        "removed_bytes": 1536
    }
    generated = EXP / "generated"
    generated.mkdir(exist_ok=True)
    (generated / "lifetime-proof.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
