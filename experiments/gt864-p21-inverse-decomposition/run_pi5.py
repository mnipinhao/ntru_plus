#!/usr/bin/env python3
"""Prepare, upload, run, and collect P21 from the selected Pi 5."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYNC = HERE / "build/sync"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p21-20260912"


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
    run_log = ssh(f"cd {REMOTE} && python3 pi_run.py")
    (HERE / "build/remote-run.log").write_text(run_log)
    for name in ("p21-results.json", "environment.json"):
        subprocess.run(["rsync", "-av", f"{HOST}:{REMOTE}/{name}",
                        str(HERE / name)], check=True)
    print(run_log)


if __name__ == "__main__":
    main()
