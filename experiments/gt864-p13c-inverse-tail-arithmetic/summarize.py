#!/usr/bin/env python3
"""Summarize candidate-minus-baseline paired PMU samples."""
import csv
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = []
for path in sorted((HERE / "pi-run").glob("paired-*.csv")):
    current = [r for r in csv.reader(path.read_text().splitlines())
               if r and r[0] in ("full", "component")]
    assert len(current) % 2 == 0
    for i in range(0, len(current), 2):
        first, second = current[i:i+2]
        assert first[0:2] == second[0:2]
        pair = {first[2]: list(map(float, first[3:6])),
                second[2]: list(map(float, second[3:6]))}
        assert set(pair) == {"baseline", "candidate"}
        rows.append((first[1], [c-b for b, c in zip(pair["baseline"], pair["candidate"])]))

result = {}
for operation in ("inverse_to_ternary", "keygen", "encaps", "decaps"):
    values = [delta for name, delta in rows if name == operation]
    result[operation] = {"pairs": len(values)}
    for index, metric in enumerate(("cycles", "instructions", "branches")):
        samples = [v[index] for v in values]
        q1, _, q3 = statistics.quantiles(samples, n=4, method="inclusive")
        result[operation][metric] = {
            "median_delta": statistics.median(samples), "iqr": [q1, q3],
            "minimum": min(samples), "maximum": max(samples)}
(HERE / "paired-summary.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
