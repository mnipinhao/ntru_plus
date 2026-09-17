#!/usr/bin/env python3
"""Install Serializer V2 into a new disposable SUPERCOP implementation."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from supercop_workflow import read_lock, sha256_file

REPO = Path(__file__).resolve().parent.parent
EXP = REPO / ("ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
              "NTRU+1152/experiments/avx2_gt9x16_official_001")


def checksums(directory: Path) -> None:
    files = sorted(path for path in directory.iterdir()
                   if path.is_file() and path.name != "SHA256SUMS")
    (directory / "SHA256SUMS").write_text(
        "\n".join(f"{sha256_file(path)}  {path.name}" for path in files) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--source-implementation", required=True)
    parser.add_argument("--implementation", required=True)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker = json.loads((root / ".ntruplus-campaign.json").read_text())
    if marker.get("kind") != "disposable-supercop-campaign" or marker.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign marker/lock mismatch")
    base = root / "crypto_kem/ntruplus1152"
    source, destination = base / args.source_implementation, base / args.implementation
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)
    installed = destination / "zz_serializer_v2.S"
    shutil.copy2(EXP / "asm/scale1_r_serializer_v2.S", installed)
    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["scale1_r_serializer_v2"] = {
        "source_implementation": source.name,
        "installed_source": installed.name,
        "boundary": "materialized wire-monotone scale-1 state to exact 1728 bytes",
        "native_caller_changed": False,
        "purpose": "SUPERCOP-derived boundary-only pricing",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    checksums(destination)
    print(f"installed {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
