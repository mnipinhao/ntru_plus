#!/usr/bin/env python3
"""Import a pinned official NTRU+ AVX2 implementation into an experiment."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import REPO_ROOT, copy_tree_nonoverwriting, implementation_path, read_lock, verify_supercop


def experiment_root(parameter: str) -> Path:
    return (
        REPO_ROOT
        / "ntruplus-ntt-Optimized"
        / "Additional_Implementation"
        / "avx2"
        / f"NTRU+{parameter}"
        / "experiments"
        / "avx2_gt9x16_official_001"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supercop-root", type=Path, required=True)
    parser.add_argument("--parameter", choices=("864", "1152"), required=True)
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    lock = read_lock()
    hashes = verify_supercop(args.supercop_root, lock)
    upstream = args.destination or experiment_root(args.parameter) / "upstream"
    destination = upstream / "supercop-avx2"
    metadata = upstream / "UPSTREAM.json"
    if upstream.exists() or destination.exists() or metadata.exists():
        raise SystemExit(f"refusing to overwrite existing import: {upstream}")
    copy_tree_nonoverwriting(implementation_path(args.supercop_root, args.parameter), destination)
    record = {
        "archive_sha256": lock["archive_sha256"],
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "source_path": f"crypto_kem/ntruplus{args.parameter}/avx2",
        "source_tree_sha256": hashes[args.parameter],
        "supercop_url": lock["url"],
        "supercop_version": lock["version"],
    }
    metadata.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"imported {record['source_path']} to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
