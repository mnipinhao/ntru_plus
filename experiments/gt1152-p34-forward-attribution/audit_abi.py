#!/usr/bin/env python3
"""Static audit: no assembly symbol C can call may clobber d8-d15 or x19-x28.

P34's harness hit this: calling ntt9_asm directly from C is an AAPCS64
violation, because ntt9_asm leaves d8-d15 destroyed and relies on its ntt.S
wrapper to save them.  GCC had spilled a live double into the callee-saved half
of the vector file, and three measurements came back as ~6e252 rather than a
time.  This checks the shipped package for the same shape.

Usage:  python3 audit_abi.py [package-dir]

Method, and its limits.  For each .S file the tool expands `.macro` bodies (so
a save hidden inside SAVE_PUBLIC is seen), splits the file into the regions each
exported label owns, and records for each region whether it writes v8-v15 or
x19-x28, whether it saves and restores them, and which symbols it `bl`s.  It
then propagates "clobbers" along the call graph -- a symbol that saves and
restores is a barrier -- and reports any symbol reachable from C that still
clobbers.  Comments are stripped from the C sources first, because a symbol
named only in a comment is not a call.

This is a complement to test/test_abi.c, not a replacement: the sentinel there
proves the property at run time for the entry points it wraps, while this proves
it for every exported symbol and says which ones C is allowed to reach.
"""
import re
import sys
import pathlib

CALLEE_V = {f"v{i}" for i in range(8, 16)}
CALLEE_X = {f"x{i}" for i in range(19, 29)}

SAVE_V = re.compile(r'^\s*(stp|str)\s+d(?:8|9|1[0-5])\b')
REST_V = re.compile(r'^\s*(ldp|ldr)\s+d(?:8|9|1[0-5])\b')
SAVE_X = re.compile(r'^\s*(stp|str)\s+x(?:19|2[0-8])\b')
REST_X = re.compile(r'^\s*(ldp|ldr)\s+x(?:19|2[0-8])\b')
BL = re.compile(r'^\s*bl\s+(?:C\()?([A-Za-z_][A-Za-z0-9_]*)\)?')
GLOBAL = re.compile(r'^\s*\.global\s+(?:C\()?([A-Za-z_][A-Za-z0-9_]*)\)?')
LABEL = re.compile(r'^(?:C\()?([A-Za-z_][A-Za-z0-9_]*)\)?:\s*$')

# Instructions whose first vector operand is a destination.  Loads write their
# whole register list; stores read it.
LOADLIST = re.compile(r'^\s*(ld[1-4]|ldp|ldr)\b')
STORELIST = re.compile(r'^\s*(st[1-4]|stp|str)\b')


def expand_macros(lines):
    """Inline .macro bodies at their use sites (no-argument macros only)."""
    macros, out, name = {}, [], None
    for ln in lines:
        m = re.match(r'^\s*\.macro\s+(\S+)\s*$', ln)
        if m:
            name = m.group(1); macros[name] = []; continue
        if re.match(r'^\s*\.endm\b', ln):
            name = None; continue
        if name:
            macros[name].append(ln)
        else:
            out.append(ln)
    changed = True
    while changed:
        changed, new = False, []
        for ln in out:
            key = ln.strip().split()[0] if ln.strip() else ""
            if key in macros:
                new.extend(macros[key]); changed = True
            else:
                new.append(ln)
        out = new
    return out


def touches(body, regs):
    """Does this region write any of `regs` as a destination?"""
    for ln in body:
        s = ln.strip()
        if not s or s.startswith(('.', '/', '*', '#')):
            continue
        if STORELIST.match(ln):
            continue                      # stores read their operands
        if LOADLIST.match(ln):            # loads write their whole list
            if {f"v{n}" for n in re.findall(r'v(\d+)\s*\.', ln)} & regs:
                return True
            if {f"x{n}" for n in re.findall(r'\bx(\d+)\b', ln.split(',[')[0])} & regs:
                return True
            continue
        m = re.match(r'^[a-z][a-z0-9._]*\s+\{?\s*([vx])(\d+)', s)
        if m and f"{m.group(1)}{m.group(2)}" in regs:
            return True
    return False


def strip_c_comments(t):
    return re.sub(r'//[^\n]*', ' ', re.sub(r'/\*.*?\*/', ' ', t, flags=re.S))


def main(pkg):
    pkg = pathlib.Path(pkg)
    c_text = "\n".join(strip_c_comments(p.read_text())
                       for p in sorted(pkg.glob("*.c")) + sorted(pkg.glob("*.h")))
    c_names = set(re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(', c_text))

    info = {}
    for f in sorted(pkg.glob("*.S")):
        lines = expand_macros(f.read_text().split("\n"))
        exported = {m.group(1) for ln in lines if (m := GLOBAL.match(ln))
                    and not m.group(1).startswith("_")}
        pos = {}
        for i, ln in enumerate(lines):
            m = LABEL.match(ln)
            if m and m.group(1) in exported:
                pos.setdefault(m.group(1), i)
        order = sorted(pos.items(), key=lambda kv: kv[1])
        for k, (name, start) in enumerate(order):
            end = order[k + 1][1] if k + 1 < len(order) else len(lines)
            body = lines[start:end]
            info[name] = {
                "file": f.name,
                "writes": (touches(body, CALLEE_V), touches(body, CALLEE_X)),
                "saves": (any(SAVE_V.match(b) for b in body) and any(REST_V.match(b) for b in body),
                          any(SAVE_X.match(b) for b in body) and any(REST_X.match(b) for b in body)),
                "calls": {m.group(1) for b in body if (m := BL.match(b))},
            }

    def clobbers(name, idx, seen=None):
        """Transitively: does `name` return with callee-saved state destroyed?"""
        seen = seen or set()
        if name in seen or name not in info:
            return False
        seen.add(name)
        d = info[name]
        if d["saves"][idx]:
            return False                              # saves/restores: a barrier
        return d["writes"][idx] or any(clobbers(c, idx, seen) for c in d["calls"])

    print(f"{'file':22} {'symbol':30} {'clobbers':>9} {'C reaches':>10}  verdict")
    violations = []
    for name in sorted(info, key=lambda n: (info[n]["file"], n)):
        d = info[name]
        bad = [lbl for lbl, i in (("d8-d15", 0), ("x19-x28", 1)) if clobbers(name, i)]
        reached = name in c_names
        if reached and bad:
            verdict = f"*** AAPCS VIOLATION: {', '.join(bad)} ***"
            violations.append((name, bad))
        elif reached:
            verdict = "ok"
        elif bad:
            verdict = f"internal only; caller must save {', '.join(bad)}"
        else:
            verdict = "internal"
        print(f"{d['file']:22} {name:30} {','.join(bad) or '-':>9} {str(reached):>10}  {verdict}")

    print(f"\nviolations: {len(violations)}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
