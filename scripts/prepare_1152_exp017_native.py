#!/usr/bin/env python3
"""Build the exp017 cumulative NTRU+1152 native candidate non-destructively."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import REPO_ROOT, read_lock, sha256_file, sha256_tree


EXPERIMENT = (REPO_ROOT / "ntruplus-ntt-Optimized" /
              "Additional_Implementation" / "avx2" / "NTRU+1152" /
              "experiments" / "avx2_gt9x16_official_001")
EXPECTED_NAME = "avx2-gt9x16-wire-h3-pairunpack-serializer-v2-exp017-sc20260831"


def checksums(directory: Path) -> None:
    files = sorted(path for path in directory.iterdir()
                   if path.is_file() and path.name != "SHA256SUMS")
    (directory / "SHA256SUMS").write_text(
        "\n".join(f"{sha256_file(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--source-directory", type=Path, required=True,
                        help="qualified exp009 flat implementation")
    parser.add_argument("--implementation", default=EXPECTED_NAME)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    source = args.source_directory.resolve()
    marker_path = root / ".ntruplus-campaign.json"
    if not marker_path.is_file():
        raise SystemExit("installation requires a disposable SUPERCOP campaign")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    lock = read_lock()
    if marker.get("kind") != "disposable-supercop-campaign" or \
            marker.get("supercop_version") != lock["version"]:
        raise SystemExit("campaign marker/lock mismatch")
    if args.implementation != EXPECTED_NAME:
        raise SystemExit(f"formal exp017 name must be {EXPECTED_NAME}")
    if not (source / "SOURCE-MANIFEST.json").is_file():
        raise SystemExit("source implementation lacks SOURCE-MANIFEST.json")
    source_manifest = json.loads((source / "SOURCE-MANIFEST.json").read_text())
    if "h3_pairunpack_native" not in source_manifest:
        raise SystemExit("source implementation is not the exp009 H3 pair-unpack candidate")
    target = root / "crypto_kem" / "ntruplus1152" / args.implementation
    if target.exists() or target.is_symlink():
        raise SystemExit(f"refusing to overwrite {target}")
    shutil.copytree(source, target, symlinks=False)

    old_serializer = target / "zz_native_41_r_serializer.S"
    if not old_serializer.is_file():
        raise SystemExit("exp009 source lacks the direct wire serializer")
    old_serializer.unlink()
    shutil.copy2(EXPERIMENT / "asm" / "scale1_r_serializer_v2.S",
                 target / "zz_native_41_r_serializer_v2.S")
    shutil.copy2(EXPERIMENT / "src" / "scale1_r_serializer_v2_hash_g.c",
                 target / "zz_native_42_serializer_v2_hash_g.c")
    shutil.copy2(EXPERIMENT / "src" / "scale1_r_serializer_v2_hash_g.h",
                 target / "scale1_r_serializer_v2_hash_g.h")
    shutil.copy2(EXPERIMENT / "generated" / "scale1-r-serializer-v2-asm.h",
                 target / "scale1-r-serializer-v2-asm.h")

    kem_path = target / "kem.c"
    kem = kem_path.read_text(encoding="utf-8")
    include_anchor = '#include "wire-monotone-kem.h"\n'
    if kem.count(include_anchor) != 1:
        raise SystemExit("unexpected exp009 include shape")
    kem = kem.replace(include_anchor,
                      include_anchor + '#include "scale1_r_serializer_v2_hash_g.h"\n')
    old_calls = ("    ntruplus1152_exp001_direct_serializer_wire(ct, r_f0.coeffs);\n"
                 "    hash_g(ct, ct);\n")
    new_call = ("    ntruplus1152_exp001_scale1_r_serializer_v2_hash_g(\n"
                "        ct, r_f0.coeffs);\n")
    if kem.count(old_calls) != 1:
        raise SystemExit("unexpected exp009 r serializer/hash_g call shape")
    kem_path.write_text(kem.replace(old_calls, new_call), encoding="utf-8")

    manifest_path = target / "SOURCE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    installed = manifest["wire_monotone_native_rebase2"]["installed_sources"]
    installed["r_serializer"] = "zz_native_41_r_serializer_v2.S"
    manifest["exp017_serializer_v2_native"] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_directory": str(source),
        "source_tree_sha256": sha256_tree(source),
        "caller_change": (
            "replace direct wire serialization plus hash_g with the selected "
            "Serializer V2 direct hash_g stage"),
        "installed_sources": {
            "serializer": "zz_native_41_r_serializer_v2.S",
            "hash_stage": "zz_native_42_serializer_v2_hash_g.c",
        },
        "rejected_not_integrated": "D1 pair-resident fusion",
    }
    manifest["implementation"] = args.implementation
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksums(target)
    print(f"installed {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
