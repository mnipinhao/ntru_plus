#!/usr/bin/env python3
"""Linked-ELF audit of the caller-lazy Forward (NTRU+768/864/1152), not its source.

Port of NTRU+768 avx2_official_opt_001/tools/audit_forward_caller_lazy.py,
extended to diff the linked candidate against the linked Official poly_ntt of
the same ELF instruction by instruction:
  * candidate symbol: unique, sized, 32-byte aligned; one ret; no stack
    (%rsp/%rbp/push/pop/leave), call or vzeroupper; no vpmulhrsw, no _16xv;
  * Official poly_ntt present in the same ELF (coexistence);
  * candidate == Official with exactly the terminal Barrett rows (regs x
    vpmulhrsw/vpmullw/vpsubw, contiguous) and the _16xv load removed; every
    other row (opcode, operands, rip symbol, branch target row) identical,
    ignoring only alignment-padding nops;
  * KEM objects: diagnostic lazy KEM has 6 call relocations to the candidate
    and none to poly_ntt; the reference KEM has 6 to poly_ntt.
"""

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

REGS = {768: 8, 864: 6, 1152: 8}
ITERATIONS = {768: 6, 864: 9, 1152: 9}
PAD = ("nop", "nopw", "nopl", "data16", "cs", "xchg")


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def disasm_rows(elf):
    rows = []
    text = run("objdump", "-d", "--no-show-raw-insn", "-M", "att", str(elf))
    for m in re.finditer(r"^[ \t]*([0-9a-f]+):[ \t]+([a-z][a-z0-9]*)[ \t]*(.*?)$", text, re.M):
        rows.append((int(m[1], 16), m[2], m[3].strip()))
    return rows


def function_rows(rows, start, end=None):
    out = []
    for addr, op, operands in rows:
        if addr < start:
            continue
        if end is not None and addr >= end:
            break
        out.append((addr, op, operands))
        if end is None and op == "ret":
            break
    return out


def normalise(rows):
    """Drop padding; express rip operands by symbol and branches by row index."""
    body = [r for r in rows if r[1] not in PAD]
    index = {addr: i for i, (addr, _, _) in enumerate(body)}
    norm = []
    for addr, op, operands in body:
        if op.startswith("j"):
            target = int(operands.split()[0], 16)
            if target not in index:
                raise ValueError(f"branch at {addr:#x} leaves the function or hits padding")
            norm.append((op, ("row", index[target])))
        else:
            sym = re.search(r"<([A-Za-z0-9_]+)(?:\+0x[0-9a-f]+)?>", operands)
            text = re.sub(r"\s*#.*$", "", operands)
            text = re.sub(r"-?0x[0-9a-f]+\(%rip\)", "(%rip)", text)
            norm.append((op, (text, sym[1] if sym and "(%rip)" in operands else None)))
    return norm


def relocs_to(obj, symbol):
    text = run("objdump", "-dr", str(obj))
    return len(re.findall(r"R_X86_64_(?:PLT32|PC32)\s+" + re.escape(symbol) + r"(?:-0x4)?\s*$",
                          text, re.M))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--param", type=int, choices=sorted(REGS), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--official-obj", type=Path, required=True,
                    help="upstream ntt.s assembled alone (hash recorded)")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    n, regs = args.param, REGS[args.param]
    name = f"ntruplus{n}_officialopt_ntt_caller_lazy"
    root = args.experiment.resolve()

    nm = run("nm", "-S", str(args.elf))
    sized = re.findall(r"^([0-9a-f]+)\s+([0-9a-f]+)\s+\w\s+" + name + r"$", nm, re.M)
    if len(sized) != 1:
        raise ValueError("missing or ambiguous sized candidate symbol")
    start, size = (int(x, 16) for x in sized[0])
    if start % 32 or size == 0:
        raise ValueError("candidate symbol lacks 32-byte alignment or size")
    official = re.findall(r"^([0-9a-f]+)\s+(?:[0-9a-f]+\s+)?\w\s+poly_ntt$", nm, re.M)
    if len(official) != 1:
        raise ValueError("Official poly_ntt not uniquely linked next to the candidate")
    ostart = int(official[0], 16)

    rows = disasm_rows(args.elf)
    cand = function_rows(rows, start, start + size)
    offi = function_rows(rows, ostart)
    if not cand or cand[0][0] != start or not offi or offi[0][0] != ostart:
        raise ValueError("incomplete disassembly")
    ops = Counter(r[1] for r in cand)
    forbidden = [r for r in cand if "%rsp" in r[2] or "%rbp" in r[2] or r[1].startswith("call")
                 or r[1] in ("push", "pop", "leave", "vzeroupper", "vzeroall")]
    if forbidden:
        raise ValueError(f"unexpected stack/call/AVX-boundary rows: {forbidden[:4]}")
    if ops["vpmulhrsw"] or any("_16xv>" in r[2] for r in cand):
        raise ValueError("terminal Barrett still present in candidate")
    if ops["ret"] != 1 or cand[-1][1] not in ("ret",) + PAD:
        raise ValueError("unexpected return structure")

    oc, lc = normalise(offi), normalise(cand)
    # Rows removed from Official: the _16xv load and one contiguous Barrett run.
    v_rows = [i for i, (op, (text, sym)) in enumerate(oc) if sym == "_16xv"]
    rs_rows = [i for i, (op, _) in enumerate(oc) if op == "vpmulhrsw"]
    if len(v_rows) != 1 or len(rs_rows) != regs:
        raise ValueError("Official structure differs from expectation")
    block = list(range(rs_rows[0], rs_rows[0] + 3 * regs))
    block_ops = Counter(oc[i][0] for i in block)
    if block_ops != Counter({"vpmulhrsw": regs, "vpmullw": regs, "vpsubw": regs}):
        raise ValueError(f"Official terminal block not contiguous: {block_ops}")
    removed = set(v_rows) | set(block)
    keep = [i for i in range(len(oc)) if i not in removed]
    if len(keep) != len(lc):
        raise ValueError(f"row count mismatch {len(keep)} != {len(lc)}")
    to_official = {li: oi for li, oi in enumerate(keep)}
    for li, oi in to_official.items():
        (lop, lval), (oop, oval) = lc[li], oc[oi]
        if lop != oop:
            raise ValueError(f"opcode mismatch at candidate row {li}: {lop} vs {oop}")
        if lop.startswith("j"):
            if to_official[lval[1]] != oval[1]:
                raise ValueError(f"branch target mismatch at candidate row {li}")
        elif lval != oval:
            raise ValueError(f"operand mismatch at candidate row {li}: {lval} vs {oval}")
    delta = Counter(r[1] for r in offi if r[1] not in PAD)
    delta.subtract(Counter(r[1] for r in cand if r[1] not in PAD))
    delta = {k: v for k, v in sorted(delta.items()) if v}
    if delta != {"vmovdqa": 1, "vpmulhrsw": regs, "vpmullw": regs, "vpsubw": regs}:
        raise ValueError(f"unexpected static opcode delta {delta}")

    kem_lazy = root / "build/kem_lazy.o"
    kem_ref = root / "build/kem_ref.o"
    calls = {"kem_lazy.o->candidate": relocs_to(kem_lazy, name),
             "kem_lazy.o->poly_ntt": relocs_to(kem_lazy, "poly_ntt"),
             "kem_ref.o->poly_ntt": relocs_to(kem_ref, "poly_ntt"),
             "kem_ref.o->candidate": relocs_to(kem_ref, name)}
    if calls != {"kem_lazy.o->candidate": 6, "kem_lazy.o->poly_ntt": 0,
                 "kem_ref.o->poly_ntt": 6, "kem_ref.o->candidate": 0}:
        raise ValueError(f"unexpected KEM call graph {calls}")

    out = {
        "class": "linked ELF audit (Phase A, correctness only; no timing)",
        "parameter": f"NTRU+{n}",
        "elf": str(args.elf),
        "elf_sha256": sha(args.elf),
        "official_ntt_obj_sha256": sha(args.official_obj),
        "asm_sha256": sha(root / f"asm/{name}.s"),
        "compiler": run("cc", "--version").splitlines()[0],
        "symbol": name,
        "address_mod_32": start % 32,
        "aligned_32": True,
        "size_bytes": size,
        "instruction_rows": len([r for r in cand if r[1] not in PAD]),
        "official_poly_ntt_rows": len([r for r in offi if r[1] not in PAD]),
        "opcode_counts": dict(sorted(Counter(r[1] for r in cand if r[1] not in PAD).items())),
        "static_delta_official_minus_candidate": delta,
        "dynamic_delta_per_forward": {"vpmulhrsw": regs * ITERATIONS[n], "vpmullw": regs * ITERATIONS[n],
                                      "vpsubw": regs * ITERATIONS[n], "terminal_constant_load": 1},
        "rows_identical_to_official_except_removed": True,
        "stack_references": 0, "calls": 0, "vzeroupper": 0,
        "official_vzeroupper": Counter(r[1] for r in offi)["vzeroupper"],
        "terminal_barrett_vectors": 0,
        "kem_call_relocations": calls,
        "remaining_branches": [op for _, op, _ in cand if op.startswith("j")],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("parameter", "size_bytes", "instruction_rows",
                                          "official_poly_ntt_rows",
                                          "static_delta_official_minus_candidate",
                                          "kem_call_relocations")}, indent=1))


if __name__ == "__main__":
    main()
