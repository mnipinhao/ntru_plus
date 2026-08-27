#!/usr/bin/env python3
"""Clone the cumulative PROD3 implementation for attribution placement controls."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import read_lock, sha256_file


def rewrite_checksums(directory: Path) -> None:
    lines = [
        f"{sha256_file(path)}  {path.name}"
        for path in sorted(directory.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name != "SHA256SUMS"
    ]
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def relocate(directory: Path, placement: str) -> dict[str, str]:
    prefix = "zz" if placement == "normal" else "aa"
    sources = (
        "top_split_adapter.c",
        "gt9x16_prod3_aos_t0_beta.S",
        "gt9x16_prod3_cumulative_ma2.S",
        "gt9x16_prod3_ma2_qorder_natural.S",
    )
    renamed = {}
    for number, name in enumerate(sources):
        source = directory / name
        if not source.is_file():
            raise SystemExit(f"missing cumulative source {source}")
        destination = directory / f"{prefix}{number}_{name}"
        source.rename(destination)
        renamed[name] = destination.name
    return renamed


def install(source: Path, destination: Path, placement: str) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)
    renamed = relocate(destination, placement)
    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["implementation"] = destination.name
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["encap_caller_attribution_v2"] = {
        "placement": placement,
        "source_implementation": source.name,
        "relocated_sources": renamed,
        "candidate": (
            "persistent-AoS + Natural-Q + T0-beta + scale4 MA2 + Direct H1"
        ),
        "new_asm": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (destination / "PLACEMENT.json").write_text(
        json.dumps(manifest["encap_caller_attribution_v2"],
                   indent=2, sort_keys=True) + "\n"
    )
    rewrite_checksums(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--source-implementation", required=True)
    parser.add_argument("--normal-implementation", required=True)
    parser.add_argument("--reversed-implementation", required=True)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit(f"not a disposable SUPERCOP campaign: {root}")
    campaign = json.loads(marker.read_text())
    if campaign.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("campaign marker has the wrong kind")
    if campaign.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign version does not match bench/supercop.lock")
    base = root / "crypto_kem/ntruplus1152"
    source = base / args.source_implementation
    if not source.is_dir():
        raise SystemExit(f"missing source implementation: {source}")
    install(source, base / args.normal_implementation, "normal")
    install(source, base / args.reversed_implementation, "reversed")
    print("prepared cumulative attribution V2 normal/reversed implementations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
