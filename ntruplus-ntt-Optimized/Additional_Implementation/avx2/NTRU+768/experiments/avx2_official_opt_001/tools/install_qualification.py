#!/usr/bin/env python3
"""Install a verified flat qualification export into a disposable campaign."""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = next(p for p in ROOT.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, sha256_file, sha256_tree  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", required=True, type=Path)
    parser.add_argument("--export-root", required=True, type=Path)
    args = parser.parse_args()
    lock = read_lock(REPO / "bench/supercop.lock")
    campaign = args.campaign_root.resolve()
    marker = campaign / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit("installation requires a disposable campaign")
    record = json.loads(marker.read_text())
    if (record.get("kind") != "disposable-supercop-campaign" or
            record.get("supercop_version") != lock["version"]):
        raise SystemExit("campaign/lock mismatch")
    export_root = args.export_root.resolve()
    manifest_path = export_root.with_suffix(".json")
    manifest = json.loads(manifest_path.read_text())
    if (manifest.get("kind") != "caller-lazy-qualification-source" or
            manifest.get("supercop_version") != lock["version"] or
            manifest.get("official_tree_sha256") != lock["ntruplus768_avx2_tree_sha256"] or
            sha256_tree(export_root) != manifest["tree_sha256"]):
        raise SystemExit("qualification export verification failed")
    for name, expected in manifest["files_sha256"].items():
        if sha256_file(export_root / name) != expected:
            raise SystemExit(f"qualification source mismatch: {name}")
    target = campaign / "crypto_kem/ntruplus768" / manifest["implementation"]
    if target.exists():
        raise SystemExit(f"refusing to overwrite {target}")
    shutil.copytree(export_root, target, symlinks=False)
    if sha256_tree(target) != manifest["tree_sha256"]:
        raise SystemExit("installed source hash mismatch")
    print(target)


if __name__ == "__main__":
    main()
