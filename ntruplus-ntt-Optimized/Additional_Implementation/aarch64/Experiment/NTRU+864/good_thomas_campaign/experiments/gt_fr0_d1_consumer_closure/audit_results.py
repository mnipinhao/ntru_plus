#!/usr/bin/env python3
"""Audit D1-C1/C2 correctness and full-chain penetration."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMMARY = HERE / "build/pi5/summary.json"
LOG = HERE / "build/pi5/raw/build-and-correctness.log"


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    log = LOG.read_text(encoding="utf-8")
    assert "d1_c1_polymul=pass cases=34 coefficient_mismatches=0 alias=0 sentinel=0" in log
    assert "d1_c2_serializer=pass cases=34 byte_mismatches=0" in log
    assert "d1_c2b_real_encap=pass cases=24 byte_mismatches=0" in log
    assert summary["correctness"] == {
        "D1-C1": "pass", "D1-C2a": "pass", "D1-C2b": "pass"
    }
    assert summary["throttled"] == "0x0"
    deltas = [row["d1_minus_old"] for row in summary["repetitions"]]
    assert all(row["cycles"] < -450 for row in deltas)
    assert all(row["instructions"] == -755 for row in deltas)
    assert all(row["branches"] == 0 for row in deltas)
    overall = summary["overall"]
    print(json.dumps({
        "gate": "D1-C1_and_C2_consumer_closure",
        "status": "C1_pass_C2_pass",
        "D1-C1": {
            "cases": 34,
            "coefficient_mismatches": 0,
            "alias_mismatches": 0,
            "sentinel_mismatches": 0,
            "old_cycles_p50": overall["old_chain"]["cycles"]["p50"],
            "d1_cycles_p50": overall["d1_chain"]["cycles"]["p50"],
            "delta_cycles": overall["d1_minus_old"]["cycles"],
            "delta_instructions": overall["d1_minus_old"]["instructions"],
            "penetration_category": "excellent_over_450_cycles",
        },
        "D1-C2a": {
            "actual_serializer": "stock_NTRU+864_poly_tobytes",
            "cases": 34,
            "byte_mismatches": 0,
            "coverage": ["boundary", "random_full", "encap_shaped"],
        },
        "D1-C2b": {
            "actual_path": "stock_NTRU+864_Encapsulation_derivation_and_poly_tobytes",
            "keypairs": 3,
            "deterministic_coins_per_keypair": 8,
            "cases": 24,
            "byte_mismatches": 0,
            "coordinate_bridge": "generated_exact_official_to_FR0_permutation",
        },
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
