#!/usr/bin/env python3
"""Install the D1 pair-resident fanout diagnostic in a disposable campaign."""

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
    text = source.read_text()
    destination.write_text(text.replace('"generated/', '"').replace('"asm/', '"'))


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
    if (marker.get("kind") != "disposable-supercop-campaign"
            or marker.get("supercop_version") != read_lock()["version"]):
        raise SystemExit("campaign marker/lock mismatch")

    base = root / "crypto_kem/ntruplus1152"
    source = base / args.source_implementation
    destination = base / args.implementation
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)

    flatten(EXP / "asm/gt9x16_prod3_aos_d1_pair_resident_v2.S",
            destination / "zz_d1_pair_resident_v2.S")
    for name in (
        "d1-wire-monotone-absorption.inc",
        "d1-pair-resident-v2-macros.inc",
        "gt9x16-ntt16-constants.inc",
        "gt9x16-prod3-natural-q-t0-beta-constants.inc",
        "encap-h4-m3-scale1-producer-constants.inc",
        "gt9x16-prod3-aos-branch0-constants.inc",
        "gt9x16-prod3-aos-branch1-constants.inc",
    ):
        flatten(EXP / "generated" / name, destination / name)
    shutil.copy2(EXP / "src/d1_pair_resident_v2_fanout.c",
                 destination / "scale1_r_dual_output_fanout.c")

    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["d1_pair_resident_v2_fanout"] = {
        "source_implementation": source.name,
        "purpose": "one short SUPERCOP-derived full hash_g/SOTP fanout diagnostic",
        "start": "coefficient-domain CBD1-compatible r",
        "end": "retained scale-1 wire state plus hash_g output plus SOTP m",
        "only_change": "Serializer V2 consumes final D1 pairs before their retained-state stores",
        "removed_boundary": "72 materialized-state serializer reloads",
        "native_caller_changed": False,
        "candidate_source_sha256": sha256_file(
            EXP / "asm/gt9x16_prod3_aos_d1_pair_resident_v2.S"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    checksums(destination)
    print(f"installed {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
