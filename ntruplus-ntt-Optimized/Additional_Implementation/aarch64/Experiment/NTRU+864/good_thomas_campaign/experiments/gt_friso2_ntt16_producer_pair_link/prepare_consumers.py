#!/usr/bin/env python3
"""Pin each CF3 consumer to the allocated CF5 NTT16 producer live-outs."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF3 = ROOT.parent / "gt_friso2_two_block_boundary_slothy"
CF2 = ROOT.parent / "gt_friso2_scaled_ntt9_slothy"
CF1 = ROOT.parent / "gt_friso2_scaled_ntt9_search"
PRODUCER_SYMBOLIC = ROOT / "gt864_cf5_ntt16_producer.sym.S"
PRODUCER_ALLOC = ROOT / "slothy-output" / "producer.n1.alloc.S"
CF3_SOURCE = CF3 / "gt864_friso2_two_block_variants.sym.S"
OUTPUT = ROOT / "gt864_cf5_fixed_livein_consumers.sym.S"
LEDGER = ROOT / "boundary-ledger.json"
CASES = ("t0c1", "t0c2", "t1c1", "t1c2")
RAW_NAMES = ([f"lo_f{i}_raw" for i in range(9)]
             + [f"hi_f{i}_raw" for i in range(9)])


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cf2 = load_module("cf5_cf2_generator", CF2 / "generate_candidates.py")


def instructions(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()
            if re.match(r"^\s{4}[a-z][a-z0-9]*\s", line)]


def producer_map() -> dict[str, str]:
    symbolic = PRODUCER_SYMBOLIC.read_text(encoding="utf-8")
    allocated = PRODUCER_ALLOC.read_text(encoding="utf-8")
    sym_lines = instructions(symbolic)
    real_lines = []
    region = allocated[allocated.index("gt864_cf5_ntt16_producer_slothy_start:"):
                       allocated.index("gt864_cf5_ntt16_producer_slothy_end:")]
    for raw in region.splitlines():
        code = raw.split("//", 1)[0].strip()
        if re.match(r"^[a-z][a-z0-9]*\s", code) and "<" not in code:
            real_lines.append(code)
    if len(sym_lines) != 345 or len(real_lines) != 345:
        raise RuntimeError(f"producer pairing mismatch: {len(sym_lines)}, {len(real_lines)}")
    mapping: dict[str, str] = {}
    for sym, real in zip(sym_lines, real_lines):
        sm = re.match(r"[a-z][a-z0-9]*\s+(?:V|Q)<([A-Za-z_][A-Za-z0-9_]*)>", sym)
        pm = re.match(r"[a-z][a-z0-9]*\s+(?:\{\s*)?[vq]([0-9]|[12][0-9]|3[01])\b", real)
        if sm and pm and sm.group(1) in RAW_NAMES:
            mapping[sm.group(1)] = "v" + pm.group(1)
    if set(mapping) != set(RAW_NAMES) or len(set(mapping.values())) != 18:
        raise RuntimeError(f"invalid producer live-out map: {mapping}")
    if "v14" in mapping.values():
        raise RuntimeError("producer allocated q register as a raw live-out")
    return mapping


def witness_common_packs(case: str) -> list[list[int]]:
    top = int(case[1])
    component = int(case[3])
    witness = json.loads((CF1 / f"solution-t{top}c{component}.json").read_text())
    labels = {name: tuple(value) for name, value in witness["assignment"].items()}
    uniform = cf2.common_constants(labels, top)
    packs = []
    for offset in range(0, len(uniform), 4):
        lanes: list[int] = []
        for exponent in uniform[offset:offset + 4]:
            lanes.extend(cf2.pair_from_exponent(exponent))
        lanes.extend([0] * (8 - len(lanes)))
        packs.append(lanes)
    return packs


def render_case(case: str, mapping: dict[str, str]) -> tuple[str, dict[str, object]]:
    source = CF3_SOURCE.read_text(encoding="utf-8")
    old_start = f"gt864_friso2_pair_{case}_slothy_start:"
    old_end = f"gt864_friso2_pair_{case}_slothy_end:"
    region = source[source.index(old_start):source.index(old_end) + len(old_end)]
    body_lines = []
    for raw in region.splitlines()[1:-1]:
        if raw.startswith("//"):
            continue
        body_lines.append(raw)
    body = "\n".join(body_lines).strip("\n")
    # Rewrite CF3's fixed modulus before substituting physical producer
    # live-ins: one valid producer output is v31 and must not be mistaken for q.
    body = body.replace("v31.8h", "v14.8h")
    for name, register in mapping.items():
        body = body.replace(f"V<{name}>", register)
    packs = witness_common_packs(case)
    common_loads = "\n".join(
        f"    ldr Q<common{i}>, [x3], #16" for i in range(len(packs)))
    start = f"gt864_cf5_pair_{case}_slothy_start:"
    end = f"gt864_cf5_pair_{case}_slothy_end:"
    text = "\n".join((
        start,
        "// fixed live-in registers are the exact allocated producer live-outs in boundary-ledger.json.",
        "// v13=bitrev and v15=roots remain preserved; v14=q; x3 points to the case table.",
        "// live-out: Q<out0>..Q<out17>, updated x3; no copy/spill/store is permitted.",
        common_loads,
        body,
        end,
        "",
    ))
    expected = (309 if case.startswith("t0") else 279)
    if len(instructions(text)) != expected:
        raise RuntimeError(f"{case}: unexpected instruction count")
    return text, {
        "case": case,
        "producer_liveins": mapping,
        "common_packs": packs,
        "common_loads": len(packs),
        "lane_varying_loads": 68 if case.startswith("t0") else 36,
        "instructions": expected,
        "x3_advance_bytes": 16 * len(packs) + (1088 if case.startswith("t0") else 576),
    }


if __name__ == "__main__":
    mapping = producer_map()
    regions, cases = [], []
    for case in CASES:
        region, report = render_case(case, mapping)
        regions.append(region.rstrip())
        cases.append(report)
    OUTPUT.write_text("\n\n".join(regions) + "\n", encoding="utf-8")
    LEDGER.write_text(json.dumps({"status": "generated", "producer_liveouts": mapping,
                                  "cases": cases}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "pass", "producer_liveouts": mapping,
                      "cases": [{k: row[k] for k in ("case", "instructions",
                                                       "common_loads", "x3_advance_bytes")}
                                for row in cases]}, indent=2))
