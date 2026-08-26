#!/usr/bin/env python3
"""Clone disposable PROD3 implementations and add H1 placement controls."""

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
    lines = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "SHA256SUMS":
            lines.append(f"{sha256_file(path)}  {path.name}")
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n",
                                             encoding="utf-8")


def clone(source: Path, destination: Path, asm_source: Path,
          header_source: Path, placement: str) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)
    old_placement = destination / "PLACEMENT.json"
    if old_placement.exists():
        old_placement.unlink()
    asm_name = ("gt9x16_prod3_ma2_hash_h1.S" if placement == "normal"
                else "aa_gt9x16_prod3_ma2_hash_h1.S")
    shutil.copy2(asm_source, destination / asm_name)
    shutil.copy2(header_source,
                 destination / "gt9x16-prod3-ma2-hash-h1.h")
    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["implementation"] = destination.name
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["installed_overlays"][asm_name] = (
        "asm/gt9x16_prod3_ma2_hash_h1.S")
    manifest["installed_overlays"]["gt9x16-prod3-ma2-hash-h1.h"] = (
        "generated/gt9x16-prod3-ma2-hash-h1.h")
    record = {
        "candidate_source": asm_name,
        "control_source": "f0_prod3_hash_bridge.c",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "method": "flat-source filename order before SUPERCOP okar",
        "placement": placement,
    }
    manifest["prod3_hash_h1_price_placement"] = record
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (destination / "PLACEMENT.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit(f"not a disposable SUPERCOP campaign: {root}")
    repo = Path(__file__).resolve().parent.parent
    experiment = repo / EXPERIMENT_REL
    asm_source = experiment / "asm/gt9x16_prod3_ma2_hash_h1.S"
    header_source = experiment / "generated/gt9x16-prod3-ma2-hash-h1.h"
    base = root / "crypto_kem/ntruplus1152"
    clone(base / args.source_normal, base / args.normal_implementation,
          asm_source, header_source, "normal")
    clone(base / args.source_reversed, base / args.reversed_implementation,
          asm_source, header_source, "reversed")
    print("prepared PROD3 H1 PRICE normal/reversed placement controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
