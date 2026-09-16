#!/usr/bin/env python3
"""Integrate P47 privately into Decaps and run correctness plus paired Pi5 PMU."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNNER = ROOT / "experiments/gt864-p18-partial-transpose-tobytes/run_pi5.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("p47_p18_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


p18 = load_runner()
p15 = p18.p15
p18.HERE = HERE
p15.HERE = HERE
p15.BUILD = HERE / "build"
p15.SYNC = p15.BUILD / "sync"
p15.RAW = p15.BUILD / "pi5"
p15.REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p47-20260916"
p18.EXPECTED_KAT = "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
p18.EXPECTED_MALFORMED = "2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"


def update_manifest(package: Path, extra: str | None = None) -> None:
    path = package / "SOURCE-MANIFEST.sha256"
    names = [line.split(None, 1)[1] for line in path.read_text().splitlines() if line.strip()]
    if extra and extra not in names:
        names.append(extra)
    lines = []
    for name in names:
        source = package / name
        if not source.is_file():
            raise RuntimeError(f"manifest source missing: {source}")
        lines.append(f"{hashlib.sha256(source.read_bytes()).hexdigest()}  {name}")
    path.write_text("\n".join(lines) + "\n")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"expected one replacement in {path}: {old!r}")
    path.write_text(text.replace(old, new))


def stage() -> None:
    if p15.SYNC.exists():
        shutil.rmtree(p15.SYNC)
    for name in ("baseline", "candidate"):
        p15.extract(p15.SYNC / "packages" / name)
    candidate = p15.SYNC / "packages/candidate"
    shutil.copy2(HERE / "candidate-compare.g3.opt.S",
                 candidate / "gt864_p47_decaps_compare.S")

    replace_once(candidate / "Makefile",
                 "TOBYTES_OBJECTS := gt864_p18_tobytes_full.o",
                 "TOBYTES_OBJECTS := gt864_p47_decaps_compare.o gt864_p18_tobytes_full.o")
    makefile = candidate / "Makefile"
    text = makefile.read_text()
    anchor = "gt864_p18_tobytes_full.o: gt864_p18_tobytes_full.S gt864_p18_tobytes.h\n"
    rule = ("gt864_p47_decaps_compare.o: gt864_p47_decaps_compare.S gt864_p18_tobytes.h\n"
            "\t$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@\n")
    if text.count(anchor) != 1:
        raise RuntimeError("P47 Makefile anchor drift")
    makefile.write_text(text.replace(anchor, rule + anchor))

    header = candidate / "gt864_tobytes.h"
    replace_once(header, "void gt864_fr0_tobytes_full(uint8_t *out, const poly *in);",
                 "void gt864_fr0_tobytes_full(uint8_t *out, const poly *in);\n"
                 "int gt864_fr0_tobytes_full_compare(const uint8_t expected[1296], const poly *in);")
    source = candidate / "gt864_tobytes.c"
    replace_once(source,
                 "void gt864_tobytes_small_asm(uint8_t*,const int16_t*,const void*,const void*,const void*);",
                 "void gt864_tobytes_small_asm(uint8_t*,const int16_t*,const void*,const void*,const void*);\n"
                 "int gt864_p47_decaps_compare_asm(const uint8_t*,const int16_t*);")
    replace_once(source,
                 "void gt864_fr0_tobytes_small(uint8_t*out,const poly*in){",
                 "int gt864_fr0_tobytes_full_compare(const uint8_t*expected,const poly*in){\n"
                 " return gt864_p47_decaps_compare_asm(expected,in->coeffs);\n}\n"
                 "void gt864_fr0_tobytes_small(uint8_t*out,const poly*in){")

    kem = candidate / "kem.c"
    replace_once(kem, "\tuint8_t buf2[NTRUPLUS_POLYBYTES];",
                 "\tuint8_t buf2[NTRUPLUS_N / 4];")
    replace_once(kem,
                 "    gt864_fr0_tobytes_full(buf2, &f);\n\n"
                 "    fail |= verify(buf1, buf2, NTRUPLUS_POLYBYTES);",
                 "    fail |= gt864_fr0_tobytes_full_compare(buf1, &f);")
    update_manifest(candidate, "gt864_p47_decaps_compare.S")

    shutil.copy2(HERE / "test.c", p15.SYNC / "compare-test.c")
    harness = (ROOT / "experiments/gt864-official-profile-p8/full_harness.c").read_text()
    (p15.SYNC / "kem.c").write_text(harness.replace('v?"gt":"official"',
                                                       'v?"candidate":"baseline"'))
    shutil.copy2(ROOT / "experiments/gt864-native-asm/kem-malformed-transcript.c",
                 p15.SYNC / "malformed.c")
    manifest = {str(path.relative_to(p15.SYNC)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(p15.SYNC.rglob("*")) if path.is_file()}
    (p15.BUILD / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def audit() -> dict[str, object]:
    result: dict[str, object] = {}
    for variant in ("baseline", "candidate"):
        kem = p15.ssh(f"cd {p15.REMOTE}/packages/{variant} && objdump -dr kem-normal.o")
        (p15.RAW / f"kem-{variant}.objdump").write_text(kem)
        result[variant] = {
            "object_calls_generic_full": len(re.findall(
                r"R_AARCH64_CALL26\s+gt864_fr0_tobytes_full$", kem, re.M)),
            "object_calls_fused_compare": len(re.findall(
                r"R_AARCH64_CALL26\s+gt864_fr0_tobytes_full_compare$", kem, re.M)),
            "crypto_kem_dec_stack_bytes": int(re.search(
                r"Disassembly of section \.text\.crypto_kem_dec:.*?mov\s+x12,\s*#0x[0-9a-f]+\s+// #(\d+)",
                kem, re.I | re.S).group(1)),
        }
    compare = p15.ssh(f"cd {p15.REMOTE}/packages/candidate && objdump -d gt864_p47_decaps_compare.o")
    (p15.RAW / "compare-candidate.objdump").write_text(compare)
    q_stack = len(re.findall(r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$", compare))
    if q_stack:
        raise RuntimeError("P47 compare object spills Q registers")
    result["compare_object"] = {
        "instructions": len(re.findall(r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+", compare)),
        "q_stack_accesses": q_stack,
        "candidate_byte_stores": len(re.findall(r"(?mi)^.*\bstr[bhdq]?\b", compare)),
    }
    return result


def main() -> None:
    stage()
    p15.RAW.mkdir(parents=True, exist_ok=True)
    p15.ssh(f"mkdir -p {p15.REMOTE}")
    print(p15.output(["rsync", "-av", str(p15.SYNC) + "/",
                      p15.HOST + ":" + p15.REMOTE + "/"]), flush=True)
    environment = p15.ssh(
        "uname -a; gcc --version | head -1; "
        "cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor; "
        "vcgencmd measure_temp; vcgencmd get_throttled; "
        "ps -eo args | grep '[d]o-part' || true")
    if "throttled=0x0" not in environment or p15.ssh("lscpu | grep 'Model name'").count("Cortex-A76") != 1:
        raise RuntimeError(environment)
    if "do-part" in environment:
        raise RuntimeError("Pi5 has a competing SUPERCOP do-part process")
    (p15.RAW / "environment-before.txt").write_text(environment)
    commands = []
    for variant in ("baseline", "candidate"):
        commands += [
            f"make -C packages/{variant} clean >/dev/null 2>&1 || true",
            f"make -C packages/{variant} -B -j4 manifest-check libgt864.so test_kem PQCgenKAT_kem",
            f"packages/{variant}/test_kem",
            f"cd packages/{variant}; ./PQCgenKAT_kem >/dev/null; cd ../..",
        ]
    commands += [
        "gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -Ipackages/candidate "
        "compare-test.c packages/candidate/randombytes.c -Lpackages/candidate -lgt864 "
        f"-Wl,-rpath,{p15.REMOTE}/packages/candidate -o compare-test",
        "./compare-test",
    ]
    build = p15.ssh(f"cd {p15.REMOTE} && " + " && ".join(commands))
    if build.count("PASS: 64 KEM") != 2 or "P47 native differential passed" not in build:
        raise RuntimeError("P47 target correctness failed")
    (p15.RAW / "build.log").write_text(build)
    kat_lines = p15.ssh(
        f"cd {p15.REMOTE} && sha256sum packages/baseline/PQCkemKAT_2624.rsp "
        "packages/candidate/PQCkemKAT_2624.rsp").strip().splitlines()
    hashes = [line.split()[0] for line in kat_lines]
    if hashes != [p18.EXPECTED_KAT, p18.EXPECTED_KAT]:
        raise RuntimeError(f"KAT mismatch: {kat_lines}")
    target_audit = audit()
    full = p18.full_kem_gate()
    result = {
        "experiment": "GT864-P47-DECAPS-FULL-TOBYTES-COMPARE-20260916",
        "baseline_revision": p15.output(["git", "rev-parse", "HEAD"], ROOT).strip(),
        "host": p15.HOST,
        "remote": p15.REMOTE,
        "kat_sha256": hashes[0],
        "target_audit": target_audit,
        "slothy_result": "slothy-compare-g3.json",
        "full_kem_gate": full,
        "decaps_wins": full["kem"]["decaps"]["paired_delta"]["cycles"] < 0,
        "environment_before": environment.strip().splitlines(),
        "source_manifest_sha256": hashlib.sha256((p15.BUILD / "source-manifest.json").read_bytes()).hexdigest(),
    }
    (HERE / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
