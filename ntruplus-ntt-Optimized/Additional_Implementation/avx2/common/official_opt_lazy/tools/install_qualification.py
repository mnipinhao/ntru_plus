#!/usr/bin/env python3
"""Install a verified flat qualification export into a disposable campaign.

Port of NTRU+768 avx2_official_opt_001/tools/install_qualification.py for
768/864/1152.  Only a campaign carrying the `.ntruplus-campaign.json` marker of
scripts/prepare_supercop.py is accepted; nothing is overwritten.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, sha256_file, sha256_tree  # noqa: E402

# export_caller_lazy_qualification.py,
# official_opt_keccak/tools/export_keccak_flat.py --qualification-root and
# official_opt_ht/tools/export_ht_flat.py --qualification-root
KINDS = ("caller-lazy-qualification-source", "keccak-qualification-source", "ht-qualification-source")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    parser.add_argument("--campaign-root", required=True, type=Path)
    parser.add_argument("--export-root", required=True, type=Path)
    args = parser.parse_args()
    lock = read_lock(REPO / "bench/supercop.lock")
    key = f"ntruplus{args.param}_avx2_tree_sha256"
    campaign = args.campaign_root.resolve()
    marker = campaign / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit("installation requires a disposable campaign")
    record = json.loads(marker.read_text())
    if (record.get("kind") != "disposable-supercop-campaign" or
            record.get("supercop_version") != lock["version"] or
            record.get(key) != lock[key]):
        raise SystemExit("campaign/lock mismatch")
    if sha256_tree(campaign / f"crypto_kem/ntruplus{args.param}/avx2") != lock[key]:
        raise SystemExit("campaign Official avx2 baseline differs from the lock")
    export_root = args.export_root.resolve()
    manifest = json.loads(export_root.with_suffix(".json").read_text())
    if (manifest.get("kind") not in KINDS or
            manifest.get("parameter") != str(args.param) or
            manifest.get("supercop_version") != lock["version"] or
            manifest.get("official_tree_sha256") != lock[key] or
            sha256_tree(export_root) != manifest["tree_sha256"]):
        raise SystemExit("qualification export verification failed")
    if {p.name for p in export_root.iterdir()} != set(manifest["files_sha256"]):
        raise SystemExit("qualification export file set differs from its manifest")
    for name, expected in manifest["files_sha256"].items():
        if sha256_file(export_root / name) != expected:
            raise SystemExit(f"qualification source mismatch: {name}")
    target = campaign / f"crypto_kem/ntruplus{args.param}" / manifest["implementation"]
    if target.exists():
        raise SystemExit(f"refusing to overwrite {target}")
    shutil.copytree(export_root, target, symlinks=False)
    if sha256_tree(target) != manifest["tree_sha256"]:
        raise SystemExit("installed source hash mismatch")
    print(target)


if __name__ == "__main__":
    main()
