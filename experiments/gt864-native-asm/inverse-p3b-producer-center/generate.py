#!/usr/bin/env python3
"""Generate symbolic and fixed-allocation P3-B candidates after contracts pass."""

import json
import re
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
BASE = ROOT / "experiments/gt864-native-asm"


def code(path: Path) -> list[str]:
    result = []
    for line in path.read_text().splitlines():
        instruction = line.split("//", 1)[0].strip()
        if not instruction or instruction.startswith(".") or instruction.endswith(":") or instruction == "ret":
            continue
        if re.match(r"^[a-z]", instruction):
            result.append(instruction)
    return result


def registers(instruction: str, symbolic: bool) -> list[str]:
    if symbolic:
        return re.findall(r"(?:V|Q)<(\w+)>", instruction)
    return re.findall(r"\bv(\d+)", instruction.lower())


def defs_uses(instruction: str, symbolic: bool) -> tuple[set[str], set[str]]:
    op = instruction.split()[0]
    regs = registers(instruction, symbolic)
    if not regs:
        return set(), set()
    if op in ("str", "strh", "st1", "st2", "st3", "umov"):
        return set(), set(regs)
    definitions = {regs[0]}
    uses = set(regs[1:])
    if op in ("mls", "mla", "smlal", "smlal2", "ins"):
        uses |= definitions
    return definitions, uses


def spell(reg: str, symbolic: bool, width: str) -> str:
    return f"V<{reg}>.{width}" if symbolic else f"v{reg}.{width}"


def transform(source: list[str], *, symbolic: bool, q: str, useful: int) -> tuple[list[str], list[dict]]:
    live_before = [set() for _ in source]
    live = set()
    for index in range(len(source) - 1, -1, -1):
        definitions, uses = defs_uses(source[index], symbolic)
        live = (live - definitions) | uses
        live_before[index] = set(live)

    candidates = ([f"r{i}" for i in range(32)] if symbolic else [str(i) for i in range(32)])
    result = []
    records = []
    index = 0
    while index < len(source):
        if not source[index].startswith("umov "):
            result.append(source[index])
            index += 1
            continue
        group = []
        while index + 1 < len(source) and source[index].startswith("umov ") and source[index + 1].startswith("strh "):
            group.append((source[index], source[index + 1]))
            index += 2
        assert len(group) == 2 * useful
        src = []
        for umov, _ in group:
            reg = registers(umov, symbolic)[0]
            if reg not in src:
                src.append(reg)
        assert len(src) == 2
        dead = [reg for reg in candidates if reg != q and reg not in live_before[index - len(group) * 2]]
        dead = [reg for reg in dead if reg not in src]
        assert len(dead) >= 3
        packed, quotient, constant = dead[:3]
        result.extend([
            f"zip1 {spell(packed, symbolic, '2d')}, {spell(src[0], symbolic, '2d')}, {spell(src[1], symbolic, '2d')}",
            f"movi {spell(constant, symbolic, '8h')}, #9",
            f"sqrdmulh {spell(quotient, symbolic, '8h')}, {spell(packed, symbolic, '8h')}, {spell(constant, symbolic, '8h')}",
            f"mls {spell(packed, symbolic, '8h')}, {spell(quotient, symbolic, '8h')}, {spell(q, symbolic, '8h')}",
            f"sshr {spell(quotient, symbolic, '8h')}, {spell(packed, symbolic, '8h')}, #15",
            f"and {spell(quotient, symbolic, '16b')}, {spell(quotient, symbolic, '16b')}, {spell(q, symbolic, '16b')}",
            f"add {spell(packed, symbolic, '8h')}, {spell(packed, symbolic, '8h')}, {spell(quotient, symbolic, '8h')}",
            f"ushr {spell(constant, symbolic, '8h')}, {spell(q, symbolic, '8h')}, #1",
            f"cmgt {spell(quotient, symbolic, '8h')}, {spell(packed, symbolic, '8h')}, {spell(constant, symbolic, '8h')}",
            f"and {spell(quotient, symbolic, '16b')}, {spell(quotient, symbolic, '16b')}, {spell(q, symbolic, '16b')}",
            f"sub {spell(packed, symbolic, '8h')}, {spell(packed, symbolic, '8h')}, {spell(quotient, symbolic, '8h')}",
        ])
        offsets = []
        for position, (umov, store) in enumerate(group):
            gpr = re.search(r"\b(w\d+)", umov).group(1)
            lane = position if position < useful else 4 + position - useful
            result.append(f"umov {gpr}, {spell(packed, symbolic, '8h').rsplit('.', 1)[0]}.h[{lane}]")
            result.append(store)
            offsets.append(int(re.search(r"#(\d+)", store).group(1)))
        records.append({"sources": src, "temps": [packed, quotient, constant], "offsets": offsets})
    return result, records


def write_source(path: Path, function: str, body: list[str], symbolic: bool) -> None:
    suffix = "symbolic DAG" if symbolic else "inherited P3-A physical allocation with dead-register reuse"
    text = [
        ".text", f".global {function}", f"{function}:",
        f"// P3-B {suffix}; final stores are centered in producer registers.",
        "// live-in: x0 output, x1 packed scratch, x3 stage table, x4 scale table, and documented vector inputs.",
        "// live-out: x0 and the centered natural-order coefficient output in memory.",
        "// coefficient range: I9 <= 3456; I16 <= 30939; terminal <= 6912; stored centered <= 1728.",
        "// reserved physical registers: x18-x30, sp, and xzr; no stack spill is permitted.",
        f"{function}_slothy_start:",
    ]
    text += ["    " + instruction for instruction in body]
    text += [f"{function}_slothy_end:", "    ret"]
    path.write_text("\n".join(text) + "\n")


report = {}
for variant, directory, function, useful, physical_q in (
    ("inverse16_lazy", "main", "lazy_i16", 4, "18"),
    ("inverse_tail_lazy", "tail", "lazy_itail", 3, "10"),
):
    target = P / directory
    symbolic_body, symbolic_groups = transform(code(BASE / variant / "candidate.sym.S"), symbolic=True, q="r31", useful=useful)
    physical_body, physical_groups = transform(code(BASE / variant / "candidate.alloc.S"), symbolic=False, q=physical_q, useful=useful)
    assert len(symbolic_groups) == len(physical_groups) == 16
    assert [group["offsets"] for group in symbolic_groups] == [group["offsets"] for group in physical_groups]
    assert len(symbolic_body) == len(physical_body)
    write_source(target / "candidate.sym.S", function, symbolic_body, True)
    write_source(target / "candidate.alloc.S", function, physical_body, False)
    report[directory] = {
        "baseline_instructions": len(symbolic_body) - 16 * 11,
        "candidate_instructions": len(symbolic_body),
        "groups": symbolic_groups,
        "physical_groups": physical_groups,
        "q_register": "r31" if directory == "main" else "r31 symbolic; v10 physical",
    }

(P / "generation-report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({name: {"baseline": value["baseline_instructions"], "candidate": value["candidate_instructions"]} for name, value in report.items()}, indent=2))
