#!/usr/bin/env python3
"""Build only the direct hash-staging diagnostic, with no cycle measurement."""
import hashlib
import json
import os
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean/avx2-gt32-clean"
BUILD = ROOT / "build/encap-consumer-edges-research"
REPORT = ROOT / "generated/tile4_encap_hash_direct_stage_check.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, **kwargs):
    return subprocess.run(command, check=True, capture_output=True, text=True, **kwargs)


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    sources = [ROOT / "tests/test_encap_hash_direct_stage.c"] + [CLEAN / f for f in
               ("pack.s", "symmetric.c", "fips202.c", "KeccakP-1600-AVX2.s",
                "ntt.s", "ntt_m.s", "consts.c")]
    cc = shlex.split(os.environ.get("CC", "cc"))
    records = {}
    for name, opts in (("normal", ["-O3"]),
                       ("sanitized", ["-O1", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"])):
        elf = BUILD / name
        command = cc + opts + ["-g", "-mavx2", "-fwrapv", "-fno-strict-aliasing",
                              "-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections",
                              "-Wall", "-Wextra", "-Werror", "-I"+str(CLEAN),
                              *map(str, sources), "-o", str(elf)]
        built = run(command)
        (BUILD / (name + ".build.log")).write_text(built.stdout + built.stderr)
        result = run([str(elf)], env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0"})
        (BUILD / (name + ".out")).write_text(result.stdout + result.stderr)
        records[name] = dict(command=command, elf_sha256=sha(elf), checks=json.loads(result.stdout))
    document = dict(scope="test-only direct hash stage; no production change or timing",
                    compiler=run(cc+["--version"]).stdout.splitlines()[0],
                    sources={str(p): sha(p) for p in sources + [Path(__file__)]},
                    results=records,
                    sanitizer_scope="C harness; ASM extent separately checked by guard page and canaries")
    REPORT.write_text(json.dumps(document, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k: v["checks"] for k, v in records.items()}, indent=2))


if __name__ == "__main__":
    main()
