#!/usr/bin/env python3
"""Install the scale-1 r dual-output fanout diagnostic in a disposable tree."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from supercop_workflow import read_lock, sha256_file


REPO = Path(__file__).resolve().parent.parent
EXP = REPO / ("ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
              "NTRU+1152/experiments/avx2_gt9x16_official_001")


def flatten(source: Path, destination: Path) -> None:
    destination.write_text(source.read_text().replace('"generated/', '"').replace('"asm/', '"'))


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
    # The dual-output tile map is a live-register ABI, not merely a mapping of
    # the materialized Forward output.  Install the exact branch template from
    # which the map was generated; an older template can produce the same
    # stored state while assigning the terminal values to different YMMs.
    flatten(EXP / "asm/gt9x16_prod3_aos_branch0.S",
            destination / "gt9x16_prod3_aos_branch0.S")
    flatten(EXP / "asm/gt9x16_prod3_aos_scale1_dual_r.S",
            destination / "zz_dual_r_60_forward_serializer.S")
    flatten(EXP / "generated/scale1-r-dual-output-tiles.inc",
            destination / "scale1-r-dual-output-tiles.inc")
    shutil.copy2(EXP / "src/scale1_r_dual_output_fanout.c",
                 destination / "scale1_r_dual_output_fanout.c")
    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["scale1_r_dual_output_fanout"] = {
        "source_implementation": source.name,
        "purpose": "SUPERCOP-derived full hash_g/SOTP caller-boundary pricing",
        "native_caller_changed": False,
        "removed_seam": "72 serializer reloads",
        "live_register_template_sha256": sha256_file(
            EXP / "asm/gt9x16_prod3_aos_branch0.S"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    checksums(destination)
    print(f"installed {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
