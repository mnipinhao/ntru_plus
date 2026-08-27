#!/usr/bin/env python3
"""Run the static and exact-correctness parts of gate 095."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
BUILD = EXP / "build"
GENERATED = EXP / "generated"


def run(command: list[str], env: dict[str, str] | None = None) -> str:
	return subprocess.check_output(command, text=True, env=env).strip()


def build(output: Path, flags: list[str]) -> None:
	subprocess.check_call([
		"gcc", *flags, f"-I{ROOT}", "-o", str(output),
		str(EXP / "tests/test.c"), str(ROOT / "consts.c"),
		str(ROOT / "basemul.s"),
		str(ROOT / "ntt.s"), str(ROOT / "ntt_m.s"), str(ROOT / "pack.s")
	])


def main() -> None:
	BUILD.mkdir(parents=True, exist_ok=True)
	GENERATED.mkdir(exist_ok=True)
	static = run(["python3", str(EXP / "tools/audit.py")])

	native = BUILD / "test-alias"
	build(native, ["-O3", "-march=native", "-mtune=native", "-fwrapv",
		"-fomit-frame-pointer"])
	native_result = run([str(native)])

	sanitized = BUILD / "test-alias-sanitized"
	build(sanitized, ["-O1", "-march=native", "-mtune=native", "-fwrapv",
		"-fno-omit-frame-pointer", "-fsanitize=address,undefined",
		"-fno-sanitize-recover=all"])
	env = os.environ.copy()
	env["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
	env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
	sanitized_result = run([str(sanitized)], env=env)

	result = {
		"status": "PASS",
		"control_commit": "b2a4bea",
		"static": json.loads(static),
		"native": native_result,
		"asan_ubsan": sanitized_result,
		"production_modified": False,
		"next_gate": "096 — three-slot production frame"
	}
	(GENERATED / "result.json").write_text(json.dumps(result, indent=2) + "\n")
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
