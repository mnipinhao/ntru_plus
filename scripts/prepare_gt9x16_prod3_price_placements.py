#!/usr/bin/env python3
"""Prepare reproducible normal/reversed archive placement for PROD3 PRICE."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import sha256_file

CONTROL_SOURCE = "f0_prod2_ma2_p2b.S"
CANDIDATE_SOURCE = "gt9x16_prod3_aos_full_price.S"


def rewrite_checksums(directory: Path) -> None:
    lines = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "SHA256SUMS":
            lines.append(f"{sha256_file(path)}  {path.name}")
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare(directory: Path, placement: str) -> None:
    manifest_path = directory / "SOURCE-MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit(f"missing candidate manifest: {manifest_path}")
    placement_path = directory / "PLACEMENT.json"
    if placement_path.exists():
        raise SystemExit(f"refusing to overwrite {placement_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    overlays = manifest["installed_overlays"]
    if placement == "normal":
        source_names = {"control": CONTROL_SOURCE, "candidate": CANDIDATE_SOURCE}
    else:
        renamed = {
            CONTROL_SOURCE: "zz_f0_prod2_ma2_p2b.S",
            CANDIDATE_SOURCE: "aa_gt9x16_prod3_aos_full_price.S",
        }
        for old, new in renamed.items():
            source = directory / old
            destination = directory / new
            if not source.is_file() or destination.exists():
                raise SystemExit(f"cannot apply reversed placement rename {old} -> {new}")
            source.rename(destination)
            overlays[new] = overlays.pop(old)
        source_names = {
            "control": renamed[CONTROL_SOURCE],
            "candidate": renamed[CANDIDATE_SOURCE],
        }
    placement_record = {
        "archive_order_control": source_names["control"],
        "archive_order_candidate": source_names["candidate"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "method": "flat-source filename order before SUPERCOP okar",
        "placement": placement,
    }
    manifest["prod3_price_placement"] = placement_record
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    placement_path.write_text(
        json.dumps(placement_record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    rewrite_checksums(directory)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--normal-implementation", required=True)
    parser.add_argument("--reversed-implementation", required=True)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit(f"not a disposable SUPERCOP campaign: {root}")
    base = root / "crypto_kem" / "ntruplus1152"
    prepare(base / args.normal_implementation, "normal")
    prepare(base / args.reversed_implementation, "reversed")
    print("prepared PROD3 PRICE normal/reversed placement controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
