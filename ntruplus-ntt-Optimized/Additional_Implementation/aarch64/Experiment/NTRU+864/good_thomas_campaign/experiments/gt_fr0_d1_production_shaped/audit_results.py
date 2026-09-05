#!/usr/bin/env python3
"""Audit D1-P1 correctness, static instruction penetration and PMU result."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    summary = json.loads((HERE / "build/pi5/summary.json").read_text())
    boundary = json.loads((HERE / "build/boundary-proof.json").read_text())
    log = (HERE / "build/pi5/raw/build-and-correctness.log").read_text()
    assert "d1_p1_kem=pass cases=8 mismatches=0" in log
    assert summary["throttled"] == "0x0"
    assert boundary["status"] == "pass"
    assert boundary["nonnegative"] == [0, 3456]
    assert boundary["centered"] == [-1728, 1728]
    expected_instructions = {
        "basemul": -755.0, "basemuladd": -760.0,
        "keypair": -1510.0, "encaps": -760.0, "decaps": -1510.0,
    }
    for operation, expected in expected_instructions.items():
        overall = summary["overall"][operation]["d1_minus_gt_old"]
        assert overall["cycles"] < 0
        assert overall["instructions"] == expected
        assert all(rep[operation]["d1_minus_gt_old"]["cycles"] < 0
                   for rep in summary["repetitions"])
    output = {
        "gate": "D1-P1", "status": "pass",
        "correctness": summary["correctness"],
        "boundary_normalization": boundary,
        "d1_minus_gt_old": {
            op: summary["overall"][op]["d1_minus_gt_old"]
            for op in expected_instructions
        },
        "gt_d1_minus_official": {
            op: summary["overall"][op]["gt_d1_minus_official"]
            for op in expected_instructions
        },
        "production_linked": False,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
