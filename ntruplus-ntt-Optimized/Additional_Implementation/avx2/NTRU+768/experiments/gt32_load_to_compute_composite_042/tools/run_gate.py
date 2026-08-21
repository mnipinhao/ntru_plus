#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, random, statistics, subprocess
from pathlib import Path

def run(path: Path, cpu: int) -> dict[str, object]:
    def pin() -> None: os.sched_setaffinity(0, {cpu})
    text = subprocess.run([str(path.resolve())], check=True, capture_output=True,
                          text=True, preexec_fn=pin).stdout
    rows, addresses = [], {}
    for line in text.splitlines():
        f = line.split()
        if f and f[0].startswith("address_"): addresses[f[0][8:]] = f[1]
        if f and f[0] == "round":
            row = {f[i]: f[i + 1] for i in range(0, len(f), 2)}
            rows.append({k: int(row[k]) for k in ("A", "D", "B", "DB")})
    med = {k: statistics.median(r[k] for r in rows) for k in ("A", "D", "B", "DB")}
    return {"addresses": addresses, "medians": med,
            "D_minus_A": med["D"] - med["A"],
            "B_minus_A": med["B"] - med["A"],
            "DB_minus_A": med["DB"] - med["A"],
            "interaction": (med["DB"] - med["D"]) - (med["B"] - med["A"])}

def summary(values: list[float]) -> dict[str, object]:
    median = statistics.median(values)
    rng = random.Random(0x042)
    boot = sorted(statistics.median(rng.choices(values, k=len(values)))
                  for _ in range(20000))
    return {"median_delta_cycles": median,
            "mad_cycles": statistics.median(abs(x - median) for x in values),
            "bootstrap_95_ci_cycles": [boot[499], boot[19499]],
            "favorable_launches": sum(x < 0 for x in values),
            "launches": len(values)}

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--normal", type=Path, required=True)
    p.add_argument("--reversed", type=Path, required=True)
    p.add_argument("--launches", type=int, default=16)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    launches = []
    for placement in ("normal", "reversed"):
        for launch in range(a.launches):
            launches.append({"placement": placement, "launch": launch + 1,
                             **run(getattr(a, placement), cpu)})
    out_summary = {}
    for placement in ("normal", "reversed"):
        rows = [r for r in launches if r["placement"] == placement]
        for metric in ("D_minus_A", "B_minus_A", "DB_minus_A", "interaction"):
            out_summary[placement + "_" + metric] = summary([r[metric] for r in rows])
    result = {"schema": "gt32-load-to-compute-composite-042-v1",
              "cpu": cpu, "summary": out_summary, "launches": launches}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out_summary, indent=2, sort_keys=True))
if __name__ == "__main__": main()
