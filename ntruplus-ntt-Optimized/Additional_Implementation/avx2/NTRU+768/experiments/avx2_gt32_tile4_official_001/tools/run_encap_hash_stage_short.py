#!/usr/bin/env python3
"""Source-pinned C-only hash-copy experiment; clean ASM is reused unchanged."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import platform
import re
import shlex
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean/avx2-gt32-clean"
REPO = next(p for p in ROOT.parents if (p / "bench/supercop.lock").exists())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, verify_supercop


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, **kwargs)
    if result.returncode:
        print(result.stdout + result.stderr, file=sys.stderr)
        result.check_returncode()
    return result


def stq(values):
    expanded = sorted(x for x in values for _ in range(8))
    n = len(values)
    return [sum(expanded[n+2*n*i:n+2*n*(i+1)])/(2*n) for i in range(3)]


def candidate_source():
    original = (CLEAN / "encap.c").read_text()
    old = "\tntruplus768_pack_m_lazy10788_avx2(ct, scratch.r);\n\thash_g(ct, ct);"
    assert original.count(old) == 1
    helper = '''
#include "fips202.h"
/* Keep the original hash_g-sized buffer and its clearing, but have the
 * existing M serializer produce directly into its final hash input slot. */
__attribute__((noinline)) void ntruplus768_hash_stage_research(uint8_t *out,
                                                            const int16_t *r)
{
    uint8_t data[1 + HASH_G_INBYTES];
    data[0] = 0x01;
    ntruplus768_pack_m_lazy10788_avx2(data + 1, r);
    shake256(out, HASH_G_OUTBYTES, data, sizeof data);
    secure_clear(data, sizeof data);
}

'''
    body = original.replace("ntruplus768_enc_derand_impl", "ntruplus768_hash_stage_enc_derand")
    body = body.replace(old, "\tntruplus768_hash_stage_research(ct, scratch.r);")
    return body.replace("typedef struct", helper + "typedef struct", 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--supercop-root", required=True, type=Path)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--cpu", type=int, default=1)
    ap.add_argument("--launches", type=int, choices=(3, 9), default=3)
    args = ap.parse_args()
    assert run(["git", "branch", "--show-current"], cwd=REPO).stdout.strip() == "avx2-gt-ntt"
    expected = {f"/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor": "performance",
                "/sys/devices/system/cpu/intel_pstate/no_turbo": "1"}
    for path, want in expected.items():
        if Path(path).read_text().strip() != want:
            raise SystemExit(f"host preflight failed: {path}; no timing")
    lock = read_lock(REPO / "bench/supercop.lock")
    verified = verify_supercop(args.supercop_root, lock)
    result = ROOT / "results" / args.tag
    result.mkdir(parents=True, exist_ok=False)
    source = result / "hash_stage_candidate.c"
    source.write_text(candidate_source())
    assert source.read_text() == candidate_source()
    libs = list((args.supercop_root / "bench").glob("*/lib/nontimecop/amd64/libcpucycles.a"))
    if len(libs) != 1:
        raise SystemExit("expected one pinned cpucycles library")
    lib = libs[0]
    include = lib.parents[3] / "include/nontimecop/amd64"
    # SUPERCOP's implementation directory has no deterministic KAT RNG.
    # Reuse the same test-only AES-CTR RNG as this experiment's KEM tests.
    kat_support = REPO / "third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768"
    files = ("keygen.c encap.c decap.c poly.c symmetric.c fips202.c baseinv.c consts.c "
             "KeccakP-1600-AVX2.s cbd.s crepmod3.s add.s ntt.s ntt_m.s ntt_p.s "
             "invntt.s basemul.s batch_inverse.s pack.s").split()
    inputs = [ROOT / "bench/bench_encap_hash_direct_stage.c", source,
              *[CLEAN / f for f in files], kat_support / "kat/aes.c", kat_support / "kat/rng.c"]
    cc = shlex.split(os.environ.get("CC", "cc"))
    common = ["-march=native", "-mtune=native", "-mavx2", "-fwrapv", "-fno-strict-aliasing",
              "-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections", "-fPIE", "-pie",
              "-I"+str(CLEAN), "-I"+str(kat_support), "-I"+str(include)]
    build = cc + ["-O3"] + common + list(map(str, inputs)) + [str(lib), "-o", str(result / "measure")]
    built = run(build)
    (result / "build.log").write_text(built.stdout+built.stderr)
    san = cc + ["-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-DCORRECTNESS_ONLY"] + common + list(map(str, inputs)) + ["-o", str(result / "sanitize")]
    run(san)
    checked = run([str(result / "sanitize")], env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0"})
    (result / "sanitize.out").write_text(checked.stdout+checked.stderr)
    for command, filename in ((["objdump", "-d", str(result / "measure")], "disassembly.txt"),
                              (["nm", "-S", "-n", str(result / "measure")], "symbols.txt"),
                              (["size", "-A", str(result / "measure")], "sections.txt")):
        (result / filename).write_text(run(command).stdout)
    old_dis = run(["objdump", "-d", "--disassemble=hash_g", str(result / "measure")]).stdout
    new_dis = run(["objdump", "-d", "--disassemble=ntruplus768_hash_stage_research", str(result / "measure")]).stdout
    assert "<memcpy@plt>" in old_dis and "<memcpy@plt>" not in new_dis
    assert "<ntruplus768_pack_m_lazy10788_avx2>" in new_dis
    stack = r"sub\s+\$0x([0-9a-f]+),%rsp"
    old_frame = int(re.search(stack, old_dis).group(1), 16)
    new_frame = int(re.search(stack, new_dis).group(1), 16)
    assert old_frame == new_frame
    assert "vzeroupper" not in new_dis
    assert all(name in text for text in (old_dis, new_dis)
               for name in ("<fips202avx_shake256>", "<__explicit_bzero_chk@plt>"))
    (result / "hash-stage-linked-audit.json").write_text(json.dumps(dict(
        original_stack_adjust_bytes=old_frame, candidate_stack_adjust_bytes=new_frame,
        original_memcpy_call=True, candidate_memcpy_call=False, same_clean_serializer=True,
        same_shake=True, same_explicit_clear=True, new_vzeroupper=False,
        scope="generated C helper; polynomial ASM unchanged; no cycle attribution inferred"), indent=2)+"\n")
    rows = []
    for launch in range(args.launches):
        measured = run(["taskset", "-c", str(args.cpu), str(result / "measure")])
        assert "preflight=pass" in measured.stderr
        (result / f"launch-{launch}.csv").write_text(measured.stdout)
        (result / f"launch-{launch}.err").write_text(measured.stderr)
        for row in csv.DictReader(io.StringIO(measured.stdout)):
            row = {k: int(v) for k, v in row.items()}
            order = (1, 0, 0, 1) if row["block"] % 2 else (0, 1, 1, 0)
            row.update(launch=launch, variant=order[row["slot"]])
            rows.append(row)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["region"], row["variant"], row["launch"]].append(row["cycles"])
    summary = {}
    for region, name in enumerate(("retained_r_to_hash_output", "full_deterministic_encap")):
        pooled = [stq([x for launch in range(args.launches) for x in grouped[region, v, launch]]) for v in (0, 1)]
        delta = [stq(grouped[region, 1, launch])[1]-stq(grouped[region, 0, launch])[1] for launch in range(args.launches)]
        summary[name] = dict(control_stq=pooled[0], candidate_stq=pooled[1],
                             candidate_minus_control_stq2=pooled[1][1]-pooled[0][1],
                             launch_delta=delta, favorable_launches=sum(x < 0 for x in delta))
    (result / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    metadata = dict(classification="SUPERCOP-derived diagnostic; not Native KEM", lock=lock,
                    verified_snapshot=verified, compiler=run(cc+["--version"]).stdout.splitlines()[0],
                    command=build, sanitize_command=san, elf_sha256=sha(result / "measure"),
                    source_sha256={str(p): sha(p) for p in inputs+[Path(__file__)]},
                    cpucycles_library_sha256=sha(lib), host=dict(cpu=args.cpu, frequency=expected,
                    smt_siblings=Path(f"/sys/devices/system/cpu/cpu{args.cpu}/topology/thread_siblings_list").read_text().strip(),
                    aslr=Path("/proc/sys/kernel/randomize_va_space").read_text().strip(), platform=platform.platform()),
                    input_banks=16, fresh_processes=args.launches, placement="normal", ordering="ABBA/BAAB",
                    residency="same bank addresses/order; per-variant warmup; inputs immutable; outputs overwritten",
                    timed_region="one preselected function-pointer call; no variant dispatch/reset/validation/IO",
                    correctness="100 deterministic Encap coins across 16 keys; invalid PK/CT; ASan/UBSan",
                    promotion=False)
    (result / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True)+"\n")
    print(json.dumps(dict(result=str(result), summary=summary), indent=2))


if __name__ == "__main__":
    main()
