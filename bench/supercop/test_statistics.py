#!/usr/bin/env python3
"""Small exact tests for the pinned SUPERCOP output parser and StQ estimator."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_supercop_benchmark import decode_observations, stabilized_quartiles
from supercop_promotion_report import stq2


sample = """\
keypair_cycles - 10 +0+2-2+4
keypair_cycles - 20 -1+1+3-3
"""
assert decode_observations(sample, "keypair_cycles") == [10, 12, 8, 14, 19, 21, 23, 17]
assert decode_observations(sample, "enc_cycles") == []
assert stabilized_quartiles([0, 1, 2, 3]) == [0.5, 1.5, 2.5]
assert stq2([0, 1, 2, 3]) == 1.5
print("SUPERCOP measure parser and stabilized quartiles passed")
