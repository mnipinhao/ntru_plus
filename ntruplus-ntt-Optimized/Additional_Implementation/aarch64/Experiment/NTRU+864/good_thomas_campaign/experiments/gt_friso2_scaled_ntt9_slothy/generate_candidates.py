#!/usr/bin/env python3
"""Materialize four Slothy-sized CF1 NTT9 block regions."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF1 = ROOT.parent / "gt_friso2_scaled_ntt9_search"
sys.path.insert(0, str(CF1))
from search_scaled_dag import (GENERATOR, GROUP_ORDER, LOG_THETA, Q,  # noqa: E402
                               build_dag)

BASELINE = ROOT / "baseline-region.S"
OUTPUT = ROOT / "gt864_friso2_scaled_ntt9_variants.sym.S"
LEDGER = ROOT / "constant-ledger.json"


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def pair_from_exponent(exponent: int) -> tuple[int, int]:
    value = centered(pow(GENERATOR, exponent % GROUP_ORDER, Q))
    reciprocal = (abs(value) * (1 << 15) + Q // 2) // Q
    return value, -reciprocal if value < 0 else reciprocal


def instruction_count(text: str) -> int:
    return sum(bool(re.match(r"^\s{4}[a-z][a-z0-9]*\s", line))
               for line in text.splitlines())


class BlockEmitter:
    def __init__(self, top: int, component: int, block: int,
                 labels: dict[str, tuple[int, int]], common: dict[int, tuple[int, int]],
                 raw_inputs: list[str], output_base: int) -> None:
        self.top = top
        self.component = component
        self.block = block
        self.labels = labels
        self.common = common
        self.raw_inputs = raw_inputs
        self.output_base = output_base
        self.lines: list[str] = []
        self.events: list[dict[str, object]] = []
        self.values: dict[str, str] = {}
        self.dag, self.inputs, self.outputs = build_dag()
        self.output_names = {node: f"out{output_base + row}"
                             for row, node in enumerate(self.outputs)}

    @staticmethod
    def difference(output: tuple[int, int], source: tuple[int, int],
                   extra: int = 0) -> tuple[int, int]:
        return ((output[0] - source[0]) % GROUP_ORDER,
                (output[1] + extra - source[1]) % GROUP_ORDER)

    def destination(self, node: str, suffix: str = "") -> str:
        if not suffix and node in self.output_names:
            return self.output_names[node]
        return f"b{self.block}_{node}{suffix}"

    def emit_mulmod(self, destination: str, source: str,
                    factor: tuple[int, int], reason: str) -> str:
        factor = (factor[0] % GROUP_ORDER, factor[1] % GROUP_ORDER)
        assert factor != (0, 0)
        quotient = destination + "_q"
        event: dict[str, object] = {
            "reason": reason,
            "source": source,
            "destination": destination,
            "affine_exponent": list(factor),
        }
        if factor[0] == 0:
            pack, lane = self.common[factor[1]]
            constant = f"V<common{pack}>.h[{2 * lane}]"
            reciprocal = f"V<common{pack}>.h[{2 * lane + 1}]"
            event.update({"kind": "packed_uniform", "pack": pack,
                          "pair_lanes": [2 * lane, 2 * lane + 1]})
        else:
            constant_name = destination + "_b"
            reciprocal_name = destination + "_bp"
            self.lines.append(f"    ldr Q<{constant_name}>, [x3], #16")
            self.lines.append(f"    ldr Q<{reciprocal_name}>, [x3], #16")
            constant = f"V<{constant_name}>.8h"
            reciprocal = f"V<{reciprocal_name}>.8h"
            event.update({"kind": "lane_varying_two_ldr",
                          "table_vectors": [constant_name, reciprocal_name]})
        self.lines.append(
            f"    mul V<{destination}>.8h, V<{source}>.8h, {constant}")
        self.lines.append(
            f"    sqrdmulh V<{quotient}>.8h, V<{source}>.8h, {reciprocal}")
        self.lines.append(
            f"    mls V<{destination}>.8h, V<{quotient}>.8h, v31.8h")
        columns = range(8 * self.block, 8 * self.block + 8)
        exponents = [(factor[0] * column + factor[1]) % GROUP_ORDER
                     for column in columns]
        event["lane_exponents"] = exponents
        event["lane_pairs"] = [list(pair_from_exponent(value))
                               for value in exponents]
        self.events.append(event)
        return destination

    def prepare_inputs(self) -> None:
        residue = 1 if self.top == 0 else 5
        for s, node in enumerate(self.inputs):
            label = self.labels[node]
            factor = ((label[0] + LOG_THETA * 6 * s) % GROUP_ORDER,
                      (label[1] + LOG_THETA * residue * s) % GROUP_ORDER)
            source = self.raw_inputs[s]
            if factor == (0, 0):
                self.values[node] = source
            else:
                self.values[node] = self.emit_mulmod(
                    self.destination(node), source, factor, f"input:{node}")

    def emit(self) -> tuple[str, list[dict[str, object]]]:
        self.lines.append(
            f"    // CF1 scaled NTT9: top={self.top}, component={self.component}, block={self.block}.")
        self.prepare_inputs()
        operations = {item.output: item
                      for item in (*self.dag.adds, *self.dag.muls)}
        for node in self.dag.nodes[9:]:
            operation = operations[node]
            output_label = self.labels[node]
            if hasattr(operation, "subtract"):
                left_label = self.labels[operation.left]
                right_label = self.labels[operation.right]
                opcode = "sub" if operation.subtract else "add"
                if left_label == right_label:
                    factor = self.difference(output_label, left_label)
                    target = (self.destination(node) if factor == (0, 0)
                              else self.destination(node, "_pre"))
                    self.lines.append(
                        f"    {opcode} V<{target}>.8h, V<{self.values[operation.left]}>.8h, V<{self.values[operation.right]}>.8h")
                    if factor != (0, 0):
                        target = self.emit_mulmod(self.destination(node), target,
                                                  factor, f"postadd:{node}")
                    self.values[node] = target
                else:
                    left_factor = self.difference(output_label, left_label)
                    right_factor = self.difference(output_label, right_label)
                    left = self.values[operation.left]
                    right = self.values[operation.right]
                    if left_factor != (0, 0):
                        left = self.emit_mulmod(self.destination(node, "_left"),
                                                left, left_factor, f"left:{node}")
                    if right_factor != (0, 0):
                        right = self.emit_mulmod(self.destination(node, "_right"),
                                                 right, right_factor, f"right:{node}")
                    target = self.destination(node)
                    self.lines.append(
                        f"    {opcode} V<{target}>.8h, V<{left}>.8h, V<{right}>.8h")
                    self.values[node] = target
            else:
                factor = self.difference(output_label,
                                         self.labels[operation.source],
                                         operation.exponent)
                if factor == (0, 0):
                    self.values[node] = self.values[operation.source]
                else:
                    self.values[node] = self.emit_mulmod(
                        self.destination(node), self.values[operation.source],
                        factor, f"internal:{node}")
        assert all(self.values[node] == self.output_names[node]
                   for node in self.outputs)
        assert len(self.events) == 26
        return "\n".join(self.lines) + "\n", self.events


def common_constants(labels: dict[str, tuple[int, int]], top: int) -> list[int]:
    emitter = BlockEmitter(top, 1, 0, labels, {}, [f"raw{s}" for s in range(9)], 0)
    factors: list[tuple[int, int]] = []

    def collect(factor: tuple[int, int]) -> None:
        factor = (factor[0] % GROUP_ORDER, factor[1] % GROUP_ORDER)
        if factor != (0, 0):
            factors.append(factor)

    residue = 1 if top == 0 else 5
    for s, node in enumerate(emitter.inputs):
        label = labels[node]
        collect((label[0] + LOG_THETA * 6 * s,
                 label[1] + LOG_THETA * residue * s))
    operations = {item.output: item
                  for item in (*emitter.dag.adds, *emitter.dag.muls)}
    for node in emitter.dag.nodes[9:]:
        operation = operations[node]
        if hasattr(operation, "subtract"):
            if labels[operation.left] == labels[operation.right]:
                collect(emitter.difference(labels[node], labels[operation.left]))
            else:
                collect(emitter.difference(labels[node], labels[operation.left]))
                collect(emitter.difference(labels[node], labels[operation.right]))
        else:
            collect(emitter.difference(labels[node], labels[operation.source],
                                       operation.exponent))
    return sorted({factor[1] for factor in factors if factor[0] == 0})


def render_case(top: int, component: int,
                witness: dict[str, object]) -> tuple[str, dict[str, object]]:
    labels = {name: tuple(value) for name, value in witness["assignment"].items()}
    uniform = common_constants(labels, top)
    common = {value: divmod(index, 4) for index, value in enumerate(uniform)}
    common_pack_count = (len(uniform) + 3) // 4
    raw = [f"f{s}_raw" for s in range(9)]
    block = BlockEmitter(top, component, 0, labels, common, raw, 0)
    block_text, events = block.emit()
    start = f"gt864_friso2_scaled_t{top}c{component}_slothy_start:"
    end = f"gt864_friso2_scaled_t{top}c{component}_slothy_end:"
    common_names = ",".join(f"Q<common{i}>" for i in range(common_pack_count))
    raw_names = ",".join(f"Q<f{i}_raw>" for i in range(9))
    case = "\n".join((
        start,
        f"// live-in: {raw_names}, {common_names}, x3 public table, v31=q.",
        "// live-out: Q<out0> through Q<out8> and updated x3.",
        "// coefficient range: NTT16 <=9342, candidate NTT9 <=19427.",
        "// reserved physical registers: v16-v24 hold the other block; v31=q; x0-x2,x4-x30,sp unavailable.",
        block_text.rstrip(),
        end,
        "",
    ))
    varying = sum(event["kind"] == "lane_varying_two_ldr" for event in events)
    expected = 42 + 26 * 3 + 2 * varying
    assert instruction_count(case) == expected
    assert expected == (154 if top == 0 else 138)
    packs = []
    for pack in range(common_pack_count):
        exponents = uniform[4 * pack:4 * pack + 4]
        lanes = []
        for exponent in exponents:
            lanes.extend(pair_from_exponent(exponent))
        lanes.extend([0] * (8 - len(lanes)))
        packs.append({"symbol": f"common{pack}", "exponents": exponents,
                      "halfwords": lanes})
    return case, {
        "case": f"t{top}c{component}",
        "witness": f"solution-t{top}c{component}.json",
        "instruction_count": expected,
        "mulmods_per_block": 26,
        "uniform_unique_exponents": uniform,
        "common_pack_liveins_per_block": common_pack_count,
        "common_pack_loads_per_bank_outside_region": common_pack_count,
        "lane_varying_mulmods_per_block": varying,
        "independent_constant_ldrs_per_block": 2 * varying,
        "x3_advance_bytes_per_block": 32 * varying,
        "common_packs": packs,
        "events": events,
    }


def main() -> None:
    baseline = BASELINE.read_text(encoding="utf-8")
    assert instruction_count(baseline) == 112
    cases, reports = [], []
    for top in range(2):
        for component in (1, 2):
            witness = json.loads(
                (CF1 / f"solution-t{top}c{component}.json").read_text())
            case, report = render_case(top, component, witness)
            cases.append(case.rstrip())
            reports.append(report)
    OUTPUT.write_text("\n\n".join(cases) + "\n", encoding="utf-8")
    LEDGER.write_text(json.dumps({
        "status": "generated",
        "load_policy": "two independent ldr for every lane-varying pair",
        "baseline_instructions_per_block": 112,
        "CF0_measured_full_forward_delta": 292,
        "cases": reports,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "cases": [
        {key: report[key] for key in (
            "case", "instruction_count", "mulmods_per_block",
            "common_pack_liveins_per_block", "lane_varying_mulmods_per_block",
            "independent_constant_ldrs_per_block", "x3_advance_bytes_per_block")}
        for report in reports]}, indent=2))


if __name__ == "__main__":
    main()
