"""Check the flattened call-site constants by symbolically executing the old nest.

generate_driver_flat.py computes each site's offsets from index algebra I read
off the assembly by hand.  That is exactly the step worth not trusting, so this
parses the shipped nest's instructions and evaluates them, for every value of
the loop counters, with no formula of mine involved.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from generate_driver_flat import NEST_I9, NEST_MAIN   # noqa: E402

BASES = {"x25": ("scratch", 0), "x20": ("in", 0), "x21": ("t9", 0),
         "x19": ("out", 0), "x22": ("t16", 0), "x23": ("t16main", 0)}


def run_nest(nest, counters, pointers):
    """Execute one iteration's instructions with the given counter values.

    Registers hold (base_name, offset) pairs; a bare integer is (None, n).
    Only the forms the nest actually uses are implemented, and anything else
    raises -- a silent skip would be the whole bug this script exists to rule
    out.
    """
    reg = dict(BASES)
    reg.update({k: (None, v) for k, v in counters.items()})
    for line in nest.splitlines():
        # The counters are inputs here.  The nest initializes and increments
        # them itself (`mov x26, #0`, `add x28, x28, #1`); those writes are the
        # loop, not the address arithmetic, so they are held out.
        if re.match(r'\s*(mov|add) (x2[678]),', line):
            continue
        s = re.sub(r"//.*$", "", line).strip()   # trailing comments
        if not s or s.startswith("//") or s.startswith(".") or s.endswith(":"):
            continue
        if s.startswith("bl ") or s.startswith("cmp ") or s.startswith("b.ne"):
            continue
        m = re.fullmatch(r'mov (x\d+), #(\d+)', s)
        if m:
            reg[m.group(1)] = (None, int(m.group(2))); continue
        m = re.fullmatch(r'mov (x\d+), (x\d+)', s)
        if m:
            reg[m.group(1)] = reg[m.group(2)]; continue
        m = re.fullmatch(r'add (x\d+), (x\d+), #(\d+)', s)
        if m:
            b, o = reg[m.group(2)]
            reg[m.group(1)] = (b, o + int(m.group(3))); continue
        m = re.fullmatch(r'add (x\d+), (x\d+), (x\d+), lsl #(\d+)', s)
        if m:
            b, o = reg[m.group(2)]
            cb, co = reg[m.group(3)]
            assert cb is None, f"shifted operand {m.group(3)} is not a plain integer"
            reg[m.group(1)] = (b, o + (co << int(m.group(4)))); continue
        m = re.fullmatch(r'madd (x\d+), (x\d+), (x\d+), (x\d+)', s)
        if m:
            ab, ao = reg[m.group(2)]
            bb, bo = reg[m.group(3)]
            addb, addo = reg[m.group(4)]
            assert ab is None and bb is None, "madd multiplicands must be integers"
            reg[m.group(1)] = (addb, addo + ao * bo); continue
        raise SystemExit(f"unhandled instruction in nest: {s!r}")
    return {p: reg[p] for p in pointers}


def main():
    sites = json.loads((HERE / "call-sites.json").read_text())
    bad = 0

    got = []
    for top in range(2):
        for comp in range(4):
            for blk in range(2):
                got.append(run_nest(NEST_I9, {"x26": top, "x27": comp, "x28": blk},
                                    ("x0", "x1", "x2", "x3")))
    want_base = {"x0": "scratch", "x1": "scratch", "x2": "in", "x3": "t9"}
    for s, g in zip(sites["packed_i9"], got):
        for p, base in want_base.items():
            b, o = g[p]
            if (b, o) != (base, s[p]):
                print(f"packed_i9 top={s['top']} comp={s['comp']} blk={s['blk']} "
                      f"{p}: nest says {b}+{o}, generator says {base}+{s[p]}")
                bad += 1

    got = []
    for comp in range(4):
        for half in range(2):
            got.append(run_nest(NEST_MAIN, {"x26": comp, "x27": half},
                                ("x0", "x1", "x2", "x3", "x4")))
    for s, g in zip(sites["invntt16_asm"], got):
        for p, base in (("x0", "out"), ("x1", "scratch")):
            b, o = g[p]
            if (b, o) != (base, s[p]):
                print(f"invntt16 comp={s['comp']} half={s['half']} "
                      f"{p}: nest says {b}+{o}, generator says {base}+{s[p]}")
                bad += 1
        if g["x2"] != (None, 0) or g["x3"] != ("t16", 0) or g["x4"] != ("t16main", 0):
            print(f"invntt16 comp={s['comp']} half={s['half']}: "
                  f"x2/x3/x4 are {g['x2']}/{g['x3']}/{g['x4']}")
            bad += 1

    n = len(sites["packed_i9"]) * 4 + len(sites["invntt16_asm"]) * 2
    print(f"{n - bad}/{n} pointer constants agree with symbolic execution of the nest")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
