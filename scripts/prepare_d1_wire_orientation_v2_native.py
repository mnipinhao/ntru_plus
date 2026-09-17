#!/usr/bin/env python3
"""Install the D1-orientation Forward as a non-overwriting native candidate."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from supercop_workflow import read_lock, sha256_file


REPO = Path(__file__).resolve().parent.parent
EXPERIMENT = REPO / (
    "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
    "experiments/avx2_gt9x16_official_001"
)
OLD_SYMBOL = (
    "ntruplus1152_exp001_gt9x16_prod3_aos_full_"
    "wire_monotone_scale1_lazy_reduce"
)
NEW_SYMBOL = OLD_SYMBOL + "_d1v2"


def flatten(source: Path, destination: Path) -> None:
    destination.write_text(
        source.read_text().replace('"generated/', '"').replace('"asm/', '"'),
        encoding="utf-8",
    )


def checksums(directory: Path) -> None:
    files = sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.name != "SHA256SUMS"
    )
    (directory / "SHA256SUMS").write_text(
        "\n".join(f"{sha256_file(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--source-implementation", required=True)
    parser.add_argument("--implementation", required=True)
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

    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    installed = manifest["wire_monotone_native_rebase2"]["installed_sources"]
    forward_path = destination / installed["forward"]
    flatten(
        EXPERIMENT / "asm/gt9x16_prod3_aos_h4_scale1_lazy_reduce_wire_d1v2.S",
        forward_path,
    )
    flatten(
        EXPERIMENT / "asm/gt9x16_prod3_aos_branch0.S",
        destination / "gt9x16_prod3_aos_branch0.S",
    )
    for filename in (
        "d1-wire-orientation-v2-controls.inc",
        "d1-wire-orientation-v2-twiddles.inc",
    ):
        shutil.copy2(EXPERIMENT / "generated" / filename, destination / filename)

    kem_path = destination / "kem.c"
    kem_text = kem_path.read_text(encoding="utf-8")
    if kem_text.count(OLD_SYMBOL) != 2:
        raise SystemExit("unexpected Forward call count in installed kem.c")
    kem_path.write_text(kem_text.replace(OLD_SYMBOL, NEW_SYMBOL), encoding="utf-8")

    header_path = destination / "wire-monotone-kem.h"
    header_text = header_path.read_text(encoding="utf-8")
    if OLD_SYMBOL not in header_text:
        raise SystemExit("missing Forward declaration in wire-monotone-kem.h")
    header_path.write_text(
        header_text.replace(OLD_SYMBOL, NEW_SYMBOL), encoding="utf-8"
    )

    manifest["d1_wire_orientation_v2"] = {
        "source_implementation": source.name,
        "forward_symbol": NEW_SYMBOL,
        "semantic_wire_abi": "unchanged",
        "selected_tiles": [2, 16],
        "linked_vpshufb": "56 -> 48",
        "benchmark_policy": "native SUPERCOP only",
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checksums(destination)
    print(f"installed {args.implementation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
