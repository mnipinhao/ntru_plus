#!/usr/bin/env python3
"""Install the H3 pair-unpack native candidate without overwriting its source."""

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
OLD_SYMBOL = "ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire"
NEW_SYMBOL = "ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire_pairunpack"


def checksums(directory: Path) -> None:
    files = sorted(path for path in directory.iterdir()
                   if path.is_file() and path.name != "SHA256SUMS")
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
    installed = manifest.get("wire_monotone_native_rebase2", {}).get(
        "installed_sources", {})
    old_h4 = installed.get("h4_egress")
    if not old_h4 or not (destination / old_h4).is_file():
        raise SystemExit("source implementation does not expose its H4 source")
    (destination / old_h4).unlink()

    candidate_name = "zz_native_52_h4_pairunpack.S"
    candidate = (EXPERIMENT / "asm/encap_h4_m3b_exact_egress_wire_pairunpack.S")
    text = candidate.read_text(encoding="utf-8")
    text = text.replace('"generated/', '"').replace('"asm/', '"')
    if text.count(NEW_SYMBOL) < 3:
        raise SystemExit("candidate H4 symbol was not found")
    text = text.replace(NEW_SYMBOL, OLD_SYMBOL)
    (destination / candidate_name).write_text(text, encoding="utf-8")

    installed["h4_egress"] = candidate_name
    manifest["h3_pairunpack_native"] = {
        "source_implementation": source.name,
        "installed_source": candidate_name,
        "semantic_change": "none",
        "machine_change": (
            "form both adjacent-p h planes with two word-unpacks and two "
            "half-selects; remove 216 H3 routing instructions"
        ),
        "caller": "unchanged cumulative scale-1 wire-monotone encapsulation",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    checksums(destination)
    print(f"installed {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
