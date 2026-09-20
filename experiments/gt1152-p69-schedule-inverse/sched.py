#!/usr/bin/env python3
"""P69: re-schedule the lane-basis inverse kernels for Cortex-A76.

Neither kernel has ever been scheduled for 1152.  inverse9.S carries NTRU+864's
A76 schedule with 35 instructions deleted out of it (P68) and inverse16.S the
same with 224 deleted (P67), so both are schedules for code that no longer
exists.  P36 measured the gap before the deletions: packed_i9 at 90.5% of its
mix floor, invntt16_asm at 94.6%.

Register policy: reserve every GPR the region does not already use, so the
solver cannot introduce a callee-saved register the public wrapper does not
save.  All vector registers are available -- the wrapper saves d8-d15 and
wipes v0-v31 on exit.
"""
import logging, re, sys, time, json
from pathlib import Path
SLOTHY = '/private/tmp/claude-501/-Users-chenpinhao-ntruplus/a827c50f-9c4e-40e1-b926-99dea89f0d8e/scratchpad/slothy-patched'
sys.path.insert(0, SLOTHY)
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
PKG  = HERE / ".." / "gt1152-p10-kem"

KERNELS = {
    "inverse9":  ("packed_i9",      {"x0","x2","x3","x5","x6","x8","x10","x11","x15","x17"}),
    "inverse16": ("invntt16_asm",   {"x0","x1","x3","x4","x7","x15"}),
}

def used_count(path, start, end):
    txt = Path(path).read_text()
    body = txt.split(start+":",1)[1].split(end+":",1)[0]
    return len([l for l in body.splitlines() if re.match(r'\s+[a-z]', re.sub(r'//.*','',l))])

def run(name, tag, cfgfn, timeout):
    sym, used = KERNELS[name]
    src = PKG / f"{name}.S"
    n = used_count(src, f"{sym}_slothy_start", f"{sym}_slothy_end")
    reserved = [f"x{i}" for i in range(31) if f"x{i}" not in used] + ["sp", "xzr"]
    lg = logging.getLogger(f"{name}-{tag}"); lg.handlers.clear()
    lg.setLevel(logging.DEBUG); lg.propagate = False
    lg.addHandler(logging.FileHandler(HERE / f"log-{name}-{tag}.log", mode="w"))
    s = Slothy(Arch, Target, logger=lg)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.variable_size = True          # P59: False forces an external binary search
    s.config.constraints.allow_spills = False
    s.config.constraints.allow_renaming = True
    s.config.constraints.allow_reordering = True
    s.config.constraints.functional_only = False
    s.config.reserved_regs = reserved
    s.config.timeout = timeout
    cfgfn(s.config)
    s.load_source_from_file(str(src))
    t0 = time.time()
    try:
        s.optimize(start=f"{sym}_slothy_start", end=f"{sym}_slothy_end")
        ok, err = True, ""
    except Exception as e:
        ok, err = False, f"{type(e).__name__}: {e}"
    dt = time.time() - t0
    out = HERE / f"{name}.{tag}.S"
    cyc = None
    if ok:
        s.write_source_to_file(str(out))
        m = re.findall(r'cycles?\s*[:=]\s*(\d+)', out.read_text())
        cyc = int(m[-1]) if m else None
    print(f"  {name:<10} {tag:<22} {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
          f"in={n:<4} {'cyc='+str(cyc) if cyc else err[:60]}", flush=True)
    return {"kernel": name, "tag": tag, "sec": dt, "ok": ok, "in": n,
            "cycles": cyc, "err": err}

if __name__ == "__main__":
    which = sys.argv[1]
    results = []
    if which == "inverse9":
        for tag, fn, to in [
            ("plain",        lambda c: None, 300),
            ("split4-zip",   lambda c: (setattr(c,'split_heuristic',True),
                                        setattr(c,'split_heuristic_factor',4),
                                        setattr(c,'split_heuristic_preprocess_naive_interleaving',True)), 120),
            ("split8-zip",   lambda c: (setattr(c,'split_heuristic',True),
                                        setattr(c,'split_heuristic_factor',8),
                                        setattr(c,'split_heuristic_preprocess_naive_interleaving',True)), 120),
        ]:
            results.append(run("inverse9", tag, fn, to))
    else:
        for tag, fn, to in [
            ("split8-zip",   lambda c: (setattr(c,'split_heuristic',True),
                                        setattr(c,'split_heuristic_factor',8),
                                        setattr(c,'split_heuristic_preprocess_naive_interleaving',True)), 120),
            ("split16-zip",  lambda c: (setattr(c,'split_heuristic',True),
                                        setattr(c,'split_heuristic_factor',16),
                                        setattr(c,'split_heuristic_preprocess_naive_interleaving',True)), 120),
        ]:
            results.append(run("inverse16", tag, fn, to))
    (HERE / f"sched-{which}.json").write_text(json.dumps(results, indent=2))
