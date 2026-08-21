#!/usr/bin/env python3
"""Build byte-identical fixed-address epilogue variants and run paired launches."""

from __future__ import annotations

import json
import os
import pathlib
import re
import statistics
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
EXP = pathlib.Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
RESULTS = EXP / "results"

EDGES = {
    "frontend_m": "ntruplus768_ntt_frontend_avx2",
    "frontend_p": "ntruplus768_ntt_frontend_avx2",
    "nttm_pack": "ntruplus768_ntt_m_avx2",
    "nttm_b3": "ntruplus768_ntt_m_avx2",
    "b3scale_inv": "ntruplus768_basemul_scale_m_avx2",
    "b3general_add": "ntruplus768_basemul_general_m_avx2",
    "invcore_tail": "ntruplus768_invntt_m_avx2",
    "invtail_crep": "ntruplus768_invntt_tail_avx2",
}

LINE = re.compile(
    r"region=(\S+) tsc=([-0-9.]+) core=([-0-9.]+) "
    r"instructions=([-0-9.]+)"
)


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, **kwargs)


def build() -> pathlib.Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    binary = BUILD / "bench_control"
    sources = [
        EXP / "bench_internal_edges.c",
        ROOT / "baseinv.c",
        ROOT / "consts.c",
        ROOT / "ntt.s",
        ROOT / "ntt_m.s",
        ROOT / "ntt_p.s",
        ROOT / "basemul.s",
        ROOT / "batch_inverse.s",
        ROOT / "invntt.s",
        ROOT / "pack.s",
        ROOT / "add.s",
        ROOT / "crepmod3.s",
    ]
    run(
        [
            "gcc", "-O3", "-mavx2", "-march=native", "-mtune=native",
            "-fno-pie", "-no-pie", "-ffunction-sections", "-fdata-sections",
            "-Wl,--gc-sections", "-I", str(ROOT), "-o", str(binary),
            *map(str, sources),
        ]
    )
    return binary


def parse(binary: pathlib.Path, region: str) -> dict[str, float]:
    command = [str(binary), region]
    taskset = subprocess.run(
        ["taskset", "-pc", str(os.getpid())], capture_output=True, text=True
    )
    if taskset.returncode == 0:
        allowed = re.search(r":\s*([0-9]+)(?:[-,]|$)", taskset.stdout)
        if allowed:
            command = ["taskset", "-c", allowed.group(1), *command]
    completed = run(command, capture_output=True)
    match = LINE.search(completed.stdout)
    if not match:
        raise RuntimeError(completed.stdout + completed.stderr)
    return {
        "tsc": float(match.group(2)),
        "core": float(match.group(3)),
        "instructions": float(match.group(4)),
    }


def main() -> None:
    control = build()
    patcher = EXP / "tools" / "patch_leaf_epilogue.py"
    variants: dict[str, pathlib.Path] = {}
    nop_variants: dict[str, pathlib.Path] = {}
    for symbol in sorted(set(EDGES.values())):
        candidate = BUILD / f"bench_no_vzu_{symbol}"
        run([str(patcher), str(control), str(candidate), symbol])
        variants[symbol] = candidate
        if symbol in {
            "ntruplus768_ntt_m_avx2", "ntruplus768_invntt_m_avx2"
        }:
            nop_candidate = BUILD / f"bench_nop_vzu_{symbol}"
            run([
                str(patcher), str(control), str(nop_candidate), symbol,
                "--mode", "nop-ret"
            ])
            nop_variants[symbol] = nop_candidate

    # Prove that geometry is identical and only four bytes differ.
    geometry = {}
    control_bytes = control.read_bytes()
    for symbol, candidate in variants.items():
        data = candidate.read_bytes()
        changed = [i for i, (a, b) in enumerate(zip(control_bytes, data)) if a != b]
        geometry[symbol] = {
            "elf_bytes": len(data),
            "changed_byte_count": len(changed),
            "changed_offsets": changed,
        }
        if len(data) != len(control_bytes) or len(changed) != 4:
            raise RuntimeError(f"geometry mismatch for {symbol}: {geometry[symbol]}")

    launches = 12
    records: dict[str, list[dict[str, object]]] = {edge: [] for edge in EDGES}
    for launch in range(launches):
        order = list(EDGES)
        if launch & 1:
            order.reverse()
        for edge in order:
            symbol = EDGES[edge]
            if launch & 1:
                candidate = parse(variants[symbol], edge)
                baseline = parse(control, edge)
            else:
                baseline = parse(control, edge)
                candidate = parse(variants[symbol], edge)
            delta = {metric: candidate[metric] - baseline[metric] for metric in baseline}
            records[edge].append(
                {"launch": launch, "control": baseline, "candidate": candidate, "delta": delta}
            )

    summary = {}
    for edge, edge_records in records.items():
        medians = {
            metric: statistics.median(record["delta"][metric] for record in edge_records)
            for metric in ("tsc", "core", "instructions")
        }
        summary[edge] = {
            "predecessor": EDGES[edge],
            "launches": launches,
            "median_delta": medians,
            "negative_core_launches": sum(
                record["delta"]["core"] < 0 for record in edge_records
            ),
            "negative_tsc_launches": sum(
                record["delta"]["tsc"] < 0 for record in edge_records
            ),
        }

    mechanism_controls = {}
    for edge in ("nttm_pack", "invcore_tail"):
        symbol = EDGES[edge]
        edge_records = []
        for launch in range(launches):
            if launch & 1:
                candidate = parse(nop_variants[symbol], edge)
                baseline = parse(control, edge)
            else:
                baseline = parse(control, edge)
                candidate = parse(nop_variants[symbol], edge)
            edge_records.append({
                "launch": launch,
                "control": baseline,
                "candidate": candidate,
                "delta": {
                    metric: candidate[metric] - baseline[metric]
                    for metric in baseline
                },
            })
        mechanism_controls[edge] = {
            "mode": "same_ret_address_nop_replaces_vzeroupper",
            "median_delta": {
                metric: statistics.median(
                    record["delta"][metric] for record in edge_records
                )
                for metric in ("tsc", "core", "instructions")
            },
            "negative_core_launches": sum(
                record["delta"]["core"] < 0 for record in edge_records
            ),
            "records": edge_records,
        }

    RESULTS.mkdir(parents=True, exist_ok=True)
    result = {
        "geometry": geometry,
        "records": records,
        "summary": summary,
        "mechanism_controls": mechanism_controls,
    }
    (RESULTS / "internal_edges.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(json.dumps({"mechanism_controls": mechanism_controls}, indent=2))


if __name__ == "__main__":
    main()
