#!/usr/bin/env python3
"""Audit CF3 pair allocation, boundary coloring, schedule, and assembly."""

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_friso2_two_block_variants.sym.S"
OUT = ROOT / "slothy-output"
EXPECTED = {"t0c1": (308, 68, 77), "t0c2": (308, 68, 77),
            "t1c1": (276, 36, 69), "t1c2": (276, 36, 69)}


def region(text: str, case: str):
    start = f"gt864_friso2_pair_{case}_slothy_start:"
    end = f"gt864_friso2_pair_{case}_slothy_end:"
    return text[text.index(start):text.index(end)]


def paired_lines(text: str, case: str):
    physical, symbolic = [], []
    for raw in region(text, case).splitlines():
        stripped = raw.strip()
        code = raw.split("//", 1)[0].strip()
        if re.match(r"^[a-z][a-z0-9]*\s", code) and "<" not in code:
            physical.append(code)
        elif (re.match(r"^//\s*[a-z][a-z0-9]*\s", stripped)
              and ("V<" in stripped or "Q<" in stripped)):
            symbolic.append(re.sub(r"^//\s*", "", stripped))
    return physical, symbolic


def destination(line: str):
    match = re.match(r"[a-z][a-z0-9]*\s+(?:\{\s*)?[vq]([0-9]|[12][0-9]|3[01])\b", line)
    return "v" + match.group(1) if match else None


def output_map(physical, symbolic):
    mapping, definitions = {}, {}
    for index, (real, sym) in enumerate(zip(physical, symbolic)):
        match = re.match(r"[a-z][a-z0-9]*\s+(?:V|Q)<(out(?:[0-9]|1[0-7]))>", sym)
        if match:
            mapping[match.group(1)] = destination(real)
            definitions[match.group(1)] = index
    assert set(mapping) == {f"out{i}" for i in range(18)}
    assert len(set(mapping.values())) == 18
    return mapping, definitions


symbolic_all = SOURCE.read_text()
reports = []
build = ROOT / "build"
build.mkdir(exist_ok=True)
for case, (expected_count, expected_loads, expected_cycles) in EXPECTED.items():
    alloc_text = (OUT / f"{case}.n1.alloc.S").read_text()
    opt_text = (OUT / f"{case}.n1.opt.S").read_text()
    ra_log = (OUT / f"{case}.ra.log").read_text()
    schedule_log = (OUT / f"{case}.schedule.log").read_text()
    allocated, symbolic = paired_lines(alloc_text, case)
    optimized, _ = paired_lines(opt_text, case)
    source_lines = [line.strip() for line in region(symbolic_all, case).splitlines()
                    if re.match(r"^\s{4}[a-z][a-z0-9]*\s", line)]
    assert len(source_lines) == len(allocated) == len(optimized) == expected_count
    assert [x.split()[0] for x in source_lines] == [x.split()[0] for x in allocated]
    counts = Counter(x.split()[0] for x in optimized)
    assert counts["ldr"] == expected_loads
    assert counts["mul"] == counts["sqrdmulh"] == counts["mls"] == 52
    assert counts["add"] + counts["sub"] == 84
    assert not any(op in counts for op in ("orr", "mov", "str", "stp", "st1", "ld1"))
    assert all(re.fullmatch(r"ldr q(?:[0-9]|[12][0-9]|3[01]), \[x3\], #16", x,
                            flags=re.IGNORECASE)
               for x in optimized if x.startswith("ldr "))
    assert not any(re.match(r"^(?:b|bl|br|cbz|cbnz|tbz|tbnz|ret)\b", x)
                   for x in optimized)
    assert not any(re.search(r"\b(?:sp|x29|x30)\b", x) for x in optimized)
    mapping, definitions = output_map(allocated, symbolic)
    boundary = next(i for i, line in enumerate(symbolic)
                    if re.search(r"(?:V|Q)<b1_", line) or "hi_f" in line)
    assert all(definitions[f"out{i}"] < boundary for i in range(9))
    assert all(definitions[f"out{i}"] >= boundary for i in range(9, 18))
    first_regs = {mapping[f"out{i}"] for i in range(9)}
    for index in range(boundary, len(allocated)):
        assert destination(allocated[index]) not in first_regs
    assert "OPTIMAL" in ra_log and ".selfcheck:OK!" in ra_log
    assert "split_heuristic_full:OK!" in schedule_log
    assert "Traceback" not in ra_log + schedule_log
    cycle = re.search(r"Expected cycles:\s*([0-9]+)", region(opt_text, case))
    assert cycle and int(cycle.group(1)) == expected_cycles
    logged = next(line for line in schedule_log.splitlines()
                  if line.startswith("allocated_liveouts="))
    assert len(logged.split("=", 1)[1].split(",")) == 18
    asm = build / f"{case}.audit.S"
    asm.write_text(".text\n" + f"audit_{case}:\n" + "\n".join(optimized) + "\n")
    subprocess.run(["clang", "--target=aarch64-linux-gnu", "-c", str(asm),
                    "-o", str(build / f"{case}.audit.o")], check=True)
    reports.append({"case": case, "instructions": expected_count,
                    "N1_proxy_cycles": expected_cycles,
                    "first_output_registers": [mapping[f"out{i}"] for i in range(9)],
                    "second_output_registers": [mapping[f"out{i}"] for i in range(9, 18)],
                    "first_outputs_untouched_after_boundary": True,
                    "boundary_copies_spills_stores": 0,
                    "assembler": "pass", "RA": "OPTIMAL_selfcheck_OK",
                    "schedule": "split_heuristic_full_OK"})

print(json.dumps({"status": "pass", "reports": reports,
                  "physical_vector_budget": "v0-v30 allocated; v31 fixed q",
                  "cycle_claim": "N1 proxy only; no Cortex-A76 claim"}, indent=2))
