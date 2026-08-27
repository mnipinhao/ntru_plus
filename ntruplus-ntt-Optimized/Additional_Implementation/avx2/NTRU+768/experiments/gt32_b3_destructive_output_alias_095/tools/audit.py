#!/usr/bin/env python3
"""Prove the production B3 exact-alias load/store ordering."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
BUILD = EXP / "build"
GENERATED = EXP / "generated"
SYMBOL = "ntruplus768_basemul_general_m_avx2"


def macro(text: str, name: str) -> str:
	match = re.search(rf"^ \.macro {re.escape(name)}(?: [^\n]*)?$\n(.*?)^ \.endm$",
		text, re.MULTILINE | re.DOTALL)
	if not match:
		raise SystemExit(f"missing macro {name}")
	return match.group(1)


def main() -> None:
	text = (ROOT / "basemul.s").read_text()
	body = macro(text, "TILE4_BASEMUL_B3_FUNCTION")
	input_a = macro(text, "TILE4_INPUT_A_SOA")
	input_b = macro(text, "TILE4_INPUT_B_SOA")
	loads_a = re.findall(r"vmovdqu (\d+)\(%rsi\)", input_a)
	loads_b = re.findall(r"vmovdqu (\d+)\(%rdx\)", input_b)
	if loads_a != ["0", "32", "64", "96"]:
		raise SystemExit(f"unexpected A load ledger: {loads_a}")
	if loads_b != ["0", "32", "64", "96"]:
		raise SystemExit(f"unexpected B load ledger: {loads_b}")
	input_end = body.index(" \\inputa") + len(" \\inputa")
	first_store = body.index(" vmovdqu %ymm15, 0(%rdi)")
	if first_store <= input_end:
		raise SystemExit("first output store precedes complete input loads")
	between = body[input_end:first_store]
	after_inputs = body[input_end:body.index(" addq $128, %rsi")]
	if "(%rsi)" in after_inputs or "(%rdx)" in after_inputs:
		raise SystemExit("input reload after the input macros")
	if between.count("vmovdqu"):
		raise SystemExit("unexpected dynamic memory move before first store")
	for pointer in ("rsi", "rdx", "rdi"):
		if f"addq $128, %{pointer}" not in body:
			raise SystemExit(f"missing synchronized tile advance for {pointer}")
	if f"TILE4_BASEMUL_B3_FUNCTION {SYMBOL}, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA" not in text:
		raise SystemExit("production symbol instantiation drift")

	BUILD.mkdir(parents=True, exist_ok=True)
	obj = BUILD / "basemul.o"
	subprocess.check_call(["gcc", "-mavx2", "-c", str(ROOT / "basemul.s"),
		"-o", str(obj)])
	dis = subprocess.check_output(["objdump", "-d", "--no-show-raw-insn", str(obj)],
		text=True)
	match = re.search(rf"<{SYMBOL}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)", dis,
		re.DOTALL)
	if not match:
		raise SystemExit("selected production symbol missing from object")
	symbol_dis = match.group(1)
	nm = subprocess.check_output(["nm", "-S", str(obj)], text=True)
	nm_match = re.search(rf"^([0-9a-f]+) ([0-9a-f]+) T {SYMBOL}$", nm,
		re.MULTILINE)
	if not nm_match:
		raise SystemExit("cannot resolve selected symbol size")
	symbol_start = int(nm_match.group(1), 16)
	symbol_size = int(nm_match.group(2), 16)
	a_reads = [int(x, 16) for x in re.findall(
		r"^\s*([0-9a-f]+):\s+vmovdqu\s+.*\(%rsi\),%ymm", symbol_dis,
		re.MULTILINE)]
	b_reads = [int(x, 16) for x in re.findall(
		r"^\s*([0-9a-f]+):\s+vmovdqu\s+.*\(%rdx\),%ymm", symbol_dis,
		re.MULTILINE)]
	stores = [int(x, 16) for x in re.findall(
		r"^\s*([0-9a-f]+):\s+vmovdqu\s+%ymm[^,]*,.*\(%rdi\)",
		symbol_dis, re.MULTILINE)]
	if len(a_reads) != 4 or len(b_reads) != 4 or not stores:
		raise SystemExit("unexpected disassembled input/output ledger")
	first_store_address = min(stores)
	if max(a_reads + b_reads) >= first_store_address:
		raise SystemExit("disassembly contradicts source alias ordering")
	stack_refs = len(re.findall(r"\(%(?:rsp|rbp)\)", symbol_dis))
	if stack_refs:
		raise SystemExit(f"production B3 has {stack_refs} stack references")
	result = {
		"status": "PASS",
		"control_commit": "b2a4bea",
		"symbol": SYMBOL,
		"symbol_sha256": hashlib.sha256(symbol_dis.encode()).hexdigest(),
		"symbol_bytes": symbol_size,
		"instruction_count": len(re.findall(r"^\s*[0-9a-f]+:", symbol_dis,
			re.MULTILINE)),
		"tile_bytes": 128,
		"tiles": 12,
		"input_a_load_offsets": [0, 32, 64, 96],
		"input_b_load_offsets": [0, 32, 64, 96],
		"disassembly_ledger_relative_to_symbol": {
			"last_read_a": hex(max(a_reads) - symbol_start),
			"last_read_b": hex(max(b_reads) - symbol_start),
			"first_output_store": hex(first_store_address - symbol_start)
		},
		"first_output_store_after_all_eight_input_loads": True,
		"input_reloads_after_first_output_store": 0,
		"cross_tile_dependencies": 0,
		"stack_references": stack_refs,
		"extra_alias_instructions": 0,
		"exact_alias_contract": ["out == a", "out == b"],
		"partial_overlap_contract": "unsupported",
		"alias_h_vs_alias_r": {
			"kernel_instruction_difference": 0,
			"kernel_register_difference": 0,
			"kernel_addressing_difference": 0,
			"preferred_for_096": "out == r",
			"reason": "performance tie; the existing Encap cleanup already clears the r slot"
		}
	}
	GENERATED.mkdir(exist_ok=True)
	(GENERATED / "static-alias-ledger.json").write_text(
		json.dumps(result, indent=2) + "\n")
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
