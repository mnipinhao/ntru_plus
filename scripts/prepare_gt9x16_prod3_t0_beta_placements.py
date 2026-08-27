#!/usr/bin/env python3
"""Clone frozen Natural-Q implementations and add T0-beta placement controls."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import sha256_file

EXPERIMENT_REL = Path(
    "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
    "experiments/avx2_gt9x16_official_001")


def rewrite_checksums(directory: Path) -> None:
    lines = [f"{sha256_file(path)}  {path.name}"
             for path in sorted(directory.iterdir(), key=lambda item: item.name)
             if path.is_file() and path.name != "SHA256SUMS"]
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def flatten(text: str) -> str:
    return text.replace('"generated/', '"').replace('.include "generated/',
                                                        '.include "')


def install(source: Path, destination: Path, experiment: Path,
            placement: str) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)
    (destination / "PLACEMENT.json").unlink(missing_ok=True)
    candidate_name = ("zz_gt9x16_prod3_aos_t0_beta.S"
                      if placement == "normal"
                      else "aa0_gt9x16_prod3_aos_t0_beta.S")
    overlays = {
        "gt9x16_prod3_aos_branch0.S":
            experiment / "asm/gt9x16_prod3_aos_branch0.S",
        candidate_name: experiment / "asm/gt9x16_prod3_aos_t0_beta.S",
        "gt9x16-prod3-natural-q-t0-beta-constants.inc":
            experiment / "generated/gt9x16-prod3-natural-q-t0-beta-constants.inc",
    }
    for name, source_path in overlays.items():
        (destination / name).write_text(flatten(source_path.read_text()))
    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["implementation"] = destination.name
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    record = {
        "placement": placement,
        "control": "frozen Natural-Q PROD3",
        "candidate": candidate_name,
        "semantic_abi": "Natural-Q scale-4; raw representative may differ",
        "schedule_taxonomy": {
            "constant_operands": [666, 650],
            "estimated_rodata_delta_bytes": 448,
        },
        "linked_taxonomy": {
            "constant_operands": [594, 578],
            "actual_rodata_delta_bytes": 416,
        },
        "taxonomy_note": (
            "absolute baselines differ by schedule taxonomy and linker retained "
            "set; the -16 operand direction agrees"),
    }
    manifest["t0_beta_price"] = record
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (destination / "PLACEMENT.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    rewrite_checksums(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--source-normal", required=True)
    parser.add_argument("--source-reversed", required=True)
    parser.add_argument("--normal-implementation", required=True)
    parser.add_argument("--reversed-implementation", required=True)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    if not (root / ".ntruplus-campaign.json").is_file():
        raise SystemExit(f"not a disposable SUPERCOP campaign: {root}")
    experiment = Path(__file__).resolve().parent.parent / EXPERIMENT_REL
    base = root / "crypto_kem/ntruplus1152"
    install(base / args.source_normal, base / args.normal_implementation,
            experiment, "normal")
    install(base / args.source_reversed, base / args.reversed_implementation,
            experiment, "reversed")
    print("prepared Natural-Q T0-beta normal/reversed implementations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
