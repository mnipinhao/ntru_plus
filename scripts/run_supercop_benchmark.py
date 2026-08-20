#!/usr/bin/env python3
"""Run native-KEM or SUPERCOP-derived polynomial measurement in a campaign."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import stat
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import LOCK_PATH, REPO_ROOT, read_lock, sha256_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--parameter", choices=("864", "1152"), required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--mode", choices=("native-kem", "derived-poly"), required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--compiler-wrapper", type=Path,
                        help="force one common SUPERCOP okc recipe (campaign only)")
    args = parser.parse_args()

    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit("benchmarking is allowed only in a prepared disposable campaign")
    marker_record = json.loads(marker.read_text(encoding="utf-8"))
    if marker_record.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("campaign marker has the wrong kind")
    pinned = read_lock()
    if marker_record.get("supercop_version") != pinned["version"]:
        raise SystemExit("campaign version does not match bench/supercop.lock")
    if not (root / "do-part").is_file():
        raise SystemExit(f"missing SUPERCOP do-part in {root}")
    primitive = f"ntruplus{args.parameter}"
    primitive_dir = root / "crypto_kem" / primitive
    selected = primitive_dir / args.implementation
    if not selected.is_dir():
        raise SystemExit(f"missing implementation: {selected}")
    if args.result_dir.exists():
        raise SystemExit(f"refusing to overwrite result directory: {args.result_dir}")
    args.result_dir.mkdir(parents=True)

    implementations = sorted(path for path in primitive_dir.iterdir() if path.is_dir())
    original_modes = {path: stat.S_IMODE(path.stat().st_mode) for path in implementations}
    measure_path = root / "crypto_kem" / "measure.c"
    original_measure = measure_path.read_bytes()
    original_measure_mode = stat.S_IMODE(measure_path.stat().st_mode)
    adapter_backups: dict[Path, bytes | None] = {}
    compiler_backup: tuple[Path, bytes, int] | None = None
    started = time.time()
    try:
        for path in implementations:
            path.chmod(original_modes[path] | stat.S_ISVTX)
        selected.chmod(original_modes[selected] & ~stat.S_ISVTX)
        if args.mode == "derived-poly":
            replacement = REPO_ROOT / "bench" / "supercop" / "poly_measure.c"
            shutil.copyfile(replacement, measure_path)
            for name in ("ntruplus_bench.c", "ntruplus_bench.h"):
                destination = selected / name
                adapter_backups[destination] = destination.read_bytes() if destination.exists() else None
                shutil.copy2(REPO_ROOT / "bench" / "supercop" / name, destination)
        if args.compiler_wrapper:
            wrappers = list((root / "bench").glob("*/bin/okc-amd64"))
            if len(wrappers) != 1:
                raise SystemExit(f"expected one campaign okc-amd64, found {len(wrappers)}")
            wrapper = wrappers[0]
            compiler_backup = (wrapper, wrapper.read_bytes(), stat.S_IMODE(wrapper.stat().st_mode))
            shutil.copy2(args.compiler_wrapper, wrapper)
            wrapper.chmod(wrapper.stat().st_mode | 0o111)
        with (args.result_dir / "run.out").open("wb") as output:
            completed = subprocess.run(
                ["taskset", "-c", str(args.cpu), "./do-part", "crypto_kem", primitive],
                cwd=root,
                stdout=output,
                stderr=subprocess.STDOUT,
                check=False,
            )
    finally:
        measure_path.write_bytes(original_measure)
        measure_path.chmod(original_measure_mode)
        for path, content in adapter_backups.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        if compiler_backup:
            path, content, mode = compiler_backup
            path.write_bytes(content)
            path.chmod(mode)
        for path, mode in original_modes.items():
            path.chmod(mode)

    data_files = [
        path for path in (root / "bench").glob("*/data")
        if path.stat().st_mtime >= started - 1
    ]
    if len(data_files) != 1:
        raise SystemExit(f"expected one updated bench/*/data, found {len(data_files)}")
    shutil.copy2(data_files[0], args.result_dir / "data")
    run_text = (args.result_dir / "run.out").read_text(encoding="utf-8", errors="replace")
    data_text = (args.result_dir / "data").read_text(encoding="utf-8", errors="replace")
    if completed.returncode:
        raise SystemExit(f"SUPERCOP do-part exited {completed.returncode}; see run.out")
    if "tryfails" in run_text.lower() or "measurefails" in run_text.lower():
        raise SystemExit("SUPERCOP reported tryfails or measurefails")
    required = (
        ("keypair_cycles", "enc_cycles", "dec_cycles")
        if args.mode == "native-kem"
        else ("forward_small_cycles", "forward_general_cycles", "basemul_cycles",
              "inverse_cycles", "baseinv_cycles", "poly_mul_small_cycles",
              "poly_mul_general_cycles")
    )
    missing = [name for name in required if f" {name} " not in data_text]
    if missing:
        raise SystemExit(f"benchmark data lacks {', '.join(missing)}")

    lock = read_lock()
    cpu_model = "unknown"
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lower().startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    governor_path = Path(f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor")
    metadata = {
        **lock,
        "benchmark_class": "supercop-native-kem" if args.mode == "native-kem" else "supercop-derived-poly",
        "bench_cpu": args.cpu,
        "campaign": str(root),
        "compiler_policy": "fixed-common" if args.compiler_wrapper else "native-supercop-selection",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()) if args.compiler_wrapper else None,
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper) if args.compiler_wrapper else None,
        "cpu_model": cpu_model,
        "do_part_exit_code": completed.returncode,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "implementation": args.implementation,
        "kernel": platform.release(),
        "machine": platform.machine(),
        "scaling_governor": governor_path.read_text().strip() if governor_path.is_file() else "unavailable",
        "measure_source_sha256": sha256_file(
            root / "crypto_kem" / "measure.c" if args.mode == "native-kem"
            else REPO_ROOT / "bench" / "supercop" / "poly_measure.c"
        ),
        "parameter": args.parameter,
        "result_data_source": str(data_files[0]),
    }
    (args.result_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    shutil.copy2(LOCK_PATH, args.result_dir / "supercop.lock")
    print(f"completed {metadata['benchmark_class']}: {args.result_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
