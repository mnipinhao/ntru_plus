#!/usr/bin/env python3
"""Machine oracle for the P3-B producer-side packed centering DAG."""

import json
import random
import re
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
BASE = ROOT / "experiments/gt864-native-asm"
Q = 3457
HALF_Q = 1728
RECIPROCAL_1 = 9


def instructions(path: Path) -> list[str]:
    result = []
    for line in path.read_text().splitlines():
        instruction = line.split("//", 1)[0].strip()
        if not instruction or instruction.startswith(".") or instruction.endswith(":") or instruction == "ret":
            continue
        if re.match(r"^[a-z]", instruction):
            result.append(instruction)
    return result


def vector_registers(instruction: str) -> list[str]:
    return re.findall(r"\bv(\d+)", instruction.lower())


def defs_uses(instruction: str) -> tuple[set[str], set[str]]:
    op = instruction.split()[0]
    regs = vector_registers(instruction)
    if not regs:
        return set(), set()
    if op in ("str", "strh", "st1", "st2", "st3", "umov"):
        return set(), set(regs)
    definitions = {regs[0]}
    uses = set(regs[1:])
    if op in ("mls", "mla", "smlal", "smlal2", "ins"):
        uses |= definitions
    return definitions, uses


def signed_sqrdmulh(a: int, b: int) -> int:
    return (2 * a * b + (1 << 15)) // (1 << 16)


def center_dag(value: int) -> int:
    reduced = value - signed_sqrdmulh(value, RECIPROCAL_1) * Q
    reduced += Q if reduced < 0 else 0
    reduced -= Q if reduced > HALF_Q else 0
    return reduced


def canonical_center(value: int) -> int:
    return ((value + HALF_Q) % Q) - HALF_Q


def baseline_groups(code: list[str], useful: int) -> list[dict]:
    live_before = [set() for _ in code]
    live = set()
    for index in range(len(code) - 1, -1, -1):
        definitions, uses = defs_uses(code[index])
        live = (live - definitions) | uses
        live_before[index] = set(live)

    result = []
    index = 0
    while index < len(code):
        if not code[index].startswith("umov "):
            index += 1
            continue
        start = index
        pairs = []
        while index + 1 < len(code) and code[index].startswith("umov ") and code[index + 1].startswith("strh "):
            source = vector_registers(code[index])[0]
            lane = int(re.search(r"\.h\[(\d+)\]", code[index]).group(1))
            offset = int(re.search(r"#(\d+)", code[index + 1]).group(1))
            pairs.append((source, lane, offset))
            index += 2
        assert len(pairs) == 2 * useful
        result.append({"start": start, "pairs": pairs, "live": live_before[start]})
    return result


def candidate_groups(code: list[str], useful: int) -> list[dict]:
    result = []
    for index, instruction in enumerate(code):
        if not instruction.startswith("zip1 "):
            continue
        regs = vector_registers(instruction)
        assert len(regs) == 3
        packed, source0, source1 = regs
        window = code[index:index + 11 + 4 * useful]
        assert [item.split()[0] for item in window[:11]] == [
            "zip1", "movi", "sqrdmulh", "mls", "sshr", "and", "add", "ushr", "cmgt", "and", "sub"
        ]
        pairs = []
        for position in range(2 * useful):
            umov = window[11 + 2 * position]
            store = window[12 + 2 * position]
            assert umov.startswith("umov ") and store.startswith("strh ")
            assert vector_registers(umov) == [packed]
            lane = int(re.search(r"\.h\[(\d+)\]", umov).group(1))
            offset = int(re.search(r"#(\d+)", store).group(1))
            pairs.append((packed, lane, offset))
        result.append({"sources": [source0, source1], "packed": packed, "pairs": pairs, "window": window})
    assert len(result) == 16
    return result


report = {"exhaustive_center_inputs": 0, "variants": {}}
for value in range(-6912, 6913):
    assert center_dag(value) == canonical_center(value)
    assert -HALF_Q <= center_dag(value) <= HALF_Q
    report["exhaustive_center_inputs"] += 1

generation = json.loads((P / "generation-report.json").read_text())
for variant, directory, useful, q_register in (
    ("inverse16_lazy", "main", 4, "18"),
    ("inverse_tail_lazy", "tail", 3, "10"),
):
    baseline = baseline_groups(instructions(BASE / variant / "candidate.alloc.S"), useful)
    candidate = candidate_groups(instructions(P / directory / "candidate.alloc.S"), useful)
    physical_records = generation[directory]["physical_groups"]
    assert len(baseline) == len(candidate) == len(physical_records) == 16
    random_trials = 0
    for old, new, record in zip(baseline, candidate, physical_records):
        old_sources = list(dict.fromkeys(source for source, _, _ in old["pairs"]))
        assert new["sources"] == old_sources
        assert record["sources"] == old_sources
        assert set(record["temps"]).isdisjoint(old["live"])
        assert set(record["temps"]).isdisjoint(set(old_sources) | {q_register})
        assert new["packed"] == record["temps"][0]
        expected_lanes = list(range(useful)) + list(range(4, 4 + useful))
        assert [lane for _, lane, _ in new["pairs"]] == expected_lanes
        assert [offset for _, _, offset in new["pairs"]] == [offset for _, _, offset in old["pairs"]]
        for _ in range(1000):
            first = [random.randint(-6912, 6912) for _ in range(4)]
            second = [random.randint(-6912, 6912) for _ in range(4)]
            packed = first + second
            observed = [center_dag(packed[lane]) for lane in expected_lanes]
            expected = [canonical_center(value) for value in first[:useful] + second[:useful]]
            assert observed == expected
            random_trials += 1
    report["variants"][directory] = {
        "store_groups": 16,
        "coefficients_per_group": 2 * useful,
        "random_group_trials": random_trials,
        "physical_dead_temp_proof": True,
        "same_store_offsets": True,
        "same_logical_values_mod_q": True,
    }

(P / "verification-report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
