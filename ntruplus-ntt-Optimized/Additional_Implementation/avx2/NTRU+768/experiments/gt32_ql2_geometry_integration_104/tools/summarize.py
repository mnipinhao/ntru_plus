#!/usr/bin/env python3
"""Preserve the three 104 formal summaries and the predeclared decision."""

from __future__ import annotations

import json
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
campaigns = {
    "initial": EXP / "results/formal/manifest.json",
    "confirmation_1": EXP / "results/formal-confirmation/manifest.json",
    "confirmation_2": EXP / "results/formal-confirmation-2/manifest.json",
}
result = {
    "schema": "gt32-ql2-geometry-integration-104-v1",
    "baseline": "b2a4bea",
    "campaigns": {name: json.loads(path.read_text())["summary"]
                  for name, path in campaigns.items()},
    "decision": {
        "ql2_architecture": "PASS",
        "production_encap": "PASS",
        "keypair_collateral": "NEUTRAL",
        "decap_collateral": "ASLR_OFF_REGRESSION_REPRODUCED",
        "promotion": "DEFERRED",
        "official_comparison": "NOT_RUN_UNQUALIFIED_CANDIDATE",
    },
}
(EXP / "generated/qualification-summary.json").write_text(
    json.dumps(result, indent=2) + "\n")
