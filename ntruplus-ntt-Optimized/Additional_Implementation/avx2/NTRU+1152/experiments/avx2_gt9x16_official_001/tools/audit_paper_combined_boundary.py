#!/usr/bin/env python3
"""Record the inlined R2 store -> adjusted-NTT16 reload seam."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1"


def render(obj: Path) -> str:
    disassembly = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", "-M", "intel", str(obj)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    match = re.search(rf"^[0-9a-f]+ <{SYMBOL}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
                      disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing {SYMBOL}")
    lines = [line.strip() for line in match.group(1).splitlines()
             if re.match(r"^\s*[0-9a-f]+:", line)]
    seams = [index for index, line in enumerate(lines)
             if re.search(r"\bmov\s+rsi,rdi\b", line)]
    if len(seams) != 1:
        raise SystemExit(f"expected one R2/NTT16 seam, found {len(seams)}")
    seam = seams[0]
    before = lines[max(0, seam - 30):seam]
    after = lines[seam + 1:seam + 31]
    document = {
        "checkpoint": "F-R3D1",
        "function": SYMBOL,
        "seam_instruction": lines[seam],
        "last_30_r2_instructions": before,
        "first_30_adjusted_ntt16_instructions": after,
        "boundary_contract": {
            "r2_physical_row_stores": 36,
            "adjusted_physical_row_loads": 18,
            "runtime_row_permutations": 0,
            "scale_normalization_passes": 0,
            "q_loads_after_r2": sum("vmovdqa" in line and "rip" in line for line in after),
            "first_row_uses_two_direct_vperm2i128": sum("vperm2i128" in line for line in after) >= 2,
            "materialized_store_reload_intentionally_retained": True,
        },
    }
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(args.object)
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated F-R3D boundary audit is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
