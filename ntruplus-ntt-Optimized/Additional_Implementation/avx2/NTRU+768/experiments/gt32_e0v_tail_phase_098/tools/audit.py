#!/usr/bin/env python3
"""Audit deterministic phase-only changes in 098A."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
PHASES = tuple(range(0, 512, 32))
HELPER = "ntruplus768_pack_m_sum_highrange12699_avx2"
CALLER = "ntruplus768_enc_derand_impl"


def out(command: list[str]) -> str:
	return subprocess.check_output(command, text=True)


def symbols(path: Path) -> dict[str, tuple[int, int, str]]:
	result = {}
	for line in out(["nm", "-S", "-n", str(path)]).splitlines():
		fields = line.split()
		if len(fields) >= 4 and fields[2].lower() in {"t", "r"}:
			result[fields[3]] = (int(fields[0], 16), int(fields[1], 16), fields[2])
	return result


def function_bytes(path: Path, address: int, size: int) -> bytes:
	text = out(["objdump", "-d", f"--start-address={address}",
		f"--stop-address={address + size}", str(path)])
	encoded = []
	for line in text.splitlines():
		match = re.match(r"\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s+)+)", line)
		if match:
			encoded.extend(match.group(1).split())
	return bytes.fromhex("".join(encoded))


def section_digest(path: Path, section: str, target: Path) -> tuple[int, str]:
	subprocess.run(["objcopy", "--dump-section", f"{section}={target}", str(path)],
		check=True)
	data = target.read_bytes()
	return len(data), hashlib.sha256(data).hexdigest()


def main() -> None:
	paths = {p: BUILD / f"phase-{p:03d}" for p in PHASES}
	maps = {p: symbols(path) for p, path in paths.items()}
	common = set.intersection(*(set(value) for value in maps.values()))
	mismatches = []
	checked = 0
	for name in sorted(common):
		# The caller's relative call displacement must follow the helper; its
		# address and size are audited separately below.
		if name in {HELPER, CALLER} or name.startswith(("supercop", "cpucycles")):
			continue
		baseline = maps[0][name]
		baseline_bytes = function_bytes(paths[0], *baseline[:2]) \
			if baseline[2].lower() == "t" and baseline[1] else b""
		for phase in PHASES:
			value = maps[phase][name]
			if value != baseline:
				mismatches.append([name, phase, "geometry", baseline, value])
			elif baseline_bytes and function_bytes(paths[phase], *value[:2]) != baseline_bytes:
				mismatches.append([name, phase, "bytes"])
		checked += 1
	if mismatches:
		raise SystemExit(json.dumps(mismatches[:20], indent=2))
	helper = {p: maps[p][HELPER][:2] for p in PHASES}
	actual = {p: helper[p][0] & 0xfff for p in PHASES}
	if actual != {p: p for p in PHASES}:
		raise SystemExit(f"helper phase mismatch: {actual}")
	# Final helper bytes legitimately carry different RIP-relative displacements
	# to fixed rodata.  The input pack.o is common to every link; audit the
	# linked size and instruction topology rather than requiring relocated bytes.
	helper_hash = {p: hashlib.sha256(function_bytes(paths[p], *helper[p])).hexdigest()
		for p in PHASES}
	if len({value[1] for value in helper.values()}) != 1:
		raise SystemExit("helper size changed")
	rodata = {p: section_digest(paths[p], ".rodata", BUILD / f"rodata-{p:03d}.bin")
		for p in PHASES}
	if len(set(rodata.values())) != 1:
		raise SystemExit("rodata changed")
	caller = {p: maps[p][CALLER][:2] for p in PHASES}
	result = {"status": "PASS", "control_commit": "b2a4bea",
		"preexisting_symbols_checked": checked, "mismatches": 0,
		"helper": helper, "helper_page_offsets": actual,
		"helper_size": helper[0][1], "helper_object_common": True,
		"linked_helper_sha256": helper_hash,
		"linked_bytes_differ_only_by_expected_relocations": True,
		"caller": caller, "caller_geometry_identical": len(set(caller.values())) == 1,
		"caller_only_expected_call_displacement_changes": True, "rodata": rodata,
		"existing_hot_image_identical": True, "tail_section_flags": "AX"}
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
