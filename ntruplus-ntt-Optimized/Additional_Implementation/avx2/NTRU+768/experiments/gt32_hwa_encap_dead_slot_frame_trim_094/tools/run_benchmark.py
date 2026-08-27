#!/usr/bin/env python3
"""Run balanced F0/FP/F1 fixed-ELF SUPERcop-style measurements."""

from __future__ import annotations

import json
import platform
import random
import re
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
OPERATIONS = ("keypair_cycles", "enc_cycles", "dec_cycles")
PROFILES = ("f0", "fp", "f1")


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


def launch(binary: Path, aslr_off: bool) -> str:
    command = ["taskset", "-c", "1"]
    if aslr_off:
        command.extend(["setarch", platform.machine(), "-R"])
    command.append(str(binary.resolve()))
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    if result.returncode:
        raise SystemExit(result.stdout)
    for operation in OPERATIONS:
        if len(observations(result.stdout, operation)) < 96:
            raise SystemExit(f"too few {operation} observations")
    return result.stdout


def median_ci(samples: list[float]) -> list[float]:
    generator = random.Random(0x094E0F1)
    medians = sorted(statistics.median(generator.choice(samples)
                                      for _ in samples) for _ in range(50000))
    return [medians[1250], medians[48750]]


def main() -> None:
    destination = EXP / "results/formal"
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    destination.mkdir(parents=True)
    records = []
    binaries = {profile: BUILD / profile for profile in PROFILES}
    for aslr_off in (False, True):
        setting = "aslr-off" if aslr_off else "aslr-on"
        directory = destination / setting
        directory.mkdir()
        for block in range(1, 17):
            order = ("f0", "fp", "f1", "f1", "fp", "f0") if block % 2 else \
                    ("f1", "fp", "f0", "f0", "fp", "f1")
            for slot, profile in enumerate(order, 1):
                output = launch(binaries[profile], aslr_off)
                filename = f"block-{block:02d}-slot-{slot}-{profile}.out"
                (directory / filename).write_text(output)
                records.append({"setting": setting, "block": block, "slot": slot,
                                "profile": profile, "file": f"{setting}/{filename}"})

    summary = {}
    for setting in ("aslr-on", "aslr-off"):
        summary[setting] = {}
        selected = [record for record in records if record["setting"] == setting]
        for operation in OPERATIONS:
            blocks = {}
            for record in selected:
                values = observations((destination / record["file"]).read_text(), operation)
                block = blocks.setdefault(record["block"], {p: [] for p in PROFILES})
                block[record["profile"]].append(statistics.median(values))
            effects = {}
            for label, candidate, control in (("FP-F0", "fp", "f0"),
                                               ("F1-FP", "f1", "fp"),
                                               ("F1-F0", "f1", "f0")):
                differences = [statistics.fmean(blocks[n][candidate]) -
                               statistics.fmean(blocks[n][control])
                               for n in sorted(blocks)]
                effects[label] = {"block_differences": differences,
                                  "median": statistics.median(differences),
                                  "median_bootstrap_95ci": median_ci(differences),
                                  "negative_blocks": sum(x < 0 for x in differences)}
            summary[setting][operation] = effects
    manifest = {"schema": "gt32-e0v-dead-slot-frame-trim-094-v1",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "cpu": 1, "blocks": 16,
                "order": "odd F0 FP F1 F1 FP F0; even reversed",
                "summary": summary, "records": records}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    generated = EXP / "generated"
    generated.mkdir(exist_ok=True)
    (generated / "benchmark-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
