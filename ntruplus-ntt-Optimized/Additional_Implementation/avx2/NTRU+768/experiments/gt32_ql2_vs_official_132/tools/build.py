#!/usr/bin/env python3
"""Build exact Official and qualified QL2 images with a private 768 harness."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
E104 = ROOT / "experiments/gt32_ql2_geometry_integration_104"
OFFICIAL = ROOT.parents[3] / "third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768"
SUPER = Path("/home/nuc/supercop-20260627")
BENCH = SUPER / "bench/nucpromtlhcubinucai1ummsb209"
WORK = BENCH / "work/compile"
BUILD = EXP / "build"
GEN = EXP / "generated"
OBJ = BUILD / "objects"
FLAGS = ["-DSUPERCOP", '-DCOMPILER="gcc-supercop-132"', "-DLOOPS=3",
         "-march=native", "-mtune=native", "-O3", "-fwrapv", "-fPIC",
         "-fPIE", "-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections"]
OFFICIAL_SOURCES = ["asm/add.s", "asm/baseinv.s", "asm/basemul.s", "asm/cbd.s",
    "asm/crepmod3.s", "asm/invntt.s", "asm/ntt.s", "asm/pack.s", "consts.c",
    "kem.c", "poly.c", "symmetric.c", "fips202/fips202.c",
    "fips202/KeccakP-1600-AVX2.s"]
QL2_OBJECT_ORDER = [
    "common-baseinv.o", "common-consts.o", "common-decap.o",
    "@encap", "common-fips202.o", "@kem", "common-keygen.o",
    "common-poly.o", "common-symmetric.o", "common-add.o",
    "common-basemul-ql2.o", "common-batch_inverse.o", "common-cbd.o",
    "common-crepmod3.o", "common-invntt.o", "common-ntt.o",
    "common-ntt-ql2.o", "common-ntt_p.o", "common-pack-ql2.o",
    "common-KeccakP-1600-AVX2.o",
]

def run(command: list[str]) -> None:
    subprocess.run(command, check=True)

def compile_one(source: Path, output: Path, includes: list[str]) -> None:
    run(["gcc", *FLAGS, *includes, "-c", str(source), "-o", str(output)])

def write_private_header() -> None:
    GEN.mkdir(exist_ok=True)
    (GEN / "crypto_kem.h").write_text(
        "#ifndef GT132_CRYPTO_KEM_H\n#define GT132_CRYPTO_KEM_H\n"
        "#define crypto_kem_keypair crypto_kem_ntruplus768_gt132_keypair\n"
        "#define crypto_kem_enc crypto_kem_ntruplus768_gt132_enc\n"
        "#define crypto_kem_dec crypto_kem_ntruplus768_gt132_dec\n"
        "#define crypto_kem_PUBLICKEYBYTES 1152\n"
        "#define crypto_kem_SECRETKEYBYTES 2336\n"
        "#define crypto_kem_BYTES 32\n"
        "#define crypto_kem_CIPHERTEXTBYTES 1152\n"
        "#define crypto_kem_IMPLEMENTATION \"NTRU+768/GT132\"\n"
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
    run(["python3", str(E104 / "tools/build.py")])
    if BUILD.exists():
        shutil.rmtree(BUILD)
    OBJ.mkdir(parents=True)
    write_private_header()
    includes = [f"-I{GEN}", f"-I{SUPER / 'include'}", f"-I{BENCH / 'include'}",
        f"-I{BENCH / 'include/amd64'}", f"-I{BENCH / 'include/nontimecop/amd64'}",
        f"-I{WORK}"]
    harness = []
    for index, source in enumerate((WORK / "measure-anything.c", SUPER / "crypto_kem/measure.c")):
        target = OBJ / f"harness-{index}.o"
        compile_one(source, target, includes)
        harness.append(target)

    q104 = E104 / "build/objects"
    qkem = OBJ / "ql2-kem.o"
    compile_one(ROOT / "kem.c", qkem, [f"-I{ROOT}", *includes])
    qobjects = []
    for name in QL2_OBJECT_ORDER:
        if name == "@encap":
            qobjects.append(q104 / "encap-ql2.o")
        elif name == "@kem":
            qobjects.append(qkem)
        else:
            qobjects.append(q104 / name)
    missing = [str(path) for path in qobjects if not path.exists()]
    if missing:
        raise SystemExit(f"missing QL2 objects: {missing}")
    run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
         "-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
         f"-Wl,-T,{E104 / 'generated/tails.ld'}", f"-Wl,-Map,{BUILD / 'ql2.map'}",
         "-o", str(BUILD / "ql2"),
         *(str(path) for path in harness + qobjects + libraries())])

    oobjects = []
    for index, name in enumerate(OFFICIAL_SOURCES):
        target = OBJ / f"official-{index:02d}.o"
        official_includes = [f"-I{OFFICIAL}", f"-I{OFFICIAL / 'fips202'}", *includes]
        extra = ["-DNTRUPLUS_SUPERCOP"] if name == "kem.c" else []
        run(["gcc", *FLAGS, *extra, *official_includes, "-c",
             str(OFFICIAL / name), "-o", str(target)])
        if name == "kem.c":
            run(["objcopy",
                 "--redefine-sym=crypto_kem_keypair=crypto_kem_ntruplus768_gt132_keypair",
                 "--redefine-sym=crypto_kem_enc=crypto_kem_ntruplus768_gt132_enc",
                 "--redefine-sym=crypto_kem_dec=crypto_kem_ntruplus768_gt132_dec",
                 str(target)])
        oobjects.append(target)
    run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
         "-o", str(BUILD / "official"),
         *(str(path) for path in harness + oobjects + libraries())])

    manifest = {"production_anchor": "b2a4bea",
        "harness": "private NTRU+768 SUPERCOP measure.c",
        "sizes": {"pk": 1152, "sk": 2336, "ct": 1152, "ss": 32},
        "sha256": {name: hashlib.sha256((BUILD / name).read_bytes()).hexdigest()
                   for name in ("official", "ql2")},
        "bytes": {name: (BUILD / name).stat().st_size for name in ("official", "ql2")}}
    (GEN / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
