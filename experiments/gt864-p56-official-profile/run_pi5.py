#!/usr/bin/env python3
"""Execute P56 in an isolated selected-SUPERCOP Pi 5 directory."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYNC = HERE / "build/sync"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p56-20260917-v2"


def output(args: list[object]) -> str:
    return subprocess.check_output([str(x) for x in args], text=True,
                                   stderr=subprocess.STDOUT)


def ssh(command: str) -> str:
    return output(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
                   HOST, command])


def main() -> None:
    subprocess.run([sys.executable, HERE / "prepare.py"], check=True)
    if ssh("ps -eo args | grep '[d]o-part' || true").strip():
        raise RuntimeError("SUPERCOP do-part is active; refusing contaminated PMU")
    ssh(f"mkdir -p {REMOTE}")
    print(output(["rsync", "-av", str(SYNC) + "/", HOST + ":" + REMOTE + "/"]),
          flush=True)
    run_log = ssh(
        f"cd {REMOTE} && python3 pi_run.py && python3 summarize.py && "
        "python3 run_events.py && python3 summarize_events.py"
    )
    (HERE / "build/remote-run.log").write_text(run_log)
    fetches = {
        "results.json": "results.json",
        "event-results.json": "event-results.json",
        "environment.json": "build/environment.json",
        "symbols.txt": "build/symbols.txt",
    }
    for local, remote in fetches.items():
        subprocess.run(["rsync", "-av", f"{HOST}:{REMOTE}/{remote}",
                        str(HERE / local)], check=True)
    environment = json.loads((HERE / "environment.json").read_text())
    if (environment["throttled_before"] != "throttled=0x0" or
            environment["throttled_after"] != "throttled=0x0"):
        raise RuntimeError("Pi 5 throttled during P56")
    print(run_log)


if __name__ == "__main__":
    main()
