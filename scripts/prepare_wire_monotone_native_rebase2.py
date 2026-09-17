#!/usr/bin/env python3
"""Install complete wire-monotone KEM candidates in a disposable campaign."""

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


def flatten(source: Path, destination: Path) -> None:
    destination.write_text(
        source.read_text().replace('"generated/', '"').replace('"asm/', '"'),
        encoding="utf-8",
    )


def checksums(directory: Path) -> None:
    files = sorted(path for path in directory.iterdir()
                   if path.is_file() and path.name != "SHA256SUMS")
    (directory / "SHA256SUMS").write_text(
        "\n".join(f"{sha256_file(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def install(source: Path, destination: Path, placement: str) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)
    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    old = manifest.get("wire_monotone_shared_abi", {}).get("installed_sources", {})
    for filename in old.values():
        path = destination / filename
        if path.is_file():
            path.unlink()

    prefix = "aa_native" if placement == "reversed" else "zz_native"
    roles = [
        ("forward", EXPERIMENT / "asm/gt9x16_prod3_aos_h4_scale1_lazy_reduce_wire.S"),
        ("r_serializer", EXPERIMENT / "asm/direct_serializer_wire.S"),
        ("h4_egress", EXPERIMENT / "asm/encap_h4_m3b_exact_egress_wire.S"),
    ]
    if placement == "reversed":
        roles.reverse()
    installed = {}
    for index, (role, source_path) in enumerate(roles, 40):
        filename = f"{prefix}_{index:02d}_{role}.S"
        flatten(source_path, destination / filename)
        installed[role] = filename

    flatten(EXPERIMENT / "asm/gt9x16_prod3_aos_branch0.S",
            destination / "gt9x16_prod3_aos_branch0.S")
    shutil.copy2(EXPERIMENT / "src/kem_wire_cumulative_native.c",
                 destination / "kem.c")
    shutil.copy2(EXPERIMENT / "generated/wire-monotone-kem.h",
                 destination / "wire-monotone-kem.h")
    for filename in (
        "d1-wire-monotone-absorption.inc",
        "gt9x16-prod3-ma2-wire-monotone-constants.inc",
    ):
        shutil.copy2(EXPERIMENT / "generated" / filename, destination / filename)

    manifest["wire_monotone_native_rebase2"] = {
        "placement": placement,
        "source_implementation": source.name,
        "installed_sources": installed,
        "kem": "wire-monotone scale-1 lazy forward + direct r serializer + H3/MA2 + H4 exact egress",
        "keypair_and_decap": "unchanged pinned upstream paths",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    checksums(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--normal-source", required=True)
    parser.add_argument("--reversed-source", required=True)
    parser.add_argument("--normal-implementation", required=True)
    parser.add_argument("--reversed-implementation", required=True)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker = json.loads((root / ".ntruplus-campaign.json").read_text())
    if marker.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("target is not a disposable SUPERCOP campaign")
    if marker.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign lock mismatch")
    base = root / "crypto_kem/ntruplus1152"
    install(base / args.normal_source, base / args.normal_implementation, "normal")
    install(base / args.reversed_source, base / args.reversed_implementation, "reversed")
    print("installed complete wire-monotone native rebase2 candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
