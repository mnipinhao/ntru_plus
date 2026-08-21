#!/usr/bin/env python3
"""Move one GT hot cluster inside fixed-size per-function cages."""

from __future__ import annotations

import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[3]
EXP = pathlib.Path(__file__).resolve().parents[1]
EXPORTS = EXP / "exports"
OFFSETS = (0x000, 0x400, 0x800)
RESERVE = 0x800

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

CLUSTERS = {
    "d0_decode3": (
        ("pack.s", ".globl ntruplus768_unpack_m_body_avx2\n",
         ".size ntruplus768_unpack_m_body_avx2,.-ntruplus768_unpack_m_body_avx2\n"),
        ("pack.s", ".globl ntruplus768_unpack3_m_avx2\n",
         ".size ntruplus768_unpack3_m_avx2,.-ntruplus768_unpack3_m_avx2\n"),
    ),
    "d1_b3scale_inverse": (
        ("basemul.s",
         "TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_scale_m_avx2, TILE4_OUTPUT_SOA_LATE_C3CENTER,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA\n",
         "TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_scale_m_avx2, TILE4_OUTPUT_SOA_LATE_C3CENTER,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA\n"),
        ("invntt.s", ".globl ntruplus768_invntt_m_avx2\n",
         ".size ntruplus768_invntt_m_avx2,.-ntruplus768_invntt_m_avx2\n"),
    ),
    "d2_inverse_tail": (
        ("invntt.s", ".globl ntruplus768_invntt_m_avx2\n",
         ".size ntruplus768_invntt_m_avx2,.-ntruplus768_invntt_m_avx2\n"),
        ("invntt.s", ".globl ntruplus768_invntt_tail_avx2\n",
         ".size ntruplus768_invntt_tail_avx2,.-ntruplus768_invntt_tail_avx2\n"),
    ),
    "d3_frontend_n5": (
        ("ntt.s", ".globl ntruplus768_ntt_frontend_avx2\n",
         ".size ntruplus768_ntt_frontend_avx2,.-ntruplus768_ntt_frontend_avx2\n"),
        ("ntt_m.s", ".globl ntruplus768_ntt_m_avx2\n",
         ".size ntruplus768_ntt_m_avx2,.-ntruplus768_ntt_m_avx2\n"),
    ),
    "d4_recover_b3_q24": (
        ("basemul.s",
         "TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_general_m_avx2, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA\n",
         "TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_general_m_avx2, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA\n"),
        ("pack.s", ".globl ntruplus768_pack_m_centered_avx2\n",
         ".size ntruplus768_pack_m_centered_avx2,.-ntruplus768_pack_m_centered_avx2\n"),
    ),
    "e0_decode_h": (
        ("pack.s", ".globl ntruplus768_unpack_m_body_avx2\n",
         ".size ntruplus768_unpack_m_body_avx2,.-ntruplus768_unpack_m_body_avx2\n"),
        ("pack.s", ".globl ntruplus768_unpack_m_avx2\n",
         ".size ntruplus768_unpack_m_avx2,.-ntruplus768_unpack_m_avx2\n"),
    ),
    "e1_frontend_n5": (
        ("ntt.s", ".globl ntruplus768_ntt_frontend_avx2\n",
         ".size ntruplus768_ntt_frontend_avx2,.-ntruplus768_ntt_frontend_avx2\n"),
        ("ntt_m.s", ".globl ntruplus768_ntt_m_avx2\n",
         ".size ntruplus768_ntt_m_avx2,.-ntruplus768_ntt_m_avx2\n"),
    ),
    "e2_q24_outputs": (
        ("pack.s", ".globl ntruplus768_pack_m_lazy10788_avx2\n",
         ".size ntruplus768_pack_m_lazy10788_avx2,.-ntruplus768_pack_m_lazy10788_avx2\n"),
    ),
    "e3_b3_q24": (
        ("basemul.s",
         "TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_general_m_avx2, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA\n",
         "TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_general_m_avx2, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA\n"),
        ("pack.s", ".globl ntruplus768_pack_m_lazy10788_avx2\n",
         ".size ntruplus768_pack_m_lazy10788_avx2,.-ntruplus768_pack_m_lazy10788_avx2\n"),
    ),
}


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
    shutil.copy2(ROOT / "generated/tile4_inverse_tail_constants.inc",
                 destination / "generated/tile4_inverse_tail_constants.inc")


def cage(path: pathlib.Path, start: str, end: str, offset: int) -> None:
    text = path.read_text()
    if start == end:
        if text.count(start) != 1:
            raise RuntimeError(f"bad single-line marker in {path}: {start!r}")
        replacement = (
            f".space {offset}, 0x90\n" + start
            + f".space {RESERVE - offset}, 0x90\n"
        )
        path.write_text(text.replace(start, replacement, 1))
        return
    if text.count(start) != 1 or text.count(end) != 1:
        raise RuntimeError(f"bad cage markers in {path}: {start!r}, {end!r}")
    text = text.replace(start, f".space {offset}, 0x90\n" + start, 1)
    text = text.replace(end, end + f".space {RESERVE - offset}, 0x90\n", 1)
    path.write_text(text)


def main() -> None:
    variants = []
    for cluster, members in CLUSTERS.items():
        for offset in OFFSETS:
            name = f"cluster-{cluster}-pad-{offset:04x}"
            destination = EXPORTS / name
            if destination.exists():
                shutil.rmtree(destination)
            copy_gt(destination)
            for filename, start, end in members:
                cage(destination / filename, start, end, offset)
            variants.append({
                "name": name, "cluster": cluster, "offset": offset,
                "reserve_per_member": RESERVE, "members": len(members),
            })
    (EXP / "generated/cluster_manifest.json").write_text(
        json.dumps({"variants": variants}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
