#!/usr/bin/env python3
"""Deterministically export the accepted NTRU+864 GT source closure."""
from pathlib import Path
import argparse, filecmp, shutil, tempfile

ROOT=Path(__file__).resolve().parents[1]
C_SOURCES=["kem.c","symmetric.c","transform_api.c","gt864_fr0_basemul_d1.c",
 "cluster_transpose_frombytes.c","byte_api.c","gt864_tobytes.c","gt864_native.c","hash_g_fixed.c"]
ASM_SOURCES=["add.s","crepmod3.s","cbd.s","gt864_forward_poly_ntt.S","gt864_forward_six_bank.S",
 "gt864_top_split.s","tail_layout.S","gt864_p47_decaps_compare.S","gt864_p18_tobytes_full.S",
 "gt864_p18_tobytes_small.S","gt864_native_public.S","gt864_native_baseinv_num.S",
 "gt864_native_baseinv_prefix.S","gt864_native_baseinv_inverse.S","gt864_native_baseinv_recover.S",
 "gt864_native_baseinv_finish.S","gt864_p35_inverse16_ternary.S","gt864_p35_inverse_tail_ternary.S",
 "gt864_crepmod3_raw.S","gt864_native_basemul.S","gt864_native_inverse9.S","gt864_support_abi.S","keccakf1600.S"]
RENAMES={
 "add.s":{"poly_sub":"gt864_raw_poly_sub","poly_triple":"gt864_raw_poly_triple"},
 "crepmod3.s":{"poly_crepmod3":"gt864_raw_poly_crepmod3"},
 "cbd.s":{"poly_cbd1":"gt864_raw_poly_cbd1","poly_sotp_encode":"gt864_raw_poly_sotp_encode","poly_sotp_decode":"gt864_raw_poly_sotp_decode"},
}
KEM_PREFIX="""#define poly_ntt gt_d1_poly_ntt
#define poly_invntt gt_d1_poly_invntt
#define poly_baseinv gt864_native_poly_baseinv
#define poly_basemul gt_d1_poly_basemul
#define poly_basemul_add gt_d1_poly_basemul_add
"""

def write_tree(dst):
    dst.mkdir(parents=True)
    for name in C_SOURCES:
        text=(ROOT/name).read_text()
        if name=="kem.c": text=KEM_PREFIX+text
        text=text.replace('"NO_CE/fips202.h"','"fips202.h"')
        (dst/name).write_text(text)
    (dst/"fips202.c").write_text((ROOT/"NO_CE/fips202.c").read_text())
    (dst/"fips202.h").write_text((ROOT/"NO_CE/fips202.h").read_text())
    for name in ASM_SOURCES:
        text=(ROOT/name).read_text()
        for old,new in RENAMES.get(name,{}).items():
            text=text.replace(old,new)
        (dst/name).write_text(text)
    for p in sorted(ROOT.glob("*.h")): shutil.copyfile(p,dst/p.name)
    (dst/"architectures").write_text("aarch64\narmv8-a\n")
    (dst/"implementors").write_text("Chen Pin-Hao and contributors\n")

def equal(a,b):
    cmp=filecmp.dircmp(a,b)
    return not (cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files) and all(equal(Path(a)/n,Path(b)/n) for n in cmp.common_dirs)

ap=argparse.ArgumentParser(); ap.add_argument("destination",type=Path,nargs="?"); ap.add_argument("--check",action="store_true"); ap.add_argument("--self-check",action="store_true"); args=ap.parse_args()
if args.self_check:
    with tempfile.TemporaryDirectory(prefix="gt864-export-a-") as a, tempfile.TemporaryDirectory(prefix="gt864-export-b-") as b:
        pa=Path(a)/"aarch64"; pb=Path(b)/"aarch64"; write_tree(pa); write_tree(pb)
        if not equal(pa,pb): raise SystemExit("export-check: nondeterministic output")
        print("export-check: deterministic regeneration pass")
    raise SystemExit(0)
if args.destination is None: ap.error("destination is required unless --self-check is used")
with tempfile.TemporaryDirectory(prefix="gt864-export-") as td:
    generated=Path(td)/"aarch64"; write_tree(generated)
    if args.check:
        if not args.destination.is_dir() or not equal(generated,args.destination): raise SystemExit("export-check: destination differs")
        print("export-check: deterministic match")
    else:
        if args.destination.exists(): raise SystemExit("destination exists; remove it explicitly first")
        shutil.copytree(generated,args.destination)
        print(f"exported {args.destination}")
