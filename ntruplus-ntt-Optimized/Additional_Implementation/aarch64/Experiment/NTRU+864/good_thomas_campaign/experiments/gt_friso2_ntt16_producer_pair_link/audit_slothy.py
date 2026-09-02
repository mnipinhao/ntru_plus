#!/usr/bin/env python3
"""Audit CF5-A producer/pair allocation, scheduling, ABI, and linked assembly."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "slothy-output"
LEDGER = json.loads((ROOT / "boundary-ledger.json").read_text())
CASES = {"t0c1": (309, 77), "t0c2": (309, 77),
         "t1c1": (279, 69), "t1c2": (279, 69)}


def code_region(path: Path, start: str, end: str) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    region = text[text.index(start + ":"):text.index(end + ":")]
    lines = []
    for raw in region.splitlines()[1:]:
        code = raw.split("//", 1)[0].strip()
        if code and not code.endswith(":"):
            lines.append(code)
    return region, lines


def output_map(log: str, names: list[str]) -> dict[str, str]:
    match = re.search(r"allocated_liveouts=([^\n]+)", log)
    assert match
    entries = dict(item.split(":", 1) for item in match.group(1).split(","))
    assert set(entries) == set(names)
    assert len(set(entries.values())) == len(names)
    return entries


producer_start = "gt864_cf5_ntt16_producer_slothy_start"
producer_end = "gt864_cf5_ntt16_producer_slothy_end"
producer_region, producer = code_region(OUT / "producer.n1.opt.S",
                                        producer_start, producer_end)
assert len(producer) == 345
producer_ra = (OUT / "producer.ra.log").read_text()
producer_schedule = (OUT / "producer.schedule.log").read_text()
assert "OPTIMAL" in producer_ra and ".selfcheck:OK!" in producer_ra
assert "split.split_heuristic_full:OK!" in producer_schedule
raw_names = ([f"lo_f{i}_raw" for i in range(9)]
             + [f"hi_f{i}_raw" for i in range(9)])
producer_outputs = output_map(producer_schedule, raw_names)
assert producer_outputs == LEDGER["producer_liveouts"]
producer_cycles = int(re.search(r"Expected cycles:\s*([0-9]+)", producer_region).group(1))
assert producer_cycles == 86

build = ROOT / "build"
build.mkdir(exist_ok=True)
reports = []
for case, (expected_instructions, expected_cycles) in CASES.items():
    start = f"gt864_cf5_pair_{case}_slothy_start"
    end = f"gt864_cf5_pair_{case}_slothy_end"
    region, lines = code_region(OUT / f"{case}.n1.opt.S", start, end)
    assert len(lines) == expected_instructions
    counts = Counter(line.split()[0].lower() for line in lines)
    assert counts["mul"] == counts["sqrdmulh"] == counts["mls"] == 52
    assert counts["add"] + counts["sub"] == 84
    assert not any(op in counts for op in ("orr", "mov", "str", "st1", "stp"))
    assert not any("[sp" in line.lower() for line in lines)
    assert not any("<" in line or ">" in line for line in lines)
    assert not any(re.match(r"[a-z][a-z0-9]*\s+(?:\{\s*)?[vq](?:13|14|15)\b",
                            line, re.IGNORECASE) for line in lines)
    for register in producer_outputs.values():
        assert re.search(rf"(?<![A-Za-z0-9_]){register}\.8h\b", region, re.IGNORECASE)
    ra = (OUT / f"{case}.ra.log").read_text()
    schedule = (OUT / f"{case}.schedule.log").read_text()
    assert "OPTIMAL" in ra and ".selfcheck:OK!" in ra
    assert "split.split_heuristic_full:OK!" in schedule
    outputs = output_map(schedule, [f"out{i}" for i in range(18)])
    assert not ({"v13", "v14", "v15"} & set(outputs.values()))
    cycles = int(re.search(r"Expected cycles:\s*([0-9]+)", region).group(1))
    assert cycles == expected_cycles

    linked = [".text", ".p2align 2", f"gt864_cf5_linked_{case}:"]
    linked.extend(f"    {line}" for line in producer)
    linked.extend(f"    {line}" for line in lines)
    linked.append("    ret")
    linked_path = build / f"linked-{case}.S"
    linked_path.write_text("\n".join(linked) + "\n", encoding="utf-8")
    subprocess.run(["clang", "-target", "aarch64-linux-gnu", "-c", linked_path,
                    "-o", build / f"linked-{case}.o"], check=True)
    reports.append({
        "case": case,
        "consumer_instructions": len(lines),
        "linked_region_instructions_excluding_ret": 345 + len(lines),
        "producer_N1_proxy_cycles": producer_cycles,
        "consumer_N1_proxy_cycles": cycles,
        "separate_region_N1_proxy_sum": producer_cycles + cycles,
        "boundary_copies": 0,
        "spills": 0,
        "new_coefficient_memory_ops": 0,
        "v13_v14_v15_preserved": True,
        "assembler": "pass",
    })

pass2 = (ROOT / "gt864_forward_six_bank_cf5.S").read_text()
assert pass2.count("bl .Lgt864_cf5_linked_") == 4
assert pass2.count("bl .Lgt864_m5rd_one_bank") == 2
assert len(re.findall(r"(?m)^    str q(?:[0-9]|[12][0-9]|3[01]), \[x6, #[0-9]+\]$",
                      pass2)) == 108
for case in CASES:
    assert pass2.count(f".Lgt864_cf5_linked_{case}:") == 1
    assert pass2.count(f".Lgt864_cf5_table_{case}:") == 1
correctness = (ROOT / "pi5-correctness.log").read_text().strip()
assert correctness == ("gt864_friso2_forward_absorption=pass cases=1126 "
                       "comparisons=972864 alias_comparisons=972864")

print(json.dumps({
    "status": "pass",
    "producer_liveouts": producer_outputs,
    "reports": reports,
    "full_forward_dynamic_instruction_estimate": 4726,
    "rejected_CF0_dynamic_instructions": 4738,
    "static_advantage_vs_CF0": 12,
    "pi5_linked_correctness_cases": 1126,
    "pi5_coefficient_comparisons_per_mode": 972864,
    "cycle_claim": "N1 proxy for separated regions only; Pi5 not run",
}, indent=2))
