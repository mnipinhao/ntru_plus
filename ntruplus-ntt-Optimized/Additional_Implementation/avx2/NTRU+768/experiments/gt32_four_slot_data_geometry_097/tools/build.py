#!/usr/bin/env python3
"""Generate and build all 24 four-slot production-shaped images."""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import shutil
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
BUILD = EXP / "build"
OBJ = BUILD / "objects"
SRC = BUILD / "sources"
SUPER = Path("/home/nuc/supercop-20260627")
MEASURES = sorted((SUPER / "bench").glob("*/work/compile/measure.c"))
if len(MEASURES) != 1:
	raise SystemExit("expected one prepared SUPERcop measure work directory")
WORK = MEASURES[0].parent
BENCH = WORK.parents[1]
FIELDS = ("h", "r", "m", "c")
PROFILES = tuple("".join(p) for p in itertools.permutations(FIELDS))
BASELINE = "hrmc"
FLAGS = ["-DSUPERCOP", '-DCOMPILER="gcc-supercop-097"', "-DLOOPS=3",
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


def materialize_sources() -> None:
	template = (ROOT / "encap.c").read_text()
	pattern = re.compile(
		r"typedef struct __attribute__\(\(aligned\(64\)\)\) \{\n"
		r"(?:\tint16_t [hrmc]\[NTRUPLUS_N\];\n){4}"
		r"\} encap_scratch;")
	if len(pattern.findall(template)) != 1:
		raise SystemExit("production encap_scratch template drift")
	SRC.mkdir(parents=True)
	for profile in PROFILES:
		fields = "".join(f"\tint16_t {name}[NTRUPLUS_N];\n" for name in profile)
		replacement = ("typedef struct __attribute__((aligned(64))) {\n" + fields +
			"} encap_scratch;")
		(SRC / f"encap-{profile}.c").write_text(pattern.sub(replacement, template))


def section_size(path: Path) -> int:
	text = subprocess.check_output(["readelf", "-SW", str(path)], text=True)
	line = next(line for line in text.splitlines()
		if ".text.ntruplus768_enc_derand_impl " in line)
	fields = line.split()
	return int(fields[fields.index("PROGBITS") + 3], 16)


def qualify_encap(profile: str, includes: list[str]) -> Path:
	raw = OBJ / f"encap-{profile}-raw.o"
	compile_one(SRC / f"encap-{profile}.c", raw, includes)
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
	materialize_sources()
	includes = [f"-I{ROOT}", f"-I{SUPER / 'include'}",
		f"-I{BENCH / 'include'}", f"-I{BENCH / 'include/amd64'}",
		f"-I{BENCH / 'include/nontimecop/amd64'}", f"-I{WORK}"]
	ordered = []
	for name in COMMON_C + COMMON_ASM:
		target = OBJ / f"common-{Path(name).stem}.o"
		compile_one(ROOT / name, target, includes)
		ordered.append(target)
	encap = {p: qualify_encap(p, includes) for p in PROFILES}
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
	for profile in PROFILES:
		objects = ordered[:insert_at] + [encap[profile]] + ordered[insert_at:]
		run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
			"-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
			f"-Wl,-T,{ROOT / 'e0v-tail.ld'}", "-o", str(BUILD / profile),
			*(str(path) for path in harness + objects + libraries)])
	manifest = {"control_commit": "b2a4bea", "baseline": BASELINE,
		"profiles": list(PROFILES),
		"source_sha256": {p: hashlib.sha256((SRC / f'encap-{p}.c').read_bytes()).hexdigest()
			for p in PROFILES}}
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
	run(["python3", str(EXP / "tools/audit.py")])


if __name__ == "__main__":
	main()
