#!/usr/bin/env python3
"""Linked-ELF audit of the 2-op-freeze poly_tobytes (NTRU+768 / NTRU+1152).

In the linked candidate KEM test ELF (build/test_kem_lazy_freeze2op):
  * candidate symbol ntruplus{N}_officialopt_tobytes_freeze2op: unique, sized,
    32-byte aligned; exactly one ret, at the end; no stack (%rsp/%rbp,
    push/pop/leave), no call, no vzeroupper;
  * Official poly_tobytes linked in the same ELF (coexistence);
  * candidate == Official row for row (opcode, operands, rip symbol, branch
    target row; alignment nops ignored) except for the freeze rows: per
    function body exactly 8 vpsraw + 8 vpand + 8 vpaddw removed and 8 vpaddw
    + 8 vpminuw added, the added vpaddw reading the _16xq register;
  * KEM objects (relocations, calls and tail jumps): candidate KEM
    build/kem_lazy_freeze2op.o has 7 references to the candidate, 0 to
    poly_tobytes, 6 to the lazy Forward and 0 to poly_ntt; freeze-only
    control build/kem_freeze2op.o has 7 / 0 and 6 to poly_ntt; the lazy-only
    KEM build/kem_lazy.o is unchanged (7 to poly_tobytes, 0 to the candidate).
"""

import argparse
import difflib
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

PAD = ("nop", "nopw", "nopl", "data16", "cs", "xchg")
ITERATIONS = {768: 6, 1152: 9}


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows_of(elf):
    text = run("objdump", "-d", "--no-show-raw-insn", "-M", "att", str(elf))
    return [(int(m[1], 16), m[2], m[3].strip()) for m in
            re.finditer(r"^[ \t]*([0-9a-f]+):[ \t]+([a-z][a-z0-9]*)[ \t]*(.*?)$", text, re.M)]


def function(rows, start, size):
    return [r for r in rows if start <= r[0] < start + size]


def normalise(rows):
    body = [r for r in rows if r[1] not in PAD]
    index = {a: i for i, (a, _, _) in enumerate(body)}
    out = []
    for a, op, operands in body:
        if op.startswith("j"):
            t = int(operands.split()[0], 16)
            if t not in index:
                raise ValueError(f"branch at {a:#x} leaves the function")
            out.append(f"{op} ->row{index[t]}")
        else:
            sym = re.search(r"<([A-Za-z0-9_]+)(?:\+0x[0-9a-f]+)?>", operands)
            text = re.sub(r"\s*#.*$", "", operands)
            text = re.sub(r"-?0x[0-9a-f]+\(%rip\)", "(%rip)", text)
            out.append(f"{op} {text}" + (f" <{sym[1]}>" if sym and "(%rip)" in operands else ""))
    return out


def refs(obj, symbol):
    text = run("objdump", "-dr", str(obj))
    return len(re.findall(r"R_X86_64_(?:PLT32|PC32)\s+" + re.escape(symbol) + r"(?:-0x4)?\s*$", text, re.M))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=sorted(ITERATIONS), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    n = args.param
    root = args.experiment.resolve()
    name = f"ntruplus{n}_officialopt_tobytes_freeze2op"
    lazy = f"ntruplus{n}_officialopt_ntt_caller_lazy"

    nm = run("nm", "-S", str(args.elf))

    def sized(sym):
        m = re.findall(r"^([0-9a-f]+)\s+([0-9a-f]+)\s+\w\s+" + re.escape(sym) + r"$", nm, re.M)
        return [tuple(int(x, 16) for x in t) for t in m]
    cand = sized(name)
    if len(cand) != 1:
        raise ValueError("missing or ambiguous sized candidate symbol")
    start, size = cand[0]
    if start % 32 or not size:
        raise ValueError("candidate not 32-byte aligned or unsized")
    off = re.findall(r"^([0-9a-f]+)\s+(?:[0-9a-f]+\s+)?\w\s+poly_tobytes$", nm, re.M)
    fro = re.findall(r"^([0-9a-f]+)\s+(?:[0-9a-f]+\s+)?\w\s+poly_frombytes$", nm, re.M)
    if len(off) != 1 or len(fro) != 1:
        raise ValueError("Official poly_tobytes / poly_frombytes not uniquely linked")
    ostart = int(off[0], 16)
    rows = rows_of(args.elf)
    c = function(rows, start, size)
    o = function(rows, ostart, int(fro[0], 16) - ostart)   # Official has no .size; ends at poly_frombytes
    if not c or c[0][0] != start or not o or o[0][0] != ostart:
        raise ValueError("incomplete disassembly")
    bad = [r for r in c if "%rsp" in r[2] or "%rbp" in r[2] or r[1].startswith("call")
           or r[1] in ("push", "pop", "leave", "vzeroupper", "vzeroall")]
    if bad:
        raise ValueError(f"stack/call/vzeroupper rows: {bad[:4]}")
    creal = [r for r in c if r[1] not in PAD]
    if Counter(r[1] for r in creal)["ret"] != 1 or creal[-1][1] != "ret":
        raise ValueError("unexpected return structure")
    q_reg = next(r[2].split("#")[0].split(",")[-1].strip() for r in c
                 if r[1] == "vmovdqa" and "<_16xq>" in r[2])
    cn, on = normalise(c), normalise(o)
    removed, added = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=on, b=cn, autojunk=False).get_opcodes():
        if tag != "equal":
            removed += on[i1:i2]
            added += cn[j1:j2]
    rc, ac = Counter(l.split()[0] for l in removed), Counter(l.split()[0] for l in added)
    if rc != Counter({"vpsraw": 8, "vpand": 8, "vpaddw": 8}) or ac != Counter({"vpaddw": 8, "vpminuw": 8}):
        raise ValueError(f"row diff is not the freeze replacement: -{dict(rc)} +{dict(ac)}")
    if not all(l.startswith(f"vpaddw {q_reg},") for l in added if l.startswith("vpaddw")):
        raise ValueError("added vpaddw not by the _16xq register")
    if not all(l.startswith("vpsraw $0xf,") for l in removed if l.startswith("vpsraw")):
        raise ValueError("removed vpsraw is not by 15")
    delta = Counter(r[1] for r in o if r[1] not in PAD)
    delta.subtract(Counter(r[1] for r in creal))
    delta = {k: v for k, v in sorted(delta.items()) if v}
    if delta != {"vpand": 8, "vpminuw": -8, "vpsraw": 8}:
        raise ValueError(f"unexpected static opcode delta {delta}")

    b = root / "build"
    graph = {
        "kem_lazy_freeze2op.o->candidate": refs(b / "kem_lazy_freeze2op.o", name),
        "kem_lazy_freeze2op.o->poly_tobytes": refs(b / "kem_lazy_freeze2op.o", "poly_tobytes"),
        "kem_lazy_freeze2op.o->lazy_forward": refs(b / "kem_lazy_freeze2op.o", lazy),
        "kem_lazy_freeze2op.o->poly_ntt": refs(b / "kem_lazy_freeze2op.o", "poly_ntt"),
        "kem_freeze2op.o->candidate": refs(b / "kem_freeze2op.o", name),
        "kem_freeze2op.o->poly_tobytes": refs(b / "kem_freeze2op.o", "poly_tobytes"),
        "kem_freeze2op.o->poly_ntt": refs(b / "kem_freeze2op.o", "poly_ntt"),
        "kem_lazy.o->poly_tobytes": refs(b / "kem_lazy.o", "poly_tobytes"),
        "kem_lazy.o->candidate": refs(b / "kem_lazy.o", name),
    }
    want = {"kem_lazy_freeze2op.o->candidate": 7, "kem_lazy_freeze2op.o->poly_tobytes": 0,
            "kem_lazy_freeze2op.o->lazy_forward": 6, "kem_lazy_freeze2op.o->poly_ntt": 0,
            "kem_freeze2op.o->candidate": 7, "kem_freeze2op.o->poly_tobytes": 0,
            "kem_freeze2op.o->poly_ntt": 6, "kem_lazy.o->poly_tobytes": 7, "kem_lazy.o->candidate": 0}
    if graph != want:
        raise ValueError(f"unexpected KEM call graph {graph}")
    it = ITERATIONS[n]
    out = {
        "class": "linked ELF audit (Phase A, correctness only; no timing)",
        "parameter": f"NTRU+{n}", "elf": str(args.elf), "elf_sha256": sha(args.elf),
        "asm_sha256": sha(root / f"asm/{name}.s"),
        "compiler": run("cc", "--version").splitlines()[0],
        "symbol": name, "address_mod_32": start % 32, "aligned_32": True, "size_bytes": size,
        "instruction_rows": len(creal), "official_poly_tobytes_rows": len([r for r in o if r[1] not in PAD]),
        "opcode_counts": dict(sorted(Counter(r[1] for r in creal).items())),
        "static_delta_official_minus_candidate": delta,
        "row_diff": {"removed": dict(rc), "added": dict(ac)},
        "dynamic_delta_per_call": {"vpsraw": -8 * it, "vpand": -8 * it, "vpminuw": 8 * it,
                                   "net_instructions": -8 * it},
        "rows_identical_to_official_except_freeze": True,
        "stack_references": 0, "calls": 0, "vzeroupper": 0,
        "kem_call_relocations": graph,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("parameter", "size_bytes", "instruction_rows",
                                          "official_poly_tobytes_rows",
                                          "static_delta_official_minus_candidate",
                                          "kem_call_relocations")}, indent=1))


if __name__ == "__main__":
    main()
