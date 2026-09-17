#!/usr/bin/env python3
"""Compile and run the repository-local D3 same-ELF paired diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import statistics
import subprocess
import tempfile


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reversed_assembly(source: str) -> str:
    baseline_marker = ".p2align 5\n.global ntruplus864_exp001_d3_tile_baseline"
    candidate_marker = ".p2align 5\n.global ntruplus864_exp001_d3_tile_vpmaddwd"
    baseline = source.index(baseline_marker)
    candidate = source.index(candidate_marker)
    suffix = source.index('.section .note.GNU-stack,"",@progbits', candidate)
    return source[:baseline] + source[candidate:suffix] + source[baseline:candidate] + source[suffix:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[1]
    asm = root / "asm/d3_vpmaddwd_tile.s"
    harness = root / "bench/bench_d3_vpmaddwd_tile_paired.c"
    header = root / "src/d3_vpmaddwd_tile.h"
    with tempfile.TemporaryDirectory(prefix="ntruplus864-d3-price-") as directory:
        reversed_asm = pathlib.Path(directory) / "d3_vpmaddwd_tile_reversed.s"
        reversed_asm.write_text(reversed_assembly(asm.read_text()))
        placements = {}
        elf_hashes = {}
        for placement, selected_asm in (("normal", asm), ("reversed", reversed_asm)):
            binary = pathlib.Path(directory) / f"d3-paired-{placement}"
            subprocess.run([
                "cc", "-O3", "-fPIE", "-pie", "-Wall", "-Wextra", "-Werror",
                "-mavx2", "-I", str(root / "src"), "-I", str(root),
                str(harness), str(selected_asm), "-o", str(binary),
            ], check=True)
            elf_hashes[placement] = sha(binary)
            launches = []
            for launch in range(args.launches):
                completed = subprocess.run(
                    ["taskset", "-c", str(args.cpu), str(binary)],
                    check=True, text=True, stdout=subprocess.PIPE,
                )
                payload = json.loads(completed.stdout)
                values = {"two-P-plus-official-cubic": [], "direct-packed-vpmaddwd-mr32": []}
                for record in payload["records"]:
                    name = record["implementation"]
                    if name in values:
                        values[name].append(record["median_cycles"])
                control = statistics.median(values["two-P-plus-official-cubic"])
                candidate = statistics.median(values["direct-packed-vpmaddwd-mr32"])
                launches.append({
                    "launch": launch + 1,
                    "control_median_cycles": control,
                    "candidate_median_cycles": candidate,
                    "candidate_minus_control_cycles": candidate - control,
                    "raw": payload,
                })
            deltas = [entry["candidate_minus_control_cycles"] for entry in launches]
            placements[placement] = {
                "summary": {
                    "median_candidate_minus_control_cycles": statistics.median(deltas),
                    "candidate_faster_launches": sum(delta < 0 for delta in deltas),
                    "candidate_slower_launches": sum(delta > 0 for delta in deltas),
                    "ties": sum(delta == 0 for delta in deltas),
                },
                "launches": launches,
            }
    report = {
        "benchmark_class": "repository-local-d3-tile-paired-not-for-promotion",
        "cutpoint": "two packed T3 operands plus zeta -> three coefficient planes",
        "cpu": args.cpu,
        "fresh_launches": args.launches,
        "compiler": "cc -O3 -fPIE -pie -mavx2",
        "elf_sha256": elf_hashes,
        "sources": {str(path.relative_to(root)): sha(path) for path in (asm, harness, header, root / "generated/d3-vpmaddwd-asm-masks.inc")},
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({name: data["summary"] for name, data in placements.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
