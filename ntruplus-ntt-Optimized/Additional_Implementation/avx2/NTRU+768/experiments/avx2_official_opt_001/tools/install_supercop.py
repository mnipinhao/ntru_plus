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

NAME = "avx2-officialopt-fused-exp001"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-root", required=True, type=Path)
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
    target = root / "crypto_kem/ntruplus768" / NAME
    if target.exists():
        raise SystemExit(f"refusing overwrite: {target}")
    shutil.copytree(source, target, symlinks=False)
    shutil.copy2(ROOT / "src/kem_fused.c", target / "kem.c")
    shutil.copy2(ROOT / "asm/ntruplus768_officialopt_basemul_add.s",
                 target / "basemul_add.s")
    if set((target / "architectures").read_text().split()).isdisjoint({"amd64"}):
        raise SystemExit("candidate does not declare amd64")
    for goal in ("goal-constbranch", "goal-constindex"):
        if not (target / goal).is_file():
            raise SystemExit(f"missing {goal}")
    manifest = dict(kind="Official-derived research candidate",
                    implementation=NAME, installed_at=datetime.now(timezone.utc).isoformat(),
                    pinned_version=lock["version"], official_tree_sha256=sha256_tree(source),
                    overlays={"kem.c": sha256_file(ROOT / "src/kem_fused.c"),
                              "basemul_add.s": sha256_file(ROOT / "asm/ntruplus768_officialopt_basemul_add.s")})
    (target / "SOURCE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
