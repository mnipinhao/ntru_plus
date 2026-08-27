#!/usr/bin/env python3
"""Run the formal current-GT versus Official SUPERCOP comparison."""

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
RESULTS = EXP / "results"
RAW = RESULTS / "raw"
BINARIES = {"official": BUILD / "official", "gt_clean": BUILD / "gt-clean"}
OPERATIONS = ("keypair", "enc", "dec")


def decode_line(line: str) -> list[int]:
	fields = line.split()
	base = int(fields[-2])
	return [base + int(item) for item in re.findall(r"[+-]\d+", fields[-1])]


def observations(text: str) -> dict[str, list[int]]:
	result = {operation: [] for operation in OPERATIONS}
	for line in text.splitlines():
		for operation in OPERATIONS:
			if f" {operation}_cycles " in f" {line} ":
				result[operation].extend(decode_line(line))
	if any(len(values) < 96 for values in result.values()):
		raise RuntimeError({key: len(value) for key, value in result.items()})
	return result


def stabilized_quartiles(values: list[int]) -> list[float]:
	expanded = sorted(value for value in values for _ in range(8))
	count = len(values)
	return [sum(expanded[count + 2 * count * index:
		count + 2 * count * (index + 1)]) / (2 * count) for index in range(3)]


def bootstrap_ci(values: list[float], seed: int) -> list[float]:
	generator = random.Random(seed)
	medians = sorted(statistics.median(generator.choice(values) for _ in values)
		for _ in range(50000))
	return [medians[1250], medians[48750]]


def launch(binary: Path) -> tuple[str, dict[str, list[int]]]:
	completed = subprocess.run(["taskset", "-c", "1", str(binary.resolve())],
		text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	if completed.returncode:
		raise RuntimeError(completed.stdout)
	return completed.stdout, observations(completed.stdout)


def main() -> None:
	if RESULTS.exists():
		raise SystemExit(f"refusing to overwrite {RESULTS}")
	RAW.mkdir(parents=True)
	launches = []
	run_number = 0
	for block in range(1, 17):
		order = ("official", "gt_clean", "gt_clean", "official") if block % 2 else \
			("gt_clean", "official", "official", "gt_clean")
		for position, implementation in enumerate(order, 1):
			run_number += 1
			output, measured = launch(BINARIES[implementation])
			raw = RAW / f"run-{run_number:03d}-block-{block:02d}-pos-{position}-{implementation}.out"
			raw.write_text(output)
			launches.append({"run": run_number, "block": block, "position": position,
				"implementation": implementation, "raw": str(raw),
				"observations": measured,
				"launch_q2": {operation: stabilized_quartiles(measured[operation])[1]
					for operation in OPERATIONS}})
	aggregate = {}
	for implementation in BINARIES:
		aggregate[implementation] = {}
		selected = [entry for entry in launches if entry["implementation"] == implementation]
		for operation in OPERATIONS:
			values = [value for entry in selected for value in entry["observations"][operation]]
			q = stabilized_quartiles(values)
			aggregate[implementation][operation] = {"observations": len(values),
				"launches": len(selected), "stabilized_quartiles": q, "q2_cycles": q[1]}
	comparison = {}
	for index, operation in enumerate(OPERATIONS):
		deltas = []
		for block in range(1, 17):
			selected = [entry for entry in launches if entry["block"] == block]
			means = {implementation: statistics.fmean(entry["launch_q2"][operation]
				for entry in selected if entry["implementation"] == implementation)
				for implementation in BINARIES}
			deltas.append(means["gt_clean"] - means["official"])
		official = aggregate["official"][operation]["q2_cycles"]
		gt = aggregate["gt_clean"][operation]["q2_cycles"]
		comparison[operation] = {"official_q2_cycles": official, "gt_q2_cycles": gt,
			"aggregate_gt_minus_official": gt - official,
			"relative_percent": 100 * (gt - official) / official,
			"paired_block_median_delta": statistics.median(deltas),
			"favorable_blocks": sum(value < 0 for value in deltas), "blocks": 16,
			"bootstrap_95_ci": bootstrap_ci(deltas, 20260827 + index),
			"block_deltas": deltas}
	result = {"schema": "gt32-current-vs-official-099-v1",
		"created_at": datetime.now(timezone.utc).isoformat(), "cpu": 1,
		"aslr": "enabled", "sequence": "O/G/G/O alternating with reverse",
		"estimator": "SUPERcop stabilized quartiles; Q2 primary",
		"frequency_policy": {
			"intel_pstate_no_turbo": Path("/sys/devices/system/cpu/intel_pstate/no_turbo").read_text().strip(),
			"cpu1_governor": Path("/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor").read_text().strip(),
			"cpu1_max_khz": Path("/sys/devices/system/cpu/cpu1/cpufreq/scaling_max_freq").read_text().strip()},
		"aggregate": aggregate, "comparison": comparison, "launches": launches}
	(RESULTS / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
	generated = EXP / "generated"
	generated.mkdir(exist_ok=True)
	(generated / "benchmark-summary.json").write_text(json.dumps({
		"aggregate": aggregate, "comparison": comparison}, indent=2) + "\n")
	print(json.dumps({"aggregate": aggregate, "comparison": comparison}, indent=2))


if __name__ == "__main__":
	main()
