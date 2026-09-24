#!/usr/bin/env python3
"""Linked-ELF audit of the NTRU+768 / 864 / 1152 HT Forward / R^2-fold candidate (not its source).

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

Flat mode (Phase B, --flat-root DIR --flat-kem-obj OBJ): the same entry, table
and fold-BaseInv checks on an ELF linked from the SUPERCOP-flat qualification
export DIR (entries compared with DIR/{ntt_ht,basemul_nor2,invntt_ht}.s), and
the call relocations of the flat kem.c object OBJ against FLAT_EXPECT (the
candidate bindings with the Official hash_f/g/h names, as in the flat tree).
Each --phase-a-obj FLAT=PHASEA pair must be the same object up to the file
symbol and the repo-only hash names (ntruplus768_keccak_hash_* -> hash_*):
identical section headers, contents, relocations and symbol table.

--param 864 / 1152 (default 768): the same checks without the HT inverse
(not part of those candidates); the KEM objects are the candidate
(HT Forward + R^2 fold) and the ht_only / r2fold_only controls, and the
tobytes/frombytes bindings are the base's (864: direct 12-bit codec, 7
tobytes + 4 frombytes call sites after inlining; 1152: 2-op-freeze tobytes x 7).
"""
import argparse
import difflib
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
HTINV = "ntruplus768_officialopt_invntt_ht"
NOR2 = "ntruplus768_officialopt_basemul_nor2"
R2INV = "ntruplus768_officialopt_baseinv_r2fold"
LAZY = "ntruplus768_officialopt_ntt_caller_lazy"
FREEZE = "ntruplus768_officialopt_tobytes_freeze2op"
TABLES = ("ntruplus768_officialopt_ht_zetas_a", "ntruplus768_officialopt_ht_zetas_b",
          "ntruplus768_officialopt_htinv_zetas_b")
PARAMETER = 768
ASM = {HT: "ntt_ht.s", NOR2: "basemul_nor2.s", HTINV: "invntt_ht.s"}
TARGETS = [HT, LAZY, "poly_ntt", HTINV, "poly_invntt_scale", R2INV, "poly_baseinv", NOR2, "poly_basemul", FREEZE, "poly_tobytes",
           "ntruplus_mlkfips202_shake256", "fips202avx_shake256", "ntruplus768_keccak_hash_f",
           "ntruplus768_keccak_hash_g", "ntruplus768_keccak_hash_h", "hash_f", "hash_g", "hash_h"]
KEM_BASE = {LAZY: 6, "poly_ntt": 0, HT: 0, HTINV: 0, "poly_invntt_scale": 1, "poly_baseinv": 2, R2INV: 0, "poly_basemul": 4, NOR2: 0,
            FREEZE: 7, "poly_tobytes": 0, "ntruplus_mlkfips202_shake256": 2, "fips202avx_shake256": 0,
            "ntruplus768_keccak_hash_f": 2, "ntruplus768_keccak_hash_g": 2, "ntruplus768_keccak_hash_h": 2,
            "hash_f": 0, "hash_g": 0, "hash_h": 0}
FOLD = {"poly_baseinv": 0, R2INV: 2, "poly_basemul": 2, NOR2: 2}
EXPECT = {
    "kem_lazy_r2fold_freeze2op_keccak_ht_htinv": {**KEM_BASE, LAZY: 0, HT: 6, **FOLD,
                                                  HTINV: 1, "poly_invntt_scale": 0},   # candidate
    "kem_lazy_freeze2op_keccak_ht": {**KEM_BASE, LAZY: 0, HT: 6},
    "kem_lazy_r2fold_freeze2op_keccak": {**KEM_BASE, **FOLD},
    "kem_lazy_freeze2op_keccak_htinv": {**KEM_BASE, HTINV: 1, "poly_invntt_scale": 0},
    "kem_lazy_r2fold_freeze2op_keccak_ht": {**KEM_BASE, LAZY: 0, HT: 6, **FOLD},
}
# flat kem.c (qualification export): candidate bindings, Official hash names
FLAT_EXPECT = {**EXPECT["kem_lazy_r2fold_freeze2op_keccak_ht_htinv"],
               "ntruplus768_keccak_hash_f": 0, "ntruplus768_keccak_hash_g": 0, "ntruplus768_keccak_hash_h": 0,
               "hash_f": 2, "hash_g": 2, "hash_h": 2}
FLAT_NAME_MAP = {f"ntruplus768_keccak_hash_{x}": f"hash_{x}" for x in "fgh"}


def configure(param):
    """NTRU+864 / 1152: rebind the module constants (no HT inverse)."""
    global HT, HTINV, NOR2, R2INV, LAZY, TABLES, TARGETS, EXPECT, FLAT_EXPECT, FLAT_NAME_MAP, PARAMETER, ASM
    if param == 768:
        return
    p = f"ntruplus{param}_officialopt"
    HT, NOR2, R2INV, LAZY, HTINV = f"{p}_ntt_ht", f"{p}_basemul_nor2", f"{p}_baseinv_r2fold", \
        f"{p}_ntt_caller_lazy", None
    TABLES = (f"{p}_ht_zetas_a", f"{p}_ht_zetas_b")
    PARAMETER = param
    ASM = {HT: "ntt_ht.s", NOR2: "basemul_nor2.s"}
    hashes = [f"ntruplus{param}_keccak_hash_{x}" for x in "fgh"]
    if param == 864:     # direct 12-bit codec (declassify_poly_frombytes inlined: 1 Encap + 3 Decap sites)
        codec = {f"{p}_tobytes_direct": 7, f"{p}_frombytes_direct": 4, "poly_tobytes": 0, "poly_frombytes": 0}
        stem = "codec_direct"
    else:                # 2-op-freeze tobytes; Official frombytes
        codec = {f"{p}_tobytes_freeze2op": 7, "poly_tobytes": 0}
        stem = "freeze2op"
    TARGETS = [HT, LAZY, "poly_ntt", "poly_invntt_scale", R2INV, "poly_baseinv", NOR2, "poly_basemul",
               *codec, "ntruplus_mlkfips202_shake256", "fips202avx_shake256", *hashes, "hash_f", "hash_g", "hash_h"]
    base = {LAZY: 6, "poly_ntt": 0, HT: 0, "poly_invntt_scale": 1, "poly_baseinv": 2, R2INV: 0, "poly_basemul": 4,
            NOR2: 0, **codec, "ntruplus_mlkfips202_shake256": 2, "fips202avx_shake256": 0,
            **{h: 2 for h in hashes}, "hash_f": 0, "hash_g": 0, "hash_h": 0}
    fold = {"poly_baseinv": 0, R2INV: 2, "poly_basemul": 2, NOR2: 2}
    EXPECT = {
        f"kem_lazy_r2fold_{stem}_keccak_ht": {**base, LAZY: 0, HT: 6, **fold},   # candidate
        f"kem_lazy_{stem}_keccak_ht": {**base, LAZY: 0, HT: 6},
        f"kem_lazy_r2fold_{stem}_keccak": {**base, **fold},
    }
    FLAT_EXPECT = {**EXPECT[f"kem_lazy_r2fold_{stem}_keccak_ht"], **{h: 0 for h in hashes},
                   "hash_f": 2, "hash_g": 2, "hash_h": 2}
    FLAT_NAME_MAP = {h: f"hash_{x}" for h, x in zip(hashes, "fgh")}


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


def object_dump(obj, name_map):
    """Section headers, contents, relocations and symbols of one object, minus the file symbol."""
    text = run("objdump", "-h", "-s", "-r", "-t", "-w", str(obj))
    lines = []
    for line in text.splitlines()[2:]:  # drop the '<file>: file format' header
        if re.search(r"\sdf\s+\*ABS\*\s", line):
            continue
        for a, b in name_map.items():
            line = re.sub(r"\b" + a + r"\b", b, line)
        lines.append(line)
    return lines


def compare_objects(flat, phase_a, name_map):
    a, b = object_dump(flat, {}), object_dump(phase_a, name_map)
    if a != b:
        diff = [l for l in difflib.unified_diff(b, a, lineterm="", n=0)][:12]
        raise ValueError(f"{flat} differs from Phase-A {phase_a}: {diff}")
    return {"flat": str(flat), "phase_a": str(phase_a), "flat_sha256": sha(flat), "phase_a_sha256": sha(phase_a),
            "identical_modulo": ["file symbol", *(f"{k}->{v}" for k, v in name_map.items())],
            "dump_lines": len(a)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), default=768)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--flat-root", type=Path, help="flat qualification export (flat mode)")
    ap.add_argument("--flat-kem-obj", type=Path, help="flat kem.c object (flat mode)")
    ap.add_argument("--phase-a-obj", action="append", default=[], metavar="FLAT=PHASEA",
                    help="flat-mode object pair that must be identical up to the file symbol and hash names")
    args = ap.parse_args()
    configure(args.param)
    root = args.experiment.resolve()
    flat = args.flat_root.resolve() if args.flat_root else None
    if (flat is None) != (args.flat_kem_obj is None):
        ap.error("--flat-root and --flat-kem-obj go together")
    asm = ASM
    src = {n: (flat / asm[n]) if flat else root / f"asm/{n}.s" for n in asm}
    nm = run("nm", "-S", str(args.elf))
    rows = disasm_rows(args.elf)
    with tempfile.TemporaryDirectory() as tmp:
        entries = {name: audit_entry(nm, rows, name, src[name], Path(tmp))
                   for name in asm}
    if set(entries[HT]["rip_symbols"]) != {"_16xq", "_16xzeta1", "_16xw", "_16xwqinv", "zetas", *TABLES[:2]}:
        raise ValueError(f"HT rip symbols {entries[HT]['rip_symbols']}")
    if HTINV and set(entries[HTINV]["rip_symbols"]) != {"_16xq", "_16xv", "_16xw", "_16xwqinv", "zetas_inv",
                                                        "_16xNinv_scale", "_16xNinv_scaleqinv", TABLES[2]}:
        raise ValueError(f"HT inverse rip symbols {entries[HTINV]['rip_symbols']}")
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
    objects = {"flat kem.c": (args.flat_kem_obj, FLAT_EXPECT)} if flat else \
        {v: (root / f"build/{v}.o", exp) for v, exp in EXPECT.items()}
    for v, (obj, exp) in objects.items():
        got = {t: relocs_to(obj, t) for t in TARGETS}
        if got != exp:
            raise ValueError(f"{v}: call relocations {got} != {exp}")
        relocs[v] = {k: n for k, n in got.items() if n}
    equivalence = {}
    for pair in args.phase_a_obj:
        f, p = (Path(x) for x in pair.split("=", 1))
        equivalence[f.name] = compare_objects(f, p, FLAT_NAME_MAP)
    elf_path = args.elf.resolve()
    out = {
        "class": "linked ELF audit (Phase A, correctness only; no timing)" if not flat else
                 "linked ELF audit of the SUPERCOP-flat qualification export (Phase B, correctness only; no timing)",
        "parameter": f"NTRU+{PARAMETER}",
        "elf": str(elf_path.relative_to(root) if elf_path.is_relative_to(root) else args.elf),
        "elf_sha256": sha(args.elf),
        "asm_sha256": {n: sha(src[n]) for n in asm},
        "compiler": run("cc", "--version").splitlines()[0],
        "entries": entries, "ht_tables": tables,
        "fold_baseinv": {"size_bytes": r2size, "calls": r2calls},
        "kem_call_relocations": relocs,
        "candidate_calls_old_lazy_or_official_forward": False,
    }
    if flat:
        out["flat_root"] = str(flat.relative_to(root) if flat.is_relative_to(root) else flat)
        out["phase_a_object_equivalence"] = equivalence
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"entries": {k: {x: v[x] for x in ("size_bytes", "instruction_rows")}
                                  for k, v in entries.items()}, "kem_call_relocations": relocs}, indent=1))


if __name__ == "__main__":
    main()
