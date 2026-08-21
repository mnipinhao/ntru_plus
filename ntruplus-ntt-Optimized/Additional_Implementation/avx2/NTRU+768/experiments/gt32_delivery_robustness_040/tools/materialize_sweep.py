#!/usr/bin/env python3
"""Create Official and current GT Clean exports with deterministic text shifts."""

from __future__ import annotations

import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[3]
EXP = pathlib.Path(__file__).resolve().parents[1]
SUPERCOP = pathlib.Path("/home/nuc/supercop-20260627")
OFFICIAL = SUPERCOP / "crypto_kem/ntruplus768/avx2"
EXPORTS = EXP / "exports"
OFFSETS = (0x000, 0x200, 0x400, 0x600, 0x800)

GT_FILES = (
    "KeccakP-1600-AVX2.s", "KeccakP-1600-SnP.h", "add.s", "api.h",
    "architectures", "baseinv.c", "baseinv.h", "baseinv_impl.inc",
    "baseinv_tables.inc", "basemul.h", "basemul.s", "batch_inverse.s",
    "cbd.s", "consts.c", "consts.h", "crepmod3.s", "decap.c", "encap.c",
    "fips202.c", "fips202.h", "goal-constbranch", "goal-constindex",
    "internal.h", "invntt.s", "kem.c", "keygen.c", "ntt.h", "ntt.s",
    "ntt_bounds.h", "ntt_m.s", "ntt_p.s", "pack.s", "params.h", "poly.c",
    "poly.h", "symmetric.c", "symmetric.h", "util.h",
)


def reset(path: pathlib.Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def copy_gt(destination: pathlib.Path) -> None:
    destination.mkdir(parents=True)
    for name in GT_FILES:
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
    (destination / "generated").mkdir()
    shutil.copy2(
        ROOT / "generated/tile4_inverse_tail_constants.inc",
        destination / "generated/tile4_inverse_tail_constants.inc",
    )


def inject(path: pathlib.Path, marker: str, amount: int) -> None:
    text = path.read_text()
    if text.count(marker) != 1:
        raise RuntimeError(f"expected one marker in {path}: {marker!r}")
    directive = f".space {amount}, 0x90\n" if amount else ""
    path.write_text(text.replace(marker, directive + marker, 1))


def main() -> None:
    reset(EXPORTS)
    manifest = {"offsets": list(OFFSETS), "variants": []}
    for family in ("official", "gt"):
        for amount in OFFSETS:
            name = f"{family}-pad-{amount:04x}"
            destination = EXPORTS / name
            if family == "official":
                shutil.copytree(OFFICIAL, destination)
                inject(destination / "ntt.s", ".global poly_ntt\n", amount)
            else:
                copy_gt(destination)
                inject(
                    destination / "ntt.s",
                    ".globl ntruplus768_ntt_frontend_avx2\n",
                    amount,
                )
            manifest["variants"].append(
                {"name": name, "family": family, "requested_shift": amount}
            )
    (EXP / "generated").mkdir(exist_ok=True)
    (EXP / "generated/sweep_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()

