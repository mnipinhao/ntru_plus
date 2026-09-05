#!/usr/bin/env python3
"""Generate exact P3B1 map and byte-index tables from the M5O oracle."""
from __future__ import annotations
import importlib.util
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
P3A = HERE.parent / "gt_fr0_d1_byte_abi_architecture/analyze_architecture.py"
spec = importlib.util.spec_from_file_location("p3a", P3A)
assert spec and spec.loader
p3a = importlib.util.module_from_spec(spec); spec.loader.exec_module(p3a)
M, PROOF = p3a.official_map(ROOT)
P = [0, 3, 6, 1, 4, 7, 2, 5, 8]

def bytes_for_lanes(lanes):
    return [2*x+b for x in lanes for b in (0, 1)]

def emit_array(name, values, ctype, dims):
    def rec(v, depth=0):
        if depth == len(dims)-1:
            return "{" + ", ".join(str(x) for x in v) + "}"
        return "{\n" + ",\n".join("  "*(depth+1)+rec(x,depth+1) for x in v) + "\n" + "  "*depth + "}"
    shape="".join(f"[{d}]" for d in dims)
    return f"static const {ctype} {name}{shape} __attribute__((aligned(16))) = " + rec(values) + ";\n"

leaf=[M[24*(j//8)+(j%8)] for j in range(144)]

# R9-B exact forward/reverse lookup byte indices for the even top-0 route.
fwd=[]
for j in range(9):
    banks=[[255]*16 for _ in range(3)]
    for ol in range(8):
        x=M[24*(2*j)+ol]; s=x//24; sl=x%8; bank=s//4; local=s%4
        for b in (0,1): banks[bank][2*ol+b]=16*local+2*sl+b
    fwd.append(banks)
rev=[]
for s in range(9):
    banks=[[255]*16 for _ in range(3)]
    for sl in range(8):
        hit=[]
        for j in range(9):
            for ol in range(8):
                x=M[24*(2*j)+ol]
                if x//24==s and x%8==sl: hit.append((j,ol))
        assert len(hit)==1
        j,ol=hit[0]; bank=j//4; local=j%4
        for b in (0,1): banks[bank][2*sl+b]=16*local+2*ol+b
    rev.append(banks)

# R9-A: W_k lanes use J0..J7 positions, with J8 inserted at position k.
a_fwd=[]; a_rev=[]
for k,j in enumerate(P):
    group=2*j
    source_by_ol=[M[24*group+ol]//24 for ol in range(8)]
    w_source=[0 if pos==k else 8-pos for pos in range(8)]
    a_fwd.append(bytes_for_lanes([w_source.index(s) for s in source_by_ol]))
    a_rev.append(bytes_for_lanes([source_by_ol.index(s) for s in w_source]))
for k in range(9):
    assert all(a_rev[k][a_fwd[k][i]]==i for i in range(16))

prefix=[]
for count in range(1,8): prefix.append([65535 if lane<count else 0 for lane in range(8)])

out=["/* generated; map_sha256=%s */"%PROOF["mapping_sha256"],"#ifndef P3B1_TABLES_H","#define P3B1_TABLES_H","#include <stdint.h>"]
out.append("static const uint16_t p3b1_map[864] __attribute__((aligned(16))) = {\n    " + ", ".join(map(str,M)) + "\n};\n")
out.append("static const uint16_t p3b1_leaf[144] __attribute__((aligned(16))) = {\n    " + ", ".join(map(str,leaf)) + "\n};\n")
out.append(emit_array("p3b1_b_fwd", fwd, "uint8_t", [9,3,16]))
out.append(emit_array("p3b1_b_rev", rev, "uint8_t", [9,3,16]))
out.append(emit_array("p3b1_a_fwd", a_fwd, "uint8_t", [9,16]))
out.append(emit_array("p3b1_a_rev", a_rev, "uint8_t", [9,16]))
out.append(emit_array("p3b1_prefix", prefix, "uint16_t", [7,8]))
out.extend(["#endif",""])
Path("build/p3b1_tables.h").write_text("\n".join(out))
print(PROOF["mapping_sha256"])
