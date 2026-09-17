#!/usr/bin/env python3
"""Install the NTRU+1152 W1 Forward into a disposable SUPERCOP campaign."""
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
CONTROL_SYMBOL = (
    "ntruplus1152_exp001_gt9x16_prod3_aos_full_"
    "wire_monotone_scale1_lazy_reduce"
)
W1_SYMBOL = CONTROL_SYMBOL + "_w1"


def flatten_text(source: Path) -> str:
    return source.read_text(encoding="utf-8").replace(
        '"generated/', '"'
    ).replace('"asm/', '"')


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
    marker_path = root / ".ntruplus-campaign.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    if marker.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("target is not a disposable SUPERCOP campaign")
    if marker.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign lock mismatch")

    base = root / "crypto_kem/ntruplus1152"
    source = base / args.source_implementation
    destination = base / args.implementation
    if not source.is_dir():
        raise SystemExit(f"missing source implementation {source}")
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    shutil.copytree(source, destination)

    manifest_path = destination / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    installed = manifest.get("wire_monotone_native_rebase2", {}).get(
        "installed_sources", {}
    )
    forward_name = installed.get("forward", "zz_native_40_forward.S")
    forward_path = destination / forward_name
    if not forward_path.is_file():
        raise SystemExit(f"cannot identify installed Forward source {forward_path}")

    wrapper = flatten_text(
        EXPERIMENT / "asm/gt9x16_prod3_aos_h4_scale1_lazy_reduce_wire_w1.S"
    ).replace(W1_SYMBOL, CONTROL_SYMBOL)
    if W1_SYMBOL in wrapper or CONTROL_SYMBOL not in wrapper:
        raise SystemExit("failed to rebind W1 symbol for standalone installation")
    forward_path.write_text(wrapper, encoding="utf-8")
    (destination / "gt9x16_prod3_aos_branch0.S").write_text(
        flatten_text(EXPERIMENT / "asm/gt9x16_prod3_aos_branch0.S"),
        encoding="utf-8",
    )

    manifest["ntt9_wavefront_w1"] = {
        "source_implementation": source.name,
        "installed_forward": forward_name,
        "selected_p_row": 5,
        "boundary_delta_per_forward": {
            "intermediate_stores": -8,
            "intermediate_reloads": -8,
        },
        "arithmetic_scale_wire_abi": "unchanged",
        "production_promotion": False,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checksums(destination)
    print(f"installed {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
