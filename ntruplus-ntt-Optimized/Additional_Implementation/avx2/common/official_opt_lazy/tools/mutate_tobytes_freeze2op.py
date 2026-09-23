#!/usr/bin/env python3
"""Mutation check: the tobytes freeze2op differential must reject broken kernels.

Each mutant is the generated asm/ntruplus{N}_officialopt_tobytes_freeze2op.s
with one line changed (written to a temporary directory; the tracked file is
never modified).  tests/test_tobytes_freeze2op.c is rebuilt against the
mutant with the Makefile's release flags and must exit non-zero; the
unmutated build must pass.  Run after `make freeze-check` (from the
experiment directory):

  mutate_tobytes_freeze2op.py --param 768 --experiment . --output build/evidence/freeze2op-mutation-check.json
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON = HERE.parents[1]
MUTANTS = [
    ("signed_min", "vpminuw %ymm13, %ymm7, %ymm7", "vpminsw %ymm13, %ymm7, %ymm7"),
    ("dropped_min", "vpminuw %ymm10, %ymm0, %ymm0", ""),
    ("sub_instead_of_add_q", "vpaddw %ymm14, %ymm5, %ymm11", "vpsubw %ymm14, %ymm5, %ymm11"),
    ("min_wrong_operand", "vpminuw %ymm12, %ymm6, %ymm6", "vpminuw %ymm11, %ymm6, %ymm6"),
    ("barrett_dropped", "vpsubw %ymm13, %ymm3,  %ymm3", ""),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    n = args.param
    root = args.experiment.resolve()
    asm = root / f"asm/ntruplus{n}_officialopt_tobytes_freeze2op.s"
    lazy = root / f"asm/ntruplus{n}_officialopt_ntt_caller_lazy.s"
    up = root / "upstream/supercop-avx2"
    text = asm.read_text()
    pristine = "/home/nuc/src/supercop-pristine-20260831"
    flags = ["-O3", "-mavx2", "-march=native", "-mtune=native", "-fPIE",
             f"-I{COMMON}/tests/support", f"-I{up}", f"-I{pristine}/cryptoint", f"-I{pristine}/include",
             f"-DFREEZE_TOBYTES=ntruplus{n}_officialopt_tobytes_freeze2op",
             f"-DLAZY_NTT=ntruplus{n}_officialopt_ntt_caller_lazy"]
    srcs = [COMMON / "tests/test_tobytes_freeze2op.c", COMMON / "tests/support/crypto_declassify.c", lazy]
    srcs += [up / f for f in ("poly.c", "symmetric.c", "fips202.c", "consts.c", "KeccakP-1600-AVX2.s",
                              "ntt.s", "basemul.s", "baseinv.s", "invntt.s", "pack.s", "add.s", "cbd.s",
                              "crepmod3.s")]
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, old, new in [("unmutated", None, None)] + MUTANTS:
            if old is None:
                body = text
            else:
                if text.count(old + "\n") != 1:
                    raise SystemExit(f"mutant {name}: target line not unique")
                body = text.replace(old + "\n", new + "\n" if new else "", 1)
            m = Path(tmp) / f"{name}.s"
            m.write_text(body)
            exe = Path(tmp) / name
            subprocess.run(["cc", *flags, "-o", str(exe), *map(str, srcs), str(m)], check=True)
            r = subprocess.run([str(exe)], capture_output=True, text=True)
            detected = r.returncode != 0
            first = (r.stderr.strip().splitlines() or [""])[0]
            results.append({"mutant": name, "from": old, "to": new, "exit": r.returncode,
                            "detected": detected, "first_failure": first})
            print(f"{name:22s} exit={r.returncode} {first}")
    ok = not results[0]["detected"] and all(r["detected"] for r in results[1:])
    record = {"class": "mutation check of the tobytes freeze2op differential", "parameter": f"NTRU+{n}",
              "mutants": results, "pass": ok}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n")
    print("mutation check", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
