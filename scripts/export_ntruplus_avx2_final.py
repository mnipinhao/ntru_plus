#!/usr/bin/env python3
"""Export a KpqC-style package from frozen skeleton plus qualified AVX2 clean trees."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import REPO_ROOT, read_lock, sha256_tree


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--qualification-report", type=Path, required=True)
    args = parser.parse_args()
    if args.destination.exists() or args.destination.is_symlink():
        raise SystemExit(f"refusing to overwrite {args.destination}")
    if not args.qualification_report.is_file():
        raise SystemExit(f"missing qualification report: {args.qualification_report}")
    skeleton = REPO_ROOT / "ntruplus-KpqC-Final"
    avx2_parent = skeleton / "Additional_Implementation" / "avx2"

    def ignore(path: str, names: list[str]) -> set[str]:
        del names
        return {"NTRU+864", "NTRU+1152"} if Path(path).resolve() == avx2_parent.resolve() else set()

    clean_trees = {}
    for parameter in ("864", "1152"):
        clean = (REPO_ROOT / "ntruplus-ntt-Optimized" / "Additional_Implementation" /
                 "avx2" / f"NTRU+{parameter}" / "clean" / "avx2-fastest-clean")
        if not (clean / "SOURCE-MANIFEST.json").is_file():
            raise SystemExit(f"NTRU+{parameter} clean tree is not qualified (missing SOURCE-MANIFEST.json)")
        clean_trees[parameter] = clean

    # Exclude replacement targets while copying, so no existing package file is
    # ever deleted or overlaid.
    shutil.copytree(skeleton, args.destination, ignore=ignore)
    clean_hashes = {}
    for parameter, clean in clean_trees.items():
        target = args.destination / "Additional_Implementation" / "avx2" / f"NTRU+{parameter}"
        shutil.copytree(clean, target)
        clean_hashes[parameter] = sha256_tree(clean)
    release = {
        **read_lock(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "format": "ntruplus-AVX2-Final",
        "qualification_report": args.qualification_report.name,
        "ntruplus864_clean_tree_sha256": clean_hashes["864"],
        "ntruplus1152_clean_tree_sha256": clean_hashes["1152"],
    }
    (args.destination / "AVX2-RELEASE.json").write_text(
        json.dumps(release, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    shutil.copy2(args.qualification_report, args.destination / args.qualification_report.name)
    print(f"exported {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
