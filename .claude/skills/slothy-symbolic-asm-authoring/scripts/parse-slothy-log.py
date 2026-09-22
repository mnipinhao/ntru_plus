#!/usr/bin/env python3
"""Parse Slothy logs into a small JSON result used by scoring gates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CYCLE_RE = re.compile(
    r"(?i)(?:expected\s+cycles|cycle\s+count|cycles|estimated\s+performance|objective)[^0-9]{0,40}([0-9]+(?:\.[0-9]+)?)"
)
OUTPUT_RE = re.compile(r"(?i)(?:write|wrote|output|saved).*?([A-Za-z0-9_./-]+\.(?:s|S|asm))")
BAD_RE = re.compile(r"(?i)(traceback|error|exception|unsat|infeasible|failed|timeout)")
GOOD_RE = re.compile(r"(?i)(success|optimal|optimized|solution|result)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log")
    args = parser.parse_args()

    path = Path(args.log)
    if not path.is_file():
        print(f"parse-slothy-log: error: log not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(errors="replace")
    cycles = [float(match.group(1)) for match in CYCLE_RE.finditer(text)]
    outputs = sorted(set(match.group(1) for match in OUTPUT_RE.finditer(text)))
    bad = sorted(set(match.group(1).lower() for match in BAD_RE.finditer(text)))
    good = sorted(set(match.group(1).lower() for match in GOOD_RE.finditer(text)))

    if bad:
        status = "fail"
    elif cycles or good:
        status = "pass"
    else:
        status = "unknown"

    result = {
        "log": str(path),
        "slothy_status": status,
        "expected_cycles_best": min(cycles) if cycles else None,
        "expected_cycles_all": cycles,
        "outputs": outputs,
        "signals": {"good": good, "bad": bad},
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
