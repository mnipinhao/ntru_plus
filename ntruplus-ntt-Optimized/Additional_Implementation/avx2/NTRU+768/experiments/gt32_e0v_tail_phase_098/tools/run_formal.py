#!/usr/bin/env python3
"""Formal balanced qualification of the four best E0V phases."""

from __future__ import annotations

import json
import random
import re
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
BASELINE = 0
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


def launch(phase: int) -> str:
	result = subprocess.run(["taskset", "-c", "1",
		str((BUILD / f"phase-{phase:03d}").resolve())], text=True,
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	if result.returncode:
		raise SystemExit(result.stdout)
	for operation in OPERATIONS:
		if len(observations(result.stdout, operation)) < 96:
			raise SystemExit(f"too few {operation} observations")
	return result.stdout


def median_ci(samples: list[float]) -> list[float]:
	generator = random.Random(0x098F0A11)
	medians = sorted(statistics.median(generator.choice(samples)
		for _ in samples) for _ in range(50000))
	return [medians[1250], medians[48750]]


def main() -> None:
	sweep = json.loads((EXP / "generated/sweep-summary.json").read_text())
	phases = [BASELINE, *sweep["ranking"][:4]]
	destination = EXP / "results/formal"
	if destination.exists():
		raise SystemExit(f"refusing to overwrite {destination}")
	raw = destination / "raw"
	raw.mkdir(parents=True)
	records = []
	for block in range(1, 17):
		forward = phases if block % 2 else list(reversed(phases))
		order = [*forward, *reversed(forward)]
		for slot, phase in enumerate(order, 1):
			output = launch(phase)
			filename = f"block-{block:02d}-slot-{slot:02d}-phase-{phase:03d}.out"
			(raw / filename).write_text(output)
			records.append({"block": block, "slot": slot, "phase": phase,
				"file": f"raw/{filename}"})
	summary = {}
	for operation in OPERATIONS:
		blocks = {}
		for record in records:
			values = observations((destination / record["file"]).read_text(), operation)
			blocks.setdefault(record["block"], {}).setdefault(record["phase"], []).append(
				statistics.median(values))
		effects = {}
		for phase in phases[1:]:
			differences = [statistics.fmean(blocks[n][phase]) -
				statistics.fmean(blocks[n][BASELINE]) for n in sorted(blocks)]
			effects[f"{phase}-0"] = {"block_differences": differences,
				"median": statistics.median(differences),
				"median_bootstrap_95ci": median_ci(differences),
				"negative_blocks": sum(value < 0 for value in differences)}
		summary[operation] = effects
	manifest = {"schema": "gt32-e0v-tail-phase-098-formal-v1",
		"created_at": datetime.now(timezone.utc).isoformat(), "cpu": 1,
		"aslr": "host-default-on", "blocks": 16, "phases": phases,
		"protocol": "balanced palindrome, two launches/phase/block",
		"summary": summary, "records": records}
	(destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
	generated = EXP / "generated"
	(generated / "formal-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
	print(json.dumps({"phases": phases, "summary": summary}, indent=2))


if __name__ == "__main__":
	main()
