#!/usr/bin/env python3
"""Build a byte/geometry-preserving production QL2 A/B pair."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
E103 = ROOT / "experiments/gt32_ql2_shared_convergence_103"
SUPER = Path("/home/nuc/supercop-20260627")
BUILD = EXP / "build"
OBJ = BUILD / "objects"
GEN = EXP / "generated"
BENCH = SUPER / "bench/nucpromtlhcubinucai1ummsb209"
WORK = BENCH / "work/compile"
FLAGS = ["-DSUPERCOP", '-DCOMPILER="gcc-gtclean-e0v-qualified"', "-DLOOPS=3",
         "-march=native", "-mtune=native", "-O3", "-fwrapv", "-fPIC",
         "-fPIE", "-fomit-frame-pointer", "-ffunction-sections",
         "-fdata-sections"]
COMMON_C = ["baseinv.c", "consts.c", "decap.c", "fips202.c", "kem.c",
            "keygen.c", "poly.c", "symmetric.c"]
COMMON_ASM = ["add.s", "basemul-ql2.s", "batch_inverse.s", "cbd.s",
              "crepmod3.s", "invntt.s", "ntt.s", "ntt-ql2.s", "ntt_p.s",
              "pack-ql2.s", "KeccakP-1600-AVX2.s"]


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"expected one occurrence of {old!r}")
    return text.replace(old, new)


def generate() -> None:
    GEN.mkdir(exist_ok=True)
    specifications = (
        ("ntt_ql2.s", "ntt-ql2.s", ".text.gt103_ntt_ql2",
         ".ql2_tail.1_ntt", "gt103_ntt_ql2_avx2",
         "ntruplus768_ntt_ql2_avx2"),
        ("basemul_ql2.s", "basemul-ql2.s", ".text.gt103_b3_ql2",
         ".ql2_tail.2_b3", "gt103_basemul_general_ql2_avx2",
         "ntruplus768_basemul_general_ql2_avx2"),
        ("pack_ql2.s", "pack-ql2.s", ".text.gt103_pack_ql2_sum",
         ".ql2_tail.3_pack", "gt103_pack_ql2_sum_avx2",
         "ntruplus768_pack_ql2_sum_avx2"),
    )
    for source, target, old_section, new_section, old_symbol, new_symbol in specifications:
        text = (E103 / "generated" / source).read_text()
        text = replace_once(text, old_section, new_section)
        text = text.replace(old_symbol, new_symbol)
        (GEN / target).write_text(text)
    (GEN / "tails.ld").write_text(
        "SECTIONS\n{\n"
        "  .e0v_tail ALIGN(0x1000) : { KEEP(*(.e0v_tail)) }\n"
        "  .ql2_tail ALIGN(0x1000) : {\n"
        "    KEEP(*(.ql2_tail.1_ntt))\n"
        "    KEEP(*(.ql2_tail.2_b3))\n"
        "    KEEP(*(.ql2_tail.3_pack))\n"
        "  }\n}\nINSERT AFTER .bss;\n")


def compile_one(source: Path, output: Path, includes: list[str]) -> None:
    run(["gcc", *FLAGS, *includes, "-c", str(source), "-o", str(output)])


def section_size(path: Path) -> int:
    text = subprocess.check_output(["readelf", "-SW", str(path)], text=True)
    for line in text.splitlines():
        if ".text.ntruplus768_enc_derand_impl " in line:
            fields = line.split()
            return int(fields[fields.index("PROGBITS") + 3], 16)
    raise SystemExit(f"missing Encap section in {path}")


def caller(name: str, source: Path, includes: list[str]) -> Path:
    raw = OBJ / f"encap-{name}-raw.o"
    compile_one(source, raw, includes)
    size = section_size(raw)
    if size > 611:
        raise SystemExit(f"{name} caller exceeds 611-byte slot: {size}")
    pad_source = GEN / f"encap-{name}-pad.s"
    pad_source.write_text(
        '.section .text.ntruplus768_enc_derand_impl,"ax",@progbits\n'
        f'.fill {611 - size},1,0x90\n'
        '.section .note.GNU-stack,"",@progbits\n')
    pad = OBJ / f"encap-{name}-pad.o"
    compile_one(pad_source, pad, includes)
    result = OBJ / f"encap-{name}.o"
    run(["ld", "-r", str(raw), str(pad), "-o", str(result)])
    return result


def main() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    OBJ.mkdir(parents=True)
    generate()
    includes = [f"-I{ROOT}", f"-I{SUPER / 'include'}", f"-I{BENCH / 'include'}",
                f"-I{BENCH / 'include/amd64'}",
                f"-I{BENCH / 'include/nontimecop/amd64'}", f"-I{WORK}"]
    ordered: list[Path] = []
    for name in COMMON_C:
        target = OBJ / f"common-{Path(name).stem}.o"
        compile_one(ROOT / name, target, includes)
        ordered.append(target)
    for name in COMMON_ASM:
        source = GEN / name if name.endswith("-ql2.s") else ROOT / name
        target = OBJ / f"common-{Path(name).stem}.o"
        compile_one(source, target, includes)
        ordered.append(target)

    controls = {"control": caller("control", ROOT / "encap.c", includes),
                "ql2": caller("ql2", EXP / "encap-ql2.c", includes)}
    harness = []
    for name in ("measure-anything.c", "measure.c"):
        target = OBJ / f"harness-{Path(name).stem}.o"
        compile_one(WORK / name, target, includes)
        harness.append(target)
    insert_at = next(i for i, path in enumerate(ordered)
                     if path.name == "common-fips202.o")
    libraries = [BENCH / "lib/amd64/libfastrandombytes.a",
                 BENCH / "lib/amd64/libkernelrandombytes.a",
                 BENCH / "lib/nontimecop/amd64/libcpucycles.a",
                 BENCH / "lib/amd64/libsupercop.a"]
    for profile, encap in controls.items():
        objects = ordered[:insert_at] + [encap] + ordered[insert_at:]
        run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
             "-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
             f"-Wl,-T,{GEN / 'tails.ld'}",
             f"-Wl,-Map,{BUILD / f'measure-{profile}.map'}",
             "-o", str(BUILD / f"measure-{profile}"),
             *(str(path) for path in harness + objects + libraries)])
    run(["python3", str(ROOT / "qualified/build-supercop.py"),
         "--supercop-root", str(SUPER), "--output", str(BUILD / "anchor")])


if __name__ == "__main__":
    main()
