#!/usr/bin/env python3
"""Run normal/reversed fixed-ELF ABBA campaigns with ASLR on and off."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import LOCK_PATH, read_lock, sha256_file

DEFAULT_OPERATIONS = ("keypair_cycles", "enc_cycles", "dec_cycles")


def elf_info(path: Path) -> dict[str, object]:
    if not path.is_file() or not path.stat().st_mode & 0o111:
        raise SystemExit(f"not an executable ELF: {path}")
    info: dict[str, object] = {"path": str(path.resolve()), "sha256": sha256_file(path)}
    for command, key in ((["size", "-A", str(path)], "sections"),
                         (["nm", "-n", str(path)], "symbols"),
                         (["readelf", "-h", str(path)], "elf_header")):
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode:
            raise SystemExit(f"failed to inspect ELF with {command[0]}: {path}")
        info[key] = result.stdout
    if not re.search(r"Type:\s+DYN\b", str(info["elf_header"])):
        raise SystemExit(f"formal production-like ELF must be PIE (ET_DYN): {path}")
    return info


def observations(text: str, operation: str) -> list[int]:
    values: list[int] = []
    for line in text.splitlines():
        if f" {operation} " in f" {line} ":
            tail = line.split(operation, 1)[1]
            encoded = re.findall(r"[+-]?\d+", tail)
            if len(encoded) >= 2:
                center = int(encoded[0])
                values.extend(center + int(delta) for delta in encoded[1:])
    return values


def launch(binary: Path, cpu: int, aslr_off: bool,
           operations: tuple[str, ...], minimum: int) -> tuple[str, dict[str, int]]:
    command = ["taskset", "-c", str(cpu)]
    if aslr_off:
        command.extend(["setarch", platform.machine(), "-R"])
    command.append(str(binary.resolve()))
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        raise SystemExit(f"fixed ELF failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")
    counts = {operation: len(observations(result.stdout, operation)) for operation in operations}
    short = {operation: count for operation, count in counts.items() if count < minimum}
    if short:
        raise SystemExit(
            f"fixed ELF produced fewer than {minimum} observations: {short}")
    return result.stdout, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--official-reversed", type=Path, required=True)
    parser.add_argument("--candidate-reversed", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--blocks", type=int, default=16)
    parser.add_argument("--compiler-recipe", required=True)
    parser.add_argument("--operation", action="append", dest="operations",
                        help="measured output label; repeat for component ELFs")
    parser.add_argument("--operations-file", type=Path,
                        help="newline-delimited operation labels")
    parser.add_argument("--minimum-observations", type=int, default=96)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.blocks != 16:
        raise SystemExit("formal paired campaigns require exactly 16 blocks")
    if args.operations and args.operations_file:
        raise SystemExit("use --operation or --operations-file, not both")
    if args.operations_file:
        operations = tuple(line.strip() for line in
                           args.operations_file.read_text(encoding="utf-8").splitlines()
                           if line.strip() and not line.lstrip().startswith("#"))
    else:
        operations = tuple(args.operations or DEFAULT_OPERATIONS)
    if not operations or len(set(operations)) != len(operations):
        raise SystemExit("operation labels must be nonempty and unique")
    if args.minimum_observations < 1:
        raise SystemExit("--minimum-observations must be positive")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    args.output.mkdir(parents=True)

    binaries = {
        "normal": {"official": args.official, "candidate": args.candidate},
        "reversed": {"official": args.official_reversed, "candidate": args.candidate_reversed},
    }
    aslr_value = Path("/proc/sys/kernel/randomize_va_space").read_text().strip()
    if aslr_value == "0":
        raise SystemExit("ASLR-on control requested but kernel randomize_va_space is 0")
    binary_info = {placement: {name: elf_info(path) for name, path in pair.items()}
                   for placement, pair in binaries.items()}
    for name in ("official", "candidate"):
        if binary_info["normal"][name]["sha256"] == binary_info["reversed"][name]["sha256"]:
            raise SystemExit(f"{name} reversed-placement ELF is identical to the normal ELF")
    manifest = {
        **read_lock(),
        "benchmark_class": "fixed-elf-paired",
        "blocks": args.blocks,
        "compiler_recipe": args.compiler_recipe,
        "cpu": args.cpu,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "operations": list(operations),
        "observations_per_operation_per_launch_minimum": args.minimum_observations,
        "binaries": binary_info,
    }
    records = []
    for placement, pair in binaries.items():
        for aslr_off in (False, True):
            setting = f"{placement}-aslr-{'off' if aslr_off else 'on'}"
            setting_dir = args.output / setting
            setting_dir.mkdir()
            launch_number = 0
            for block in range(1, args.blocks + 1):
                order = ("official", "candidate", "candidate", "official") if block % 2 else (
                    "candidate", "official", "official", "candidate")
                for slot, implementation in enumerate(order, 1):
                    launch_number += 1
                    output, counts = launch(pair[implementation], args.cpu, aslr_off,
                                            operations, args.minimum_observations)
                    filename = f"block-{block:02d}-slot-{slot}-{implementation}.out"
                    (setting_dir / filename).write_text(output, encoding="utf-8")
                    records.append({"setting": setting, "block": block, "slot": slot,
                                    "implementation": implementation, "file": f"{setting}/{filename}",
                                    "observations": counts})
            if launch_number != 64:
                raise AssertionError("formal setting did not produce 64 fresh launches")
    manifest["launches"] = records
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(f"completed fixed-ELF paired campaign: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
