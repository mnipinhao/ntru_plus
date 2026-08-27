#!/usr/bin/env python3
"""Build and run the frozen 100-vector NTRU+1152 KAT for PROD3 H1."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import read_lock, sha256_file

IMPLEMENTATION_SOURCES = (
    "add.s", "baseinv.s", "basemul.s", "cbd.s", "crepmod3.s",
    "invntt.s", "ntt.s", "pack.s", "consts.c", "kem.c", "poly.c",
    "symmetric.c", "fips202.c", "KeccakP-1600-AVX2.s",
    "top_split_adapter.c", "gt9x16_prod3_aos_branch0.S", "f0_ma2.S",
    "gt9x16_prod3_ma2_hash_h1.S",
)

CUMULATIVE_SOURCES = IMPLEMENTATION_SOURCES + (
    "gt9x16_prod3_aos_natural.S",
    "gt9x16_prod3_aos_t0_beta.S",
    "gt9x16_prod3_ma2_qorder_natural.S",
    "gt9x16_prod3_cumulative_ma2.S",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cc", default="cc")
    parser.add_argument("--profile", choices=("h1", "cumulative"), default="h1")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit(f"not a disposable SUPERCOP campaign: {root}")
    marker_record = json.loads(marker.read_text(encoding="utf-8"))
    if marker_record.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("campaign marker has the wrong kind")
    if marker_record.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign version does not match bench/supercop.lock")
    implementation = root / "crypto_kem/ntruplus1152" / args.implementation
    if not implementation.is_dir():
        raise SystemExit(f"missing implementation: {implementation}")
    implementation_sources = (CUMULATIVE_SOURCES if args.profile == "cumulative"
                              else IMPLEMENTATION_SOURCES)
    missing = [name for name in implementation_sources
               if not (implementation / name).is_file()]
    if missing:
        raise SystemExit(f"implementation lacks KAT sources: {missing}")
    repo = Path(__file__).resolve().parent.parent
    experiment = repo / (
        "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
        "experiments/avx2_gt9x16_official_001")
    kat_dir = repo / "ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768/kat"
    frozen = repo / "ntruplus-ntt-Optimized/KAT/NTRU+1152"
    includes = list((root / "bench").glob("*/include"))
    if len(includes) != 1:
        raise SystemExit(f"expected one SUPERCOP include root, found {includes}")
    include = includes[0]
    compile_command = [
        args.cc, "-Wno-unused-result", "-mavx2", "-mbmi2", "-mpopcnt",
        "-maes", "-march=native", "-mtune=native", "-O3",
        "-fomit-frame-pointer", f"-I{experiment / 'tests/kat_compat'}",
        f"-I{implementation}", f"-I{include / 'amd64'}", f"-I{include}",
    ]
    compile_command.extend(str(kat_dir / name) for name in (
        "PQCgenKAT_kem.c", "aes.c", "rng.c"))
    compile_command.extend(str(implementation / name)
                           for name in implementation_sources)
    with tempfile.TemporaryDirectory(prefix="ntruplus-prod3-h1-kat-") as temp:
        work = Path(temp)
        binary = work / "PQCgenKAT_kem"
        command = compile_command[:]
        command[1:1] = ["-o", str(binary)]
        subprocess.run(command, cwd=implementation, check=True)
        subprocess.run([str(binary)], cwd=work, check=True)
        request = work / "PQCkemKAT_3488.req"
        response = work / "PQCkemKAT_3488.rsp"
        frozen_request = frozen / request.name
        frozen_response = frozen / response.name
        request_match = request.read_bytes() == frozen_request.read_bytes()
        response_match = response.read_bytes() == frozen_response.read_bytes()
        if not request_match or not response_match:
            raise SystemExit("PROD3 H1 KAT differs from frozen NTRU+1152 KAT")
        compiler = subprocess.run(
            [args.cc, "--version"], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=True).stdout.splitlines()[0]
        manifest = implementation / "SOURCE-MANIFEST.json"
        result = {
            "schema": "ntruplus-prod3-h1-kat-evidence/v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "parameter": 1152,
            "implementation": args.implementation,
            "profile": args.profile,
            "campaign": str(root),
            "compiler": compiler,
            "cases": 100,
            "passed": True,
            "comparison": "byte-exact against frozen NTRU+1152 KAT",
            "request_sha256": sha256_file(request),
            "response_sha256": sha256_file(response),
            "frozen_request_sha256": sha256_file(frozen_request),
            "frozen_response_sha256": sha256_file(frozen_response),
            "candidate_manifest_sha256": (
                sha256_file(manifest) if manifest.is_file() else None),
            "kem_source_sha256": sha256_file(implementation / "kem.c"),
            "h1_source_sha256": sha256_file(
                implementation / "gt9x16_prod3_ma2_hash_h1.S"),
            "native_performance_run": False,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PROD3 H1 KAT passed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
