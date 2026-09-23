#!/usr/bin/env python3
"""Linked-ELF audit of the NTRU+864 exp002 direct codec (Phase A gate 4).

Audits linked ELFs, not the source (helpers shared with audit_codec_fused.py):
  * direct symbols (in --elf) and the freeze-only control tobytes_fused_min
    (in --min-elf): unique, sized, 32-byte aligned, one ret, one backward
    loop branch, no stack / call / vzeroupper;
  * the direct kernels' constants are RIP-relative loads from .rodata (the
    ELF has no text relocations left);
  * dynamic instruction mix per call by class, for Official (pack.s
    kernels), exp001 (fused, from --exp001-elf), fused_min and direct, plus a
    per-96-coefficient table and an issue-port class model;
  * KEM objects: build/kem_lazy_codec_direct.o calls the direct codec and the
    lazy Forward only; build/kem_codec_direct.o the direct codec and Official
    poly_ntt; neither references poly_tobytes/poly_frombytes; call-site counts
    equal Official's.
"""

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("acf", HERE / "audit_codec_fused.py")
acf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(acf)

TOB = "ntruplus864_officialopt_tobytes_direct"
FROMB = "ntruplus864_officialopt_frombytes_direct"
TOB_MIN = "ntruplus864_officialopt_tobytes_fused_min"
TOB1, FROMB1 = acf.TOB, acf.FROMB
LAZY = acf.LAZY
TRIPS = dict(acf.TRIPS, **{TOB: 4, FROMB: 4, TOB_MIN: 4})
SHUF = {"vpunpcklwd", "vpunpckhwd", "vpunpckldq", "vpunpckhdq", "vpunpcklqdq", "vpunpckhqdq",
        "vpshufb", "vpshufd", "vpblendw", "vpackusdw"}


def classify(op, operands):
    ops = operands.split(",")
    if op in ("vmovq", "vpextrd") and "(" in ops[-1]:
        return "store"
    if op == "vextracti128" and "(" not in ops[-1]:
        return "cross_lane_permute"
    if op == "vpmaddwd":
        return "multiply"
    if op in SHUF:
        return "in_lane_shuffle"
    return acf.classify(op, operands)


def port_class(op, operands):
    """Coarse issue-port model (Golden/Redwood Cove classes; see doc)."""
    c = classify(op, operands)
    if c in ("multiply", "shift"):
        return "p01"
    if c == "in_lane_shuffle":
        return "p15_shuffle"
    if c == "cross_lane_permute":
        return "p5"
    if c in ("alu", "blendd"):
        return "p015"
    if c == "insert_from_memory":
        return "load+p015"
    return c


def dynamic(fn_rows, trips, key=classify):
    branches = [(i, r) for i, r in enumerate(fn_rows) if r[1].startswith("j")]
    (bi, (_, _, operands)), = branches
    target = int(operands.split()[0], 16)
    ti = next(i for i, r in enumerate(fn_rows) if r[0] == target)
    counts = Counter()
    for i, (_, op, o) in enumerate(fn_rows):
        n = trips if ti <= i <= bi else 1
        counts[key(op, o)] += n
        counts["total"] += n
        if "(%rip)" in o:
            counts["constant_memory_operands"] += n
    return dict(sorted(counts.items()))


def function(syms, rows, name, check=True):
    entries = syms.get(name, [])
    if len(entries) != 1 or (check and entries[0][1] is None):
        raise ValueError(f"{name}: missing, ambiguous or unsized")
    start, size = entries[0]
    fr = acf.body(rows, start, start + size if size else None)   # unsized pack.s: up to ret
    if check:
        if start % 32:
            raise ValueError(f"{name}: not 32-byte aligned")
        bad = [r for r in fr if "%rsp" in r[2] or "%rbp" in r[2] or r[1].startswith("call")
               or r[1] in ("push", "pop", "leave", "vzeroupper", "vzeroall")]
        if bad:
            raise ValueError(f"{name}: stack/call/AVX-boundary rows {bad[:4]}")
        ops = Counter(r[1] for r in fr)
        if ops["ret"] != 1 or fr[-1][1] != "ret":
            raise ValueError(f"{name}: unexpected return structure")
        if sum(1 for r in fr if r[1].startswith("j")) != 1:
            raise ValueError(f"{name}: expected exactly one loop branch")
    return start, size, fr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--min-elf", type=Path, required=True)
    ap.add_argument("--exp001-elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.experiment.resolve()
    per = {}
    fns = {}
    for elf, names in ((args.elf, (TOB, FROMB)), (args.min_elf, (TOB_MIN,)), (args.exp001_elf, (TOB1, FROMB1))):
        syms, rows = acf.symbols(elf), acf.disasm(elf)
        for name in names:
            start, size, fr = function(syms, rows, name)
            fns[name] = {"elf": str(elf), "address_mod_32": start % 32, "size_bytes": size,
                         "instruction_rows": len(fr), "stack_references": 0, "calls": 0, "vzeroupper": 0,
                         "dynamic_per_call": dynamic(fr, TRIPS[name]),
                         "port_classes_per_call": dynamic(fr, TRIPS[name], port_class),
                         "opcode_counts": dict(sorted(Counter(r[1] for r in fr).items()))}
        if elf == args.elf:
            for name in ("poly_ntt_pack", "poly_tobytes_raw", "poly_frombytes_raw", "poly_ntt_unpack"):
                start, size, fr = function(syms, rows, name, check=False)
                per[name] = {"dynamic_per_call": dynamic(fr, TRIPS[name]),
                             "port_classes_per_call": dynamic(fr, TRIPS[name], port_class)}
            for name in ("poly_tobytes", "poly_frombytes"):
                if len(syms.get(name, [])) != 1:
                    raise ValueError(f"Official {name} not uniquely linked")
    reloc_text = acf.run("readelf", "-r", str(args.elf))
    textrel = "TEXTREL" in acf.run("readelf", "-d", str(args.elf))
    if textrel:
        raise ValueError("ELF has text relocations")

    def add(*names, field="dynamic_per_call"):
        total = Counter()
        for n in names:
            total.update(per[n][field])
        return total
    table = {}
    for direction, off_parts, names in (
            ("tobytes", ("poly_ntt_pack", "poly_tobytes_raw"), (TOB1, TOB_MIN, TOB)),
            ("frombytes", ("poly_frombytes_raw", "poly_ntt_unpack"), (FROMB1, FROMB))):
        for field in ("dynamic_per_call", "port_classes_per_call"):
            cols = {"official": add(*off_parts, field=field)}
            for n in names:
                cols[n] = Counter(fns[n][field])
            keys = sorted(set().union(*cols.values()))
            table.setdefault(direction, {})[field] = {k: {c: cols[c][k] for c in cols} for k in keys}
            table[direction][field.replace("per_call", "per_96_coefficients")] = {
                k: {c: round(cols[c][k] / 9, 1) for c in cols} for k in keys}

    objs = {"kem_lazy_codec_direct.o": root / "build/kem_lazy_codec_direct.o",
            "kem_codec_direct.o": root / "build/kem_codec_direct.o", "kem_ref.o": root / "build/kem_ref.o"}
    calls = {f"{o}->{s}": acf.relocs(p, s) for o, p in objs.items()
             for s in (TOB, FROMB, "poly_tobytes", "poly_frombytes", "poly_ntt", LAZY, TOB1, FROMB1)}
    expect_zero = [f"{o}->{s}" for o in ("kem_lazy_codec_direct.o", "kem_codec_direct.o")
                   for s in ("poly_tobytes", "poly_frombytes", TOB1, FROMB1)]
    expect_zero += ["kem_lazy_codec_direct.o->poly_ntt", f"kem_codec_direct.o->{LAZY}",
                    f"kem_ref.o->{TOB}", f"kem_ref.o->{FROMB}"]
    if any(calls[k] for k in expect_zero):
        raise ValueError(f"unexpected KEM call graph {calls}")
    for o in ("kem_lazy_codec_direct.o", "kem_codec_direct.o"):
        if calls[f"{o}->{TOB}"] != calls["kem_ref.o->poly_tobytes"] or \
           calls[f"{o}->{FROMB}"] != calls["kem_ref.o->poly_frombytes"]:
            raise ValueError(f"{o}: codec call-site count differs from Official {calls}")
    if calls[f"kem_lazy_codec_direct.o->{LAZY}"] != 6 or calls["kem_codec_direct.o->poly_ntt"] != 6:
        raise ValueError(f"unexpected Forward call graph {calls}")
    out = {
        "class": "linked ELF audit (exp002 codec Phase A, correctness only; no timing)",
        "parameter": "NTRU+864",
        "elf": str(args.elf), "elf_sha256": acf.sha(args.elf),
        "asm_sha256": {p: acf.sha(root / p) for p in ("asm/ntruplus864_officialopt_codec_direct.s",
                                                     "asm/ntruplus864_officialopt_codec_fused_min.s",
                                                     "asm/ntruplus864_officialopt_codec_fused.s")},
        "compiler": acf.run("cc", "--version").splitlines()[0],
        "functions": fns,
        "text_relocations": textrel,
        "dynamic_relocations_mentioning_direct": sum("direct" in l for l in reloc_text.splitlines()),
        "dynamic_comparison": table,
        "port_model_note": "p01 = vector multiply/shift, p015 = vector add/logic/min/blendd, p15_shuffle = "
                           "in-lane shuffles (unpck/pshufb/pshufd/blendw/packusdw; p5 only on Skylake-class), "
                           "p5 = cross-lane; loads/stores on their own ports",
        "kem_call_relocations": calls,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"functions": {k: {x: v[x] for x in ("size_bytes", "instruction_rows")}
                                    for k, v in fns.items()},
                      "per_96": {d: t["dynamic_per_96_coefficients"]["total"] for d, t in table.items()},
                      "kem_call_relocations": {k: v for k, v in calls.items() if v}}, indent=1))


if __name__ == "__main__":
    main()
