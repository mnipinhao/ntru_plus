#!/usr/bin/env python3
"""Audit the returned GCC disassembly and paired Cortex-A76 PMU summary."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DISASSEMBLY = ROOT / "build/pi5-formal/raw/build-and-disassembly.log"
SUMMARY = ROOT / "build/pi5-formal/summary.json"
SYMBOLS = (
    "gt864_friso2_basemul_staged",
    "gt864_friso2_basemul_direct",
    "gt864_friso2_basemul_add_staged",
    "gt864_friso2_basemul_add_direct",
)


def functions(text: str) -> dict[str, list[str]]:
    headers = list(re.finditer(r"^([0-9a-f]+) <([^>]+)>:", text, re.M))
    result = {}
    for index, header in enumerate(headers):
        name = header.group(2)
        if name not in SYMBOLS:
            continue
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        lines = text[header.end():end].splitlines()
        result[name] = [line for line in lines if re.match(
            r"^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+", line)]
    return result


def main() -> None:
    text = DISASSEMBLY.read_text(encoding="utf-8")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    found = functions(text)
    assert set(found) == set(SYMBOLS)
    expected_static = {
        "gt864_friso2_basemul_staged": 104,
        "gt864_friso2_basemul_direct": 96,
        "gt864_friso2_basemul_add_staged": 121,
        "gt864_friso2_basemul_add_direct": 110,
    }
    reports = {}
    for name, lines in found.items():
        body = "\n".join(lines)
        vectors = sorted({int(value) for value in re.findall(r"\bv(\d+)\b", body)})
        assert len(lines) == expected_static[name]
        assert not re.search(r"\bsp\b", body)
        assert not re.search(r"\b(?:bl|blr)\b", body)
        assert not any(8 <= vector <= 15 for vector in vectors)
        reports[name] = {
            "static_instructions": len(lines),
            "vectors": vectors,
            "stack_or_spill": False,
            "calls": False,
            "callee_saved_v8_v15": False,
        }

    overall = summary["overall"]
    derived = overall["derived"]
    assert derived["staged_kernel_instructions"] == 2808
    assert derived["direct_kernel_instructions"] == 2447
    assert derived["staged_add_kernel_instructions"] == 3243
    assert derived["direct_add_kernel_instructions"] == 2881
    bm_saved = overall["staged"]["cycles"]["p50"] \
        - overall["direct"]["cycles"]["p50"]
    add_saved = overall["staged_add"]["cycles"]["p50"] \
        - overall["direct_add"]["cycles"]["p50"]
    bm_percent = 100 * bm_saved / overall["staged"]["cycles"]["p50"]
    add_percent = 100 * add_saved / overall["staged_add"]["cycles"]["p50"]
    assert bm_percent > 10 and add_percent > 10
    assert summary["throttled"] == "0x0"
    print(json.dumps({
        "gate": "gt864_friso2_basemul_cycle_remote_audit",
        "status": "pass",
        "host": summary["host"],
        "core": summary["core"],
        "functions": reports,
        "pmu": {
            "BaseMul_cycles_saved_p50": bm_saved,
            "BaseMul_percent_faster": bm_percent,
            "BaseMul_instructions_saved": 361,
            "BaseMulAdd_cycles_saved_p50": add_saved,
            "BaseMulAdd_percent_faster": add_percent,
            "BaseMulAdd_instructions_saved": 362,
            "samples_per_variant": overall["staged"]["count"],
            "throttled": summary["throttled"],
        },
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
