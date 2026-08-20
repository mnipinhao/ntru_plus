#!/usr/bin/env python3
"""Install a qualified flat clean implementation in a disposable campaign."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from supercop_workflow import REPO_ROOT, read_lock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--parameter", choices=("864", "1152"), required=True)
    args = parser.parse_args()
    campaign = args.campaign_root.resolve()
    marker_path = campaign / ".ntruplus-campaign.json"
    if not marker_path.is_file():
        raise SystemExit("clean installation requires a disposable SUPERCOP campaign")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    if marker.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("campaign marker has the wrong kind")
    if marker.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign version does not match the pinned release")
    source = (REPO_ROOT / "ntruplus-ntt-Optimized" / "Additional_Implementation" / "avx2" /
              f"NTRU+{args.parameter}" / "clean" / "avx2-fastest-clean")
    if not (source / "SOURCE-MANIFEST.json").is_file():
        raise SystemExit(f"clean implementation is not qualified: {source}")
    nonflat = [path for path in source.iterdir() if path.is_dir() or path.is_symlink()]
    if nonflat:
        raise SystemExit(f"clean SUPERCOP implementation must be flat: {nonflat[0]}")
    target = campaign / "crypto_kem" / f"ntruplus{args.parameter}" / "avx2-fastest-clean"
    if target.exists() or target.is_symlink():
        raise SystemExit(f"refusing to overwrite {target}")
    for required in ("architectures", "goal-constbranch", "goal-constindex"):
        if not (source / required).is_file():
            raise SystemExit(f"clean implementation lacks {required}")
    architectures = set((source / "architectures").read_text(encoding="utf-8").split())
    if not {"x86", "amd64"}.issubset(architectures):
        raise SystemExit("clean architectures must contain x86 and amd64")
    shutil.copytree(source, target, symlinks=False)
    print(f"installed {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
