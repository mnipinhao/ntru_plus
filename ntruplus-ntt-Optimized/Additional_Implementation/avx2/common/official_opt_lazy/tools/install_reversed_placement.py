#!/usr/bin/env python3
"""Create content-identical implementations with changed link member order.

Port of NTRU+768 avx2_official_opt_001/tools/install_reversed_placement.py for
864/1152, with the same renames.  SUPERCOP compiles every .s file of a flat
implementation; renaming only basenames changes archive member order and thus
hot-code placement while keeping exact source bytes and arithmetic.
A direct-codec export's `codec_direct.s` is renamed to `ccc_codec_direct.s`
(normal order basemul, codec_direct, ntt, ntt_caller_lazy, pack becomes
ntt, ntt_caller_lazy, codec_direct, pack, basemul).  --skip-baseline adds only
the candidate when `<baseline>-reversed` already exists.
NTRU+768 (--param 768) uses the same renames as NTRU+768
avx2_official_opt_001/tools/install_reversed_placement.py.  An HT export's
Forward and keygen BaseMul follow the files they replace:
`ntt_ht.s` -> `bbb_ntt_ht.s` (next to bbb_ntt_caller_lazy.s) and
`basemul_nor2.s` -> `zzz_basemul_nor2.s` (next to zzz_basemul.s);
`invntt_ht.s` stays, like `invntt.s`.  An Inverse D / Shoup export's Shoup BaseMul
follows the BaseMul it replaces (`basemul_shoup.s` -> `zzz_basemul_shoup.s`, next to
zzz_basemul.s); its `invntt_crep.s` stays, like `invntt.s`.  Trees without these files are
renamed exactly as before.
"""

import argparse
import json
import shutil
from pathlib import Path

RENAMES = {"ntt.s": "aaa_ntt.s", "basemul.s": "zzz_basemul.s", "pack.s": "yyy_pack.s"}
LAZY_RENAME = {"ntt_caller_lazy.s": "bbb_ntt_caller_lazy.s"}
CODEC_RENAME = {"codec_direct.s": "ccc_codec_direct.s"}
HT_RENAME = {"ntt_ht.s": "bbb_ntt_ht.s", "basemul_nor2.s": "zzz_basemul_nor2.s"}
INVSHOUP_RENAME = {"basemul_shoup.s": "zzz_basemul_shoup.s"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    parser.add_argument("--campaign-root", required=True, type=Path)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--baseline", default="avx2")
    parser.add_argument("--skip-baseline", action="store_true",
                        help="copy only the candidate (baseline-reversed must already exist)")
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file() or json.loads(marker.read_text()).get("kind") != "disposable-supercop-campaign":
        raise SystemExit("requires a disposable SUPERCOP campaign")
    impl = root / f"crypto_kem/ntruplus{args.param}"
    names = (args.baseline, args.candidate)
    if args.skip_baseline:
        if not (impl / (args.baseline + "-reversed")).is_dir():
            raise SystemExit("--skip-baseline needs an existing baseline-reversed copy")
        names = (args.candidate,)
    for name in names:
        source = impl / name
        target = impl / (name + "-reversed")
        if target.exists():
            raise SystemExit(f"refusing overwrite: {target}")
        shutil.copytree(source, target, symlinks=False)
        renames = dict(RENAMES)
        if (source / "ntt_caller_lazy.s").exists():
            renames.update(LAZY_RENAME)
        if (source / "codec_direct.s").exists():
            renames.update(CODEC_RENAME)
        renames.update({old: new for old, new in HT_RENAME.items() if (source / old).exists()})
        renames.update({old: new for old, new in INVSHOUP_RENAME.items() if (source / old).exists()})
        for old, new in renames.items():
            (target / old).rename(target / new)
        (target / "PLACEMENT.json").write_text(json.dumps(
            {"kind": "assembly-member-order-control", "source": name,
             "renames": renames}, indent=2) + "\n")
        print(target)


if __name__ == "__main__":
    main()
