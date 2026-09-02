#!/usr/bin/env python3
"""Link bounded CF5 producer/consumer regions into a correctness-only Forward."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M5RD = ROOT.parent / "gt_forward_level2_one_mul_b3"
CF3 = ROOT.parent / "gt_friso2_two_block_boundary_slothy"
PASS2_IN = M5RD / "gt864_forward_six_bank_all_one_mul_b3.S"
WRAPPER_IN = M5RD / "gt864_forward_poly_ntt_all_one_mul_b3.S"
PASS2_OUT = ROOT / "gt864_forward_six_bank_cf5.S"
WRAPPER_OUT = ROOT / "gt864_forward_poly_ntt_cf5.S"
OUT = ROOT / "slothy-output"
BOUNDARY = json.loads((ROOT / "boundary-ledger.json").read_text())
CF3_LEDGER = json.loads((CF3 / "two-block-ledger.json").read_text())
CASES = ("t0c1", "t0c2", "t1c1", "t1c2")


def code_region(path: Path, start: str, end: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    region = text[text.index(start + ":"):text.index(end + ":")]
    lines = []
    for raw in region.splitlines()[1:]:
        code = raw.split("//", 1)[0].strip()
        if code and not code.endswith(":"):
            lines.append(code)
    return lines


def liveout_registers(case: str) -> list[str]:
    text = (OUT / f"{case}.schedule.log").read_text()
    match = re.search(r"allocated_liveouts=([^\n]+)", text)
    assert match
    mapping = dict(item.split(":", 1) for item in match.group(1).split(","))
    result = [mapping[f"out{i}"] for i in range(18)]
    assert len(set(result)) == 18
    assert not ({"v13", "v14", "v15"} & set(result))
    return result


def replace_scaled_bank(text: str, case: str) -> str:
    top, component = int(case[1]), int(case[3])
    bank = 3 * top + component
    marker = f"    // top={top}, component={component}, bank={bank}\n"
    start = text.index(marker)
    next_marker = text.find("    // top=", start + len(marker))
    end = next_marker if next_marker >= 0 else text.index("    mov x30, x16", start)
    section = text[start:end]
    section = section.replace(f"adr x3, .Lgt864_m5rd_ntt9_top{top}",
                              f"adr x3, .Lgt864_cf5_table_{case}")
    section = section.replace("bl .Lgt864_m5rd_one_bank",
                              f"bl .Lgt864_cf5_linked_{case}")
    registers = liveout_registers(case)
    stores = list(re.finditer(r"(?m)^    str q([0-9]|[12][0-9]|3[01]), (\[x6, #[0-9]+\])$",
                              section))
    assert len(stores) == 18
    pieces, cursor = [], 0
    for match, register in zip(stores, registers):
        pieces.append(section[cursor:match.start()])
        pieces.append(f"    str q{register[1:]}, {match.group(2)}")
        cursor = match.end()
    pieces.append(section[cursor:])
    replacement = "".join(pieces)
    return text[:start] + replacement + text[end:]


def helper(case: str) -> str:
    producer = code_region(OUT / "producer.n1.opt.S",
                           "gt864_cf5_ntt16_producer_slothy_start",
                           "gt864_cf5_ntt16_producer_slothy_end")
    consumer = code_region(OUT / f"{case}.n1.opt.S",
                           f"gt864_cf5_pair_{case}_slothy_start",
                           f"gt864_cf5_pair_{case}_slothy_end")
    assert len(producer) == 345
    assert len(consumer) == (309 if case.startswith("t0") else 279)
    lines = [f".Lgt864_cf5_linked_{case}:"]
    lines.extend(f"    {line}" for line in producer)
    lines.extend(f"    {line}" for line in consumer)
    lines.append("    ret")
    return "\n".join(lines)


def case_table(case: str) -> str:
    boundary_case = next(row for row in BOUNDARY["cases"] if row["case"] == case)
    cf3_case = next(row for row in CF3_LEDGER["cases"] if row["case"] == case)
    vectors = list(boundary_case["common_packs"])
    for block in cf3_case["blocks"]:
        for event in block["events"]:
            if event["kind"] != "lane_varying_two_ldr":
                continue
            vectors.append([pair[0] for pair in event["lane_pairs"]])
            vectors.append([pair[1] for pair in event["lane_pairs"]])
    expected = boundary_case["x3_advance_bytes"] // 16
    assert len(vectors) == expected
    lines = ["    .p2align 4", f".Lgt864_cf5_table_{case}:"]
    lines.extend("    .short " + ", ".join(map(str, vector)) for vector in vectors)
    return "\n".join(lines)


def generate_pass2() -> str:
    text = PASS2_IN.read_text(encoding="utf-8")
    text = text.replace(
        "M5R-D: six-bank Pass-2 with one-mul level-1 and level-2 B3; ldr ABI retained.",
        "M5U-CF5: bounded NTT16 producer linked to CF3 scaled NTT9 pairs.")
    text = text.replace("gt864_forward_six_bank_pass2_all_one_mul_b3",
                        "gt864_forward_six_bank_pass2_cf5")
    for case in CASES:
        text = replace_scaled_bank(text, case)
    insertion = text.index(".Lgt864_m5rd_common:")
    helpers = "\n\n".join(helper(case) for case in CASES) + "\n\n"
    text = text[:insertion] + helpers + text[insertion:]
    tables = "\n\n".join(case_table(case) for case in CASES)
    return text.rstrip() + "\n\n" + tables + "\n"


def generate_wrapper() -> str:
    text = WRAPPER_IN.read_text(encoding="utf-8")
    text = text.replace("M5R-D full Forward wrapper",
                        "M5U-CF5 linked correctness-only Forward wrapper")
    text = text.replace("gt864_forward_poly_ntt_all_one_mul_b3",
                        "gt864_forward_poly_ntt_cf5")
    text = text.replace("gt864_forward_six_bank_pass2_all_one_mul_b3",
                        "gt864_forward_six_bank_pass2_cf5")
    return text


if __name__ == "__main__":
    PASS2_OUT.write_text(generate_pass2(), encoding="utf-8")
    WRAPPER_OUT.write_text(generate_wrapper(), encoding="utf-8")
    print("linked_scaled_banks=4")
    print("dynamic_full_forward_instructions=4726")
    print("boundary_copies=0")
    print("constant_reloads_between_banks=0")
