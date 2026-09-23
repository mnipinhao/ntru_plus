#!/usr/bin/env python3
"""Mutation check: the SHAKE256 differential must reject one-line Keccak mutants.

Each mutant is a copy of one vendored mlkem-native source (or of the pinned
Official symmetric.c that src/symmetric_keccak.c includes) with exactly one
textual change, compiled with the release CFLAGS into build/keccak_mutants/<name>/
and linked into tests/test_shake256_keccak.c exactly like the real
candidate.  Gate: every mutant build fails the differential (non-zero exit);
the unmutated control built the same way passes.

  mutate_keccak.py --param 768 --experiment . --output build/evidence/keccak-mutation-check.json
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON = HERE.parents[1]
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
MLK = REPO / "third_party/mlkem-native-fips202-b3ba7b32/mlkem/src/fips202"
LAZY = COMMON.parent / "official_opt_lazy"

MUTANTS = [
    ("shake256_domain_0x1f_to_0x1e", "fips202.c",
     "mlk_keccak_absorb_once(state.ctx, SHAKE256_RATE, input, inlen, 0x1F);",
     "mlk_keccak_absorb_once(state.ctx, SHAKE256_RATE, input, inlen, 0x1E);"),
    ("pad_last_byte_merge_128_to_64", "fips202.c", "    p |= 128;", "    p |= 64;"),
    ("squeeze_block_len_r_minus_1", "fips202.c", "      len = r;", "      len = r - 1;"),
    ("round_constant_23", "keccakf1600.c", "(uint64_t)0x8000000080008008ULL};", "(uint64_t)0x8000000080008009ULL};"),
    ("rho_age_44_to_43", "keccakf1600.c", "    BCe = MLK_KECCAK_ROL(Age, 44);", "    BCe = MLK_KECCAK_ROL(Age, 43);"),
    ("chi_first_row_and_to_or", "keccakf1600.c", "    Eba = BCa ^ ((~BCe) & BCi);", "    Eba = BCa ^ ((~BCe) | BCi);"),
    ("hash_g_domain_0x01_to_0x02", "symmetric.c", "    data[0] = 0x01;", "    data[0] = 0x02;"),
    ("hash_h_input_one_byte_short", "symmetric.c", "    shake256(buf, HASH_H_OUTBYTES, data, HASH_H_INBYTES + 1);",
     "    shake256(buf, HASH_H_OUTBYTES, data, HASH_H_INBYTES);"),
]
CFLAGS = "-O3 -mavx2 -march=native -mtune=native -fPIE -Wall -Wextra -Werror".split()


def sh(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)


def build_and_run(root, work, sources, includes):
    """sources: {'fips202.c': path, 'keccakf1600.c': path, 'symmetric.c': dir-or-None}."""
    up = root / "upstream/supercop-avx2"
    cfg = COMMON / "config"
    objs = []
    for name in ("fips202.c", "keccakf1600.c"):
        o = work / f"mlk_{name[:-2]}.o"
        r = sh(["cc", *CFLAGS, f"-I{cfg}", "-c", "-o", o, sources[name]])
        if r.returncode:
            raise RuntimeError(r.stderr)
        objs.append(o)
    inc = [f"-I{sources['symmetric_dir']}"] if sources.get("symmetric_dir") else []
    o = work / "symmetric_keccak.o"
    r = sh(["cc", *CFLAGS, *inc, *includes, f"-I{COMMON / 'src'}", f"-I{cfg}",
            f"-I{REPO / 'third_party/mlkem-native-fips202-b3ba7b32'}", "-c", "-o", o, COMMON / "src/symmetric_keccak.c"])
    if r.returncode:
        raise RuntimeError(r.stderr)
    objs.append(o)
    official = [up / f for f in ("poly.c", "symmetric.c", "fips202.c", "consts.c", "KeccakP-1600-AVX2.s", "ntt.s",
                                 "basemul.s", "baseinv.s", "invntt.s", "pack.s", "add.s", "cbd.s", "crepmod3.s")]
    elf = work / "test_shake256_keccak"
    r = sh(["cc", *CFLAGS, *includes, "-o", elf, COMMON / "tests/test_shake256_keccak.c",
            LAZY / "tests/support/crypto_declassify.c", *official, *objs])
    if r.returncode:
        raise RuntimeError(r.stderr)
    r = sh([elf, COMMON / "tests/vectors/shake256_cavp_subset.txt"])
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--includes", required=True, help="the experiment's lazy.mk INCLUDES")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    includes = args.includes.split()
    root = args.experiment.resolve()
    base = root / "build/keccak_mutants"
    shutil.rmtree(base, ignore_errors=True)
    real = {"fips202.c": MLK / "fips202.c", "keccakf1600.c": MLK / "keccakf1600.c"}
    control = base / "control"
    control.mkdir(parents=True)
    code, tail = build_and_run(root, control, real, includes)
    results = {"control_unmutated": {"exit": code, "last_line": tail}}
    ok = code == 0
    for name, target, old, new in MUTANTS:
        work = base / name
        work.mkdir(parents=True)
        src = (root / "upstream/supercop-avx2/symmetric.c") if target == "symmetric.c" else MLK / target
        text = src.read_text()
        if text.count(old) != 1:
            raise ValueError(f"{name}: anchor occurs {text.count(old)}x")
        sources = dict(real)
        if target == "symmetric.c":
            (work / target).write_text(text.replace(old, new))
            sources["symmetric_dir"] = work
        else:
            # mutate inside a copy of the vendored tree so its relative includes resolve
            shutil.copytree(MLK.parents[1], work / "mlkem")
            dst = work / "mlkem/src/fips202" / target
            dst.write_text(text.replace(old, new))
            sources[target] = dst
        code, tail = build_and_run(root, work, sources, includes)
        results[name] = {"file": target, "from": old.strip(), "to": new.strip(), "exit": code, "last_line": tail,
                         "rejected": code != 0}
        ok &= code != 0
    summary = {"parameter": f"NTRU+{args.param}", "mutants": len(MUTANTS),
               "rejected": sum(1 for k, v in results.items() if k != "control_unmutated" and v["rejected"]),
               "pass": bool(ok), "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"pass": summary["pass"], "rejected": f"{summary['rejected']}/{len(MUTANTS)}",
                      "control": results["control_unmutated"]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
