#!/usr/bin/env python3
"""Normalize GCC 14.2 P9 assembly and add bounded timing-only regions."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"


def normalize_instruction(text: str) -> str:
    text = " ".join(text.strip().split())
    match = re.fullmatch(r"mov (v\d+\.16b), (v\d+\.16b)", text)
    if match:
        destination, source = match.groups()
        text = f"orr {destination}, {source}, {source}"
    match = re.fullmatch(
        r"tbl (v\d+\.16b), \{(v\d+)\.16b - (v\d+)\.16b\}, (v\d+\.16b)",
        text,
    )
    if match:
        destination, first, last, index = match.groups()
        if int(last[1:]) != int(first[1:]) + 1:
            raise RuntimeError(f"unexpected TBL2 range: {text}")
        text = f"tbl {destination}, {{{first}.16b, {last}.16b}}, {index}"
    text = re.sub(r"^(str d\d+, \[[^]]+\]), (\d+)$", r"\1, #\2", text)
    return text


def is_instruction(raw: str) -> bool:
    text = raw.strip()
    return bool(text and not text.startswith((".", "#", "//")) and not text.endswith(":"))


def prepare(mode: str) -> dict[str, object]:
    source = BUILD / f"p9-{mode}.gcc.S"
    lines = source.read_text().splitlines()
    function = f"p9_input_once_top_{mode}:"
    start = lines.index(function)
    size = next(index for index in range(start + 1, len(lines))
                if lines[index].lstrip().startswith(f".size\tp9_input_once_top_{mode}"))

    # Preserve directives and labels, while making only instruction spelling
    # canonical for Slothy.  MOV V,V is the architectural ORR alias and GCC's
    # TBL range spelling is expanded to the equivalent explicit register list.
    normalized = [
        ("// " + line.lstrip()) if line.lstrip() in {"#APP", "#NO_APP"} else line
        for line in lines
    ]
    for index in range(start + 1, size):
        if is_instruction(lines[index]):
            normalized[index] = "\t" + normalize_instruction(lines[index])

    constant_index = next(
        index for index in range(start + 1, size)
        if is_instruction(normalized[index])
        and normalized[index].strip().startswith("ldr q")
        and "#:lo12:.LC2" in normalized[index]
    )
    epilogue = next(
        index for index in range(constant_index + 1, size)
        if normalize_instruction(normalized[index]).startswith("ldp d8, d9, [sp],")
    )
    all_body_instructions = [
        index for index in range(constant_index + 1, epilogue)
        if is_instruction(normalized[index])
    ]
    # Slothy does not model GCC's one D-register post-index store spelling.
    # Keep that exact instruction in place and use it as a hard region barrier.
    unsupported = {
        index for index in all_body_instructions
        if re.fullmatch(r"str d\d+, \[x\d+\], #\d+", normalized[index].strip())
    }
    segments: list[list[int]] = []
    current: list[int] = []
    for index in all_body_instructions:
        if index in unsupported:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(index)
    if current:
        segments.append(current)

    # Prefer a completed 12-byte store as a boundary.  Target 140 and cap 190
    # instructions, keeping the final short tail with its predecessor.
    regions: list[list[int]] = []
    for instruction_indices in segments:
        cuts = [0]
        cursor = 0
        total = len(instruction_indices)
        while total - cursor > 190:
            lo = cursor + 100
            hi = min(cursor + 190, total)
            candidates = []
            for position in range(lo, hi + 1):
                raw = normalized[instruction_indices[position - 1]].strip()
                if raw.startswith("st1 "):
                    candidates.append(position)
            if candidates:
                cut = min(candidates, key=lambda value: abs(value - (cursor + 140)))
            else:
                cut = min(cursor + 140, total)
            cuts.append(cut)
            cursor = cut
        cuts.append(total)
        regions.extend(instruction_indices[left:right]
                       for left, right in zip(cuts, cuts[1:]))

    insert_before: dict[int, list[str]] = {}
    for number, region in enumerate(regions):
        first = region[0]
        after_last = region[-1] + 1
        insert_before.setdefault(first, []).extend([
            "// live-in: every fixed physical register read by this window",
            "// live-out: every fixed physical register and memory location written by this window",
            "// range: unchanged P9 full/small coefficient and canonical byte bounds",
            "// reserved physical registers: x18-x30, sp; renaming and spills disabled",
            f"p15_{mode}_window_{number}_slothy_start:",
        ])
        insert_before.setdefault(after_last, []).append(
            f"p15_{mode}_window_{number}_slothy_end:"
        )

    output_lines = []
    for index, line in enumerate(normalized):
        output_lines.extend(insert_before.get(index, []))
        output_lines.append(line)
    output = BUILD / f"p15-{mode}.input.S"
    output.write_text("\n".join(output_lines) + "\n")
    return {
        "mode": mode,
        "source": str(source.relative_to(HERE)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output": str(output.relative_to(HERE)),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "scheduled_instructions": sum(map(len, regions)),
        "window_instruction_counts": list(map(len, regions)),
        "windows": len(regions),
        "unscheduled_body_instructions": len(unsupported),
        "unscheduled_prefix_instructions": sum(
            is_instruction(normalized[index]) for index in range(start + 1, constant_index + 1)
        ),
        "unscheduled_epilogue_instructions": sum(
            is_instruction(normalized[index]) for index in range(epilogue, size)
        ),
    }


def main() -> None:
    result = {mode: prepare(mode) for mode in ("full", "small")}
    (HERE / "preparation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
