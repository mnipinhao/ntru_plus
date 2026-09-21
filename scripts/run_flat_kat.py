#!/usr/bin/env python3
"""Run a flat SUPERCOP implementation against the frozen 100-vector KAT."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import REPO_ROOT, read_lock, sha256_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--parameter", choices=("768", "864", "1152"), required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cc", default="cc")
    parser.add_argument("--sanitize", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    root = args.campaign_root.resolve()
    marker = json.loads((root / ".ntruplus-campaign.json").read_text())
    if marker.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign version mismatch")
    implementation = root / "crypto_kem" / f"ntruplus{args.parameter}" / args.implementation
    sources = sorted(path for path in implementation.iterdir()
                     if path.suffix in (".c", ".s", ".S") and
                     path.name != "ntruplus_bench.c")
    if not sources:
        raise SystemExit(f"no implementation sources in {implementation}")
    includes = list((root / "bench").glob("*/include"))
    if len(includes) != 1:
        raise SystemExit(f"expected one SUPERCOP include root, found {includes}")
    include = includes[0]
    kat_source = REPO_ROOT / "ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768/kat"
    frozen = REPO_ROOT / "ntruplus-ntt-Optimized/KAT" / f"NTRU+{args.parameter}"
    api_bytes = {"768": "2336", "864": "2624", "1152": "3488"}[args.parameter]
    compat = (REPO_ROOT / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
              "NTRU+1152/experiments/avx2_gt9x16_official_001/tests/kat_compat")
    command = [args.cc, "-Wno-unused-result", "-mavx2", "-mbmi2", "-mpopcnt",
               "-maes", "-march=native", "-mtune=native", "-O3",
               "-fomit-frame-pointer", f"-I{compat}", f"-I{implementation}",
               f"-I{include / 'amd64'}", f"-I{include}"]
    if args.sanitize:
        command.extend(("-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                        "-fno-omit-frame-pointer"))
    command.extend(str(kat_source / name) for name in
                   ("PQCgenKAT_kem.c", "aes.c", "rng.c"))
    command.extend(str(path) for path in sources)
    with tempfile.TemporaryDirectory(prefix=f"ntruplus{args.parameter}-kat-") as temp:
        work = Path(temp)
        binary = work / "PQCgenKAT_kem"
        subprocess.run(command[:1] + ["-o", str(binary)] + command[1:],
                       cwd=implementation, check=True)
        environment = os.environ.copy()
        if args.sanitize:
            environment["ASAN_OPTIONS"] = "detect_leaks=0"
        subprocess.run([str(binary)], cwd=work, env=environment, check=True)
        request = work / f"PQCkemKAT_{api_bytes}.req"
        response = work / f"PQCkemKAT_{api_bytes}.rsp"
        frozen_request = frozen / request.name
        frozen_response = frozen / response.name
        if request.read_bytes() != frozen_request.read_bytes() or \
                response.read_bytes() != frozen_response.read_bytes():
            raise SystemExit("candidate differs from frozen KAT")
        record = {
            "schema": "ntruplus-flat-kat/v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "parameter": int(args.parameter),
            "implementation": args.implementation,
            "cases": 100,
            "passed": True,
            "sanitizers": "address,undefined" if args.sanitize else None,
            "comparison": "byte-exact against frozen KAT",
            "request_sha256": sha256_file(request),
            "response_sha256": sha256_file(response),
            "source_manifest_sha256": (sha256_file(implementation / "SOURCE-MANIFEST.json")
                                       if (implementation / "SOURCE-MANIFEST.json").is_file()
                                       else None),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"KAT passed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
