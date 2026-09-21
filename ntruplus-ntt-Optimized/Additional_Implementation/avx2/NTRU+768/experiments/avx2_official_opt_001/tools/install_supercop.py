#!/usr/bin/env python3
"""Install one Official-derived candidate in a disposable SUPERCOP campaign."""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = next(p for p in ROOT.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, sha256_file, sha256_tree  # noqa: E402

VARIANTS = {
    "D": ("avx2-officialopt-duplicate-control-exp002",
          {"kem.c": "src/kem_dup.c",
           "basemul_dup.s": "asm/ntruplus768_officialopt_dup_basemul.s"}),
    "F": ("avx2-officialopt-fused-exp002",
          {"kem.c": "src/kem_fused.c",
           "basemul_add.s": "asm/ntruplus768_officialopt_basemul_add.s"}),
    "S": ("avx2-officialopt-shared-exp002",
          {"kem.c": "src/kem_shared.c",
           "basemul.s": "asm/ntruplus768_officialopt_shared_native.s"}),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-root", required=True, type=Path)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit("candidate installation requires a disposable campaign")
    record = json.loads(marker.read_text())
    lock = read_lock(REPO / "bench/supercop.lock")
    if record.get("kind") != "disposable-supercop-campaign" or record.get("supercop_version") != lock["version"]:
        raise SystemExit("campaign marker does not match the lock")
    source = ROOT / "upstream/supercop-avx2"
    if sha256_tree(source) != lock["ntruplus768_avx2_tree_sha256"]:
        raise SystemExit("imported upstream tree hash mismatch")
    name, overlays = VARIANTS[args.variant]
    target = root / "crypto_kem/ntruplus768" / name
    if target.exists():
        raise SystemExit(f"refusing overwrite: {target}")
    shutil.copytree(source, target, symlinks=False)
    for destination, source_path in overlays.items():
        shutil.copy2(ROOT / source_path, target / destination)
    if set((target / "architectures").read_text().split()).isdisjoint({"amd64"}):
        raise SystemExit("candidate does not declare amd64")
    for goal in ("goal-constbranch", "goal-constindex"):
        if not (target / goal).is_file():
            raise SystemExit(f"missing {goal}")
    source_files = {str(path.relative_to(target)): sha256_file(path)
                    for path in sorted(target.iterdir()) if path.is_file()}
    manifest = dict(kind="Official-derived research candidate",
                    implementation=name, variant=args.variant,
                    installed_at=datetime.now(timezone.utc).isoformat(),
                    pinned_version=lock["version"], official_tree_sha256=sha256_tree(source),
                    overlays={name: sha256_file(ROOT / path) for name, path in overlays.items()},
                    installed_files_sha256=source_files)
    (target / "SOURCE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
