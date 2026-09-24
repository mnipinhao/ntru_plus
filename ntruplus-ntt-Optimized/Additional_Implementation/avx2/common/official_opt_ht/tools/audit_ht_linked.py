#!/usr/bin/env python3
"""Linked-ELF audit of the NTRU+768 HT Forward / R^2-fold candidate (not its source).

  * new asm entries (HT Forward, no-R^2 BaseMul): unique, sized, 32-byte
    aligned; one ret; no stack (%rsp/%rbp/push/pop/leave), call or
    vzeroupper/vzeroall; the HT RIP tables are 32-byte aligned;
  * linked instruction stream == the stream of the same .s assembled alone
    (normalised: rip operands by symbol, branches by row), so the symbolic
    proof on the source applies to the linked code; rip symbols recorded;
  * the fold BaseInv (C) is linked and does not call poly_baseinv;
  * call relocations of the three KEM objects (candidate and both controls):
    Forward, BaseInv, BaseMul, tobytes and SHAKE256/hash bindings are exactly
    the intended ones (the candidate never calls the old lazy or the Official
    Forward, nor Official BaseInv, nor poly_tobytes).
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "official_opt_lazy/tools"))
from audit_forward_caller_lazy import PAD, disasm_rows, function_rows, normalise, relocs_to, run  # noqa: E402

HT = "ntruplus768_officialopt_ntt_ht"
NOR2 = "ntruplus768_officialopt_basemul_nor2"
R2INV = "ntruplus768_officialopt_baseinv_r2fold"
LAZY = "ntruplus768_officialopt_ntt_caller_lazy"
FREEZE = "ntruplus768_officialopt_tobytes_freeze2op"
TABLES = ("ntruplus768_officialopt_ht_zetas_a", "ntruplus768_officialopt_ht_zetas_b")
TARGETS = [HT, LAZY, "poly_ntt", R2INV, "poly_baseinv", NOR2, "poly_basemul", FREEZE, "poly_tobytes",
           "ntruplus_mlkfips202_shake256", "fips202avx_shake256", "ntruplus768_keccak_hash_f",
           "ntruplus768_keccak_hash_g", "ntruplus768_keccak_hash_h", "hash_f", "hash_g", "hash_h"]
KEM_BASE = {LAZY: 6, "poly_ntt": 0, HT: 0, "poly_baseinv": 2, R2INV: 0, "poly_basemul": 4, NOR2: 0,
            FREEZE: 7, "poly_tobytes": 0, "ntruplus_mlkfips202_shake256": 2, "fips202avx_shake256": 0,
            "ntruplus768_keccak_hash_f": 2, "ntruplus768_keccak_hash_g": 2, "ntruplus768_keccak_hash_h": 2,
            "hash_f": 0, "hash_g": 0, "hash_h": 0}
EXPECT = {
    "kem_lazy_r2fold_freeze2op_keccak_ht": {**KEM_BASE, LAZY: 0, HT: 6, "poly_baseinv": 0, R2INV: 2,
                                            "poly_basemul": 2, NOR2: 2},
    "kem_lazy_freeze2op_keccak_ht": {**KEM_BASE, LAZY: 0, HT: 6},
    "kem_lazy_r2fold_freeze2op_keccak": {**KEM_BASE, "poly_baseinv": 0, R2INV: 2, "poly_basemul": 2, NOR2: 2},
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def symbol(nm, name, sized=True):
    pat = r"^([0-9a-f]+)\s+([0-9a-f]+)\s+\w\s+" + name + r"$" if sized else \
        r"^([0-9a-f]+)\s+(?:[0-9a-f]+\s+)?\w\s+" + name + r"$"
    found = re.findall(pat, nm, re.M)
    if len(found) != 1:
        raise ValueError(f"missing or ambiguous symbol {name}")
    return tuple(int(x, 16) for x in found[0]) if sized else (int(found[0], 16), None)


def audit_entry(nm, rows, name, asm, build):
    start, size = symbol(nm, name)
    if start % 32 or not size:
        raise ValueError(f"{name}: not 32-byte aligned or unsized")
    body = function_rows(rows, start, start + size)
    forbidden = [r for r in body if "%rsp" in r[2] or "%rbp" in r[2] or r[1].startswith("call")
                 or r[1] in ("push", "pop", "leave", "vzeroupper", "vzeroall")]
    ops = Counter(r[1] for r in body if r[1] not in PAD)
    if forbidden or ops["ret"] != 1:
        raise ValueError(f"{name}: forbidden rows {forbidden[:3]} or ret count {ops['ret']}")
    obj = build / f"{name}.alone.o"
    subprocess.run(["cc", "-c", "-o", str(obj), str(asm)], check=True)
    orows = disasm_rows(obj)
    onm = run("nm", "-S", str(obj))
    ostart, osize = symbol(onm, name)
    ob = function_rows(orows, ostart, ostart + osize)
    ln, on = normalise(body), normalise(ob)
    # an unlinked object shows rip operands without symbols: compare opcode/operand text
    # and branch rows, then record the linked rip symbols separately
    strip = [(op, v if op.startswith("j") else (v[0],)) for op, v in ln]
    ostrip = [(op, v if op.startswith("j") else (v[0],)) for op, v in on]
    if strip != ostrip:
        raise ValueError(f"{name}: linked stream differs from the assembled source")
    rip = sorted({v[1] for op, v in ln if not op.startswith("j") and v[1]})
    return {"address_mod_32": start % 32, "size_bytes": size,
            "instruction_rows": sum(ops.values()), "opcode_counts": dict(sorted(ops.items())),
            "linked_stream_equals_assembled_source": True, "rip_symbols": rip,
            "stack_references": 0, "calls": 0, "vzeroupper": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.experiment.resolve()
    nm = run("nm", "-S", str(args.elf))
    rows = disasm_rows(args.elf)
    with tempfile.TemporaryDirectory() as tmp:
        entries = {name: audit_entry(nm, rows, name, root / f"asm/{name}.s", Path(tmp))
                   for name in (HT, NOR2)}
    if set(entries[HT]["rip_symbols"]) != {"_16xq", "_16xzeta1", "_16xw", "_16xwqinv", "zetas", *TABLES}:
        raise ValueError(f"HT rip symbols {entries[HT]['rip_symbols']}")
    tables = {}
    for t in TABLES:
        addr, _ = symbol(nm, t, sized=False)
        if addr % 32:
            raise ValueError(f"{t} not 32-byte aligned")
        tables[t] = {"address_mod_32": 0}
    r2start, r2size = symbol(nm, R2INV)
    r2rows = function_rows(rows, r2start, r2start + r2size)
    r2calls = sorted({re.sub(r"^.*<(.*)>.*$", r"\1", r[2]) for r in r2rows if r[1].startswith("call")})
    if any("poly_baseinv>" in r[2] and "poly_baseinv_1" not in r[2] for r in r2rows) or \
            "poly_baseinv_1" not in r2calls:
        raise ValueError(f"fold BaseInv call graph {r2calls}")
    relocs = {}
    for v, exp in EXPECT.items():
        obj = root / f"build/{v}.o"
        got = {t: relocs_to(obj, t) for t in TARGETS}
        if got != exp:
            raise ValueError(f"{v}: call relocations {got} != {exp}")
        relocs[v] = {k: n for k, n in got.items() if n}
    out = {
        "class": "linked ELF audit (Phase A, correctness only; no timing)",
        "parameter": "NTRU+768", "elf": str(args.elf.relative_to(root) if args.elf.is_absolute() else args.elf),
        "elf_sha256": sha(args.elf),
        "asm_sha256": {n: sha(root / f"asm/{n}.s") for n in (HT, NOR2)},
        "compiler": run("cc", "--version").splitlines()[0],
        "entries": entries, "ht_tables": tables,
        "fold_baseinv": {"size_bytes": r2size, "calls": r2calls},
        "kem_call_relocations": relocs,
        "candidate_calls_old_lazy_or_official_forward": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"entries": {k: {x: v[x] for x in ("size_bytes", "instruction_rows")}
                                  for k, v in entries.items()}, "kem_call_relocations": relocs}, indent=1))


if __name__ == "__main__":
    main()
