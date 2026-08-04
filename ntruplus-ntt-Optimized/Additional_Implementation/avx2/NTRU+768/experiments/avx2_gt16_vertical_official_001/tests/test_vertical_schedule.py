#!/usr/bin/env python3
"""Executable invariants for the Round 4B vertical GT16 architecture gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))
import generate_vertical_schedule as gen  # noqa: E402


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def main() -> int:
    sched = load("generated/vertical-forward-schedule.json")
    bridge = load("generated/consumer-bridge.json")
    costs = load("results/round4b-static-cost.json")
    decision = load("results/round4b-decision.json")

    # 48 transforms are exactly three fixed-k3 batches of sixteen lanes.
    assert sched["abi"]["batch"] == "k3 (three batches)"
    assert len({4 * branch + degree for branch in range(4) for degree in range(4)}) == 16

    stages = sched["ntt16_stages"]
    assert sum(x["light"] + x["nontrivial"] for x in stages) == 32
    assert sum(x["nontrivial"] for x in stages) == 17
    assert sum(x["light"] for x in stages) == 15
    assert sum(x["instructions_per_batch"] for x in stages) == 132

    icost = sched["instruction_cost"]
    assert icost == {
        "r2_pack_and_explicit_preweight": 1104,
        "sixteen_dft3_groups": 176,
        "three_vertical_ntt16_batches": 396,
        "tile_materialization": 208,
        "producer_total": 1884,
    }
    regs = sched["register_allocation"]
    assert regs["peak_live"] == 9
    assert regs["peak_live"] <= 15
    assert regs["emergency_reserved"] == "ymm15"
    assert not regs["spill_required"]

    # The transpose topology is independent of B1/B2 lane naming.
    assert bridge["b1_per_k3"] == bridge["b2_per_k3"]
    assert bridge["one_way_instructions"] == 288
    assert bridge["two_forward_inputs_plus_inverse_output_instructions"] == 864
    assert bridge["direct_lane_internal_bm"]["arithmetic_replication_factor"] == 4

    gates = costs["gates"]
    assert gates["producer_forward_result"] == "pass"
    assert gates["consumer_compatible_forward"] == 2172
    assert gates["consumer_compatible_result"] == "fail"
    assert decision["status"] == "stop-vertical-gt16-before-avx2"
    assert not decision["asm_authorized"]
    assert abs(gates["producer_forward_threshold"] - 1924.947) < 1e-9
    print("vertical GT16 schedule/register/consumer gates: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
