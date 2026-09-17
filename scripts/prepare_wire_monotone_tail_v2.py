#!/usr/bin/env python3
"""Install a non-overwriting exp006 clone with the standalone wire H3 probe."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import read_lock, sha256_file


REPO = Path(__file__).resolve().parent.parent
EXPERIMENT = REPO / (
    "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
    "experiments/avx2_gt9x16_official_001")


def rewrite_checksums(directory: Path) -> None:
    files = sorted(p for p in directory.iterdir()
                   if p.is_file() and p.name != "SHA256SUMS")
    (directory / "SHA256SUMS").write_text(
        "\n".join(f"{sha256_file(p)}  {p.name}" for p in files) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--source-implementation", required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--pair-unpack", action="store_true")
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker = json.loads((root / ".ntruplus-campaign.json").read_text())
    if marker.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("target is not a disposable SUPERCOP campaign")
    if marker.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign lock mismatch")
    base = root / "crypto_kem/ntruplus1152"
    source = base / args.source_implementation
    destination = base / args.implementation
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)

    h3_name = ("encap_h_ingress_ma2_h3_wire_pairunpack.S"
               if args.pair_unpack else "encap_h_ingress_ma2_h3_wire.S")
    h3 = (EXPERIMENT / "asm" / h3_name).read_text()
    if args.pair_unpack:
        h3 = h3.replace(
            "ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire_pairunpack",
            "ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire")
    h3 = h3.replace('"generated/', '"').replace('"asm/', '"')
    installed = destination / "zz_tailv2_50_h3_wire.S"
    installed.write_text(h3)

    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["implementation"] = args.implementation
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["wire_monotone_tail_attribution_v2"] = {
        "source_implementation": args.source_implementation,
        "added_source": installed.name,
        "formation": "pair-unpack" if args.pair_unpack else "mask",
        "purpose": "derived T0/T1/T2 attribution only; Native caller unchanged",
        "t0": "Official poly_frombytes versus materialized Natural-Q ingress proxy",
        "t1": "PK bytes through streaming wire H3/MA2 raw output",
        "t2": "PK bytes through wire H3/MA2/H4 exact ciphertext",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    rewrite_checksums(destination)
    print(f"installed {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
