#!/usr/bin/env python3
"""Install the frozen cumulative PROD3 KEM into a disposable SUPERCOP tree."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import read_lock, sha256_file

EXPERIMENT_REL = Path(
    "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
    "experiments/avx2_gt9x16_official_001"
)


def flatten(text: str) -> str:
    return text.replace('"generated/', '"').replace('.include "generated/', '.include "')


def rewrite_checksums(directory: Path) -> None:
    lines = [
        f"{sha256_file(path)}  {path.name}"
        for path in sorted(directory.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name != "SHA256SUMS"
    ]
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--source-implementation", required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--producer", choices=("natural", "t0-beta"),
                        default="t0-beta")
    args = parser.parse_args()

    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit(f"not a disposable SUPERCOP campaign: {root}")
    campaign = json.loads(marker.read_text(encoding="utf-8"))
    if campaign.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("campaign marker has the wrong kind")
    if campaign.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign version does not match bench/supercop.lock")

    repo = Path(__file__).resolve().parent.parent
    experiment = repo / EXPERIMENT_REL
    base = root / "crypto_kem/ntruplus1152"
    source = base / args.source_implementation
    destination = base / args.implementation
    if not source.is_dir():
        raise SystemExit(f"missing source implementation: {source}")
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)

    overlays = {
        "kem.c": experiment / "src/kem_cumulative_native.c",
        "gt9x16_prod3_aos_branch0.S": experiment / "asm/gt9x16_prod3_aos_branch0.S",
        "gt9x16_prod3_aos_t0_beta.S": experiment / "asm/gt9x16_prod3_aos_t0_beta.S",
        "gt9x16_prod3_aos_natural.S": experiment / "asm/gt9x16_prod3_aos_natural.S",
        "gt9x16_prod3_ma2_qorder_natural.S": experiment / "asm/gt9x16_prod3_ma2_qorder_natural.S",
        "gt9x16_prod3_cumulative_ma2.S": experiment / "asm/gt9x16_prod3_cumulative_ma2.S",
        "gt9x16-prod3-natural-q-t0-beta-constants.inc":
            experiment / "generated/gt9x16-prod3-natural-q-t0-beta-constants.inc",
        "gt9x16-prod3-ma2-qorder-natural-constants.inc":
            experiment / "generated/gt9x16-prod3-ma2-qorder-natural-constants.inc",
        "gt9x16-prod3-ma2-qorder-natural-asm.h":
            experiment / "generated/gt9x16-prod3-ma2-qorder-natural-asm.h",
        "gt9x16-prod3-cumulative-ma2.h":
            experiment / "generated/gt9x16-prod3-cumulative-ma2.h",
        "gt9x16_prod3_aos_full.h": experiment / "src/gt9x16_prod3_aos_full.h",
    }
    for name, source_path in overlays.items():
        (destination / name).write_text(
            flatten(source_path.read_text(encoding="utf-8")), encoding="utf-8"
        )
    if args.producer == "natural":
        kem_path = destination / "kem.c"
        kem_path.write_text(
            kem_path.read_text(encoding="utf-8").replace(
                "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(",
                "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q(",
            ),
            encoding="utf-8",
        )

    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["implementation"] = args.implementation
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["cumulative_native_rebase"] = {
        "source_implementation": args.source_implementation,
        "persistent_aos": True,
        "qorder": "C1-natural-Q",
        "t0_beta": args.producer == "t0-beta",
        "producer": args.producer,
            "ma2": "natural-Q scale-4 coefficient planes consumed by direct H1",
        "hash_serializer": "direct H1 natural-Q",
        "encap_call_graph": {
            "producer_calls": 2,
            "ma2_calls": 1,
            "direct_h1_calls": 2,
            "old_recovery_bridge_calls": 0,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    rewrite_checksums(destination)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
