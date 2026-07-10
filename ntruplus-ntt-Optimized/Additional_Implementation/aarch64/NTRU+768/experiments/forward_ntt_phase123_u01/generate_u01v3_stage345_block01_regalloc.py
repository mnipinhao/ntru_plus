#!/usr/bin/env python3
"""Gate for U01v3 stage345 block01 regalloc ASM generation.

The first-wave search intentionally emits no primary ASM unless a candidate is
marked correctness-safe in u01v3_stage345_block01_regalloc_candidates.json.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CANDIDATES = ROOT / "u01v3_stage345_block01_regalloc_candidates.json"
OUT_MAP = ROOT / "u01v3_stage345_block01_regalloc_map.json"
OUT_RESULT = ROOT / "u01v3_stage345_block01_regalloc_result.md"


def main() -> int:
    data = json.loads(CANDIDATES.read_text())
    emitted = []
    skipped = []
    for candidate in data["candidates"]:
        if candidate["emit_asm_in_first_wave"]:
            emitted.append(candidate["name"])
        else:
            skipped.append(
                {
                    "name": candidate["name"],
                    "status": candidate["status"],
                    "reason": candidate["reason"],
                }
            )

    OUT_MAP.write_text(
        json.dumps(
            {
                "candidate_family": "u01v3_stage345_block01_regalloc",
                "production_default_changed": False,
                "first_wave_emitted_asm": emitted,
                "skipped": skipped,
                "note": "No R01 primary ASM is emitted until the semantic search marks a candidate correctness-safe.",
            },
            indent=2,
        )
        + "\n"
    )
    OUT_RESULT.write_text(
        "# U01v3 Stage345 Block01 Regalloc Result\n\n"
        "Date: 2026-07-09\n\n"
        "Status: first-wave semantic search completed.  No primary R01 ASM was "
        "emitted because no candidate is correctness-safe at the semantic-regalloc "
        "level yet.\n\n"
        "Summary:\n\n"
        "```text\n"
        "R01a delayed-produce: infeasible; requires raw q reload or duplicate Stage12\n"
        "R01b keep block1 live: plausible, but needs a verified semantic Stage345 block0 DAG emitter\n"
        "R01c consumer-shaped producer: blocked by overlapping consumer contracts\n"
        "R01d minimal move bridge: infeasible with current block0 allocation\n"
        "```\n\n"
        "The important result is that the next useful implementation is not another "
        "physical register patch.  It is a Stage345 block0 semantic DAG emitter with "
        "a register allocator that can be checked before assembly is generated.\n"
    )
    print(OUT_MAP)
    print(OUT_RESULT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
