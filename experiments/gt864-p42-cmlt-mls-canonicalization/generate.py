#!/usr/bin/env python3
"""Regenerate frozen P23/P24 route DAG with P42 CMLT+MLS correction."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
P23 = HERE.parent / "gt864-p23-tobytes-global-dag"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def consume(mode: str, output: int, instance: int, slot: int | None = None) -> list[str]:
    physical = slot is not None
    value = str(slot) if physical else f"r{instance}"
    vector = f"v{value}" if physical else f"V<{value}>"
    scalar_d = f"d{value}" if physical else f"D<{value}>"
    lines: list[str] = []
    if mode == "full":
        lines += [
            f" sqrdmulh v29.8h,{vector}.8h,v28.8h",
            f" mls {vector}.8h,v29.8h,v27.8h",
        ]
    lines += [
        f" cmlt v29.8h,{vector}.8h,#0",
        f" mls {vector}.8h,v29.8h,v27.8h",
        f" uzp1 v30.8h,{vector}.8h,{vector}.8h",
        f" uzp2 v31.8h,{vector}.8h,{vector}.8h",
        " shl v29.8h,v31.8h,#12",
        " orr v30.16b,v30.16b,v29.16b",
        " ushr v31.8h,v31.8h,#4",
        f" tbl {vector}.16b,{{v30.16b,v31.16b}},v26.16b",
    ]
    base = ("x5", "x6", "x7")[output // 18]
    offset = 12 * (output % 18)
    lines += [
        f" stur {scalar_d},[{base},#{offset}]",
        f" mov x9,{vector}.d[1]",
        f" stur w9,[{base},#{offset + 8}]",
    ]
    return lines


def main() -> None:
    gen = load("p42_p23_gen", P23 / "generate.py")
    search = gen.load_search()
    report = json.loads((P23 / "search-results.json").read_text())
    outputs, _ = search.build_dag()
    order = report["searched_order"]
    result = search.simulate(outputs, order, report["capacity_route_registers"], with_trace=True)
    instance_slots = {item["instance"]: item["slot"] for item in result["trace"]
                      if item["kind"] == "compute"}
    for item in result["trace"]:
        if item["kind"] == "compute":
            item["input_slots"] = [instance_slots[value] for value in item["inputs"]]
        else:
            item["slot"] = instance_slots[item["instance"]]
    gen.consume = consume
    for mode in ("full", "small"):
        symbolic = gen.emit(mode, result["trace"]).replace("gt864_p23_", "gt864_p42_")
        physical = gen.emit(mode, result["trace"], physical=True).replace("gt864_p23_", "gt864_p42_")
        (HERE / f"candidate-{mode}.sym.S").write_text(symbolic)
        (HERE / f"candidate-{mode}.phys.S").write_text(physical)
    print(json.dumps({
        "route_instructions_per_top": result["instructions"],
        "canonicalization_vectors_per_call": 108,
        "removed_instructions_per_call": 108,
    }, indent=2))


if __name__ == "__main__":
    main()
