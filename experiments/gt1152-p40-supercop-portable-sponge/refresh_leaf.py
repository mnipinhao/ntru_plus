"""Refresh the SUPERCOP GT leaf from the package, for a fresh measurement.

Three things the package's own build does that SUPERCOP's does not, and that
this has to supply:

  * SUPERCOP compiles every source in the directory with its own flags, so the
    `NTRUPLUS1152_ASM_*` selectors that pick the scheduled kernels over the C
    are prepended to `inverse.c` rather than passed on the command line.
  * The leaf uses lowercase `.s`, which gcc assembles without the preprocessor,
    so the `#ifdef __APPLE__` aliasing the package uses becomes the leaf's
    existing convention of a second `.global` and a second label.
  * Comments are stripped, matching every other file already in the leaf.

keccakf1600_v84a.S is deliberately NOT staged.  The whole file is inside
`#if defined(__ARM_FEATURE_SHA3)`, and this host's Cortex-A76 ships without
FEAT_SHA3 -- its /proc/cpuinfo Features line has aes, sha1 and sha2 but no
sha3 -- so under SUPERCOP's -march=native the file compiles to nothing and
fips202.c selects the scalar backend.  Omitting it produces an identical
binary; running it through to_leaf_asm would not, because that strips the
guard and would leave eor3/rax1/xar/bcax unconditional, which gas rejects
without +sha3.
"""
import re, subprocess, sys
from pathlib import Path

PKG = Path(sys.argv[1] if len(sys.argv) > 1
           else "/Users/chenpinhao/ntruplus/experiments/gt1152-p10-kem")
HOST = "pi@100.99.191.9"
LEAF = "/home/pi/supercop-20260831/crypto_kem/ntruplus1152/aarch64-gt1152"
STAGE = Path("/tmp/leafstage")

DEFINES = ["NTRUPLUS1152_ASM_BASEMUL_RINV",
           "NTRUPLUS1152_ASM_BASEINV_NUM",
           "NTRUPLUS1152_ASM_BASEINV_FINISH"]

UPDATE_C = ["inverse.c", "pack.c", "symmetric.c", "hash_fixed.c",
             "fips202.c"]
UPDATE_H = ["inverse.h", "inverse_asm.h", "fips202.h", "secure_clear.h"]
NEW_ASM = ["basemul_rinv.S", "baseinv_num.S", "baseinv_finish.S"]
# keccakf1600.S is the one file with live preprocessor branches (__APPLE__), so
# it is expanded by the compiler on the target rather than by pattern matching.
CPP_ASM = ["keccakf1600.S"]
REMOVE = []


def to_leaf_asm(text):
    """package .S -> leaf .s: drop cpp aliasing, add the dual global and label."""
    # Block comments first: the per-line strip below only catches ones that open
    # and close on the same line, and the package now has multi-line headers.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out = []
    for line in text.splitlines():
        s = line.split("//")[0].rstrip()
        s = re.sub(r"/\*.*?\*/", "", s).rstrip()
        if not s.strip():
            continue
        if re.match(r"\s*#\s*(ifdef|define|endif)\b", s):
            continue
        out.append(s)
        m = re.match(r"\s*\.global\s+(\w+)\s*$", s)
        if m:
            out.append(f".global _{m.group(1)}")
            continue
        m = re.match(r"^(\w+):\s*$", s)
        if m:
            out.append(f"_{m.group(1)}:")
    return "\n".join(out) + "\n"


STAGE.mkdir(exist_ok=True)
for f in STAGE.glob("*"):
    f.unlink()

for n in UPDATE_C + UPDATE_H:
    t = (PKG / n).read_text()
    if n == "inverse.c":
        t = "".join(f"#define {d} 1\n" for d in DEFINES) + t
    (STAGE / n).write_text(t)

for n in NEW_ASM:
    (STAGE / (Path(n).stem + ".s")).write_text(to_leaf_asm((PKG / n).read_text()))

for n in CPP_ASM:
    subprocess.run(["rsync", "-a", str(PKG / n), f"{HOST}:/tmp/"], check=True)
    out = subprocess.check_output(
        ["ssh", "-o", "BatchMode=yes", HOST,
         f"gcc -E -P -x assembler-with-cpp /tmp/{n}"], text=True)
    assert "#ifdef" not in out and "__APPLE__" not in out, n
    (STAGE / (Path(n).stem + ".s")).write_text(out)

subprocess.run(["rsync", "-a", *[str(p) for p in sorted(STAGE.glob("*"))],
                f"{HOST}:{LEAF}/"], check=True)
subprocess.run(["ssh", "-o", "BatchMode=yes", HOST,
                f"cd {LEAF} && rm -f {' '.join(REMOVE)} && ls | tr '\\n' ' '"], check=True)
print("\nstaged:", ", ".join(sorted(p.name for p in STAGE.glob("*"))))
print("removed:", ", ".join(REMOVE))
