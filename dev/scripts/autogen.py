"""Install one tier and target of the NTRU+1152 kernels into a package directory.

mlkem-native's `autogen` copies its single optimized tier into the main tree.
Here the tier and the microarchitecture are both arguments, because SUPERCOP
selects among sibling implementations per host and this repository ships more
than one.

    autogen.py clean        <pkg>       the symbolic tier, for testing the DAG
    autogen.py cortex_a76   <pkg>       the Pi 5 schedule
    autogen.py apple_m1_firestorm <pkg>

Installing a kernel replaces the C definition it supersedes: the package keeps
both, and `NTRUPLUS1152_ASM_<KERNEL>` selects the assembly, so a package with no
installed kernels still builds and still passes every gate.
"""
import argparse, hashlib, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEV = HERE.parent
TIERS = {"clean": DEV / "ntruplus1152_clean" / "src"}
for t in ("cortex_a76", "neoverse_n1", "apple_m1_firestorm"):
    TIERS[t] = DEV / "ntruplus1152_opt" / t

p = argparse.ArgumentParser()
p.add_argument("tier", choices=sorted(TIERS))
p.add_argument("package", type=Path)
p.add_argument("--kernels", nargs="*", default=None)
a = p.parse_args()

src_dir = TIERS[a.tier]
if not src_dir.is_dir():
    sys.exit(f"{src_dir} does not exist; run `make {a.tier}` in ntruplus1152_opt first")

suffix = ".sym.S" if a.tier == "clean" else ".S"
found = sorted(src_dir.glob(f"*{suffix}"))
if a.kernels:
    found = [f for f in found if f.name[: -len(suffix)] in a.kernels]
if not found:
    sys.exit(f"no kernels matching {a.kernels} in {src_dir}")

for f in found:
    name = f.name[: -len(suffix)]
    dst = a.package / f"{name}.S"
    shutil.copyfile(f, dst)
    print(f"  {a.tier}/{f.name}  ->  {dst.relative_to(a.package.parent)}"
          f"  ({hashlib.sha256(dst.read_bytes()).hexdigest()[:16]})")
print(f"installed {len(found)} kernel(s) from tier '{a.tier}'")
print("Remember to add each .S to ASM_SRC, define NTRUPLUS1152_ASM_<KERNEL>, "
      "and rebuild SOURCE-MANIFEST.sha256.")
