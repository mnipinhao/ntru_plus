#!/usr/bin/env python3
"""Independent two-profile confirmation of phase 448 and total KEM score."""

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
CONTROL = 0
CANDIDATE = 448
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
	generator = random.Random(0x098C0F17)
	medians = sorted(statistics.median(generator.choice(samples)
		for _ in samples) for _ in range(50000))
	return [medians[1250], medians[48750]]


def effect(differences: list[float]) -> dict[str, object]:
	return {"block_differences": differences,
		"median": statistics.median(differences),
		"median_bootstrap_95ci": median_ci(differences),
		"negative_blocks": sum(value < 0 for value in differences)}


def main() -> None:
	destination = EXP / "results/confirmation"
	if destination.exists():
		raise SystemExit(f"refusing to overwrite {destination}")
	raw = destination / "raw"
	raw.mkdir(parents=True)
	records = []
	for block in range(1, 33):
		order = (CONTROL, CANDIDATE, CANDIDATE, CONTROL) if block % 2 else \
			(CANDIDATE, CONTROL, CONTROL, CANDIDATE)
		for slot, phase in enumerate(order, 1):
			output = launch(phase)
			filename = f"block-{block:02d}-slot-{slot}-phase-{phase:03d}.out"
			(raw / filename).write_text(output)
			records.append({"block": block, "slot": slot, "phase": phase,
				"file": f"raw/{filename}"})
	blocks = {}
	for record in records:
		entry = blocks.setdefault(record["block"], {}).setdefault(record["phase"], {})
		for operation in OPERATIONS:
			values = observations((destination / record["file"]).read_text(), operation)
			entry.setdefault(operation, []).append(statistics.median(values))
	deltas = {operation: [] for operation in OPERATIONS}
	combined = []
	for block in sorted(blocks):
		block_sum = 0.0
		for operation in OPERATIONS:
			delta = statistics.fmean(blocks[block][CANDIDATE][operation]) - \
				statistics.fmean(blocks[block][CONTROL][operation])
			deltas[operation].append(delta)
			block_sum += delta
		combined.append(block_sum)
	summary = {operation: effect(values) for operation, values in deltas.items()}
	summary["equal_weight_kem_total"] = effect(combined)
	manifest = {"schema": "gt32-e0v-tail-phase-098-confirmation-v1",
		"created_at": datetime.now(timezone.utc).isoformat(), "cpu": 1,
		"aslr": "host-default-on", "blocks": 32, "control": CONTROL,
		"candidate": CANDIDATE,
		"protocol": "balanced ABBA/BAAB, two launches/profile/block",
		"summary": summary, "records": records}
	(destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
	generated = EXP / "generated"
	(generated / "confirmation-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
	print(json.dumps(summary, indent=2))


if __name__ == "__main__":
	main()
