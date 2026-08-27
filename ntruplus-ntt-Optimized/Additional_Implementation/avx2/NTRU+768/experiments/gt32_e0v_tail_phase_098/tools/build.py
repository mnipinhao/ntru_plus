#!/usr/bin/env python3
"""Build sixteen production-shaped E0V helper phase images."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
BUILD = EXP / "build"
OBJ = BUILD / "objects"
GEN = BUILD / "generated"
SUPER = Path("/home/nuc/supercop-20260627")
MEASURES = sorted((SUPER / "bench").glob("*/work/compile/measure.c"))
if len(MEASURES) != 1:
	raise SystemExit("expected one prepared SUPERcop measure work directory")
WORK = MEASURES[0].parent
BENCH = WORK.parents[1]
PHASES = tuple(range(0, 512, 32))
FLAGS = ["-DSUPERCOP", '-DCOMPILER="gcc-supercop-098"', "-DLOOPS=3",
	"-march=native", "-mtune=native", "-O3", "-fwrapv", "-fPIC", "-fPIE",
	"-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections"]
COMMON_C = ["baseinv.c", "consts.c", "decap.c", "fips202.c", "kem.c",
	"keygen.c", "poly.c", "symmetric.c"]
COMMON_ASM = ["add.s", "basemul.s", "batch_inverse.s", "cbd.s",
	"crepmod3.s", "invntt.s", "ntt.s", "ntt_m.s", "ntt_p.s", "pack.s",
	"KeccakP-1600-AVX2.s"]


def run(command: list[str]) -> None:
	subprocess.run(command, check=True)


def compile_one(source: Path, output: Path, includes: list[str]) -> None:
	run(["gcc", *FLAGS, *includes, "-c", str(source), "-o", str(output)])


def section_size(path: Path) -> int:
	text = subprocess.check_output(["readelf", "-SW", str(path)], text=True)
	line = next(line for line in text.splitlines()
		if ".text.ntruplus768_enc_derand_impl " in line)
	fields = line.split()
	return int(fields[fields.index("PROGBITS") + 3], 16)


def main() -> None:
	if BUILD.exists():
		shutil.rmtree(BUILD)
	OBJ.mkdir(parents=True)
	GEN.mkdir()
	includes = [f"-I{ROOT}", f"-I{SUPER / 'include'}",
		f"-I{BENCH / 'include'}", f"-I{BENCH / 'include/amd64'}",
		f"-I{BENCH / 'include/nontimecop/amd64'}", f"-I{WORK}"]
	ordered = []
	for name in COMMON_C + COMMON_ASM:
		target = OBJ / f"common-{Path(name).stem}.o"
		compile_one(ROOT / name, target, includes)
		ordered.append(target)
	raw = OBJ / "encap-raw.o"
	compile_one(ROOT / "encap.c", raw, includes)
	size = section_size(raw)
	if size > 611:
		raise SystemExit(f"caller exceeds 611-byte reservation: {size}")
	pad_source = GEN / "encap-pad.s"
	pad_source.write_text(
		'.section .text.ntruplus768_enc_derand_impl,"ax",@progbits\n'
		f'.fill {611 - size},1,0x90\n.section .note.GNU-stack,"",@progbits\n')
	pad = OBJ / "encap-pad.o"
	compile_one(pad_source, pad, includes)
	encap = OBJ / "encap.o"
	run(["ld", "-r", str(raw), str(pad), "-o", str(encap)])
	harness = []
	for name in ("measure-anything.c", "measure.c"):
		target = OBJ / f"harness-{Path(name).stem}.o"
		compile_one(WORK / name, target, includes)
		harness.append(target)
	insert_at = next(i for i, path in enumerate(ordered)
		if path.name == "common-fips202.o")
	objects = ordered[:insert_at] + [encap] + ordered[insert_at:]
	libraries = [BENCH / "lib/amd64/libfastrandombytes.a",
		BENCH / "lib/amd64/libkernelrandombytes.a",
		BENCH / "lib/nontimecop/amd64/libcpucycles.a",
		BENCH / "lib/amd64/libsupercop.a"]
	for phase in PHASES:
		linker = GEN / f"tail-{phase:03d}.ld"
		linker.write_text("SECTIONS\n{\n  .e0v_tail ALIGN(0x1000) : {\n"
			f"    . = . + 0x{phase:x};\n    KEEP(*(.e0v_tail))\n"
			"  }\n}\nINSERT AFTER .bss;\n")
		run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
			"-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
			f"-Wl,-T,{linker}", "-o", str(BUILD / f"phase-{phase:03d}"),
			*(str(path) for path in harness + objects + libraries)])
	manifest = {"control_commit": "b2a4bea", "phases": list(PHASES),
		"step": 32, "caller_raw_bytes": size,
		"source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
			for name in ["encap.c", "pack.s", "e0v-tail.ld"]}}
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
	run(["python3", str(EXP / "tools/audit.py")])


if __name__ == "__main__":
	main()
