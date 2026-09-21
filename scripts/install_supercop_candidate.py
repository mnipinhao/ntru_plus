#!/usr/bin/env python3
"""Install a flat, non-overwriting experiment candidate in a campaign tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import LOCK_PATH, read_lock, sha256_file

SOURCE_SUFFIXES = {".c", ".h", ".s", ".S", ".inc"}


def candidate_files(directory: Path):
    if not directory.is_dir():
        return
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix in SOURCE_SUFFIXES:
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--parameter", choices=("768", "864", "1152"), required=True)
    parser.add_argument("--implementation", required=True)
    args = parser.parse_args()
    campaign = args.campaign_root.resolve()
    experiment = args.experiment.resolve()
    marker_path = campaign / ".ntruplus-campaign.json"
    if not marker_path.is_file():
        raise SystemExit(f"not a disposable campaign (missing {marker_path})")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    lock = read_lock()
    if marker.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("campaign marker has the wrong kind")
    if marker.get("supercop_version") != lock["version"]:
        raise SystemExit("campaign version does not match bench/supercop.lock")
    if args.implementation == "avx2" or "/" in args.implementation:
        raise SystemExit("candidate must have a new, single-directory implementation name")

    source = experiment / "upstream" / "supercop-avx2"
    target = campaign / "crypto_kem" / f"ntruplus{args.parameter}" / args.implementation
    if target.exists() or target.is_symlink():
        raise SystemExit(f"refusing to overwrite {target}")
    if not source.is_dir():
        raise SystemExit(f"missing imported upstream source: {source}")
    shutil.copytree(source, target, symlinks=False)

    installed_from: dict[str, str] = {}
    for area in ("src", "asm", "generated", "ref"):
        for candidate in candidate_files(experiment / area) or ():
            destination = target / candidate.name
            if destination.name in installed_from:
                raise SystemExit(f"duplicate flat candidate filename: {destination.name}")
            shutil.copy2(candidate, destination)
            installed_from[destination.name] = str(candidate.relative_to(experiment))

    # The installed implementation is intentionally flat.  Rewrite only local
    # quoted include paths whose flattened basename was installed; never alter
    # system includes or references outside the experiment overlay.
    flattened_includes = {}
    include_pattern = re.compile(r'(["\'])(?:src|asm|generated|ref)/([^"\']+)\1')
    for destination_name in installed_from:
        destination = target / destination_name
        if destination.suffix not in SOURCE_SUFFIXES:
            continue
        original = destination.read_text(encoding="utf-8")

        def flatten(match: re.Match[str]) -> str:
            basename = Path(match.group(2)).name
            if basename not in installed_from:
                raise SystemExit(
                    f"cannot flatten missing include {match.group(2)} in {destination.name}")
            flattened_includes.setdefault(destination.name, []).append(match.group(2))
            return f'{match.group(1)}{basename}{match.group(1)}'

        rewritten = include_pattern.sub(flatten, original)
        if rewritten != original:
            destination.write_text(rewritten, encoding="utf-8")
    bench_source = LOCK_PATH.parent / "supercop" / "ntruplus_bench.c"
    bench_header = LOCK_PATH.parent / "supercop" / "ntruplus_bench.h"
    shutil.copy2(bench_source, target / bench_source.name)
    shutil.copy2(bench_header, target / bench_header.name)
    installed_from[bench_source.name] = str(bench_source.relative_to(LOCK_PATH.parents[1]))
    installed_from[bench_header.name] = str(bench_header.relative_to(LOCK_PATH.parents[1]))

    architecture_words = set((target / "architectures").read_text(encoding="utf-8").split())
    if not {"x86", "amd64"}.issubset(architecture_words):
        raise SystemExit("architectures must contain both x86 and amd64")
    for goal in ("goal-constbranch", "goal-constindex"):
        if not (target / goal).is_file():
            raise SystemExit(f"installed candidate lacks {goal}")
    symlinks = [path for path in target.rglob("*") if path.is_symlink()]
    if symlinks:
        raise SystemExit(f"installed candidate contains symlinks: {symlinks[0]}")

    manifest = {
        "archive_sha256": lock["archive_sha256"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "implementation": args.implementation,
        "installed_overlays": installed_from,
        "flattened_local_includes": flattened_includes,
        "parameter": args.parameter,
        "source_tree_sha256": lock[f"ntruplus{args.parameter}_avx2_tree_sha256"],
        "supercop_version": lock["version"],
    }
    (target / "SOURCE-MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checksums = []
    for path in sorted(target.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "SHA256SUMS":
            checksums.append(f"{sha256_file(path)}  {path.name}")
    (target / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(f"installed {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
