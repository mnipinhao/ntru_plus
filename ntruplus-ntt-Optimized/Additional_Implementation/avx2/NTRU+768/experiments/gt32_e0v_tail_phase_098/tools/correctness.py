#!/usr/bin/env python3
"""Run deterministic byte-exact Encap checks for every helper phase."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
BUILD = EXP / "build"
OUT = BUILD / "correctness"
OFFICIAL = ROOT.parents[3] / "third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768"
TEST = ROOT / "experiments/gt32_encap_three_slot_frame_096/tests/deterministic_encap.c"
PHASES = tuple(range(0, 512, 32))


def main() -> None:
	OUT.mkdir(parents=True, exist_ok=True)
	flags = ["-march=native", "-mtune=native", "-O3", "-fwrapv",
		"-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections",
		f"-I{ROOT}", f"-I{OFFICIAL}"]
	order = ["baseinv", "consts", "decap", "fips202", "kem", "keygen", "poly",
		"symmetric", "add", "basemul", "batch_inverse", "cbd", "crepmod3",
		"invntt", "ntt", "ntt_m", "ntt_p", "pack", "KeccakP-1600-AVX2"]
	by_stem = {p.name.removeprefix("common-").removesuffix(".o"): p
		for p in (BUILD / "objects").glob("common-*.o")}
	common = [by_stem[name] for name in order]
	insert_at = order.index("fips202")
	objects = common[:insert_at] + [BUILD / "objects/encap.o"] + common[insert_at:]
	driver = OUT / "driver.o"
	randombytes = OUT / "randombytes.o"
	subprocess.run(["gcc", *flags, "-c", str(TEST), "-o", str(driver)], check=True)
	subprocess.run(["gcc", *flags, "-c", str(OFFICIAL / "randombytes.c"),
		"-o", str(randombytes)], check=True)
	results = {}
	for phase in PHASES:
		binary = OUT / f"phase-{phase:03d}"
		linker = BUILD / f"generated/tail-{phase:03d}.ld"
		subprocess.run(["gcc", *flags, "-Wl,--gc-sections",
			"-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
			f"-Wl,-T,{linker}", "-o", str(binary), str(driver), str(randombytes),
			*(str(path) for path in objects)], check=True)
		results[str(phase)] = subprocess.check_output([str(binary)], text=True).strip()
	if len(set(results.values())) != 1:
		raise SystemExit(json.dumps(results, indent=2))
	result = {"status": "PASS", "profiles": len(PHASES),
		"deterministic_byte_exact": True, "common_output": results["0"]}
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "correctness.json").write_text(json.dumps(result, indent=2) + "\n")
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
