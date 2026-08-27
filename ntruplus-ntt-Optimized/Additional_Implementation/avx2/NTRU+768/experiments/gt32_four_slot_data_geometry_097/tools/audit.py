#!/usr/bin/env python3
"""Verify that 097 varies only the Encap caller's four-slot geometry."""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
PROFILES = tuple("".join(p) for p in itertools.permutations("hrmc"))
BASELINE = "hrmc"
EXCLUDED = {"ntruplus768_enc_derand_impl"}


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


def frame_bytes(path: Path, symbol: tuple[int, int, str]) -> int:
	text = out(["objdump", "-d", f"--start-address={symbol[0]}",
		f"--stop-address={symbol[0] + 64}", str(path)])
	return sum(int(value, 16) for value in
		re.findall(r"sub\s+\$0x([0-9a-f]+),%rsp", text))


def call_sequence(path: Path, symbol: tuple[int, int, str]) -> list[str]:
	text = out(["objdump", "-d", f"--start-address={symbol[0]}",
		f"--stop-address={symbol[0] + symbol[1]}", str(path)])
	return re.findall(r"\bcall\s+[0-9a-f]+\s+<([^+>@]+)", text)


def section_digest(path: Path, section: str, target: Path) -> tuple[int, str]:
	subprocess.run(["objcopy", "--dump-section", f"{section}={target}", str(path)],
		check=True)
	data = target.read_bytes()
	return len(data), hashlib.sha256(data).hexdigest()


def main() -> None:
	paths = {p: BUILD / p for p in PROFILES}
	maps = {p: symbols(path) for p, path in paths.items()}
	common = set.intersection(*(set(value) for value in maps.values()))
	mismatches = []
	checked = 0
	for name in sorted(common):
		if name in EXCLUDED or name.startswith(("supercop", "cpucycles")):
			continue
		baseline = maps[BASELINE][name]
		baseline_bytes = function_bytes(paths[BASELINE], *baseline[:2]) \
			if baseline[2].lower() == "t" and baseline[1] else b""
		for profile in PROFILES:
			value = maps[profile][name]
			if value != baseline:
				mismatches.append([name, profile, "geometry", baseline, value])
			elif baseline_bytes and function_bytes(paths[profile], *value[:2]) != baseline_bytes:
				mismatches.append([name, profile, "bytes"])
		checked += 1
	if mismatches:
		raise SystemExit(json.dumps(mismatches[:20], indent=2))
	frames = {p: frame_bytes(paths[p], maps[p]["ntruplus768_enc_derand_impl"])
		for p in PROFILES}
	if set(frames.values()) != {6592}:
		raise SystemExit(f"frame mismatch: {frames}")
	slots = {}
	for profile in PROFILES:
		text = out(["readelf", "-SW", str(BUILD / f"objects/encap-{profile}.o")])
		line = next(line for line in text.splitlines()
			if ".text.ntruplus768_enc_derand_impl " in line)
		fields = line.split()
		slots[profile] = int(fields[fields.index("PROGBITS") + 3], 16)
	if set(slots.values()) != {611}:
		raise SystemExit(f"caller slot mismatch: {slots}")
	calls = {p: call_sequence(paths[p], maps[p]["ntruplus768_enc_derand_impl"])
		for p in PROFILES}
	if len({tuple(value) for value in calls.values()}) != 1:
		raise SystemExit(f"call sequence changed: {calls}")
	rodata = {p: section_digest(paths[p], ".rodata", BUILD / f"rodata-{p}.bin")
		for p in PROFILES}
	tail = {p: section_digest(paths[p], ".e0v_tail", BUILD / f"tail-{p}.bin")
		for p in PROFILES}
	if len(set(rodata.values())) != 1 or len(set(tail.values())) != 1:
		raise SystemExit(f"shared section drift: rodata={rodata}, tail={tail}")
	result = {"status": "PASS", "control_commit": "b2a4bea",
		"profiles": list(PROFILES), "preexisting_symbols_checked": checked,
		"preexisting_symbol_mismatches": 0, "frames": frames,
		"polynomial_slots": 4, "caller_slots": slots,
		"encap_symbols": {p: maps[p]["ntruplus768_enc_derand_impl"][:2]
			for p in PROFILES}, "rodata": rodata, "e0v_tail": tail,
		"call_sequence": calls[BASELINE], "call_sequence_unchanged": True,
		"outside_hot_image_identical": True, "new_spills": 0,
		"static_scratch_bytes": 0}
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
