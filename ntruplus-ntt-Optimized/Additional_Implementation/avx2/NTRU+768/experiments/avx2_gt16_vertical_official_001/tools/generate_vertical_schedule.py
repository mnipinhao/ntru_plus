#!/usr/bin/env python3
"""Generate the Round 4B vertical/batched GT16 static architecture gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent.parent
REPO = next(p for p in HERE.parents if (p / ".git").exists())
HORIZONTAL = HERE.parent / "avx2_gt16_native_official_001"
CHAMPION_RESULTS = HERE.parent / "gt_ntt" / "BENCHMARK_RESULTS.md"

CHAMPION_FORWARD_INSTRUCTIONS = 2026.260
CHAMPION_CHAIN_INSTRUCTIONS = 17784.325
CHAMPION_CHAIN_CYCLES = 3179.5
FORWARD_GATE = 0.95 * CHAMPION_FORWARD_INSTRUCTIONS
CHAIN_INSTRUCTION_GATE = 0.95 * CHAMPION_CHAIN_INSTRUCTIONS
CHAIN_CYCLE_GATE = 0.95 * CHAMPION_CHAIN_CYCLES


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def mont_ops(label: str) -> list[str]:
    return [f"vpmullw:{label}", f"vpmulhw:{label}",
            f"vpmulhw-q:{label}", f"vpsubw:{label}"]


class Trace:
    """Small deterministic physical-register allocator for the static trace."""

    def __init__(self) -> None:
        self.mapping: dict[str, int] = {}
        self.records: list[dict[str, Any]] = []
        self.peak = 0

    def alloc(self, name: str) -> str:
        assert name not in self.mapping
        used = set(self.mapping.values())
        reg = next(reg for reg in range(15) if reg not in used)
        self.mapping[name] = reg
        self.peak = max(self.peak, len(self.mapping))
        return f"ymm{reg}"

    def free(self, name: str) -> None:
        del self.mapping[name]

    def reg(self, name: str) -> str:
        return f"ymm{self.mapping[name]}"

    def emit(self, phase: str, op: str, *names: str) -> None:
        self.records.append({
            "seq": len(self.records),
            "phase": phase,
            "op": op,
            "regs": [self.reg(name) for name in names],
            "live": len(self.mapping),
        })


def expanded_trace() -> tuple[list[dict[str, Any]], int]:
    trace = Trace()
    for group in range(4):
        retained: list[str] = []
        for position in range(4):
            xs = []
            for i3 in range(3):
                prefix = f"g{group}p{position}i{i3}"
                x = f"{prefix}.x"
                term = f"{prefix}.term"
                low = f"{prefix}.low"
                trace.alloc(x)
                trace.emit("r2-pack", "vpbroadcastq:A", x)
                trace.alloc(term)
                trace.alloc(low)
                for name in ("B", "C", "D"):
                    trace.emit("r2-pack", f"vpbroadcastq:{name}", term)
                    for op in mont_ops(f"lane-{name}"):
                        trace.emit("r2-pack", op, term, low)
                    trace.emit("r2-pack", f"vpaddw:{name}", x, term)
                for op in mont_ops("preweight"):
                    trace.emit("preweight", op, x, low)
                trace.free(low)
                trace.free(term)
                xs.append(x)

            temps = [f"g{group}p{position}.dft{n}" for n in range(3)]
            for temp in temps:
                trace.alloc(temp)
            for index, op in enumerate((
                "vpaddw:s", "vpsubw:d", "vpaddw:y0",
                "vpmullw:t", "vpmulhw:t", "vpmulhw-q:t", "vpsubw:t",
                "vpaddw:y1", "vpsubw:y2", "vpaddw:checkpoint1",
                "vpsubw:checkpoint2",
            )):
                trace.emit("dft3", op, xs[index % 3], temps[index % 3])
            for temp in reversed(temps):
                trace.free(temp)

            # Keep k3=0 for the four-position tile and materialize k3=1,2.
            for x in xs[1:]:
                trace.emit("stage12-materialize", "vmovdqa:store-nonretained", x)
                trace.free(x)
            retained.append(xs[0])

        # Four butterflies (two light, one light, one nontrivial) = 12 ops.
        for index in range(12):
            trace.emit("vertical-ntt16-stage12", f"tile-op:{index}",
                       retained[index % 4])
        for x in retained:
            trace.emit("stage12-materialize", "vmovdqa:store-retained", x)
            trace.free(x)

        for k3 in (1, 2):
            tile = [f"g{group}.k{k3}.v{n}" for n in range(4)]
            for x in tile:
                trace.alloc(x)
                trace.emit("stage12-materialize", "vmovdqa:reload-nonretained", x)
            for index in range(12):
                trace.emit("vertical-ntt16-stage12", f"tile-op:{index}",
                           tile[index % 4])
            for x in tile:
                trace.emit("stage12-materialize", "vmovdqa:store-stage12", x)
                trace.free(x)

    # Stages 3+4 use four-vector tiles.  Their 84 arithmetic ops per batch are
    # split evenly over four tiles; this is an execution-order trace, not an
    # assertion that twiddle classes are identical across tiles.
    for k3 in range(3):
        for tile_index in range(4):
            tile = [f"k{k3}.t{tile_index}.v{n}" for n in range(4)]
            for x in tile:
                trace.alloc(x)
                trace.emit("stage34-materialize", "vmovdqa:load-stage12", x)
            low = f"k{k3}.t{tile_index}.mont-low"
            trace.alloc(low)
            for index in range(21):
                trace.emit("vertical-ntt16-stage34", f"tile-op:{index}",
                           tile[index % 4], low)
            trace.free(low)
            for x in tile:
                trace.emit("native-store", "vmovdqa:store-vertical", x)
                trace.free(x)
    assert not trace.mapping
    assert len(trace.records) == 1884
    return trace.records, trace.peak


def schedule() -> dict[str, Any]:
    # One packed vector is one natural (i3,i16) point.  Its lanes are
    # lane=4*branch+degree.  A is the initial broadcast; B/C/D are three
    # lane-weighted contributions.  The final multiply is the explicit
    # canonical-s=1 preweight.
    pack_trace = ["vpbroadcastq:A"]
    for name in ("B", "C", "D"):
        pack_trace.append(f"vpbroadcastq:{name}")
        pack_trace.extend(mont_ops(f"lane-{name}"))
        pack_trace.append(f"vpaddw:{name}")
    pack_trace.extend(mont_ops("preweight"))
    assert len(pack_trace) == 23

    # The 11-op DFT3 is inherited as an optimistic floor from Round 4.  It is
    # deliberately not lowered here: this gate asks whether vertical GT16 is
    # viable even under that favorable assumption.
    dft3_trace = [
        "vpaddw:s", "vpsubw:d", "vpaddw:y0",
        "vpmullw:t", "vpmulhw:t", "vpmulhw-q:t", "vpsubw:t",
        "vpaddw:y1", "vpsubw:y2", "vpaddw:checkpoint1",
        "vpsubw:checkpoint2",
    ]
    assert len(dft3_trace) == 11

    stages = [
        {"stage": 1, "distance": 8, "light": 8, "nontrivial": 0},
        {"stage": 2, "distance": 4, "light": 4, "nontrivial": 4},
        {"stage": 3, "distance": 2, "light": 2, "nontrivial": 6},
        {"stage": 4, "distance": 1, "light": 1, "nontrivial": 7},
    ]
    for stage in stages:
        stage["instructions_per_batch"] = (
            2 * stage["light"] + 6 * stage["nontrivial"]
        )
    ntt_per_batch = sum(s["instructions_per_batch"] for s in stages)
    assert ntt_per_batch == 132

    materialization = {
        "four_position_groups": 4,
        "per_group": {
            "store_two_nonretained_k3_outputs": 8,
            "reload_two_nonretained_k3_tiles": 8,
            "store_three_stage12_tiles": 12,
            "total": 28,
        },
        "stage12_total": 112,
        "stage34_load_store": 96,
        "total": 208,
    }

    full_trace, allocated_peak = expanded_trace()
    peak_scenarios = [
        {
            "name": "pack-and-dft3-with-three-retained-positions",
            "live": ["retained0", "retained1", "retained2", "x0", "x1",
                     "x2", "term", "mont-low", "dft-temp"],
            "count": 9,
        },
        {
            "name": "four-position-ntt-tile",
            "live": ["v0", "v1", "v2", "v3", "mont-low"],
            "count": 5,
        },
    ]
    peak = max(x["count"] for x in peak_scenarios)
    assert allocated_peak == peak

    costs = {
        "r2_pack_and_explicit_preweight": 48 * len(pack_trace),
        "sixteen_dft3_groups": 16 * len(dft3_trace),
        "three_vertical_ntt16_batches": 3 * ntt_per_batch,
        "tile_materialization": materialization["total"],
    }
    costs["producer_total"] = sum(costs.values())
    assert costs["producer_total"] == 1884

    return {
        "abi": {
            "batch": "k3 (three batches)",
            "vector": "k16 position j (sixteen vectors per batch)",
            "lane": "4*branch + degree",
            "lane_layouts_compared": {
                "B1": "branch-major, degree-minor",
                "B2": "degree-major, branch-minor",
            },
        },
        "pack_trace_per_i3_i16": pack_trace,
        "dft3_optimistic_trace_per_i16": dft3_trace,
        "ntt16_stages": stages,
        "four_vector_tile": materialization,
        "expanded_instruction_trace": full_trace,
        "register_allocation": {
            "physical_pool": [f"ymm{i}" for i in range(15)],
            "emergency_reserved": "ymm15",
            "peak_live": peak,
            "spill_required": False,
            "scenarios": peak_scenarios,
            "constants": "aligned memory operands; no runtime exponent indexing",
        },
        "instruction_cost": costs,
    }


def consumer_bridge() -> dict[str, Any]:
    per_k3 = {
        "unpack_words": 16,
        "unpack_dwords": 16,
        "unpack_qwords": 16,
        "cross_128_permute": 16,
        "loads": 16,
        "stores": 16,
        "total": 96,
    }
    one_way = 3 * per_k3["total"]
    assert one_way == 288
    return {
        "source_axes": "vectors=k16, lanes=branch*4+degree",
        "native_bm_axes": "vectors=(branch,k3,degree), lanes=k16",
        "reason": "k16 is a vector index for vertical NTT16 but a SIMD lane for the frozen quartic BM",
        "b1_per_k3": per_k3,
        "b2_per_k3": dict(per_k3),
        "one_way_instructions": one_way,
        "two_forward_inputs_plus_inverse_output_instructions": 3 * one_way,
        "direct_lane_internal_bm": {
            "vector_quartics": 4,
            "frozen_soa_vector_quartics": 16,
            "arithmetic_replication_factor": 4,
            "decision": "reject-before-kernel",
        },
        "lower_bound_note": "B1/B2 change lane order, not the conflicting k16 vector/lane axis; both require the same 16x16 topology",
    }


def results(sched: dict[str, Any], bridge: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    producer = sched["instruction_cost"]["producer_total"]
    compatible = producer + bridge["one_way_instructions"]
    static = {
        "frozen_champion": {
            "forward_dynamic_instructions": CHAMPION_FORWARD_INSTRUCTIONS,
            "complete_chain_dynamic_instructions": CHAMPION_CHAIN_INSTRUCTIONS,
            "complete_chain_cycles": CHAMPION_CHAIN_CYCLES,
            "source": "tracked experiments/gt_ntt/BENCHMARK_RESULTS.md",
        },
        "gates": {
            "producer_forward_threshold": FORWARD_GATE,
            "producer_forward": producer,
            "producer_forward_result": "pass" if producer < FORWARD_GATE else "fail",
            "consumer_compatible_forward": compatible,
            "consumer_compatible_result": "pass" if compatible < FORWARD_GATE else "fail",
            "chain_instruction_threshold": CHAIN_INSTRUCTION_GATE,
            "chain_cycle_threshold": CHAIN_CYCLE_GATE,
        },
        "deltas": {
            "producer_vs_champion_instructions": producer - CHAMPION_FORWARD_INSTRUCTIONS,
            "producer_improvement_percent": 100 * (CHAMPION_FORWARD_INSTRUCTIONS - producer) / CHAMPION_FORWARD_INSTRUCTIONS,
            "compatible_vs_champion_instructions": compatible - CHAMPION_FORWARD_INSTRUCTIONS,
            "compatible_improvement_percent": 100 * (CHAMPION_FORWARD_INSTRUCTIONS - compatible) / CHAMPION_FORWARD_INSTRUCTIONS,
            "producer_headroom_to_gate": FORWARD_GATE - producer,
        },
        "not_claimed": [
            "instruction counts are not cycle predictions",
            "the optimistic 11-op DFT3 is inherited rather than demonstrated by assembly",
            "no inverse speedup is credited without a consumer-compatible inverse schedule",
        ],
    }
    decision = {
        "status": "stop-vertical-gt16-before-avx2",
        "producer_only_gate": "pass",
        "consumer_complete_gate": "fail",
        "reason": (
            "The 1884-instruction producer floor passes narrowly, but the mandatory "
            "vertical-to-quartic-BM axis transpose raises a usable forward to 2172 "
            "instructions, already above the 1924.947 gate before address/control, "
            "range checkpoints, or a paired inverse are charged."
        ),
        "asm_authorized": False,
        "production_changed": False,
        "reopen_condition": (
            "Demonstrate a final-stage/consumer co-schedule whose complete output bridge "
            "cost is below 40.947 instructions, or a native vertical quartic BM whose "
            "complete F+B+I static floor beats 95% of the frozen chain."
        ),
    }
    return static, decision


def artifacts() -> dict[Path, Any]:
    sched = schedule()
    bridge = consumer_bridge()
    static, decision = results(sched, bridge)
    manifest = {
        "round": "4B",
        "parent_horizontal_head": "c62ec1a",
        "sources": {
            str((HORIZONTAL / "generated/manifest.json").relative_to(REPO)): sha256(HORIZONTAL / "generated/manifest.json"),
            str((HORIZONTAL / "generated/gt16-factorization.json").relative_to(REPO)): sha256(HORIZONTAL / "generated/gt16-factorization.json"),
            str(CHAMPION_RESULTS.relative_to(REPO)): sha256(CHAMPION_RESULTS),
        },
        "production_files_modified": [],
    }
    return {
        HERE / "generated/vertical-forward-schedule.json": sched,
        HERE / "generated/consumer-bridge.json": bridge,
        HERE / "generated/source-manifest.json": manifest,
        HERE / "results/round4b-static-cost.json": static,
        HERE / "results/round4b-decision.json": decision,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    values = artifacts()
    if args.check:
        for path, value in values.items():
            expected = json.dumps(value, indent=2, sort_keys=True) + "\n"
            assert path.exists(), f"missing generated artifact: {path}"
            assert path.read_text() == expected, f"stale generated artifact: {path}"
        print("vertical GT16 generated artifacts are current")
        return 0
    for path, value in values.items():
        write_json(path, value)
    print(f"wrote {len(values)} Round 4B artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
