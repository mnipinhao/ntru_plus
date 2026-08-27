#!/usr/bin/env python3
"""Build matched C4/A4/A3 production-shaped SUPERcop measure ELFs."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
BUILD = EXP / "build"
OBJ = BUILD / "objects"
SUPER = Path("/home/nuc/supercop-20260627")
MEASURES = sorted((SUPER / "bench").glob("*/work/compile/measure.c"))
if len(MEASURES) != 1:
	raise SystemExit("expected one prepared SUPERcop measure work directory")
WORK = MEASURES[0].parent
BENCH = WORK.parents[1]
FLAGS = ["-DSUPERCOP", '-DCOMPILER="gcc-supercop-096"', "-DLOOPS=3",
	"-march=native", "-mtune=native", "-O3", "-fwrapv", "-fPIC", "-fPIE",
	"-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections"]
COMMON_C = ["baseinv.c", "consts.c", "decap.c", "fips202.c", "kem.c",
	"keygen.c", "poly.c", "symmetric.c"]
COMMON_ASM = ["add.s", "basemul.s", "batch_inverse.s", "cbd.s",
	"crepmod3.s", "invntt.s", "ntt.s", "ntt_m.s", "ntt_p.s", "pack.s",
	"KeccakP-1600-AVX2.s"]
SOURCES = {"c4": ROOT / "encap.c", "a4": EXP / "encap-a4.c",
	"a4i": EXP / "encap-a4i.c", "a3": EXP / "encap-a3.c"}


def run(command: list[str]) -> None:
	subprocess.run(command, check=True)


def compile_one(source: Path, output: Path, includes: list[str]) -> None:
	run(["gcc", *FLAGS, *includes, "-c", str(source), "-o", str(output)])


def section_size(path: Path) -> int:
	text = subprocess.check_output(["readelf", "-SW", str(path)], text=True)
	for line in text.splitlines():
		if ".text.ntruplus768_enc_derand_impl " in line:
			fields = line.split()
			index = fields.index("PROGBITS")
			return int(fields[index + 3], 16)
	raise SystemExit(f"missing encap section in {path}")


def qualify_encap(profile: str, source: Path, includes: list[str]) -> Path:
	raw = OBJ / f"encap-{profile}-raw.o"
	compile_one(source, raw, includes)
	size = section_size(raw)
	if size > 611:
		raise SystemExit(f"{profile} caller exceeds 611-byte slot: {size}")
	pad_source = BUILD / f"pad-{profile}.s"
	pad_source.write_text(
		'.section .text.ntruplus768_enc_derand_impl,"ax",@progbits\n'
		f'.fill {611 - size},1,0x90\n'
		'.section .note.GNU-stack,"",@progbits\n')
	pad = OBJ / f"encap-{profile}-pad.o"
	compile_one(pad_source, pad, includes)
	result = OBJ / f"encap-{profile}.o"
	run(["ld", "-r", str(raw), str(pad), "-o", str(result)])
	return result


def main() -> None:
	if BUILD.exists():
		shutil.rmtree(BUILD)
	OBJ.mkdir(parents=True)
	includes = [f"-I{ROOT}", f"-I{SUPER / 'include'}",
		f"-I{BENCH / 'include'}", f"-I{BENCH / 'include/amd64'}",
		f"-I{BENCH / 'include/nontimecop/amd64'}", f"-I{WORK}"]
	ordered = []
	for name in COMMON_C + COMMON_ASM:
		target = OBJ / f"common-{Path(name).stem}.o"
		compile_one(ROOT / name, target, includes)
		ordered.append(target)
	encap = {p: qualify_encap(p, source, includes)
		for p, source in SOURCES.items()}
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
	for profile in SOURCES:
		objects = ordered[:insert_at] + [encap[profile]] + ordered[insert_at:]
		run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
			"-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
			f"-Wl,-T,{ROOT / 'e0v-tail.ld'}", "-o", str(BUILD / profile),
			*(str(path) for path in harness + objects + libraries)])
	run(["python3", str(EXP / "tools/audit.py")])


if __name__ == "__main__":
	main()
