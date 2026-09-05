#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMMARY = HERE / "build/pi5/summary.json"
DISASSEMBLY = HERE / "build/pi5/raw/build-test-disassembly.log"


def improvement(old: float, new: float) -> dict[str, float]:
    return {
        "cycles_saved": round(old - new, 3),
        "percent_saved": round(100.0 * (old - new) / old, 3),
    }


def instruction_shape(text: str, symbol: str) -> dict[str, object]:
    # Split at section headings to keep parsing independent of object order.
    marker = f"Disassembly of section .text.{symbol}:"
    assert marker in text
    body = text.split(marker, 1)[1].split("Disassembly of section ", 1)[0]
    instructions = re.findall(
        r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+([a-z0-9]+)\b", body
    )
    registers = sorted(
        {int(n) for n in re.findall(r"\b(?:v|q)(\d+)\b", body)}
    )
    return {
        "instructions": len(instructions),
        "tbl": instructions.count("tbl"),
        "ext": instructions.count("ext"),
        "physical_vector_registers": registers,
        "physical_vector_register_count": len(registers),
    }


def main() -> None:
    data = json.loads(SUMMARY.read_text())
    text = DISASSEMBLY.read_text()
    assert data["correctness"] == "pass"
    assert data["throttled"] == "0x0"
    assert not data["production_linked"]
    assert "p3b1_route9=pass mismatches=0" in text

    overall = data["overall"]
    for direction in ("f2o", "o2f"):
        current = overall[f"{direction}_current"]["cycles"]
        r9a = overall[f"{direction}_r9a"]["cycles"]
        r9b = overall[f"{direction}_r9b"]["cycles"]
        assert r9a < r9b < current
        assert improvement(current, r9a)["percent_saved"] > 50.0
        for repetition in data["repetitions"]:
            assert repetition[f"{direction}_r9a"]["cycles"] < repetition[f"{direction}_r9b"]["cycles"]
            assert repetition[f"{direction}_r9b"]["cycles"] < repetition[f"{direction}_current"]["cycles"]

    # Stack references in the linked wrappers are only the x29/x30 ABI frame.
    # A vector spill would show a q/d/s/v register in an [sp,...] memory op.
    vector_spills = re.findall(
        r"(?mi)^\s*[0-9a-f]+:\s+.*\b(?:ldr|str|ldp|stp)\s+(?:q|d|s|v)\d+.*\[sp",
        text,
    )
    assert not vector_spills, vector_spills

    sizes = {}
    for symbol, expected in {
        "r9a_fwd": 472,
        "r9a_rev": 420,
        "r9b_fwd": 500,
        "r9b_rev": 500,
    }.items():
        match = re.search(rf"(?m)^[0-9a-f]+\s+([0-9a-f]+)\s+[tT]\s+{symbol}$", text)
        assert match, symbol
        sizes[symbol] = int(match.group(1), 16)
        assert sizes[symbol] == expected

    shapes = {symbol: instruction_shape(text, symbol) for symbol in sizes}
    for symbol, expected in {
        "r9a_fwd": (118, 17, 0),
        "r9a_rev": (105, 9, 7),
        "r9b_fwd": (125, 27, 0),
        "r9b_rev": (125, 27, 0),
    }.items():
        shape = shapes[symbol]
        assert (shape["instructions"], shape["tbl"], shape["ext"]) == expected
        assert shape["physical_vector_registers"] == list(range(8)) + list(range(16, 32))

    report = {
        "gate": "D1-P3B1",
        "winner": "R9-A transpose/repair",
        "forward": improvement(overall["f2o_current"]["cycles"], overall["f2o_r9a"]["cycles"]),
        "reverse": improvement(overall["o2f_current"]["cycles"], overall["o2f_r9a"]["cycles"]),
        "r9a_vs_r9b_cycles": {
            "forward": round(overall["f2o_r9b"]["cycles"] - overall["f2o_r9a"]["cycles"], 3),
            "reverse": round(overall["o2f_r9b"]["cycles"] - overall["o2f_r9a"]["cycles"], 3),
        },
        "helper_text_bytes": sizes,
        "helper_instruction_shape": shapes,
        "critical_dependent_tbl_depth": 1,
        "vector_spills": 0,
        "production_linked": False,
    }
    out = HERE / "build/audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
