#!/usr/bin/env python3
"""Install the qualified NTRU+768 GT32 clean tree into a campaign."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import REPO_ROOT, read_lock, sha256_file, sha256_tree


SOURCE = (REPO_ROOT / "ntruplus-ntt-Optimized" / "Additional_Implementation" /
          "avx2" / "NTRU+768" / "clean" / "avx2-gt32-clean")
EXCLUDED = {
    "README.md", "SYMBOLS.md", "LAYOUTS.md", "IMPLEMENTATION.md",
    "BENCHMARK.md", "SOURCE-MANIFEST.md", "SHA256SUMS", "install-supercop.sh",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--implementation", default="avx2-gt32-clean")
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker_path = root / ".ntruplus-campaign.json"
    if not marker_path.is_file():
        raise SystemExit("installation requires a disposable SUPERCOP campaign")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    lock = read_lock()
    if marker.get("kind") != "disposable-supercop-campaign" or \
            marker.get("supercop_version") != lock["version"]:
        raise SystemExit("campaign marker/lock mismatch")
    if not SOURCE.is_dir():
        raise SystemExit(f"missing qualified clean source: {SOURCE}")
    if args.implementation == "avx2" or "/" in args.implementation:
        raise SystemExit("implementation must be a new single-directory name")
    target = root / "crypto_kem" / "ntruplus768" / args.implementation
    if target.exists() or target.is_symlink():
        raise SystemExit(f"refusing to overwrite {target}")
    # Validate the one generated include before creating the target so a
    # failed preflight cannot leave a partially installed implementation.
    generated = SOURCE / "generated" / "tile4_inverse_tail_constants.inc"
    if not generated.is_file():
        raise SystemExit(f"missing generated clean source: {generated}")
    target.mkdir()
    for source in sorted(SOURCE.iterdir()):
        if source.name in EXCLUDED:
            continue
        if source.name == "generated":
            continue
        if source.is_dir() or source.is_symlink():
            raise SystemExit(f"clean implementation is not flat: {source}")
        shutil.copy2(source, target / source.name)
    shutil.copy2(generated, target / generated.name)
    invntt = target / "invntt.s"
    text = invntt.read_text(encoding="utf-8")
    include = '.include "generated/tile4_inverse_tail_constants.inc"'
    if text.count(include) != 1:
        raise SystemExit("unexpected clean invntt include shape")
    invntt.write_text(text.replace(include, '.include "tile4_inverse_tail_constants.inc"'),
                      encoding="utf-8")
    for required in ("architectures", "goal-constbranch", "goal-constindex"):
        if not (target / required).is_file():
            raise SystemExit(f"installed candidate lacks {required}")
    architectures = set((target / "architectures").read_text().split())
    if not {"x86", "amd64"}.issubset(architectures):
        raise SystemExit("architectures must contain x86 and amd64")
    manifest = {
        "schema": "ntruplus-clean-install/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "implementation": args.implementation,
        "parameter": "768",
        "source": str(SOURCE.relative_to(REPO_ROOT)),
        "source_tree_sha256": sha256_tree(SOURCE),
        "official_tree_sha256": lock["ntruplus768_avx2_tree_sha256"],
        "supercop_version": lock["version"],
        "resolved_call_graph": "GT32 TILE4; P/J1 keygen; persistent-M encap/decap",
    }
    (target / "SOURCE-MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in target.iterdir()
                   if path.is_file() and path.name != "SHA256SUMS")
    (target / "SHA256SUMS").write_text(
        "\n".join(f"{sha256_file(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8")
    print(f"installed {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
