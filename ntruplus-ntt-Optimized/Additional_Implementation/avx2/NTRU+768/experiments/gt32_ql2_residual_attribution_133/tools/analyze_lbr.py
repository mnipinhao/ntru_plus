#!/usr/bin/env python3
"""Analyze direct Encap leaf intervals in the exact Experiment 132 images."""

import argparse
import json
import re
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

CALLS = {
    "official": [
        (0x604e, "decode", True), (0x60d1, "cbd_r", True),
        (0x60de, "ntt_r", True), (0x60ee, "pack_rhat", True),
        (0x6111, "sotp_m", True), (0x611e, "ntt_m", True),
        (0x6138, "basemul", True), (0x614f, "add_m", True),
        (0x615c, "pack_ct", True),
    ],
    "gt": [
        (0x3d1f, "decode", False), (0x3da1, "cbd_r", True),
        (0x3db6, "frontend_r", True), (0x3dcb, "ntt_r", True),
        (0x3ddb, "pack_rhat", True), (0x3dfb, "sotp_m", True),
        (0x3e10, "frontend_m", True), (0x3e25, "ntt_m_ql2", True),
        (0x3e3f, "basemul_ql2", True), (0x3e57, "ql2_add_pack_ct", True),
        (0x9e0a, "decode_body", True),
    ],
}
MMAP = re.compile(r"\[0x([0-9a-f]+)\(0x([0-9a-f]+)\) @ 0x([0-9a-f]+).+\]: r-xp (.+)$")
BR = re.compile(r"0x([0-9a-f]+)/0x([0-9a-f]+)/[^/]*/[^/]*/[^/]*/(\d+)/([^/]*)/")

def perf(data, *args):
    return subprocess.run(["perf", "script", "-i", str(data), *args],
                          capture_output=True, text=True, check=True).stdout

def mapping(data, binary):
    wanted = str(binary.resolve())
    found = []
    for line in perf(data, "--show-mmap-events").splitlines():
        match = MMAP.search(line)
        if match and str(Path(match.group(4)).resolve()) == wanted:
            start, size, offset = (int(match.group(i), 16) for i in range(1, 4))
            found.append((start, size, offset))
    if not found:
        raise RuntimeError(f"missing mapping for {wanted}")
    bases = {start - offset for start, size, offset in found}
    if len(bases) != 1:
        raise RuntimeError(f"inconsistent PIE bases: {found}")
    return bases.pop()

def summarize(values):
    if not values:
        return None
    values = sorted(values)
    return {"observations": len(values), "median": statistics.median(values),
            "p10": values[round((len(values) - 1) * .1)],
            "p90": values[round((len(values) - 1) * .9)]}

def trace(data, binary, implementation):
    base = mapping(data, binary)
    returns = {address + 5: (name, leaf) for address, name, leaf in CALLS[implementation]}
    values = defaultdict(list)
    for line in perf(data, "-F", "brstack").splitlines():
        for match in BR.finditer(line):
            target = int(match.group(2), 16) - base
            if match.group(4) == "RET" and target in returns:
                name, leaf = returns[target]
                if leaf:
                    values[name].append(int(match.group(3)))
    return {name: summarize(items) for name, items in values.items()}

def launch_summary(rows):
    keys = sorted({key for row in rows for key in row["intervals"]})
    return {key: summarize([row["intervals"][key]["median"] for row in rows
                            if row["intervals"].get(key)]) for key in keys}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    binaries = {key: Path(value["path"]) for key, value in manifest["binaries"].items()}
    rows = []
    groups = defaultdict(list)
    for record in manifest["rows"]:
        implementation = record["implementation"]
        row = {**record, "intervals": trace(
            args.manifest.parent / record["perf_data"], binaries[implementation], implementation)}
        rows.append(row)
        groups[implementation].append(row)
    summaries = {key: launch_summary(value) for key, value in groups.items()}
    official, gt = summaries["official"], summaries["gt"]
    specs = {
        "decode": (["decode"], ["decode_body"]),
        "cbd_r": (["cbd_r"], ["cbd_r"]),
        "r_producer": (["ntt_r"], ["frontend_r", "ntt_r"]),
        "rhat_serializer": (["pack_rhat"], ["pack_rhat"]),
        "sotp_m": (["sotp_m"], ["sotp_m"]),
        "m_producer": (["ntt_m"], ["frontend_m", "ntt_m_ql2"]),
        "basemul": (["basemul"], ["basemul_ql2"]),
        "sum_and_ct_serializer": (["add_m", "pack_ct"], ["ql2_add_pack_ct"]),
    }
    semantic = {}
    for name, (official_keys, gt_keys) in specs.items():
        if all(key in official for key in official_keys) and all(key in gt for key in gt_keys):
            ov = sum(official[key]["median"] for key in official_keys)
            gv = sum(gt[key]["median"] for key in gt_keys)
            semantic[name] = {"official_core_cycles": ov, "ql2_core_cycles": gv,
                              "ql2_minus_official": gv - ov}
    semantic["mapped_leaf_total"] = {
        "official_core_cycles": sum(value["official_core_cycles"] for value in semantic.values()),
        "ql2_core_cycles": sum(value["ql2_core_cycles"] for value in semantic.values()),
    }
    semantic["mapped_leaf_total"]["ql2_minus_official"] = (
        semantic["mapped_leaf_total"]["ql2_core_cycles"]
        - semantic["mapped_leaf_total"]["official_core_cycles"])
    output = {"schema": "gt32-ql2-residual-attribution-133-lbr-v1",
        "warning": "leaf LBR medians are descriptive, not additive full-Encap accounting",
        "summaries": summaries, "semantic_leaf_map": semantic, "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(semantic, indent=2))

if __name__ == "__main__":
    main()
