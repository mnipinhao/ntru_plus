#!/usr/bin/env python3
"""Audit exact assembly duplication in GT production serialization sources."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


INSTRUCTION_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.]*\s+")


def instructions(path: Path) -> list[tuple[int, str]]:
    result = []
    for line_number, raw_line in enumerate(path.read_text().splitlines(), 1):
        line = raw_line.split("//", 1)[0].strip()
        if (
            not line
            or line.startswith((".", "#", "/*", "*"))
            or line.endswith(":")
            or not INSTRUCTION_RE.match(line)
        ):
            continue
        result.append((line_number, re.sub(r"\s+", " ", line.lower())))
    return result


def longest_common_run(
    left: list[tuple[int, str]], right: list[tuple[int, str]]
) -> dict[str, int]:
    previous = [0] * (len(right) + 1)
    best = (0, 0, 0)
    for left_index, (_, left_instruction) in enumerate(left, 1):
        current = [0] * (len(right) + 1)
        for right_index, (_, right_instruction) in enumerate(right, 1):
            if left_instruction == right_instruction:
                current[right_index] = previous[right_index - 1] + 1
                if current[right_index] > best[0]:
                    best = (
                        current[right_index],
                        left_index - current[right_index],
                        right_index - current[right_index],
                    )
        previous = current

    count, left_start, right_start = best
    return {
        "instruction_count": count,
        "left_start_line": left[left_start][0],
        "left_end_line": left[left_start + count - 1][0],
        "right_start_line": right[right_start][0],
        "right_end_line": right[right_start + count - 1][0],
    }


def exact_occurrences(
    haystack: list[tuple[int, str]], needle: list[str]
) -> list[dict[str, int]]:
    result = []
    for start in range(len(haystack) - len(needle) + 1):
        if [instruction for _, instruction in haystack[start : start + len(needle)]] == needle:
            result.append(
                {
                    "start_line": haystack[start][0],
                    "end_line": haystack[start + len(needle) - 1][0],
                }
            )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-root",
        type=Path,
        required=True,
        help="Path to ntruplus-GT-Production/.../NTRU+768",
    )
    args = parser.parse_args()

    asm = args.release_root / "asm"
    paths = {
        "generic_pack": asm / "pack.S",
        "keygen_cq_pack": asm / "internal" / "keygen_pack.S",
        "generic_unpack": asm / "internal" / "unpack.S",
        "support": asm / "support.S",
    }
    streams = {name: instructions(path) for name, path in paths.items()}

    # This is the exact q-register pack core, including its two 48-byte stores.
    support_core = [
        instruction
        for line_number, instruction in streams["support"]
        if 210 <= line_number <= 270
    ]
    if len(support_core) != 60:
        raise SystemExit(f"expected 60 support pack instructions, found {len(support_core)}")

    generic_hits = exact_occurrences(streams["generic_pack"], support_core)
    keygen_hits = exact_occurrences(streams["keygen_cq_pack"], support_core)
    if len(generic_hits) != 12 or len(keygen_hits) != 12:
        raise SystemExit(
            "expected twelve exact pack64 copies in both generic and keygen pack"
        )

    current_pack_family_instructions = (
        len(streams["generic_pack"]) + len(streams["keygen_cq_pack"]) + 67
    )
    # Each unrolled copy becomes one BL. qsoa_tobytes also calls the helper
    # from its existing loop. The helper contains 60 instructions plus RET.
    shared_helper_instructions = 61
    compact_generic = len(streams["generic_pack"]) - 12 * 60 + 12
    compact_keygen = len(streams["keygen_cq_pack"]) - 12 * 60 + 12
    compact_qsoa = 67 - 60 + 1
    compact_family_instructions = (
        compact_generic
        + compact_keygen
        + compact_qsoa
        + shared_helper_instructions
    )

    report = {
        "release_root": str(args.release_root),
        "source_instruction_counts": {
            name: len(stream) for name, stream in streams.items() if name != "support"
        },
        "exact_pack64_core": {
            "instruction_count": len(support_core),
            "input_contract": ["v0=q", "v9-v12=coefficients", "v26-v29=coefficients"],
            "output_contract": ["96 canonical bytes at x0", "x0 advanced by 96"],
            "generic_pack_occurrences": generic_hits,
            "keygen_cq_pack_occurrences": keygen_hits,
            "qsoa_static_occurrences": 1,
        },
        "longest_exact_runs": {
            "generic_vs_keygen": longest_common_run(
                streams["generic_pack"], streams["keygen_cq_pack"]
            ),
            "generic_vs_support": longest_common_run(
                streams["generic_pack"], streams["support"]
            ),
            "unpack_vs_support": longest_common_run(
                streams["generic_unpack"], streams["support"]
            ),
        },
        "shared_helper_static_estimate": {
            "current_pack_family_instructions": current_pack_family_instructions,
            "candidate_pack_family_instructions": compact_family_instructions,
            "instruction_delta": (
                compact_family_instructions - current_pack_family_instructions
            ),
            "byte_delta_before_alignment_and_lr_preservation": 4
            * (compact_family_instructions - current_pack_family_instructions),
            "dynamic_instruction_delta_per_64_coefficients": 2,
            "note": "BL plus helper RET replaces fall-through; wrappers must preserve LR.",
        },
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
