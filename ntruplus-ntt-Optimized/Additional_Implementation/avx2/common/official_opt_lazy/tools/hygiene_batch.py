#!/usr/bin/env python3
"""Run one timing batch under host-hygiene monitoring (read-only on the host).

Before the batch it waits (bounded) for the 1-minute load average to fall to
the threshold, then records `uptime` and the top CPU consumers sampled over a
short window.  During the batch it samples every process's CPU time; any
process outside the batch's own process tree that holds more than
--proc-threshold % of one CPU for two consecutive sample windows, or any
foreign benchmark-looking process, marks the batch contaminated.  After the
batch it records the same snapshot again.  The post-batch load average
includes the batch's own pinned process (about 1.0), so only the pre-batch
load average is compared with --load-threshold.

Nothing on the host is changed (no governor/turbo/ASLR/SMT/IRQ writes).
The record is written as JSON; the exit status is the command's, or 75 when
the command succeeded but the batch was contaminated.

  hygiene_batch.py --record hygiene.json -- python3 scripts/run_supercop_benchmark.py ...
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

CLK = os.sysconf("SC_CLK_TCK")
BENCH_NAMES = ("measure", "do-part", "bench_", "supercop", "test_kem", "test_forward")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def loadavg() -> list[float]:
    return [float(x) for x in Path("/proc/loadavg").read_text().split()[:3]]


def proc_table() -> dict[int, tuple[int, int, str, str, int]]:
    """pid -> (ppid, cpu ticks, comm, cmdline, last cpu)."""
    table = {}
    for entry in os.scandir("/proc"):
        if not entry.name.isdigit():
            continue
        try:
            raw = Path(f"/proc/{entry.name}/stat").read_text()
            cmd = Path(f"/proc/{entry.name}/cmdline").read_bytes().replace(b"\0", b" ").decode(
                errors="replace").strip()
        except OSError:
            continue
        comm = raw[raw.index("(") + 1:raw.rindex(")")]
        fields = raw[raw.rindex(")") + 2:].split()
        table[int(entry.name)] = (int(fields[1]), int(fields[11]) + int(fields[12]), comm,
                                  cmd[:200], int(fields[36]))
    return table


def descendants(table, root: int) -> set[int]:
    tree = {root}
    changed = True
    while changed:
        changed = False
        for pid, row in table.items():
            if pid not in tree and row[0] in tree:
                tree.add(pid)
                changed = True
    return tree


def top_consumers(window: float = 3.0, count: int = 8, exclude: set[int] | None = None):
    first = proc_table()
    time.sleep(window)
    second = proc_table()
    rows = []
    for pid, row in second.items():
        if pid in first and (exclude is None or pid not in exclude):
            pct = 100.0 * (row[1] - first[pid][1]) / CLK / window
            rows.append({"pid": pid, "cpu_percent": round(pct, 1), "comm": row[2],
                         "last_cpu": row[4], "cmd": row[3]})
    rows.sort(key=lambda r: -r["cpu_percent"])
    return rows[:count]


def snapshot(label: str) -> dict:
    uptime = subprocess.run(["uptime"], text=True, capture_output=True).stdout.strip()
    self_tree = descendants(proc_table(), os.getpid())
    top = top_consumers(exclude=self_tree)
    return {"label": label, "time": now(), "uptime": uptime, "loadavg": loadavg(),
            "top_cpu_consumers_3s": top}


def monitor(child: subprocess.Popen, interval: float, threshold: float, stop, out: dict):
    me = os.getpid()
    previous = proc_table()
    strikes: dict[int, int] = {}
    samples = []
    offenders = {}
    foreign_bench = {}
    while not stop.wait(interval):
        current = proc_table()
        tree = descendants(current, me)
        heavy = []
        for pid, row in current.items():
            if pid in tree or pid not in previous:
                continue
            pct = 100.0 * (row[1] - previous[pid][1]) / CLK / interval
            name = row[2]
            if any(name.startswith(b) or b in row[3].split(" ")[0] for b in BENCH_NAMES) and pct > 5:
                foreign_bench[pid] = {"comm": name, "cmd": row[3], "cpu_percent": round(pct, 1)}
            if pct > threshold:
                strikes[pid] = strikes.get(pid, 0) + 1
                heavy.append({"pid": pid, "comm": name, "cpu_percent": round(pct, 1),
                              "last_cpu": row[4]})
                if strikes[pid] >= 2:
                    best = offenders.get(pid, {"max_cpu_percent": 0})
                    offenders[pid] = {"comm": name, "cmd": row[3],
                                      "max_cpu_percent": max(best["max_cpu_percent"], round(pct, 1)),
                                      "windows": strikes[pid]}
            else:
                strikes[pid] = 0
        samples.append({"t": round(time.time(), 1), "loadavg1": loadavg()[0], "heavy": heavy})
        previous = current
    out.update(samples=samples, offenders=offenders, foreign_benchmark_processes=foreign_bench)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--label", default="")
    parser.add_argument("--load-threshold", type=float, default=0.5)
    parser.add_argument("--proc-threshold", type=float, default=25.0)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--max-wait", type=float, default=1200.0,
                        help="seconds to wait for a quiet host before starting")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("missing command")
    if args.record.exists():
        raise SystemExit(f"refusing to overwrite {args.record}")

    waited = 0.0
    while loadavg()[0] > args.load_threshold and waited < args.max_wait:
        time.sleep(15)
        waited += 15
    before = snapshot("before")
    record = {"schema": "ntruplus-host-hygiene/v1", "label": args.label, "command": command,
              "load_threshold": args.load_threshold, "proc_threshold_percent": args.proc_threshold,
              "interval_s": args.interval, "waited_for_quiet_s": waited, "before": before}
    started = time.time()
    child = subprocess.Popen(command)
    stop = threading.Event()
    during: dict = {}
    thread = threading.Thread(target=monitor, args=(child, args.interval, args.proc_threshold,
                                                    stop, during), daemon=True)
    thread.start()
    code = child.wait()
    stop.set()
    thread.join()
    record["duration_s"] = round(time.time() - started, 1)
    record["exit_code"] = code
    record["during"] = {"max_loadavg1": max([s["loadavg1"] for s in during["samples"]], default=None),
                        "samples": len(during["samples"]),
                        "offenders": during["offenders"],
                        "foreign_benchmark_processes": during["foreign_benchmark_processes"],
                        "heavy_windows": [s for s in during["samples"] if s["heavy"]]}
    record["after"] = snapshot("after")
    reasons = []
    if before["loadavg"][0] > args.load_threshold:
        reasons.append(f"pre-batch loadavg1 {before['loadavg'][0]} > {args.load_threshold}")
    if during["offenders"]:
        reasons.append("sustained foreign CPU: " + ", ".join(
            f"{v['comm']}({pid}) {v['max_cpu_percent']}%" for pid, v in during["offenders"].items()))
    if during["foreign_benchmark_processes"]:
        reasons.append("foreign benchmark process: " + ", ".join(
            f"{v['comm']}({pid})" for pid, v in during["foreign_benchmark_processes"].items()))
    record["contaminated"] = bool(reasons)
    record["contamination_reasons"] = reasons
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"hygiene: contaminated={record['contaminated']} {reasons}")
    if code:
        return code
    return 75 if reasons else 0


if __name__ == "__main__":
    raise SystemExit(main())
