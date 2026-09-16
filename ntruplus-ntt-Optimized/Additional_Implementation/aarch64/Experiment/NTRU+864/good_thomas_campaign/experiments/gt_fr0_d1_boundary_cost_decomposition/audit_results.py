#!/usr/bin/env python3
"""Audit D1-P2 correctness and KEM-ledger reconciliation."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    summary = json.loads((HERE / "build/pi5/summary.json").read_text())
    log = (HERE / "build/pi5/raw/build-and-correctness.log").read_text()
    assert "d1_p2_components=pass mismatches=0 baseinv_rc=0" in log
    assert summary["throttled"] == "0x0"
    for kem, row in summary["ledger"]["kem"].items():
        measured = abs(row["measured"]["cycles"])
        assert abs(row["residual"]["cycles"]) <= max(750.0, measured * 0.12), kem
        assert abs(row["residual"]["instructions"]) <= 64.0, kem
    print(json.dumps({
        "gate": "D1-P2", "status": "pass",
        "component_deltas": summary["ledger"]["component_deltas"],
        "kem_reconciliation": summary["ledger"]["kem"],
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
