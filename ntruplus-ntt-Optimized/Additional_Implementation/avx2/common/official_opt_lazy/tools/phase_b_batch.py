#!/usr/bin/env python3
"""Run one Phase-B timing batch with hygiene monitoring and bounded retries.

The command must write its result into the directory given by the literal
token {RESULT}.  Each attempt runs under hygiene_batch.py.  A contaminated
attempt's result directory is moved to <results>/_contaminated/<name>-aN
(ignored by Git) and the batch is re-run, up to --retries more times.  The
accepted attempt gets the full `host-hygiene.json` (Git-ignored: it holds
raw process command lines) plus a compact `host_hygiene`
object merged into its metadata file (metadata.json or manifest.json), which
also lists every earlier contaminated attempt.

  phase_b_batch.py --result-dir results/native-lazy-qual-official-20260923 \
      --metadata metadata.json -- python3 scripts/run_supercop_benchmark.py ... --result-dir {RESULT}
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def compact(record: dict) -> dict:
    def snap(s):
        return {"time": s["time"], "uptime": s["uptime"], "loadavg": s["loadavg"],
                "top_cpu_consumers_3s": [
                    {k: r[k] for k in ("comm", "pid", "cpu_percent", "last_cpu")}
                    for r in s["top_cpu_consumers_3s"][:5]]}
    return {"contaminated": record["contaminated"],
            "contamination_reasons": record["contamination_reasons"],
            "waited_for_quiet_s": record["waited_for_quiet_s"],
            "duration_s": record["duration_s"],
            "load_threshold": record["load_threshold"],
            "proc_threshold_percent": record["proc_threshold_percent"],
            "during_max_loadavg1_including_batch": record["during"]["max_loadavg1"],
            "during_offenders": {pid: {k: v for k, v in o.items() if k != "cmd"}
                                 for pid, o in record["during"]["offenders"].items()},
            "during_heavy_windows": len(record["during"]["heavy_windows"]),
            "before": snap(record["before"]), "after": snap(record["after"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--metadata", required=True, help="metadata file name inside the result dir")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if "{RESULT}" not in command:
        parser.error("command must contain {RESULT}")
    result = args.result_dir.resolve()
    if result.exists():
        raise SystemExit(f"refusing to overwrite {result}")
    quarantine = result.parent / "_contaminated"
    history = []
    for attempt in range(args.retries + 1):
        hygiene = quarantine / f"{result.name}-a{attempt}.hygiene.json"
        quarantine.mkdir(parents=True, exist_ok=True)
        if hygiene.exists():
            raise SystemExit(f"stale hygiene record {hygiene}")
        concrete = [str(result) if token == "{RESULT}" else token for token in command]
        code = subprocess.call([sys.executable, str(HERE / "hygiene_batch.py"), "--record",
                                str(hygiene), "--label", f"{result.name} attempt {attempt}",
                                "--", *concrete])
        record = json.loads(hygiene.read_text())
        if code not in (0, 75):
            raise SystemExit(f"batch command failed ({code}); see {hygiene}")
        if not record["contaminated"]:
            shutil.move(str(hygiene), result / "host-hygiene.json")
            meta_path = result / args.metadata
            meta = json.loads(meta_path.read_text())
            meta["host_hygiene"] = {**compact(record), "attempt": attempt,
                                    "earlier_contaminated_attempts": history,
                                    "host_controls_changed": False}
            meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
            print(f"accepted {result} on attempt {attempt}")
            return 0
        moved = quarantine / f"{result.name}-a{attempt}"
        shutil.move(str(result), moved)
        history.append({"attempt": attempt, "moved_to": str(moved),
                        "reasons": record["contamination_reasons"]})
        print(f"contaminated attempt {attempt}: {record['contamination_reasons']}", flush=True)
    print(f"all {args.retries + 1} attempts contaminated for {result}", file=sys.stderr)
    return 75


if __name__ == "__main__":
    raise SystemExit(main())
