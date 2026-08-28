#!/usr/bin/env python3
"""Install non-overwriting H4-M3B price implementations in a campaign."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import read_lock, sha256_file


REPO_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT = (REPO_ROOT / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
              "NTRU+1152/experiments/avx2_gt9x16_official_001")


def rewrite_checksums(directory: Path) -> None:
    lines = [
        f"{sha256_file(path)}  {path.name}"
        for path in sorted(directory.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name != "SHA256SUMS"
    ]
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def flatten_asm(source: Path, destination: Path) -> None:
    text = source.read_text()
    text = text.replace(
        '"generated/f0-ma2-constants.inc"',
        '"f0-ma2-constants.inc"',
    ).replace(
        '"generated/gt9x16-prod3-ma2-qorder-natural-constants.inc"',
        '"gt9x16-prod3-ma2-qorder-natural-constants.inc"',
    )
    destination.write_text(text)


def install(source: Path, destination: Path, placement: str) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)
    additions = {
        "encap-h4-m3.h": EXPERIMENT / "generated/encap-h4-m3.h",
        "encap-h4-m3b-exact-egress.h":
            EXPERIMENT / "generated/encap-h4-m3b-exact-egress.h",
    }
    if placement == "normal":
        asm_names = {
            "encap_h4_m3.S": "zz6_encap_h4_m3.S",
            "encap_h4_m3b_exact_egress.S": "zz7_encap_h4_m3b_exact_egress.S",
        }
    else:
        asm_names = {
            "encap_h4_m3b_exact_egress.S": "aa2_encap_h4_m3b_exact_egress.S",
            "encap_h4_m3.S": "aa3_encap_h4_m3.S",
        }
    for name, installed in asm_names.items():
        flatten_asm(EXPERIMENT / "asm" / name, destination / installed)
    for name, source_path in additions.items():
        shutil.copy2(source_path, destination / name)

    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["implementation"] = destination.name
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["encap_h4_m3b_price"] = {
        "placement": placement,
        "source_implementation": source.name,
        "added_sources": asm_names,
        "boundary": "valid PK plus resident scale-1 r/m to exact ciphertext",
        "control": "H4-M3 canonical scratch plus Natural-Q H1 fallback",
        "candidate": "H4-M3B canonical scratch plus exact direct egress",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (destination / "H4-M3B-PRICE-PLACEMENT.json").write_text(
        json.dumps(manifest["encap_h4_m3b_price"],
                   indent=2, sort_keys=True) + "\n")
    rewrite_checksums(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--normal-source", required=True)
    parser.add_argument("--reversed-source", required=True)
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
    install(base / args.normal_source, base / args.normal_implementation, "normal")
    install(base / args.reversed_source, base / args.reversed_implementation, "reversed")
    print("installed H4-M3B-price normal/reversed implementations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
