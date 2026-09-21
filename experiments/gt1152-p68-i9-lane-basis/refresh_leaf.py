"""Stage the P68 lane-basis inverse into the SUPERCOP GT leaf.

The leaf uses lowercase `.s`, which gcc assembles without the preprocessor, so
every assembly file is expanded on the target with `gcc -E -P` rather than
pattern-matched: inverse_ntt.S uses a live `C(name)` macro that the P40
script's to_leaf_asm cannot handle.  On Linux `C(name)` is `name`, which is
already the leaf's convention.

Four assembly files change and two are new; api_glue.c changes to pass the
repacked radix-9 table.
"""
import subprocess, sys
from pathlib import Path

PKG  = Path(sys.argv[1] if len(sys.argv) > 1 else "../gt1152-p10-kem")
HOST = "pi@100.99.191.9"
LEAF = "/home/pi/supercop-20260831/crypto_kem/ntruplus1152/aarch64-gt1152"
STAGE = Path("/tmp/leafstage-p68")

ASM   = ["inverse9.S", "inverse16.S", "inverse_ntt.S", "rebase.S"]
PLAIN = ["api_glue.c", "invntt9_lane_tables.h", "secure_clear.h"]

STAGE.mkdir(exist_ok=True)
for f in STAGE.glob("*"):
    f.unlink()

for n in PLAIN:
    (STAGE / n).write_text((PKG / n).read_text())

for n in ASM:
    subprocess.run(["rsync", "-a", str(PKG / n), f"{HOST}:/tmp/"], check=True)
    out = subprocess.check_output(
        ["ssh", "-o", "BatchMode=yes", HOST,
         f"gcc -E -P -x assembler-with-cpp /tmp/{n}"], text=True)
    assert "#ifdef" not in out and "__APPLE__" not in out and "C(" not in out, n
    # strip comment-only and blank lines, matching the rest of the leaf
    keep = []
    for line in out.splitlines():
        s = line.split("//")[0].rstrip()
        if s.strip():
            keep.append(s)
    (STAGE / (Path(n).stem + ".s")).write_text("\n".join(keep) + "\n")

subprocess.run(["rsync", "-a", *[str(p) for p in sorted(STAGE.glob("*"))],
                f"{HOST}:{LEAF}/"], check=True)
print("staged:", ", ".join(sorted(p.name for p in STAGE.glob("*"))))
