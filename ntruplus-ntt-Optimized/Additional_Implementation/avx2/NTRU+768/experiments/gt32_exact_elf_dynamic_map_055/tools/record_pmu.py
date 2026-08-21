#!/usr/bin/env python3
"""Sample exact production ELFs and retain LBR call chains for Encap filtering."""

import argparse
import json
import subprocess
from pathlib import Path

EVENTS = {
    "cycles": ("cpu_core/cycles/u", 5000),
    "frontend": ("cpu_core/idq_uops_not_delivered.core/u", 500),
    "load_pending": ("cpu_core/l1d_pend_miss.pending_cycles/u", 500),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--gt", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=8)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    repeat = Path(__file__).with_name("repeat_target.py").resolve()
    rows = []
    for implementation, binary in (("official", args.official), ("gt", args.gt)):
        binary = binary.resolve()
        for name, (event, period) in EVENTS.items():
            output = args.output_dir / f"{implementation}-{name}.data"
            command = [
                "perf", "record", "-q", "-o", str(output),
                "-e", event, "-c", str(period), "--call-graph", "lbr", "--",
                "taskset", "-c", str(args.cpu), "python3", str(repeat),
                str(binary), str(args.repetitions),
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, check=True)
            rows.append({
                "implementation": implementation,
                "event_class": name,
                "event": event,
                "period": period,
                "perf_data": output.name,
            })
    manifest = {
        "schema": "gt32-exact-elf-dynamic-map-055-pmu-record-v1",
        "cpu": args.cpu,
        "repetitions": args.repetitions,
        "estimated_encap_calls": args.repetitions * 96,
        "binaries": {
            "official": str(args.official.resolve()),
            "gt": str(args.gt.resolve()),
        },
        "rows": rows,
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()

