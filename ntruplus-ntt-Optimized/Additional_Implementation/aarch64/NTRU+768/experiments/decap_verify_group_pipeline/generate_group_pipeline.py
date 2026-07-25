#!/usr/bin/env python3
"""Generate an experiment-only cross-group gather pipeline."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "asm/gt/decap/verify_pointwise_compact.S"
OUTPUT = (
    ROOT
    / "asm/gt/experiment/decap/verify_pointwise_group_pipeline.S"
)
OUTPUT_V2 = (
    ROOT
    / "asm/gt/experiment/decap/verify_pointwise_group_pipeline_v2.S"
)
OUTPUT_V3 = (
    ROOT
    / "asm/gt/experiment/decap/verify_pointwise_group_pipeline_v3.S"
)
METADATA = Path(__file__).with_name("group_pipeline_contract.json")
METADATA_V2 = Path(__file__).with_name("group_pipeline_v2_contract.json")
METADATA_V3 = Path(__file__).with_name("group_pipeline_v3_contract.json")

GROUP_RE = re.compile(
    r"(?ms)^    // QSoA group (?P<group>\d+):.*?"
    r"^    bl \.Lfused_gather_mul_group\n"
)
LOAD_RE = re.compile(
    r"^    ldr d(?P<reg>2[4-9]|3[01]), \[x1, #(?P<offset>\d+)\]$"
)
HELPER_RE = re.compile(
    r"(?ms)^\.Lfused_gather_mul_group:\n(?P<body>.*?)^    ret\n"
)

# These registers are dead after the current group's final UZP and are not
# touched by the shared multiplication helper.
LOOKAHEAD_REGS = {24, 25, 26, 27, 31}
LOOKAHEAD_REGS_V2 = {24, 25, 26, 27, 28, 29, 31}
LOOKAHEAD_REGS_V3 = set(range(24, 32))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_group(match: re.Match[str]) -> dict[str, object]:
    text = match.group(0)
    lines = text.splitlines()
    loads: dict[int, str] = {}
    body: list[str] = []
    comment = lines[0]

    for line in lines[1:]:
        load = LOAD_RE.match(line)
        if load:
            loads[int(load.group("reg"))] = line
        elif line != "    bl .Lfused_gather_mul_group":
            body.append(line)

    expected = set(range(24, 32))
    if set(loads) != expected:
        raise ValueError(
            f"group {match.group('group')} load registers "
            f"{sorted(loads)} != {sorted(expected)}"
        )
    return {
        "number": int(match.group("group")),
        "comment": comment,
        "loads": loads,
        "body": body,
    }


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode()
    matches = list(GROUP_RE.finditer(source))
    groups = [parse_group(match) for match in matches]

    if [group["number"] for group in groups] != list(range(24)):
        raise ValueError("expected consecutive QSoA groups 0..23")

    helper = HELPER_RE.search(source)
    if helper is None:
        raise ValueError("missing shared multiplication helper")
    helper_body = helper.group("body")
    for reg in sorted(LOOKAHEAD_REGS):
        if re.search(rf"\bv{reg}\b", helper_body):
            raise ValueError(f"helper clobbers lookahead register v{reg}")

    generated: list[str] = [
        "/* Experiment-only one-group gather software pipeline. */",
        "#ifndef GT_DECAP_VERIFY_POINTWISE_SYMBOL",
        "#define GT_DECAP_VERIFY_POINTWISE_SYMBOL "
        "gt_decap_verify_pointwise_group_pipeline",
        "#endif",
        "#ifndef GT_DECAP_VERIFY_POINTWISE_DARWIN_SYMBOL",
        "#define GT_DECAP_VERIFY_POINTWISE_DARWIN_SYMBOL "
        "_gt_decap_verify_pointwise_group_pipeline",
        "#endif",
        "",
        source[: matches[0].start()].rstrip(),
        "",
    ]

    for index, group in enumerate(groups):
        loads = group["loads"]
        assert isinstance(loads, dict)
        generated.append(str(group["comment"]))
        if index == 0:
            generated.extend(str(loads[reg]) for reg in range(24, 32))
        else:
            generated.extend(
                str(loads[reg])
                for reg in range(24, 32)
                if reg not in LOOKAHEAD_REGS
            )
        generated.extend(str(line) for line in group["body"])
        if index + 1 < len(groups):
            next_group = groups[index + 1]
            next_loads = next_group["loads"]
            assert isinstance(next_loads, dict)
            generated.append(
                f"    // Look ahead to QSoA group {index + 1}; "
                "these registers survive the helper."
            )
            generated.extend(
                str(next_loads[reg]) for reg in sorted(LOOKAHEAD_REGS)
            )
        generated.append("    bl .Lfused_gather_mul_group")

    generated.append(source[matches[-1].end() :].lstrip())
    output = "\n".join(generated)
    if not output.endswith("\n"):
        output += "\n"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(output)
    metadata = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(source_bytes),
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": sha256(output.encode()),
        "groups": len(groups),
        "helper_calls": len(groups),
        "lookahead_registers": [f"d{reg}" for reg in sorted(LOOKAHEAD_REGS)],
        "lookahead_loads_per_transition": len(LOOKAHEAD_REGS),
        "transitions": len(groups) - 1,
        "moved_loads": len(LOOKAHEAD_REGS) * (len(groups) - 1),
        "added_instructions": 0,
        "removed_instructions": 0,
        "arithmetic_changed": False,
        "offsets_changed": False,
        "stores_changed": False,
    }
    METADATA.write_text(json.dumps(metadata, indent=2) + "\n")

    # V2 moves the helper's v28/v29 temporaries to otherwise-unused v2/v3.
    # This makes d28/d29 available as two additional cross-call lookahead
    # registers. Place each next-group load immediately after the current
    # value's last use in the transpose sequence.
    if re.search(r"\bv(?:2|3)\b", helper_body):
        raise ValueError("helper unexpectedly uses v2/v3 before V2 remap")
    renamed_helper = re.sub(r"\bv28\b", "v2", helper.group(0))
    renamed_helper = re.sub(r"\bv29\b", "v3", renamed_helper)
    for reg in sorted(LOOKAHEAD_REGS_V2):
        if re.search(rf"\bv{reg}\b", renamed_helper):
            raise ValueError(f"V2 helper clobbers lookahead register v{reg}")

    generated_v2: list[str] = [
        "/* Experiment-only seven-load cross-group software pipeline. */",
        "#ifndef GT_DECAP_VERIFY_POINTWISE_SYMBOL",
        "#define GT_DECAP_VERIFY_POINTWISE_SYMBOL "
        "gt_decap_verify_pointwise_group_pipeline_v2",
        "#endif",
        "#ifndef GT_DECAP_VERIFY_POINTWISE_DARWIN_SYMBOL",
        "#define GT_DECAP_VERIFY_POINTWISE_DARWIN_SYMBOL "
        "_gt_decap_verify_pointwise_group_pipeline_v2",
        "#endif",
        "",
        source[: matches[0].start()].rstrip(),
        "",
    ]

    for index, group in enumerate(groups):
        loads = group["loads"]
        body = group["body"]
        assert isinstance(loads, dict)
        assert isinstance(body, list)
        generated_v2.append(str(group["comment"]))
        if index == 0:
            generated_v2.extend(str(loads[reg]) for reg in range(24, 32))
        else:
            generated_v2.extend(
                str(loads[reg])
                for reg in range(24, 32)
                if reg not in LOOKAHEAD_REGS_V2
            )

        insert_after: dict[int, list[int]] = {}
        if index + 1 < len(groups):
            next_group = groups[index + 1]
            next_loads = next_group["loads"]
            assert isinstance(next_loads, dict)
            last_use: dict[int, int] = {}
            for body_index, line in enumerate(body):
                for reg in LOOKAHEAD_REGS_V2:
                    if re.search(rf"\bv{reg}\b", str(line)):
                        last_use[reg] = body_index
            if set(last_use) != LOOKAHEAD_REGS_V2:
                raise ValueError(
                    f"group {index} incomplete V2 last-use map: {last_use}"
                )
            for reg, body_index in last_use.items():
                insert_after.setdefault(body_index, []).append(reg)
            generated_v2.append(
                f"    // Earliest-death lookahead to QSoA group {index + 1}."
            )

        for body_index, line in enumerate(body):
            generated_v2.append(str(line))
            if index + 1 < len(groups):
                next_loads = groups[index + 1]["loads"]
                assert isinstance(next_loads, dict)
                generated_v2.extend(
                    str(next_loads[reg])
                    for reg in sorted(insert_after.get(body_index, []))
                )
        generated_v2.append("    bl .Lfused_gather_mul_group")

    suffix = source[matches[-1].end() :].lstrip()
    if helper.group(0) not in suffix:
        raise ValueError("helper is not contained in generated suffix")
    suffix_v2 = suffix.replace(helper.group(0), renamed_helper, 1)
    generated_v2.append(suffix_v2)
    output_v2 = "\n".join(generated_v2)
    if not output_v2.endswith("\n"):
        output_v2 += "\n"

    OUTPUT_V2.write_text(output_v2)
    metadata_v2 = {
        **metadata,
        "output": str(OUTPUT_V2.relative_to(ROOT)),
        "output_sha256": sha256(output_v2.encode()),
        "lookahead_registers": [
            f"d{reg}" for reg in sorted(LOOKAHEAD_REGS_V2)
        ],
        "lookahead_loads_per_transition": len(LOOKAHEAD_REGS_V2),
        "moved_loads": len(LOOKAHEAD_REGS_V2) * (len(groups) - 1),
        "lookahead_schedule": "immediately_after_current_value_last_use",
        "helper_register_remap": {"v28": "v2", "v29": "v3"},
    }
    METADATA_V2.write_text(json.dumps(metadata_v2, indent=2) + "\n")

    # V3 schedules the three UZP2-derived helper temporaries through q2/q3.
    # q2 is reused only after its first value's last use. This frees q30 as
    # well, allowing all eight gather registers to survive across the call.
    helper_temp_window = """\
    uzp2 v30.8h, v16.8h, v17.8h
    uzp2 v29.8h, v14.8h, v15.8h
    uzp2 v28.8h, v12.8h, v13.8h
    smull v18.4s, v7.4h, v8.4h
    smull2 v19.4s, v7.8h, v8.8h
    smull v16.4s, v30.4h, v1.4h
    smull2 v17.4s, v30.8h, v1.8h
    smull v14.4s, v29.4h, v1.4h
    smull2 v15.4s, v29.8h, v1.8h
    smull v12.4s, v28.4h, v1.4h
    smull2 v13.4s, v28.8h, v1.8h
"""
    helper_temp_window_v3 = """\
    uzp2 v2.8h, v16.8h, v17.8h
    uzp2 v3.8h, v14.8h, v15.8h
    smull v18.4s, v7.4h, v8.4h
    smull2 v19.4s, v7.8h, v8.8h
    smull v16.4s, v2.4h, v1.4h
    smull2 v17.4s, v2.8h, v1.8h
    uzp2 v2.8h, v12.8h, v13.8h
    smull v14.4s, v3.4h, v1.4h
    smull2 v15.4s, v3.8h, v1.8h
    smull v12.4s, v2.4h, v1.4h
    smull2 v13.4s, v2.8h, v1.8h
"""
    if helper.group(0).count(helper_temp_window) != 1:
        raise ValueError("V3 helper temporary window did not match exactly")
    renamed_helper_v3 = helper.group(0).replace(
        helper_temp_window, helper_temp_window_v3, 1
    )
    for reg in sorted(LOOKAHEAD_REGS_V3):
        if re.search(rf"\bv{reg}\b", renamed_helper_v3):
            raise ValueError(f"V3 helper clobbers lookahead register v{reg}")

    generated_v3: list[str] = [
        "/* Experiment-only eight-load cross-group software pipeline. */",
        "#ifndef GT_DECAP_VERIFY_POINTWISE_SYMBOL",
        "#define GT_DECAP_VERIFY_POINTWISE_SYMBOL "
        "gt_decap_verify_pointwise_group_pipeline_v3",
        "#endif",
        "#ifndef GT_DECAP_VERIFY_POINTWISE_DARWIN_SYMBOL",
        "#define GT_DECAP_VERIFY_POINTWISE_DARWIN_SYMBOL "
        "_gt_decap_verify_pointwise_group_pipeline_v3",
        "#endif",
        "",
        source[: matches[0].start()].rstrip(),
        "",
    ]

    for index, group in enumerate(groups):
        loads = group["loads"]
        body = group["body"]
        assert isinstance(loads, dict)
        assert isinstance(body, list)
        generated_v3.append(str(group["comment"]))
        if index == 0:
            generated_v3.extend(str(loads[reg]) for reg in range(24, 32))

        insert_after: dict[int, list[int]] = {}
        if index + 1 < len(groups):
            next_loads = groups[index + 1]["loads"]
            assert isinstance(next_loads, dict)
            last_use: dict[int, int] = {}
            for body_index, line in enumerate(body):
                for reg in LOOKAHEAD_REGS_V3:
                    if re.search(rf"\bv{reg}\b", str(line)):
                        last_use[reg] = body_index
            if set(last_use) != LOOKAHEAD_REGS_V3:
                raise ValueError(
                    f"group {index} incomplete V3 last-use map: {last_use}"
                )
            for reg, body_index in last_use.items():
                insert_after.setdefault(body_index, []).append(reg)
            generated_v3.append(
                f"    // Full earliest-death lookahead to QSoA group "
                f"{index + 1}."
            )

        for body_index, line in enumerate(body):
            generated_v3.append(str(line))
            if index + 1 < len(groups):
                next_loads = groups[index + 1]["loads"]
                assert isinstance(next_loads, dict)
                generated_v3.extend(
                    str(next_loads[reg])
                    for reg in sorted(insert_after.get(body_index, []))
                )
        generated_v3.append("    bl .Lfused_gather_mul_group")

    suffix_v3 = suffix.replace(helper.group(0), renamed_helper_v3, 1)
    generated_v3.append(suffix_v3)
    output_v3 = "\n".join(generated_v3)
    if not output_v3.endswith("\n"):
        output_v3 += "\n"

    OUTPUT_V3.write_text(output_v3)
    metadata_v3 = {
        **metadata,
        "output": str(OUTPUT_V3.relative_to(ROOT)),
        "output_sha256": sha256(output_v3.encode()),
        "lookahead_registers": [
            f"d{reg}" for reg in sorted(LOOKAHEAD_REGS_V3)
        ],
        "lookahead_loads_per_transition": len(LOOKAHEAD_REGS_V3),
        "moved_loads": len(LOOKAHEAD_REGS_V3) * (len(groups) - 1),
        "lookahead_schedule": "immediately_after_current_value_last_use",
        "helper_register_remap": {
            "v30_first": "v2",
            "v29": "v3",
            "v28_after_v30_last_use": "v2",
        },
        "helper_instruction_order_changed": True,
    }
    METADATA_V3.write_text(json.dumps(metadata_v3, indent=2) + "\n")
    print(OUTPUT)
    print(METADATA)
    print(OUTPUT_V2)
    print(METADATA_V2)
    print(OUTPUT_V3)
    print(METADATA_V3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
