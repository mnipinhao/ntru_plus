#!/usr/bin/env python3
"""Attribute PMU samples whose LBR call chain contains the real Encap caller."""

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

CALLERS = {
    "official": "crypto_kem_enc_derand",
    "gt": "ntruplus768_enc_derand_impl",
}
HEADER_RE = re.compile(r"^\S.*:\s+\d+\s+cpu_core/")
FRAME_RE = re.compile(r"^\s+[0-9a-f]+\s+([^ +]+)(?:\+0x[0-9a-f]+)?")


def samples(data: Path):
    result = subprocess.run(
        ["perf", "script", "-i", str(data)], capture_output=True,
        text=True, check=True,
    )
    current = []
    for line in result.stdout.splitlines() + [""]:
        if HEADER_RE.match(line):
            if current:
                yield current
            current = []
        elif not line.strip():
            if current:
                yield current
                current = []
        else:
            match = FRAME_RE.match(line)
            if match:
                current.append(match.group(1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    output_rows = []
    for row in manifest["rows"]:
        implementation = row["implementation"]
        caller = CALLERS[implementation]
        counts = Counter()
        total = 0
        for chain in samples(args.manifest.parent / row["perf_data"]):
            if caller not in chain or not chain:
                continue
            counts[chain[0]] += 1
            total += 1
        period = row["period"]
        calls = manifest["estimated_encap_calls"]
        output_rows.append({
            **row,
            "encap_samples": total,
            "estimated_events_per_encap": total * period / calls,
            "top_symbols": [
                {
                    "symbol": symbol,
                    "samples": count,
                    "share": count / total if total else 0,
                    "estimated_events_per_encap": count * period / calls,
                }
                for symbol, count in counts.most_common(20)
            ],
        })
    output = {
        "schema": "gt32-exact-elf-dynamic-map-055-pmu-analysis-v1",
        "warning": (
            "Sampling estimates classify where events occur. They are not exact "
            "component-cycle measurements and include skid."
        ),
        "rows": output_rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

