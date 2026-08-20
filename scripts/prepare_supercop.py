#!/usr/bin/env python3
"""Verify or prepare pinned pristine and disposable SUPERCOP trees."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import make_read_only, read_lock, safe_extract, sha256_file, verify_supercop


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supercop-root", type=Path, help="existing pristine tree")
    parser.add_argument("--archive", type=Path, help="pinned official archive")
    parser.add_argument("--pristine-root", type=Path, help="new pristine destination")
    parser.add_argument("--campaign-root", type=Path, help="new disposable working copy")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    lock = read_lock()

    root = args.supercop_root
    if args.archive or args.pristine_root:
        if not (args.archive and args.pristine_root):
            parser.error("--archive and --pristine-root must be used together")
        if args.pristine_root.exists():
            raise SystemExit(f"refusing to overwrite {args.pristine_root}")
        actual = sha256_file(args.archive)
        if actual != lock["archive_sha256"]:
            raise SystemExit(f"archive SHA-256 mismatch: {actual}")
        with tempfile.TemporaryDirectory(prefix="prepare-supercop-", dir=args.pristine_root.parent) as temp:
            extracted = safe_extract(args.archive, Path(temp))
            verify_supercop(extracted, lock)
            shutil.move(str(extracted), args.pristine_root)
        make_read_only(args.pristine_root)
        root = args.pristine_root

    if root is None:
        parser.error("provide --supercop-root or --archive with --pristine-root")
    hashes = verify_supercop(root, lock)
    print(f"verified pristine SUPERCOP {lock['version']} at {root.resolve()}")

    if args.verify_only and args.campaign_root:
        parser.error("--verify-only cannot be combined with --campaign-root")
    if args.campaign_root:
        if args.campaign_root.exists():
            raise SystemExit(f"refusing to overwrite {args.campaign_root}")
        shutil.copytree(root, args.campaign_root, symlinks=True, copy_function=shutil.copy2)
        # A pristine tree may be read-only; the disposable copy is intentionally writable.
        for path in [args.campaign_root, *args.campaign_root.rglob("*")]:
            if not path.is_symlink():
                path.chmod(path.stat().st_mode | 0o200)
        marker = {
            "kind": "disposable-supercop-campaign",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": str(root.resolve()),
            "supercop_version": lock["version"],
            "archive_sha256": lock["archive_sha256"],
            "ntruplus864_avx2_tree_sha256": hashes["864"],
            "ntruplus1152_avx2_tree_sha256": hashes["1152"],
        }
        (args.campaign_root / ".ntruplus-campaign.json").write_text(
            json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"created disposable campaign at {args.campaign_root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
