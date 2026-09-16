#!/usr/bin/env python3
"""Build matched E0V and promoted QL2 SUPERcop measure ELFs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMON_C = ["baseinv.c", "consts.c", "decap.c", "fips202.c", "kem.c",
            "keygen.c", "poly.c", "symmetric.c"]
COMMON_ASM = ["add.s", "basemul.s", "batch_inverse.s", "cbd.s",
              "crepmod3.s", "invntt.s", "ntt.s", "ntt_m.s", "ntt_p.s",
              "pack.s", "KeccakP-1600-AVX2.s"]
FLAGS = ["-DSUPERCOP", '-DCOMPILER="gcc-gtclean-e0v-qualified"',
         "-DLOOPS=3", "-march=native", "-mtune=native", "-O3",
         "-fwrapv", "-fPIC", "-fPIE", "-fomit-frame-pointer",
         "-ffunction-sections", "-fdata-sections"]


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def compile_one(source: Path, output: Path, includes: list[str]) -> None:
    run(["gcc", *FLAGS, *includes, "-c", str(source), "-o", str(output)])


def section_size(path: Path) -> int:
    text = subprocess.check_output(["readelf", "-SW", str(path)], text=True)
    for line in text.splitlines():
        if ".text.ntruplus768_enc_derand_impl " in line:
            fields = line.split()
            return int(fields[fields.index("PROGBITS") + 3], 16)
    raise SystemExit(f"missing Encap input section in {path}")


def qualify_encap(name: str, source: Path, objects: Path,
                  includes: list[str]) -> Path:
    raw = objects / f"encap-{name}-raw.o"
    compile_one(source, raw, includes)
    size = section_size(raw)
    if size > 611:
        raise SystemExit(f"{name} Encap exceeds qualified slot: {size}")
    pad_source = objects.parent / f"encap-{name}-pad.s"
    pad_source.write_text(
        '.section .text.ntruplus768_enc_derand_impl,"ax",@progbits\n'
        f'.fill {611 - size},1,0x90\n'
        '.section .note.GNU-stack,"",@progbits\n')
    pad = objects / f"encap-{name}-pad.o"
    compile_one(pad_source, pad, includes)
    result = objects / f"encap-{name}.o"
    run(["ld", "-r", str(raw), str(pad), "-o", str(result)])
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--supercop-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "qualified/build")
    args = parser.parse_args()
    output = args.output.resolve()
    supercop = args.supercop_root.resolve()
    benches = sorted((supercop / "bench").glob("*/work/compile/measure.c"))
    if len(benches) != 1:
        raise SystemExit("expected one prepared SUPERcop measure work directory")
    work = benches[0].parent
    bench = work.parents[1]
    if output.exists():
        shutil.rmtree(output)
    objects = output / "objects"
    objects.mkdir(parents=True)
    includes = [f"-I{ROOT}", f"-I{supercop / 'include'}",
                f"-I{bench / 'include'}", f"-I{bench / 'include/amd64'}",
                f"-I{bench / 'include/nontimecop/amd64'}", f"-I{work}"]

    ordered: list[Path] = []
    for name in COMMON_C:
        target = objects / f"common-{Path(name).stem}.o"
        compile_one(ROOT / name, target, includes)
        ordered.append(target)
    for name in COMMON_ASM:
        target = objects / f"common-{Path(name).stem}.o"
        compile_one(ROOT / name, target, includes)
        ordered.append(target)

    enc_e0v = qualify_encap("e0v", ROOT / "qualified/encap-e0v.c",
                            objects, includes)
    enc_ql2 = qualify_encap("ql2", ROOT / "encap.c", objects, includes)

    harness: list[Path] = []
    for name in ("measure-anything.c", "measure.c"):
        target = objects / f"harness-{Path(name).stem}.o"
        compile_one(work / name, target, includes)
        harness.append(target)

    # Match the flat production source ordering: encap lies after decap and
    # before fips202.  Every other object is bit-identical between profiles.
    insert_at = next(i for i, path in enumerate(ordered)
                     if path.name == "common-fips202.o")
    libraries = [bench / "lib/amd64/libfastrandombytes.a",
                 bench / "lib/amd64/libkernelrandombytes.a",
                 bench / "lib/nontimecop/amd64/libcpucycles.a",
                 bench / "lib/amd64/libsupercop.a"]
    for profile, encap in (("e0v", enc_e0v), ("ql2", enc_ql2)):
        profile_objects = ordered[:insert_at] + [encap] + ordered[insert_at:]
        run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
             "-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
             f"-Wl,-T,{ROOT / 'e0v-tail.ld'}",
             f"-Wl,-Map,{output / f'measure-{profile}.map'}",
             "-o", str(output / f"measure-{profile}"),
             *(str(path) for path in harness + profile_objects + libraries)])

    run(["python3", str(ROOT / "qualified/audit-layout.py"),
         "--build", str(output)])


if __name__ == "__main__":
    main()
