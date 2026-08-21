#!/usr/bin/env python3
"""Classify repeated source shapes without assigning relocation credit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


def extract_macro(text: str, name: str) -> list[str]:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines)
                 if re.match(rf"^\.macro\s+{re.escape(name)}(?:\s|$)", line))
    body: list[str] = []
    depth = 0
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith(".macro "):
            depth += 1
        elif stripped == ".endm":
            depth -= 1
            if depth == 0:
                return body
        elif depth == 1 and stripped and not stripped.startswith("#"):
            body.append(stripped)
    raise ValueError(f"unterminated macro {name}")


def class_labels(signatures: list[tuple]) -> tuple[list[str], dict[str, dict]]:
    labels: dict[tuple, str] = {}
    sequence: list[str] = []
    for signature in signatures:
        if signature not in labels:
            labels[signature] = chr(ord("A") + len(labels))
        sequence.append(labels[signature])
    counts = Counter(sequence)
    definitions = {
        label: {"count": counts[label], "signature": list(signature)}
        for signature, label in labels.items()
    }
    return sequence, definitions


def prefix_period(sequence: list[str]) -> int:
    for period in range(1, len(sequence) + 1):
        if all(value == sequence[index % period]
               for index, value in enumerate(sequence)):
            return period
    return len(sequence)


def runs(sequence: list[str]) -> list[dict]:
    result: list[dict] = []
    for value in sequence:
        if result and result[-1]["class"] == value:
            result[-1]["count"] += 1
        else:
            result.append({"class": value, "count": 1})
    return result


def parse_m_q24(pack: str) -> dict:
    body = extract_macro(pack, "Q24_ENCODE_SOA_BODY")
    groups: list[dict] = []
    current: list[str] = []
    for line in body:
        if re.match(r"^vmovdqu\s+\d+\(%rsi\),\s*%ymm0$", line) and current:
            groups.append(parse_m_group(current))
            current = []
        current.append(line)
    if current:
        groups.append(parse_m_group(current))
    signatures = [tuple(group["routing_signature"]) for group in groups]
    sequence, definitions = class_labels(signatures)
    for group, label in zip(groups, sequence):
        group["class"] = label
    return {
        "group_count": len(groups),
        "groups": groups,
        "class_sequence": sequence,
        "class_definitions": definitions,
        "contiguous_runs": runs(sequence),
        "minimum_prefix_period": prefix_period(sequence),
        "candidate_shapes": [
            {
                "name": "repeat_classes_A_D_B_only",
                "mechanism": "descriptor loops only for classes occurring 4, 3, and 2 times; inline all singleton classes",
                "purpose": "midpoint between 5.1-KiB unrolled and 1.8-KiB all-descriptor compact",
            },
            {
                "name": "repeat_classes_A_D_only",
                "mechanism": "descriptor loops only for the two highest-frequency routing classes",
                "purpose": "lower dynamic loop fee, smaller static reduction",
            },
        ],
    }


def parse_m_group(lines: list[str]) -> dict:
    loads = [int(match.group(1)) for line in lines
             if (match := re.match(r"^vmovdqu\s+(\d+)\(%rsi\)", line))]
    packets = []
    for line in lines:
        match = re.match(
            r"^Q24_ENCODE_REG_PACKET\s+%(ymm\d+),%xmm\d+,(\d+),(\d+),(\d+)$",
            line,
        )
        if match:
            packets.append({"register": match.group(1), "perm": int(match.group(2)),
                            "output": int(match.group(3)), "safe": int(match.group(4))})
    if len(loads) != 4 or len(packets) != 4:
        raise ValueError(f"unexpected M-Q24 group: {lines}")
    signature = [f"{item['register']}:{item['perm']}:{item['safe']}" for item in packets]
    return {"input_offsets": loads, "output_offsets": [item["output"] for item in packets],
            "routing_signature": signature}


def parse_p_sp1(pack: str) -> dict:
    body = extract_macro(pack, "Q24_ENCODE_P_SOA_HALF_SCATTER_SP1_BODY")
    groups: list[list[str]] = []
    current: list[str] = []
    prefix: list[str] = []
    for line in body:
        if line.startswith("Q24_TRANSPOSE_TF1 "):
            if current:
                groups.append(current)
            current = [line]
        elif current:
            current.append(line)
        else:
            prefix.append(line)
    if current:
        groups.append(current)
    parsed = [parse_p_group(lines) for lines in groups]
    signatures = [tuple(group["shape_signature"]) for group in parsed]
    sequence, definitions = class_labels(signatures)
    for group, label in zip(parsed, sequence):
        group["class"] = label
    return {
        "initial_load_instructions": len(prefix),
        "group_count": len(parsed),
        "groups": parsed,
        "class_sequence": sequence,
        "class_definitions": definitions,
        "contiguous_runs": runs(sequence),
        "minimum_prefix_period": prefix_period(sequence),
        "candidate_assessment": {
            "fixed_period_loop": False,
            "reason": "routing classes are heterogeneous and SP1 preloads the next physical input group",
            "next_gate": "only emit a caged midpoint if a helper/class-loop preserves SP1 and avoids table-driving every group",
        },
    }


def parse_p_group(lines: list[str]) -> dict:
    transpose = lines[0].rsplit(",", 4)[-4:]
    masks = []
    stores = []
    reducer = ""
    preload_offsets: list[int] = []
    for line in lines[1:]:
        if line.startswith("vpshufb .Lq24_p_half_mask_"):
            match = re.search(r"half_mask_(\d+).*%(ymm\d+),\s*%(ymm\d+)$", line)
            masks.append(f"{match.group(1)}:{match.group(2)}" if match else line)
        elif line.startswith("Q24_HALF_REDUCE_PACK4_SP1 "):
            reducer = "SP1"
            preload_offsets = [int(value) for value in re.findall(r"(?:,|\s)(\d+)(?=,|$)", line)[-4:]]
        elif line.startswith("Q24_HALF_REDUCE_PACK4 "):
            reducer = "FINAL"
        elif line.startswith("Q24_STORE_SCATTER_PACKET "):
            fields = line.replace("Q24_STORE_SCATTER_PACKET ", "").split(",")
            stores.append(":".join([fields[0].replace("%", ""), fields[2],
                                     fields[3].replace("%", ""), fields[5], fields[7]]))
    signature = ["T:" + ",".join(transpose), "M:" + ",".join(masks),
                 "R:" + reducer, "S:" + "|".join(stores)]
    return {"transpose_flags": transpose, "masks": masks, "reducer": reducer,
            "preload_offsets": preload_offsets, "shape_signature": signature}


def parse_inverse(inv: str) -> dict:
    body = extract_macro(inv, "RUN_8_T8")
    invocations = []
    signatures = []
    for line in body:
        match = re.match(r"^TAIL_GROUP_T8\s+(\d+),(.+)$", line)
        if not match:
            continue
        group = int(match.group(1))
        registers = [part.strip() for part in match.group(2).split(",")]
        signature = tuple(registers)
        invocations.append({"group": group, "register_rotation": registers})
        signatures.append(signature)
    sequence, definitions = class_labels(signatures)
    for item, label in zip(invocations, sequence):
        item["class"] = label
    return {
        "group_count": len(invocations),
        "groups": invocations,
        "class_sequence": sequence,
        "class_definitions": definitions,
        "minimum_prefix_period": prefix_period(sequence),
        "affine_group_operands": {
            "input_stride_bytes": 32,
            "matrix_stride_bytes": 288,
            "output_stride_bytes": 32,
        },
        "candidate_shapes": [
            {
                "name": "U3_x2_plus_U2",
                "mechanism": "three exact register rotations in a two-iteration loop plus a two-group tail",
                "requirements": ["pointerize affine group offsets", "no new YMM live range",
                                 "equal-size 5578-byte cage", "preserve T8 arithmetic verbatim"],
            }
        ],
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--inverse", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pack = args.pack.read_text()
    inverse = args.inverse.read_text()
    payload = {
        "schema": "gt32-hot-code-repeated-shapes-v1",
        "sources": {
            "pack": {"path": str(args.pack.resolve()), "sha256": sha256(args.pack)},
            "inverse": {"path": str(args.inverse.resolve()), "sha256": sha256(args.inverse)},
        },
        "m_q24": parse_m_q24(pack),
        "inverse_tail": parse_inverse(inverse),
        "p_sp1": parse_p_sp1(pack),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
