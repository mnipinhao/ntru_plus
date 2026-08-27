#!/usr/bin/env python3
"""Directional ASLR-on SUPERCOP sweep over all four-slot layouts."""

from __future__ import annotations

import itertools
import json
import random
import re
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
PROFILES = tuple("".join(p) for p in itertools.permutations("hrmc"))
BASELINE = "hrmc"
OPERATIONS = ("keypair_cycles", "enc_cycles", "dec_cycles")


def observations(text: str, operation: str) -> list[int]:
	values = []
	for line in text.splitlines():
		if f" {operation} " not in f" {line} ":
			continue
		encoded = re.findall(r"[+-]?\d+", line.split(operation, 1)[1])
		if len(encoded) >= 2:
			center = int(encoded[0])
			values.extend(center + int(delta) for delta in encoded[1:])
	return values


def launch(binary: Path) -> str:
	result = subprocess.run(["taskset", "-c", "1", str(binary.resolve())],
		text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	if result.returncode:
		raise SystemExit(result.stdout)
	for operation in OPERATIONS:
		if len(observations(result.stdout, operation)) < 96:
			raise SystemExit(f"too few {operation} observations")
	return result.stdout


def median_ci(samples: list[float], seed: int = 0x0975A33D) -> list[float]:
	generator = random.Random(seed)
	medians = sorted(statistics.median(generator.choice(samples)
		for _ in samples) for _ in range(50000))
	return [medians[1250], medians[48750]]


def main() -> None:
	destination = EXP / "results/sweep"
	if destination.exists():
		raise SystemExit(f"refusing to overwrite {destination}")
	raw = destination / "raw"
	raw.mkdir(parents=True)
	records = []
	others = [p for p in PROFILES if p != BASELINE]
	for block in range(1, 9):
		order = others.copy()
		random.Random(0x970000 + block).shuffle(order)
		order.insert(0, BASELINE)
		order.insert(12, BASELINE)
		order.append(BASELINE)
		if block % 2 == 0:
			order.reverse()
		for slot, profile in enumerate(order, 1):
			output = launch(BUILD / profile)
			filename = f"block-{block:02d}-slot-{slot:02d}-{profile}.out"
			(raw / filename).write_text(output)
			records.append({"block": block, "slot": slot, "profile": profile,
				"file": f"raw/{filename}"})
	summary = {}
	for operation in OPERATIONS:
		by_block = {}
		for record in records:
			values = observations((destination / record["file"]).read_text(), operation)
			by_block.setdefault(record["block"], {}).setdefault(record["profile"], []).append(
				statistics.median(values))
		profiles = {}
		for profile in PROFILES:
			differences = []
			for block in sorted(by_block):
				control = statistics.fmean(by_block[block][BASELINE])
				candidate = control if profile == BASELINE else by_block[block][profile][0]
				differences.append(candidate - control)
			profiles[profile] = {"block_differences": differences,
				"median": statistics.median(differences),
				"median_bootstrap_95ci": median_ci(differences),
				"negative_blocks": sum(value < 0 for value in differences)}
		summary[operation] = profiles
	ranking = sorted((p for p in PROFILES if p != BASELINE),
		key=lambda p: (summary["enc_cycles"][p]["median"],
			-summary["enc_cycles"][p]["negative_blocks"], p))
	manifest = {"schema": "gt32-four-slot-data-geometry-097-sweep-v1",
		"created_at": datetime.now(timezone.utc).isoformat(), "cpu": 1,
		"aslr": "host-default-on", "blocks": 8,
		"protocol": "three baseline anchors plus one launch per candidate per block",
		"ranking": ranking, "summary": summary, "records": records}
	(destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "sweep-summary.json").write_text(json.dumps({
		"ranking": ranking, "summary": summary}, indent=2) + "\n")
	print(json.dumps({"top": ranking[:8], "enc_cycles": {
		p: summary["enc_cycles"][p] for p in ranking[:8]}}, indent=2))


if __name__ == "__main__":
	main()
