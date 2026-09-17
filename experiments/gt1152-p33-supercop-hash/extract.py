"""Selection cycles and stabilized per-operation quartiles from a SUPERCOP data file."""
import re, sys, json
from pathlib import Path

DELTA = re.compile(r"([+-])(\d+)")
METRICS = ("keypair_cycles", "enc_cycles", "dec_cycles")

def stq(values):
    """SUPERCOP's stq.h stabilized quartiles."""
    n = len(values); e = sorted(values * 8)
    return [sum(e[o*n:(o+2)*n]) / (2*n) for o in (1, 3, 5)]

def selection(lines):
    best = {}
    for l in lines:
        f = l.split()
        if len(f) > 13 and f[6] == "try" and f[8] == "ok":
            impl = f[12].rsplit("/", 1)[-1]
            opt = re.search(r"_(-O[0-9s]?)_", f[13])
            cyc = int(f[9])
            if impl not in best or cyc < best[impl][0]:
                best[impl] = (cyc, opt.group(1) if opt else "?")
    return best

def per_op(lines):
    out = {}
    for m in METRICS:
        runs = []
        for l in lines:
            k = f"constbranchindex {m} - "
            if k in l:
                base, deltas = l.split(k, 1)[1].split(" ", 1)
                runs.append([int(base) + (int(v) if s == "+" else -int(v))
                             for s, v in DELTA.findall(deltas)])
        if runs:
            allv = [v for r in runs for v in r]
            q = stq(allv)
            out[m] = {"runs": len(runs), "samples": len(allv),
                      "q1": q[0], "median": q[1], "q3": q[2],
                      "min": min(allv), "max": max(allv)}
    return out

def impl_of(lines):
    for l in lines:
        f = l.split()
        if len(f) > 7 and f[5].endswith("/constbranchindex") and f[6] == "implementation":
            return f[7]
    return None

lines = Path(sys.argv[1]).read_text().splitlines()
print(json.dumps({"selection_cycles": selection(lines),
                  "detailed_implementation": impl_of(lines),
                  "per_operation": per_op(lines)}, indent=2))
