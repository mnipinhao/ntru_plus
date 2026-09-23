#!/usr/bin/env python3
"""Exhaustive record for the 2-op canonicalisation of the Official freeze.

Official poly_ntt_pack (NTRU+864, pack.s:401-437) and poly_tobytes (NTRU+768 /
NTRU+1152, pack.s:20-62) freeze every int16 coefficient x with

    t = vpmulhrsw(x, V); t = vpmullw(t, Q); b = vpsubw(x, t)      # Barrett
    s = vpsraw(b, 15);   s = vpand(s, Q);   out = vpaddw(b, s)    # 3-op add-q

The candidate replaces the last three instructions by

    y = vpaddw(b, Q);    out = vpminuw(b, y)                      # 2-op

This is correct iff every Barrett output b lies in (-q, q): then for b >= 0,
unsigned b < b + q < 2q < 2^16, and for b < 0, unsigned b >= 2^16 - q + 1 >
b + q in (0, q).  The script

  1. reads q and the Barrett constant V from the pinned upstream params.h /
     consts.c (V = BARRETT_V(q) = (2^15 + q/2) / q) and checks, in each given
     pack.s, that the freeze is exactly the sequence above on the _16xv /
     _16xq registers (every occurrence);
  2. evaluates both sequences with bit-exact AVX2 word semantics for all
     65536 int16 inputs and asserts: Barrett output in (-q, q) (exact min/max
     recorded), 2-op == 3-op bit for bit, and output == x mod q in [0, q).

  prove_freeze_2op.py --experiment . [--pack-dir DIR ...] [--output FILE]

The C twin tests/test_freeze_2op.c executes the same 65536 inputs through the
real instructions (intrinsics) against the linked Official constants.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def w16(x):
    return ((x + 0x8000) & 0xFFFF) - 0x8000


def u16(x):
    return x & 0xFFFF


def vpmulhrsw(a, b):
    # Intel SDM: tmp = ((a * b) >> 14) + 1; dst = tmp[16:1]
    return w16((((a * b) >> 14) + 1) >> 1)


def vpmullw(a, b):
    return w16(a * b)


def vpsubw(a, b):
    return w16(a - b)


def vpaddw(a, b):
    return w16(a + b)


def vpsraw15(a):
    return -1 if a < 0 else 0


def vpand(a, b):
    return w16(u16(a) & u16(b))


def vpminuw(a, b):
    return a if u16(a) <= u16(b) else b


def constants(src):
    params = (src / "params.h").read_text()
    consts = (src / "consts.c").read_text()
    q = int(re.search(r"#define\s+NTRUPLUS_Q\s+(\d+)", params)[1])
    if not re.search(r"#define\s+BARRETT_V\(q\)\s+\(\(\(1U << 15\) \+ \(q\)/2\)/\(q\)\)", consts) or \
       not re.search(r"#define\s+V\s+BARRETT_V\(NTRUPLUS_Q\)", consts) or \
       not re.search(r"_16xv\[16\].*FILL_16\(V\)", consts) or \
       not re.search(r"_16xq\[16\].*FILL_16\(NTRUPLUS_Q\)", consts):
        raise ValueError(f"{src}: unexpected Barrett constant definitions")
    return q, ((1 << 15) + q // 2) // q


def freeze_sites(pack_s):
    """Every Barrett + conditional-add in pack.s, checked instruction by
    instruction on the registers that hold _16xv / _16xq."""
    lines = [l.split("#")[0].strip() for l in pack_s.read_text().splitlines()]
    ins = []
    for n, l in enumerate(lines, 1):
        m = re.match(r"^([a-z0-9]+)\s+(.*)$", l)
        if m:
            ins.append((n, m[1], [o.strip() for o in m[2].split(",")]))
    creg = {}
    for n, op, ops in ins:
        if op == "vmovdqa" and ops[0] in ("_16xv(%rip)", "_16xq(%rip)"):
            creg[ops[0][:5]] = ops[1]
    v, q = creg.get("_16xv"), creg.get("_16xq")
    if v is None or q is None:
        raise ValueError(f"{pack_s}: _16xv/_16xq not loaded")
    sites = {"barrett": [], "cond_add": []}
    for i, (n, op, ops) in enumerate(ins):
        if op == "vpmulhrsw":
            if ops[0] != v:
                raise ValueError(f"{pack_s}:{n}: vpmulhrsw not by _16xv")
            x, t = ops[1], ops[2]
            # the matching vpmullw t,Q and vpsubw t,x,x follow in the same group
            mull = [j for j in ins[i + 1:] if j[1] == "vpmullw" and j[2] == [q, t, t]]
            sub = [j for j in ins[i + 1:] if j[1] == "vpsubw" and j[2] == [t, x, x]]
            if not mull or not sub or not mull[0][0] < sub[0][0]:
                raise ValueError(f"{pack_s}:{n}: Barrett sequence not recognised")
            sites["barrett"].append([n, mull[0][0], sub[0][0]])
        if op == "vpsraw":
            if ops[0] != "$15":
                raise ValueError(f"{pack_s}:{n}: vpsraw by {ops[0]}")
            x, s = ops[1], ops[2]
            andq = [j for j in ins[i + 1:] if j[1] == "vpand" and j[2] == [q, s, s]]
            add = [j for j in ins[i + 1:] if j[1] == "vpaddw" and j[2] == [s, x, x]]
            if not andq or not add or not andq[0][0] < add[0][0]:
                raise ValueError(f"{pack_s}:{n}: conditional add of q not recognised")
            sites["cond_add"].append([n, andq[0][0], add[0][0]])
    if not sites["barrett"] or len(sites["barrett"]) != len(sites["cond_add"]):
        raise ValueError(f"{pack_s}: {len(sites['barrett'])} Barrett vs {len(sites['cond_add'])} add-q sites")
    return sites


def prove(q, v):
    lo, hi, mism, wrong = 32767, -32768, [], []
    for x in range(-32768, 32768):
        t = vpmullw(vpmulhrsw(x, v), q)
        b = vpsubw(x, t)
        if (x - t) != b:
            raise AssertionError(f"Barrett subtraction wraps at x={x}")
        lo, hi = min(lo, b), max(hi, b)
        three = vpaddw(b, vpand(vpsraw15(b), q))
        two = vpminuw(b, vpaddw(b, q))
        if u16(three) != u16(two):
            mism.append(x)
        if two != x % q:
            wrong.append(x)
    ok = -q < lo and hi < q and not mism and not wrong
    return {"inputs": 65536, "barrett_min": lo, "barrett_max": hi,
            "barrett_in_open_interval_minus_q_q": -q < lo and hi < q,
            "two_op_equals_three_op_bitwise": not mism, "mismatches": len(mism),
            "output_equals_x_mod_q": not wrong, "wrong_residues": len(wrong), "pass": ok}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--pack-dir", type=Path, action="append", default=[],
                    help="extra read-only Official avx2 source dirs (params.h, consts.c, pack.s)")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    root = args.experiment.resolve()
    dirs = [root / "upstream/supercop-avx2"] + [d.resolve() for d in args.pack_dir]
    record = {"class": "exhaustive proof record (int16 domain, bit-exact AVX2 word semantics)",
              "claim": "Barrett output b in (-q,q) for every int16 input; vpminuw(b, b+q) == "
                       "b + (vpsraw(b,15) & q) bit for bit; both == x mod q",
              "sources": {}}
    for d in dirs:
        q, v = constants(d)
        sites = freeze_sites(d / "pack.s")
        res = prove(q, v)
        name = d.parent.name if d.name == "avx2" else d.name
        record["sources"][str(d)] = {
            "label": name, "q": q, "V": v,
            "pack_s_sha256": hashlib.sha256((d / "pack.s").read_bytes()).hexdigest(),
            "freeze_sites_pack_s_lines": sites, "result": res}
        print(f"{name}: q={q} V={v} sites={len(sites['barrett'])} barrett in [{res['barrett_min']}, "
              f"{res['barrett_max']}] 2op==3op={res['two_op_equals_three_op_bitwise']} "
              f"residue={res['output_equals_x_mod_q']} -> {'PASS' if res['pass'] else 'FAIL'}")
    ok = all(s["result"]["pass"] for s in record["sources"].values())
    record["pass"] = ok
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
