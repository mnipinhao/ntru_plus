#!/usr/bin/env python3
"""Create content-identical assembly with changed archive/link member order."""

import argparse
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-root", required=True, type=Path)
    parser.add_argument("--candidate", default="avx2-officialopt-fused-exp001")
    parser.add_argument("--baseline", default="avx2")
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file() or json.loads(marker.read_text()).get("kind") != "disposable-supercop-campaign":
        raise SystemExit("requires a disposable SUPERCOP campaign")
    impl = root / "crypto_kem/ntruplus768"
    for name in (args.baseline, args.candidate):
        source = impl / name
        target = impl / (name + "-reversed")
        if target.exists():
            raise SystemExit(f"refusing overwrite: {target}")
        shutil.copytree(source, target, symlinks=False)
        # SUPERCOP compiles all .s files in the flat implementation. Changing
        # only basenames changes archive member order and therefore hot-code
        # placement while preserving exact source bytes and arithmetic.
        (target / "ntt.s").rename(target / "aaa_ntt.s")
        (target / "basemul.s").rename(target / "zzz_basemul.s")
        (target / "pack.s").rename(target / "yyy_pack.s")
        if (target / "ntt_caller_lazy.s").exists():
            (target / "ntt_caller_lazy.s").rename(target / "bbb_ntt_caller_lazy.s")
        (target / "PLACEMENT.json").write_text(json.dumps(
            {"kind": "assembly-member-order-control", "source": name,
             "renames": {"ntt.s": "aaa_ntt.s", "basemul.s": "zzz_basemul.s",
                         "pack.s": "yyy_pack.s",
                         **({"ntt_caller_lazy.s": "bbb_ntt_caller_lazy.s"}
                            if (source / "ntt_caller_lazy.s").exists() else {})}},
            indent=2) + "\n")
        print(target)


if __name__ == "__main__":
    main()
