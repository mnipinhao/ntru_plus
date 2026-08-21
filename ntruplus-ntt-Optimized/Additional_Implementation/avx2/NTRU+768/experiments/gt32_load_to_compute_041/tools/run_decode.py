#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, statistics, subprocess
from pathlib import Path

def run(path: Path, cpu: int) -> float:
    def pin() -> None: os.sched_setaffinity(0, {cpu})
    text = subprocess.run([str(path.resolve())], check=True, capture_output=True,
                          text=True, preexec_fn=pin).stdout
    deltas = []
    for line in text.splitlines():
        f = line.split()
        if f and f[0] == "round":
            row = {f[i]: f[i + 1] for i in range(0, len(f), 2)}
            deltas.append(int(row["candidate"]) - int(row["control"]))
    return statistics.median(deltas)

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--normal", type=Path, required=True)
    p.add_argument("--reversed", type=Path, required=True)
    p.add_argument("--launches", type=int, default=16)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    rows = []
    for placement in ("normal", "reversed"):
        for launch in range(a.launches):
            rows.append({"placement": placement, "launch": launch + 1,
                         "delta": run(getattr(a, placement), cpu)})
    summary = {}
    for placement in ("normal", "reversed"):
        values = [r["delta"] for r in rows if r["placement"] == placement]
        summary[placement] = {"median_delta_cycles": statistics.median(values),
                              "candidate_favorable": sum(v < 0 for v in values),
                              "launches": len(values)}
    out = {"schema": "gt32-load-to-compute-041-decode-v1",
           "cpu": cpu, "summary": summary, "launches": rows}
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
if __name__ == "__main__": main()
