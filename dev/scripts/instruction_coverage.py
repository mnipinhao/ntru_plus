"""Which instructions the NTRU+1152 kernels use, and which SLOTHY models cover them.

A microarchitecture model covers an instruction when its class, or one of that
class's ancestors, appears in the model's `execution_units` map.  SLOTHY raises
`UnknownInstruction` otherwise, which is exactly how the Apple M1 and Neoverse
runs fail today.
"""
import os, sys, re
from pathlib import Path
from collections import Counter, defaultdict

SLOTHY_ROOT = Path(os.environ.get("SLOTHY_ROOT", "/Users/chenpinhao/slothy"))
sys.path.insert(0, str(SLOTHY_ROOT))
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.helper import SourceLine

MODELS = ["cortex_a76", "neoverse_n1_experimental",
          "apple_m1_firestorm_experimental", "apple_m1_icestorm_experimental"]
loaded = {m: __import__(f"slothy.targets.aarch64.{m}", fromlist=["x"]) for m in MODELS}

# Report both states for the M1 models: as SLOTHY ships them, and with this
# repository's seven-class patch applied.
if "--patched" in sys.argv:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "slothy_models"))
    import apple_m1_ntruplus
    for m in MODELS:
        if m.startswith("apple_m1"):
            apple_m1_ntruplus.patch(loaded[m])


def resolves(inst, model):
    """Ask the model itself, rather than inspecting its tables.

    `cortex_a76` resolves several classes through explicit isinstance branches
    in `get_resource_usages` that never appear in `execution_units`, so reading
    the dicts under-reports it.  Calling the three query functions is the same
    thing SLOTHY does, and `UnknownInstruction` is exactly how the Apple M1 runs
    fail today.
    """
    mod = loaded[model]
    try:
        mod.get_units(inst)
        mod.get_latency(inst, 0, inst)
        mod.get_inverse_throughput(inst)
    except Exception as e:
        if type(e).__name__ == "UnknownInstruction":
            return False
        return True      # some other complaint; the instruction is modelled
    return True


def scan(path):
    """Mnemonic -> (SLOTHY class, count) for the instructions inside a loop."""
    found = {}
    counts = Counter()
    inside = False
    for raw in Path(path).read_text().splitlines():
        t = raw.split("//")[0].strip()
        if t.endswith("_loop:"):
            inside = True
            continue
        if not inside or not t or t.endswith(":") or t.startswith("."):
            continue
        if t.startswith("b.") or t == "ret":
            continue
        try:
            inst = Arch.Instruction.parser(SourceLine(t))[0]
        except Exception:
            counts[t.split()[0] + " (unparsed)"] += 1
            continue
        m = t.split()[0]
        found[m] = inst
        counts[m] += 1
    return found, counts


srcs = sorted((Path(__file__).resolve().parent.parent
               / "ntruplus1152_clean" / "src").glob("*.sym.S"))
allcls, allcnt = {}, Counter()
per = {}
for s in srcs:
    f, c = scan(s)
    per[s.name.replace(".sym.S", "")] = c
    allcls.update(f)
    allcnt.update(c)

print(f"{'instruction':<12} {'SLOTHY class':<22} " +
      " ".join(f"{m.split('_experimental')[0][:14]:>14}" for m in MODELS))
print("-" * (12 + 22 + 15 * len(MODELS)))
gaps = defaultdict(list)
for mn in sorted(allcls, key=lambda x: -allcnt[x]):
    inst = allcls[mn]
    row = []
    for m in MODELS:
        ok = resolves(inst, m)
        row.append(f"{'yes' if ok else 'NO':>14}")
        if not ok:
            gaps[m].append((mn, type(inst).__name__))
    print(f"{mn:<12} {type(inst).__name__:<22} " + " ".join(row))

print("\nper kernel, instruction counts inside the loop")
for k, c in per.items():
    print(f"  {k:<16} {sum(c.values()):3d} instructions   " +
          ", ".join(f"{m} x{n}" for m, n in c.most_common()))

print("\nwhat each model would need added")
for m in MODELS:
    if not gaps[m]:
        print(f"  {m}: nothing -- covers every instruction these kernels use")
        continue
    cls = sorted({c for _, c in gaps[m]})
    mn = sorted({x for x, _ in gaps[m]})
    print(f"  {m}:")
    print(f"      classes    {', '.join(cls)}")
    print(f"      mnemonics  {', '.join(mn)}")
