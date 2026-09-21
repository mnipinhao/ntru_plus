#!/usr/bin/env python3
"""Create a flat, immutable-by-convention Official-derived qualification source.

This is a research export, not a clean-production promotion.  It is generated
from the pinned imported tree plus the two reviewed caller-lazy overlays.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = next(p for p in ROOT.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, sha256_file, sha256_tree  # noqa: E402

NAME = "avx2-officialopt-caller-lazy-qual001"
OVERLAYS = {
    "kem.c": "src/kem_lazy.c",
    "ntt_caller_lazy.s": "asm/ntruplus768_officialopt_ntt_caller_lazy.s",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    target = output_root / NAME
    manifest_path = output_root / (NAME + ".json")
    if target.exists() or manifest_path.exists():
        raise SystemExit("refusing to overwrite qualification export")

    lock = read_lock(REPO / "bench/supercop.lock")
    source = ROOT / "upstream/supercop-avx2"
    if sha256_tree(source) != lock["ntruplus768_avx2_tree_sha256"]:
        raise SystemExit("pinned Official import hash mismatch")
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=False)
    for destination, path in OVERLAYS.items():
        shutil.copy2(ROOT / path, target / destination)
    if "amd64" not in (target / "architectures").read_text().split():
        raise SystemExit("missing amd64 architecture")
    for goal in ("goal-constbranch", "goal-constindex"):
        if not (target / goal).is_file():
            raise SystemExit(f"missing {goal}")
    files = {str(path.relative_to(target)): sha256_file(path)
             for path in sorted(target.iterdir()) if path.is_file()}
    manifest = {
        "kind": "caller-lazy-qualification-source",
        "implementation": NAME,
        "supercop_version": lock["version"],
        "official_tree_sha256": lock["ntruplus768_avx2_tree_sha256"],
        "tree_sha256": sha256_tree(target),
        "overlays": {destination: sha256_file(ROOT / path)
                     for destination, path in OVERLAYS.items()},
        "files_sha256": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(target)


if __name__ == "__main__":
    main()
