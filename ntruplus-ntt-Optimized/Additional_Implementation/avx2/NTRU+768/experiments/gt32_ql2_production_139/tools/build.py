#!/usr/bin/env python3
"""Build Official and the promoted production QL2 source with measure.c."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
OFFICIAL = ROOT.parents[3] / "third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768"
SUPER = Path("/home/nuc/supercop-20260627")
BENCH = SUPER / "bench/nucpromtlhcubinucai1ummsb209"
WORK = BENCH / "work/compile"
BUILD = EXP / "build"
GEN = EXP / "generated"
OBJ = BUILD / "objects"
FLAGS = ["-DSUPERCOP", '-DCOMPILER="gcc-supercop-139"', "-DLOOPS=3",
         "-march=native", "-mtune=native", "-O3", "-fwrapv", "-fPIC",
         "-fPIE", "-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections"]
GT_SOURCES = ["baseinv.c", "consts.c", "decap.c", "encap.c",
              "encap-slot-pad.s", "fips202.c", "kem.c", "keygen.c",
              "poly.c", "symmetric.c", "add.s", "basemul.s",
              "batch_inverse.s", "cbd.s", "crepmod3.s", "invntt.s",
              "ntt.s", "ntt_m.s", "ntt_p.s", "pack.s",
              "KeccakP-1600-AVX2.s"]
OFFICIAL_SOURCES = ["asm/add.s", "asm/baseinv.s", "asm/basemul.s", "asm/cbd.s",
    "asm/crepmod3.s", "asm/invntt.s", "asm/ntt.s", "asm/pack.s", "consts.c",
    "kem.c", "poly.c", "symmetric.c", "fips202/fips202.c",
    "fips202/KeccakP-1600-AVX2.s"]


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def compile_one(source: Path, output: Path, includes: list[str], extra: list[str] | None = None) -> None:
    run(["gcc", *FLAGS, *(extra or []), *includes, "-c", str(source), "-o", str(output)])


def header() -> None:
    GEN.mkdir(exist_ok=True)
    (GEN / "crypto_kem.h").write_text(
        "#ifndef GT139_CRYPTO_KEM_H\n#define GT139_CRYPTO_KEM_H\n"
        "#define crypto_kem_keypair crypto_kem_ntruplus768_gt139_keypair\n"
        "#define crypto_kem_enc crypto_kem_ntruplus768_gt139_enc\n"
        "#define crypto_kem_dec crypto_kem_ntruplus768_gt139_dec\n"
        "#define crypto_kem_PUBLICKEYBYTES 1152\n"
        "#define crypto_kem_SECRETKEYBYTES 2336\n"
        "#define crypto_kem_BYTES 32\n"
        "#define crypto_kem_CIPHERTEXTBYTES 1152\n"
        "#define crypto_kem_IMPLEMENTATION \"NTRU+768/GT139-QL2-production\"\n"
        "#define crypto_kem_VERSION \"-\"\n"
        "extern int crypto_kem_keypair(unsigned char *,unsigned char *);\n"
        "extern int crypto_kem_enc(unsigned char *,unsigned char *,const unsigned char *);\n"
        "extern int crypto_kem_dec(unsigned char *,const unsigned char *,const unsigned char *);\n"
        "#endif\n")


def libraries() -> list[Path]:
    return [BENCH / "lib/amd64/libfastrandombytes.a",
            BENCH / "lib/amd64/libkernelrandombytes.a",
            BENCH / "lib/nontimecop/amd64/libcpucycles.a",
            BENCH / "lib/amd64/libsupercop.a"]


def main() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    OBJ.mkdir(parents=True)
    header()
    includes = [f"-I{GEN}", f"-I{ROOT}", f"-I{SUPER / 'include'}",
        f"-I{BENCH / 'include'}", f"-I{BENCH / 'include/amd64'}",
        f"-I{BENCH / 'include/nontimecop/amd64'}", f"-I{WORK}"]
    harness = []
    for index, source in enumerate((WORK / "measure-anything.c", SUPER / "crypto_kem/measure.c")):
        target = OBJ / f"harness-{index}.o"
        compile_one(source, target, includes)
        harness.append(target)

    gt_objects = []
    for index, name in enumerate(GT_SOURCES):
        target = OBJ / f"gt-{index:02d}-{Path(name).stem}.o"
        compile_one(ROOT / name, target, includes)
        gt_objects.append(target)
    run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
         "-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
         f"-Wl,-T,{ROOT / 'e0v-tail.ld'}", f"-Wl,-Map,{BUILD / 'gt.map'}",
         "-o", str(BUILD / "gt"),
         *(str(path) for path in harness + gt_objects + libraries())])

    official_objects = []
    official_includes = [f"-I{OFFICIAL}", f"-I{OFFICIAL / 'fips202'}", *includes]
    for index, name in enumerate(OFFICIAL_SOURCES):
        target = OBJ / f"official-{index:02d}.o"
        extra = ["-DNTRUPLUS_SUPERCOP"] if name == "kem.c" else []
        compile_one(OFFICIAL / name, target, official_includes, extra)
        if name == "kem.c":
            run(["objcopy",
                 "--redefine-sym=crypto_kem_keypair=crypto_kem_ntruplus768_gt139_keypair",
                 "--redefine-sym=crypto_kem_enc=crypto_kem_ntruplus768_gt139_enc",
                 "--redefine-sym=crypto_kem_dec=crypto_kem_ntruplus768_gt139_dec",
                 str(target)])
        official_objects.append(target)
    run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
         "-o", str(BUILD / "official"),
         *(str(path) for path in harness + official_objects + libraries())])

    manifest = {
        "production_source": str(ROOT),
        "harness": "native SUPERcop crypto_kem/measure.c",
        "object_order": GT_SOURCES,
        "sha256": {name: hashlib.sha256((BUILD / name).read_bytes()).hexdigest()
                   for name in ("official", "gt")},
        "bytes": {name: (BUILD / name).stat().st_size for name in ("official", "gt")},
    }
    (GEN / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
