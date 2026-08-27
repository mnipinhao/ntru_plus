#!/usr/bin/env python3
"""Clone disposable implementations and install current/natural Q-order objects."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import sha256_file

EXPERIMENT_REL = Path("ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
                      "NTRU+1152/experiments/avx2_gt9x16_official_001")


def rewrite_checksums(directory: Path) -> None:
    lines = [f"{sha256_file(path)}  {path.name}"
             for path in sorted(directory.iterdir(), key=lambda item: item.name)
             if path.is_file() and path.name != "SHA256SUMS"]
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def flatten(text: str) -> str:
    return text.replace('"generated/', '"').replace('.include "generated/', '.include "')


def install(source: Path, destination: Path, experiment: Path,
            placement: str) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)
    for stale in (destination / "PLACEMENT.json",):
        stale.unlink(missing_ok=True)
    overlays = {
        "gt9x16_prod3_aos_branch0.S": experiment / "asm/gt9x16_prod3_aos_branch0.S",
        "gt9x16-prod3-ma2-qorder-natural-constants.inc":
            experiment / "generated/gt9x16-prod3-ma2-qorder-natural-constants.inc",
        "gt9x16-prod3-ma2-qorder-natural-asm.h":
            experiment / "generated/gt9x16-prod3-ma2-qorder-natural-asm.h",
    }
    natural_name = ("gt9x16_prod3_aos_natural.S" if placement == "normal"
                    else "aa_gt9x16_prod3_aos_natural.S")
    qorder_name = ("gt9x16_prod3_ma2_qorder_natural.S" if placement == "normal"
                   else "ab_gt9x16_prod3_ma2_qorder_natural.S")
    overlays[natural_name] = experiment / "asm/gt9x16_prod3_aos_natural.S"
    overlays[qorder_name] = experiment / "asm/gt9x16_prod3_ma2_qorder_natural.S"
    for name, source_path in overlays.items():
        data = source_path.read_text()
        (destination / name).write_text(flatten(data))
    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["implementation"] = destination.name
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["qorder_price"] = {
        "placement": placement,
        "current_q": "existing PROD3 price producer plus current H1",
        "natural_q": [natural_name, qorder_name],
        "arithmetic_changed": False,
        "lambda_reindex": "offline constants only",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (destination / "PLACEMENT.json").write_text(
        json.dumps(manifest["qorder_price"], indent=2, sort_keys=True) + "\n")
    rewrite_checksums(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--source-normal", required=True)
    parser.add_argument("--source-reversed", required=True)
    parser.add_argument("--normal-implementation", required=True)
    parser.add_argument("--reversed-implementation", required=True)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    if not (root / ".ntruplus-campaign.json").is_file():
        raise SystemExit(f"not a disposable SUPERCOP campaign: {root}")
    experiment = Path(__file__).resolve().parent.parent / EXPERIMENT_REL
    base = root / "crypto_kem/ntruplus1152"
    install(base / args.source_normal, base / args.normal_implementation,
            experiment, "normal")
    install(base / args.source_reversed, base / args.reversed_implementation,
            experiment, "reversed")
    print("prepared current-Q/natural-Q normal and reversed implementations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
