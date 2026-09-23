#!/usr/bin/env python3
"""Fixed-ELF paired ABBA/BAAB run for ONE placement with ASLR on only.

Methodology decision (2026-09-23): production evidence is taken with ASLR
on; no ASLR-off setting is run and `setarch -R` is never used.  Normal
placement is the primary setting, reversed placement a secondary robustness
check.  This is scripts/run_supercop_paired.py restricted to one placement,
ASLR on, and a configurable block count (the formal script fixes 16 blocks
and always runs the four placement x ASLR settings).  The launch, ELF
inspection and observation-count checks are imported from that script.

Block b uses order official,candidate,candidate,official for odd b and
candidate,official,official,candidate for even b; every launch is a fresh
process pinned with taskset.  The manifest has the same layout as the formal
one (setting name `<placement>-aslr-on`), so scripts/summarize_supercop_paired.py
summarises it unchanged.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from run_supercop_paired import DEFAULT_OPERATIONS, elf_info, launch  # noqa: E402
from supercop_workflow import LOCK_PATH, read_lock  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--placement", choices=("normal", "reversed"), required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--blocks", type=int, default=48)
    parser.add_argument("--compiler-recipe", required=True)
    parser.add_argument("--minimum-observations", type=int, default=96)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.blocks < 2 or args.blocks % 2:
        raise SystemExit("--blocks must be a positive even number (ABBA/BAAB balance)")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    if Path("/proc/sys/kernel/randomize_va_space").read_text().strip() == "0":
        raise SystemExit("ASLR-on run requested but kernel randomize_va_space is 0")
    pair = {"official": args.official, "candidate": args.candidate}
    info = {name: elf_info(path) for name, path in pair.items()}
    if info["official"]["sha256"] == info["candidate"]["sha256"]:
        raise SystemExit("official and candidate ELFs are identical")
    args.output.mkdir(parents=True)
    setting = f"{args.placement}-aslr-on"
    setting_dir = args.output / setting
    setting_dir.mkdir()
    records = []
    for block in range(1, args.blocks + 1):
        order = ("official", "candidate", "candidate", "official") if block % 2 else (
            "candidate", "official", "official", "candidate")
        for slot, implementation in enumerate(order, 1):
            output, counts = launch(pair[implementation], args.cpu, False,
                                    DEFAULT_OPERATIONS, args.minimum_observations)
            filename = f"block-{block:02d}-slot-{slot}-{implementation}.out"
            (setting_dir / filename).write_text(output, encoding="utf-8")
            records.append({"setting": setting, "block": block, "slot": slot,
                            "implementation": implementation, "file": f"{setting}/{filename}",
                            "observations": counts})
    manifest = {
        **read_lock(),
        "benchmark_class": "fixed-elf-paired",
        "variant": "single-placement-aslr-on",
        "aslr": "on (kernel randomize_va_space=2; no setarch -R)",
        "placement": args.placement,
        "blocks": args.blocks,
        "compiler_recipe": args.compiler_recipe,
        "cpu": args.cpu,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "operations": list(DEFAULT_OPERATIONS),
        "observations_per_operation_per_launch_minimum": args.minimum_observations,
        "binaries": {args.placement: info},
        "launches": records,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                               encoding="utf-8")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(f"completed {setting} paired run, {args.blocks} blocks: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
