#!/usr/bin/env python3
"""Install non-overwriting H3-price normal/reversed SUPERCOP implementations."""
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


def install(source: Path, destination: Path, placement: str) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)
    # The attribution placement clone retains a historical include-wrapper
    # whose branch source was renamed by that campaign.  It is not part of the
    # cumulative caller and cannot compile as a flat SUPERCOP source.  Omit it
    # from this new non-overwriting implementation rather than editing either
    # source implementation.
    omitted = []
    for name in ("gt9x16_prod3_aos_full_price.S",):
        path = destination / name
        if path.exists():
            path.unlink()
            omitted.append(name)
    additions = {
        "encap_h_decode_natural_q_h1.S": EXPERIMENT / "asm/encap_h_decode_natural_q_h1.S",
        "encap_h_ingress_ma2_h3.S": EXPERIMENT / "asm/encap_h_ingress_ma2_h3.S",
        "encap-h-decode-natural-q-asm.h": EXPERIMENT / "generated/encap-h-decode-natural-q-asm.h",
        "encap-h-ingress-ma2-h3.h": EXPERIMENT / "generated/encap-h-ingress-ma2-h3.h",
    }
    asm_names = list(additions)[:2]
    if placement == "normal":
        installed_names = {asm_names[0]: "zz4_" + asm_names[0],
                           asm_names[1]: "zz5_" + asm_names[1]}
    else:
        installed_names = {asm_names[0]: "aa5_" + asm_names[0],
                           asm_names[1]: "aa4_" + asm_names[1]}
    for name, source_path in additions.items():
        installed = installed_names.get(name, name)
        shutil.copy2(source_path, destination / installed)
        if name.endswith(".S"):
            # Experiment assembly includes generated constants through the
            # repository layout.  A SUPERCOP implementation is deliberately
            # flat, so point those two includes at the already-installed flat
            # constant files without changing the experiment source.
            installed_path = destination / installed
            text = installed_path.read_text()
            text = text.replace(
                '"generated/f0-ma2-constants.inc"',
                '"f0-ma2-constants.inc"',
            ).replace(
                '"generated/gt9x16-prod3-ma2-qorder-natural-constants.inc"',
                '"gt9x16-prod3-ma2-qorder-natural-constants.inc"',
            )
            installed_path.write_text(text)

    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["implementation"] = destination.name
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["encap_h_ingress_ma2_h3_price"] = {
        "placement": placement,
        "source_implementation": source.name,
        "added_sources": installed_names,
        "omitted_obsolete_sources": omitted,
        "boundary": "PK bytes to raw Natural-Q scale-4 MA2 output",
        "variants": ["current cumulative", "H1 materialized", "H3 streaming"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (destination / "H3-PRICE-PLACEMENT.json").write_text(
        json.dumps(manifest["encap_h_ingress_ma2_h3_price"],
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
    print("installed H3-price normal/reversed implementations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
