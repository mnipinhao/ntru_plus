#!/usr/bin/env python3
"""Build current GT Clean and Official with one native SUPERcop harness."""

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
MEASURES = sorted((SUPER / "bench").glob("*/work/compile/measure.c"))
if len(MEASURES) != 1:
	raise SystemExit("expected one prepared SUPERcop measure work directory")
WORK = MEASURES[0].parent
BENCH = WORK.parents[1]
BUILD = EXP / "build"
OBJ = BUILD / "official-objects"
FLAGS = ["-DSUPERCOP", '-DCOMPILER="gcc-supercop-099"', "-DLOOPS=3",
	"-march=native", "-mtune=native", "-O3", "-fwrapv", "-fPIC", "-fPIE",
	"-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections"]
OFFICIAL_SOURCES = ["asm/add.s", "asm/baseinv.s", "asm/basemul.s", "asm/cbd.s",
	"asm/crepmod3.s", "asm/invntt.s", "asm/ntt.s", "asm/pack.s", "consts.c",
	"kem.c", "poly.c", "symmetric.c", "fips202/fips202.c",
	"fips202/KeccakP-1600-AVX2.s"]


def run(command: list[str]) -> None:
	subprocess.run(command, check=True)


def main() -> None:
	if BUILD.exists():
		shutil.rmtree(BUILD)
	OBJ.mkdir(parents=True)
	# The production-owned builder preserves the E0V caller slot and RX-tail
	# linker contract; its selected image is measure-e0v.
	run(["python3", str(ROOT / "qualified/build-supercop.py"),
		"--supercop-root", str(SUPER), "--output", str(BUILD / "gt-qualified")])
	shutil.copy2(BUILD / "gt-qualified/measure-e0v", BUILD / "gt-clean")
	# SUPERcop's instrumented randombytes.h must precede the implementation's
	# standalone test header.
	includes = [f"-I{SUPER / 'include'}", f"-I{BENCH / 'include'}",
		f"-I{BENCH / 'include/amd64'}", f"-I{BENCH / 'include/nontimecop/amd64'}",
		f"-I{WORK}", f"-I{OFFICIAL}", f"-I{OFFICIAL / 'fips202'}"]
	objects = []
	for index, name in enumerate(OFFICIAL_SOURCES):
		target = OBJ / f"source-{index:02d}.o"
		extra = ["-DNTRUPLUS_SUPERCOP"] if name.endswith(".c") else []
		run(["gcc", *FLAGS, *extra, *includes, "-c", str(OFFICIAL / name), "-o", str(target)])
		if name == "kem.c":
			prefix = "crypto_kem_ntruplus768_avx2_gt32_d4norm_077_constbranchindex"
			run(["objcopy",
				f"--redefine-sym=crypto_kem_keypair={prefix}_keypair",
				f"--redefine-sym=crypto_kem_enc={prefix}_enc",
				f"--redefine-sym=crypto_kem_dec={prefix}_dec", str(target)])
		objects.append(target)
	harness = []
	for name in ("measure-anything.c", "measure.c"):
		target = OBJ / f"harness-{Path(name).stem}.o"
		run(["gcc", *FLAGS, *includes, "-c", str(WORK / name), "-o", str(target)])
		harness.append(target)
	libraries = [BENCH / "lib/amd64/libfastrandombytes.a",
		BENCH / "lib/amd64/libkernelrandombytes.a",
		BENCH / "lib/nontimecop/amd64/libcpucycles.a",
		BENCH / "lib/amd64/libsupercop.a"]
	run(["gcc", "-pie", "-Wl,--build-id=none", "-Wl,--gc-sections",
		"-o", str(BUILD / "official"),
		*(str(path) for path in harness + objects + libraries)])
	manifest = {"baseline_commit": "b2a4bea", "compiler": "gcc-supercop-099",
		"sha256": {name: hashlib.sha256((BUILD / name).read_bytes()).hexdigest()
			for name in ("official", "gt-clean")},
		"bytes": {name: (BUILD / name).stat().st_size for name in ("official", "gt-clean")}}
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
	print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
	main()
