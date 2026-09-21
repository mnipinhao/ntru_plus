#!/usr/bin/env python3
"""Discover the latest official SUPERCOP release and refresh the lock."""

from __future__ import annotations

import argparse
import re
import tempfile
import urllib.request
from pathlib import Path

from supercop_workflow import implementation_path, safe_extract, sha256_file, sha256_tree, write_lock

INDEX_URL = "https://bench.cr.yp.to/supercop.html"
ARCHIVE_TEMPLATE = "https://bench.cr.yp.to/supercop/supercop-{version}.tar.xz"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-url", default=INDEX_URL)
    parser.add_argument("--lock", type=Path)
    args = parser.parse_args()

    with urllib.request.urlopen(args.index_url) as response:
        page = response.read().decode("utf-8", errors="replace")
    releases = set(re.findall(r"supercop-(\d{8})\.tar\.xz", page))
    if not releases:
        raise SystemExit(f"no SUPERCOP releases found at {args.index_url}")
    version = max(releases)
    url = ARCHIVE_TEMPLATE.format(version=version)

    with tempfile.TemporaryDirectory(prefix="refresh-supercop-") as temporary:
        temporary_path = Path(temporary)
        archive = temporary_path / f"supercop-{version}.tar.xz"
        print(f"downloading {url}")
        urllib.request.urlretrieve(url, archive)
        extracted = safe_extract(archive, temporary_path / "extract")
        values = {
            "version": version,
            "url": url,
            "archive_sha256": sha256_file(archive),
        }
        for parameter in ("768", "864", "1152"):
            tree = implementation_path(extracted, parameter)
            if not tree.is_dir():
                raise SystemExit(f"release lacks {tree.relative_to(extracted)}")
            values[f"ntruplus{parameter}_avx2_tree_sha256"] = sha256_tree(tree)

    target = args.lock if args.lock else None
    if target is None:
        write_lock(values)
    else:
        write_lock(values, target)
    print(f"locked SUPERCOP {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
