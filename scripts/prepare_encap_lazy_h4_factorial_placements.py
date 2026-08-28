#!/usr/bin/env python3
"""Install non-overwriting Lazy x H4 2x2 price implementations."""
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
    for prefix in ('"generated/', '"asm/'):
        text = text.replace(prefix, '"')
    destination.write_text(text)


def install(source: Path, destination: Path, placement: str) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)

    # Reposition every hot function used by the four cells; the mathematical
    # source remains identical between normal and reversed implementations.
    existing_h1 = destination / "gt9x16_prod3_ma2_qorder_natural.S"
    existing_h3 = list(destination.glob("*_encap_h_ingress_ma2_h3.S"))
    if not existing_h1.is_file() or len(existing_h3) != 1:
        raise SystemExit("source implementation lacks unique H1/H3 sources")
    existing_h1.unlink()
    existing_h3[0].unlink()

    # The H3-price source predates both scale-1 and the lazy mask. Replace only
    # the shared forward template/constants with the already-qualified current
    # experiment versions; wrappers below select the four distinct symbols.
    flatten_asm(EXPERIMENT / "asm/gt9x16_prod3_aos_branch0.S",
                destination / "gt9x16_prod3_aos_branch0.S")
    for name in ("gt9x16-ntt16-constants.inc",
                 "gt9x16-prod3-natural-q-t0-beta-constants.inc",
                 "encap-h4-m3-scale1-producer-constants.inc"):
        shutil.copy2(EXPERIMENT / "generated" / name, destination / name)

    sources = {
        "h1": EXPERIMENT / "asm/gt9x16_prod3_ma2_qorder_natural.S",
        "h3": EXPERIMENT / "asm/encap_h_ingress_ma2_h3.S",
        "c00_forward": EXPERIMENT / "asm/gt9x16_prod3_aos_t0_beta.S",
        "c10_forward": EXPERIMENT / "asm/gt9x16_prod3_aos_t0_beta_lazy_reduce.S",
        "c01_forward": EXPERIMENT / "asm/gt9x16_prod3_aos_h4_scale1.S",
        "c11_forward":
            EXPERIMENT / "asm/gt9x16_prod3_aos_h4_scale1_lazy_reduce.S",
        "h4": EXPERIMENT / "asm/encap_h4_m3b_exact_egress.S",
    }
    order = (["h1", "h3", "c00_forward", "c10_forward", "c01_forward",
              "c11_forward", "h4"] if placement == "normal" else
             ["h4", "c11_forward", "c01_forward", "c10_forward",
              "c00_forward", "h3", "h1"])
    installed_sources = {}
    prefix = "zz_factorial" if placement == "normal" else "aa_factorial"
    for number, role in enumerate(order, 10):
        installed = f"{prefix}_{number:02d}_{role}.S"
        flatten_asm(sources[role], destination / installed)
        installed_sources[role] = installed

    for name in ("encap-h4-m3b-exact-egress.h",
                 "encap-h-ingress-ma2-h3.h",
                 "gt9x16-prod3-ma2-qorder-natural-asm.h"):
        shutil.copy2(EXPERIMENT / "generated" / name, destination / name)

    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["implementation"] = destination.name
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["encap_lazy_h4_factorial_price"] = {
        "placement": placement,
        "source_implementation": source.name,
        "installed_sources": installed_sources,
        "boundary": "coefficient-domain small r/m plus valid PK bytes to exact ciphertext",
        "cells": {
            "C00": "scale4 current forward plus H3 plus direct H1",
            "C10": "scale4 lazy forward plus H3 plus direct H1",
            "C01": "scale1 current forward plus H4-M3B",
            "C11": "scale1 lazy forward plus H4-M3B",
        },
        "excluded": "r hash fanout, hash_g, SOTP, native KEM",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (destination / "LAZY-H4-FACTORIAL-PLACEMENT.json").write_text(
        json.dumps(manifest["encap_lazy_h4_factorial_price"],
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
    print("installed Lazy x H4 factorial normal/reversed implementations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
