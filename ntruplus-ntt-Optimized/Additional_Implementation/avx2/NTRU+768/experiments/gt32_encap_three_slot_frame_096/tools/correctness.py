#!/usr/bin/env python3
"""Run integration alias, deterministic, KAT, and sanitizer checks for 096."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
BUILD = EXP / "build/correctness"
OFFICIAL = ROOT.parents[3] / "third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768"
COMMON = ["baseinv.c", "consts.c", "decap.c", "fips202.c", "kem.c",
	"keygen.c", "poly.c", "symmetric.c", "add.s", "basemul.s",
	"batch_inverse.s", "cbd.s", "crepmod3.s", "invntt.s", "ntt.s",
	"ntt_m.s", "ntt_p.s", "pack.s", "KeccakP-1600-AVX2.s"]
SOURCES = {"c4": ROOT / "encap.c", "a4": EXP / "encap-a4.c",
	"a4i": EXP / "encap-a4i.c", "a3": EXP / "encap-a3.c"}
EXPECTED_KAT = "22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8"


def run(command: list[str], cwd: Path | None = None,
	env: dict[str, str] | None = None) -> str:
	return subprocess.check_output(command, cwd=cwd, env=env, text=True)


def build(profile: str, output: Path, flags: list[str], harness: list[Path]) -> None:
	run(["gcc", *flags, f"-I{ROOT}", f"-I{OFFICIAL}", "-Wl,--gc-sections",
		"-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
		f"-Wl,-T,{ROOT / 'e0v-tail.ld'}", "-o", str(output),
		*(str(path) for path in harness), str(SOURCES[profile]),
		str(EXP / f"build/pad-{profile}.s"),
		*(str(ROOT / name) for name in COMMON)])


def main() -> None:
	BUILD.mkdir(parents=True, exist_ok=True)
	flags = ["-march=native", "-mtune=native", "-O3", "-fwrapv",
		"-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections"]
	alias = BUILD / "alias-integration"
	run(["gcc", *flags, f"-I{ROOT}", "-o", str(alias),
		str(EXP / "tests/alias_integration.c"), str(ROOT / "basemul.s"),
		str(ROOT / "ntt.s"), str(ROOT / "ntt_m.s"), str(ROOT / "pack.s")])
	alias_result = run([str(alias)]).strip()
	deterministic = {}
	for profile in SOURCES:
		binary = BUILD / f"deterministic-{profile}"
		build(profile, binary, flags, [OFFICIAL / "randombytes.c",
			EXP / "tests/deterministic_encap.c"])
		deterministic[profile] = run([str(binary)]).strip()
	if len(set(deterministic.values())) != 1:
		raise SystemExit(f"deterministic mismatch: {deterministic}")
	kat = {}
	for profile in ("c4", "a3"):
		binary = BUILD / f"kat-{profile}"
		build(profile, binary, flags + ["-Wno-unused-result"],
			[OFFICIAL / "kat/PQCgenKAT_kem.c", OFFICIAL / "kat/aes.c",
			 OFFICIAL / "kat/rng.c"])
		run_dir = BUILD / f"kat-run-{profile}"
		if run_dir.exists():
			shutil.rmtree(run_dir)
		run_dir.mkdir()
		run([str(binary)], cwd=run_dir)
		response = run_dir / "PQCkemKAT_2336.rsp"
		digest = hashlib.sha256(response.read_bytes()).hexdigest()
		if digest != EXPECTED_KAT:
			raise SystemExit(f"KAT mismatch for {profile}: {digest}")
		kat[profile] = {"bytes": response.stat().st_size, "sha256": digest}
	sanitized = BUILD / "deterministic-a3-sanitized"
	sanitize_flags = ["-march=native", "-mtune=native", "-O1", "-fwrapv",
		"-fno-omit-frame-pointer", "-fsanitize=address,undefined",
		"-fno-sanitize-recover=all", "-ffunction-sections", "-fdata-sections"]
	build("a3", sanitized, sanitize_flags,
		[OFFICIAL / "randombytes.c", EXP / "tests/deterministic_encap.c"])
	env = os.environ.copy()
	env["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
	env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
	sanitizer = run([str(sanitized)], env=env).strip()
	result = {"status": "PASS", "alias_integration": alias_result,
		"deterministic": deterministic, "kat": kat, "asan_ubsan_a3": sanitizer}
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "correctness.json").write_text(json.dumps(result, indent=2) + "\n")
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
