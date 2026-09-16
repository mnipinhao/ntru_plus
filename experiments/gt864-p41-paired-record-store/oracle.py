#!/usr/bin/env python3
"""Exact route, precedence, and overlapping-store oracle for P41."""

from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P23_ORACLE = ROOT / "experiments/gt864-p23-tobytes-global-dag/oracle.py"
P23_SEARCH = ROOT / "experiments/gt864-p23-tobytes-global-dag/search.py"
Q = 3457


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main():
    oracle = load("p23_oracle_for_p41", P23_ORACLE)
    search = load("p23_search_for_p41_oracle", P23_SEARCH)
    report = json.loads((HERE / "precedence-search-results.json").read_text())
    outputs, _ = search.build_dag()
    result = search.simulate(outputs, report["output_order"], 26, with_trace=True)
    p18 = search.load_p18()
    forward, _, _, _ = p18.mappings()
    forward = forward[:432]
    rng = random.Random(411864)
    cases = [list(range(432)), [-(1 << 15)] * 432, [(1 << 15) - 1] * 432,
             [(-Q + 1, Q - 1)[index & 1] for index in range(432)]]
    cases += [[rng.randrange(-(1 << 15), 1 << 15) for _ in range(432)]
              for _ in range(1024)]
    for case_index, values in enumerate(cases):
        routed = oracle.evaluate(values, result["trace"])
        expected = {output: tuple(values[forward[8 * output + lane]] for lane in range(8))
                    for output in range(54)}
        assert routed == expected, f"route mismatch case {case_index}"
        memory = bytearray([0xA5] * 648)
        seen = set()
        for output in report["output_order"]:
            packed = oracle.pack(routed[output])
            bank, local = divmod(output, 18)
            offset = 216 * bank + 12 * local
            if local % 2 == 0:
                memory[offset:offset + 16] = packed + b"\x5a" * 4
            else:
                assert output - 1 in seen
                memory[offset:offset + 4] = packed[:4]
                memory[offset + 4:offset + 12] = packed[4:]
            seen.add(output)
        expected_bytes = oracle.pack([values[index] for index in forward])
        assert bytes(memory) == expected_bytes, f"wire mismatch case {case_index}"
    print(f"P41 oracle passed: {len(cases)} exact route/overlap-store cases")


if __name__ == "__main__":
    main()
