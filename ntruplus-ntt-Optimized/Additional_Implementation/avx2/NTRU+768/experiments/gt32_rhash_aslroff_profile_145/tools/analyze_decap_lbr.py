#!/usr/bin/env python3
"""Descriptive Decap leaf profile from the Experiment 145 LBR corpus.

The reported leaf medians are deliberately non-additive.  In particular,
hash_g/hash_h are non-leaf wrappers and the Official final byte comparison is
inline, so neither is assigned an invented component cost here.
"""

import argparse
import json
import re
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path


CALLS = {
    "official": [
        (0x65DC, "decode_ct"),
        (0x65FC, "decode_f"),
        (0x672F, "decode_hinv"),
        (0x6757, "scale_basemul"),
        (0x675F, "inverse"),
        (0x6767, "crepmod3"),
        (0x6777, "recover_copy"),
        (0x677F, "recover_ntt"),
        (0x6791, "sub"),
        (0x67A1, "general_basemul"),
        (0x67AC, "pack_recovered_r"),
        (0x67E9, "sotp_decode"),
        (0x6835, "cbd_derived_r"),
        (0x683D, "derived_r_ntt"),
        (0x6852, "pack_derived_r"),
    ],
    "gt": [
        (0x9E36, "decode_ct"),
        (0x9E41, "decode_f"),
        (0x9E50, "decode_hinv"),
        (0x3B1D, "scale_basemul"),
        (0x3B32, "inverse_core"),
        (0x3B47, "inverse_tail"),
        (0x3B54, "crepmod3"),
        (0x3B69, "recover_frontend"),
        (0x3B7E, "recover_ntt"),
        (0x3B95, "sub"),
        (0x3BAF, "general_basemul"),
        (0x3BCC, "pack_recovered_r"),
        (0x3C07, "sotp_decode"),
        (0x3C4F, "cbd_derived_r"),
        (0x3C64, "derived_r_frontend"),
        (0x3C79, "derived_r_ntt"),
        (0x3C8E, "native_final_compare"),
    ],
}

SEMANTIC = {
    "decode3": (
        ["decode_ct", "decode_f", "decode_hinv"],
        ["decode_ct", "decode_f", "decode_hinv"],
    ),
    "first_product": (["scale_basemul"], ["scale_basemul"]),
    "inverse_to_mod3": (
        ["inverse", "crepmod3"],
        ["inverse_core", "inverse_tail", "crepmod3"],
    ),
    "recovered_forward": (
        ["recover_copy", "recover_ntt"],
        ["recover_frontend", "recover_ntt"],
    ),
    "sub": (["sub"], ["sub"]),
    "second_product": (["general_basemul"], ["general_basemul"]),
    "recovered_r_serializer": (["pack_recovered_r"], ["pack_recovered_r"]),
    "sotp_decode": (["sotp_decode"], ["sotp_decode"]),
    "derived_r_generation": (
        ["cbd_derived_r", "derived_r_ntt"],
        ["cbd_derived_r", "derived_r_frontend", "derived_r_ntt"],
    ),
    # Not an equal-cost comparison: Official still has a following inline byte
    # loop, which LBR cannot isolate.  Kept separately for transparent context.
    "final_check_visible_leaf": (["pack_derived_r"], ["native_final_compare"]),
}

MMAP = re.compile(r"\[0x([0-9a-f]+)\(0x([0-9a-f]+)\) @ 0x([0-9a-f]+).+\]: r-xp (.+)$")
BR = re.compile(r"0x([0-9a-f]+)/0x([0-9a-f]+)/[^/]*/[^/]*/[^/]*/(\d+)/([^/]*)/")


def perf(data, *args):
    return subprocess.run(
        ["perf", "script", "-i", str(data), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def image_base(data, binary):
    values = []
    wanted = str(binary.resolve())
    for line in perf(data, "--show-mmap-events").splitlines():
        match = MMAP.search(line)
        if match and str(Path(match.group(4)).resolve()) == wanted:
            values.append(int(match.group(1), 16) - int(match.group(3), 16))
    if len(set(values)) != 1:
        raise RuntimeError((wanted, values))
    return values[0]


def summary(values):
    if not values:
        return None
    values = sorted(values)
    return {
        "observations": len(values),
        "median": statistics.median(values),
        "p10": values[round((len(values) - 1) * 0.1)],
        "p90": values[round((len(values) - 1) * 0.9)],
    }


def trace(data, binary, implementation):
    base = image_base(data, binary)
    returns = {address + 5: name for address, name in CALLS[implementation]}
    values = defaultdict(list)
    for line in perf(data, "-F", "brstack").splitlines():
        for match in BR.finditer(line):
            target = int(match.group(2), 16) - base
            if match.group(4) == "RET" and target in returns:
                values[returns[target]].append(int(match.group(3)))
    return {name: summary(samples) for name, samples in values.items()}


def launch_summary(rows):
    keys = sorted({key for row in rows for key in row["intervals"]})
    return {
        key: summary(
            [row["intervals"][key]["median"] for row in rows if row["intervals"].get(key)]
        )
        for key in keys
    }


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
        row = {
            **record,
            "intervals": trace(
                args.manifest.parent / record["perf_data"],
                binaries[implementation],
                implementation,
            ),
        }
        rows.append(row)
        groups[implementation].append(row)

    summaries = {key: launch_summary(value) for key, value in groups.items()}
    official = summaries["official"]
    gt = summaries["gt"]
    semantic = {}
    for name, (official_keys, gt_keys) in SEMANTIC.items():
        if all(official.get(key) for key in official_keys) and all(gt.get(key) for key in gt_keys):
            official_cycles = sum(official[key]["median"] for key in official_keys)
            gt_cycles = sum(gt[key]["median"] for key in gt_keys)
            semantic[name] = {
                "official_core_cycles": official_cycles,
                "gt_core_cycles": gt_cycles,
                "gt_minus_official": gt_cycles - official_cycles,
            }

    output = {
        "schema": "gt32-rhash-aslroff-profile-145-decap-analysis",
        "warning": (
            "LBR leaf medians are descriptive and non-additive. hash_g/hash_h are omitted; "
            "Official's inline final byte comparison is not present in final_check_visible_leaf."
        ),
        "summaries": summaries,
        "semantic_leaf_map": semantic,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(semantic, indent=2))


if __name__ == "__main__":
    main()
