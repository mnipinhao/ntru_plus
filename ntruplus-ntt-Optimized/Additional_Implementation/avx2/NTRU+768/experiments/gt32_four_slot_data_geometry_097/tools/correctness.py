#!/usr/bin/env python3
"""Run deterministic byte-exact Encap checks for all 24 layouts."""

from __future__ import annotations

import itertools
import json
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
BUILD = EXP / "build"
OUT = BUILD / "correctness"
OFFICIAL = ROOT.parents[3] / "third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768"
TEST = ROOT / "experiments/gt32_encap_three_slot_frame_096/tests/deterministic_encap.c"
PROFILES = tuple("".join(p) for p in itertools.permutations("hrmc"))


def run(command: list[str]) -> str:
	return subprocess.check_output(command, text=True).strip()


def main() -> None:
	OUT.mkdir(parents=True, exist_ok=True)
	flags = ["-march=native", "-mtune=native", "-O3", "-fwrapv",
		"-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections",
		f"-I{ROOT}", f"-I{OFFICIAL}"]
	common = sorted((BUILD / "objects").glob("common-*.o"))
	# Restore the production link order used by build.py.
	order = ["baseinv", "consts", "decap", "fips202", "kem", "keygen", "poly",
		"symmetric", "add", "basemul", "batch_inverse", "cbd", "crepmod3",
		"invntt", "ntt", "ntt_m", "ntt_p", "pack", "KeccakP-1600-AVX2"]
	by_stem = {p.name.removeprefix("common-").removesuffix(".o"): p for p in common}
	common = [by_stem[name] for name in order]
	insert_at = order.index("fips202")
	driver = OUT / "driver.o"
	randombytes = OUT / "randombytes.o"
	subprocess.run(["gcc", *flags, "-c", str(TEST), "-o", str(driver)], check=True)
	subprocess.run(["gcc", *flags, "-c", str(OFFICIAL / "randombytes.c"),
		"-o", str(randombytes)], check=True)
	results = {}
	for profile in PROFILES:
		objects = common[:insert_at] + [BUILD / f"objects/encap-{profile}.o"] + common[insert_at:]
		binary = OUT / profile
		subprocess.run(["gcc", *flags, "-Wl,--gc-sections",
			"-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
			f"-Wl,-T,{ROOT / 'e0v-tail.ld'}", "-o", str(binary), str(driver),
			str(randombytes), *(str(path) for path in objects)], check=True)
		results[profile] = run([str(binary)])
	if len(set(results.values())) != 1:
		raise SystemExit(json.dumps(results, indent=2))
	result = {"status": "PASS", "profiles": len(PROFILES),
		"deterministic_byte_exact": True, "common_output": results["hrmc"]}
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "correctness.json").write_text(json.dumps(result, indent=2) + "\n")
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
