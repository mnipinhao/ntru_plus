#!/usr/bin/env python3
"""Exact lane-map and byte oracle for the P23 register-capped trace."""

from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q = 3457


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def trn(a, b, group: int, upper: bool):
    start = group if upper else 0
    result = []
    for index in range(start, 8, 2 * group):
        result += a[index:index + group]
        result += b[index:index + group]
    return tuple(result)


def evaluate(values, trace):
    instances = {}
    routed = {}
    for item in trace:
        if item["kind"] == "consume":
            routed[item["output"]] = instances[item["instance"]]
            continue
        operation = item["operation"]
        args = [instances[value] for value in item["inputs"]]
        if operation == "load":
            start = 8 * item["source"]
            result = tuple(values[start:start + 8])
        elif operation.startswith("ext"):
            amount = int(operation[3:])
            result = args[0][amount:] + args[0][:amount]
        else:
            mnemonic, shape = operation.split(".")
            group = {"8h": 1, "4s": 2, "2d": 4}[shape]
            result = trn(args[0], args[1], group, mnemonic == "trn2")
        instances[item["instance"]] = result
    return routed


def pack(coefficients):
    output = bytearray()
    for left, right in zip(coefficients[::2], coefficients[1::2]):
        left %= Q
        right %= Q
        output += bytes((left & 255, ((left >> 8) | (right << 4)) & 255,
                         (right >> 4) & 255))
    return bytes(output)


def main() -> None:
    search = load_module("p23_search", HERE / "search.py")
    p18 = search.load_p18()
    report = json.loads((HERE / "search-results.json").read_text())
    outputs, _ = search.build_dag()
    result = search.simulate(outputs, report["searched_order"], 26, with_trace=True)
    forward, _, _, _ = p18.mappings()
    forward = forward[:432]
    rng = random.Random(230864)
    cases = [
        list(range(432)),
        [-(1 << 15)] * 432,
        [(1 << 15) - 1] * 432,
        [(-Q + 1, Q - 1)[index & 1] for index in range(432)],
    ]
    cases += [[rng.randrange(-(1 << 15), 1 << 15) for _ in range(432)]
              for _ in range(512)]
    for case_index, values in enumerate(cases):
        routed = evaluate(values, result["trace"])
        expected = {
            output: tuple(values[forward[8 * output + lane]] for lane in range(8))
            for output in range(54)
        }
        assert routed == expected, f"lane map mismatch in case {case_index}"
        got_bytes = b"".join(pack(routed[output]) for output in range(54))
        expected_bytes = pack([values[index] for index in forward])
        assert got_bytes == expected_bytes, f"wire bytes mismatch in case {case_index}"
    print(f"P23 oracle passed: {len(cases)} exact lane-map and canonical-byte cases")


if __name__ == "__main__":
    main()
