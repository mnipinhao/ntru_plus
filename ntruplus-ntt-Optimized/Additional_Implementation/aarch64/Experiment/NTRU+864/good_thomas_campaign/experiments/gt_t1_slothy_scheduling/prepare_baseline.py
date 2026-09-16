#!/usr/bin/env python3
"""Extract and freeze the exact unscheduled A1-T1 one-bank baseline region."""

from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
A1 = HERE.parent / "gt_tail_architecture_shootout"
SOURCE = A1 / "build" / "pass2_t1.S"
START = ".Lgt864_a1t1_one_bank:"
END = "gt864_forward_six_bank_pass2_a1_t1_end:"
EXPECTED_SOURCE_SHA256 = "1cf9efd21be0774ee094f4683b7cf7f0db1670d7f1e48ab997098496d16a84d3"
EXPECTED_REGION_SHA256 = "61ff4ca39adbca242925ddd5b21f4d3740948af0ab99b1eabdaa27f690a2fd4f"


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit("run `make prepare` in gt_tail_architecture_shootout first")
    source = SOURCE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == EXPECTED_SOURCE_SHA256
    lines = source.decode().splitlines()
    first = lines.index(START)
    last = lines.index(END, first)
    region = "\n".join(lines[first:last + 1]) + "\n"
    assert hashlib.sha256(region.encode()).hexdigest() == EXPECTED_REGION_SHA256
    instructions = [line for line in lines[first + 1:last]
                    if line.strip() and not line.lstrip().startswith("//")]
    assert len(instructions) == 553 and instructions[-1].strip() == "ret"
    output = HERE / "build" / "baseline-region.S"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(region, encoding="utf-8")
    print(f"baseline={output}")
    print("region_sha256=" + EXPECTED_REGION_SHA256)
    print("instructions=553 including ret; schedulable_dag=552")


if __name__ == "__main__":
    main()
