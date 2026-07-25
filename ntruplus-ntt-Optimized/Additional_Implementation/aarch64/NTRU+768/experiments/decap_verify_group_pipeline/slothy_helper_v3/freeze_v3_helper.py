#!/usr/bin/env python3
"""Freeze the exact V3 shared helper as an existing-region baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
NTRU768 = HERE.parents[2]
SOURCE = (
    NTRU768
    / "asm/gt/experiment/decap/verify_pointwise_group_pipeline_v3.S"
)
OUTPUT = HERE / "baseline-region.S"
METADATA = HERE / "baseline-region.json"
START = ".Lfused_gather_mul_group:"
END_RE = re.compile(r"^\s*ret\s*(?://.*)?$")
INSTRUCTION_RE = re.compile(r"^\s*[a-z][a-z0-9.]*\b")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    lines = source_bytes.decode("ascii").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == START)
    except StopIteration as exc:
        raise SystemExit(f"missing helper label {START} in {SOURCE}") from exc

    body: list[str] = []
    for line in lines[start + 1 :]:
        if END_RE.match(line):
            break
        body.append(line.rstrip())
    else:
        raise SystemExit(f"missing helper ret after {START}")

    instruction_count = sum(
        1
        for line in body
        if INSTRUCTION_RE.match(line)
        and not line.lstrip().startswith((".", "//"))
    )
    if instruction_count != 100:
        raise SystemExit(
            f"expected 100 V3 helper instructions, found {instruction_count}"
        )

    frozen = "\n".join(
        [
            "/* Mechanically extracted from the V3 shared helper. */",
            ".text",
            ".align 2",
            "slothy_start_decap_verify_helper_v3_baseline:",
            *body,
            "slothy_end_decap_verify_helper_v3_baseline:",
            "",
        ]
    ).encode("ascii")
    OUTPUT.write_bytes(frozen)
    METADATA.write_text(
        json.dumps(
            {
                "source": str(SOURCE.relative_to(NTRU768)),
                "source_sha256": sha256(source_bytes),
                "region_sha256": sha256(frozen),
                "source_start_label": START.removesuffix(":"),
                "output_start_label": (
                    "slothy_start_decap_verify_helper_v3_baseline"
                ),
                "output_end_label": "slothy_end_decap_verify_helper_v3_baseline",
                "instruction_count": instruction_count,
                "includes_ret": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="ascii",
    )
    print(f"baseline={OUTPUT}")
    print(f"metadata={METADATA}")
    print(f"instructions={instruction_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
