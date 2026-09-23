#!/usr/bin/env python3
"""Linked-ELF audit of the NTRU+864 layout-fused codec (Phase A gate 4).

Audits the linked ELF, not the source:
  * fused symbols: unique, sized, 32-byte aligned; exactly one ret; no stack
    (%rsp/%rbp/push/pop/leave), no call, no vzeroupper/vzeroall; one
    backward loop branch;
  * Official poly_tobytes/poly_frombytes and the four pack.s kernels are
    linked in the same ELF (coexistence); the Official wrappers' stack frame
    and vzeroupper use are reported for comparison;
  * dynamic instruction mix per call (loop trip counts from the loop bounds:
    fused 4 x 192 coefficients + final 96; Official pack/unpack 9 x 96,
    tobytes_raw/frombytes_raw 13 x 64 + tail), by class;
  * KEM objects: build/kem_lazy_codec.o calls the fused codec and the lazy
    Forward only; build/kem_codec.o calls the fused codec and Official
    poly_ntt; neither references poly_tobytes/poly_frombytes.
"""

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

TOB = "ntruplus864_officialopt_tobytes_fused"
FROMB = "ntruplus864_officialopt_frombytes_fused"
LAZY = "ntruplus864_officialopt_ntt_caller_lazy"
PAD = ("nop", "nopw", "nopl", "data16", "cs", "xchg")
TRIPS = {TOB: 4, FROMB: 4, "poly_ntt_pack": 9, "poly_ntt_unpack": 9,
         "poly_tobytes_raw": 13, "poly_frombytes_raw": 13}
CROSS = {"vperm2i128", "vinserti128", "vpermq", "vpermd", "vextracti128"}
INLANE = {"vpunpcklqdq", "vpunpckhqdq", "vpshufd", "vpblendw", "vpshufb"}


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def symbols(elf):
    out = {}
    for m in re.finditer(r"^([0-9a-f]+)\s+([0-9a-f]+)?\s*(\w)\s+(\S+)$", run("nm", "-S", str(elf)), re.M):
        out.setdefault(m[4], []).append((int(m[1], 16), int(m[2], 16) if m[2] else None))
    return out


def disasm(elf):
    rows = []
    text = run("objdump", "-d", "--no-show-raw-insn", "-M", "att", str(elf))
    for m in re.finditer(r"^[ \t]*([0-9a-f]+):[ \t]+([a-z][a-z0-9]*)[ \t]*(.*?)$", text, re.M):
        rows.append((int(m[1], 16), m[2], re.sub(r"\s*#.*$", "", m[3].strip())))
    return rows


def body(rows, start, end=None):
    out = []
    for r in rows:
        if r[0] < start:
            continue
        if end is not None and r[0] >= end:
            break
        if r[1] not in PAD:
            out.append(r)
        if end is None and r[1] == "ret":
            break
    return out


def classify(op, operands):
    ops = operands.split(",")
    if op in ("ret", "lea", "add", "cmp", "test", "setne", "movzbl", "xor", "sub") or op.startswith("j"):
        return "scalar"
    if op in ("vmovdqa", "vmovdqu"):
        return "store" if "(" in ops[-1] else "load"
    if op == "vextracti128" and "(" in ops[-1]:
        return "store"
    if op == "vinserti128" and "(" in operands:
        return "insert_from_memory"   # load + p015 merge, not a shuffle-port permute
    if op in CROSS:
        return "cross_lane_permute"
    if op in INLANE:
        return "in_lane_shuffle"
    if op == "vpblendd":
        return "blendd"
    if op in ("vpsllq", "vpsrlq", "vpslld", "vpsrld", "vpsllw", "vpsrlw", "vpsraw"):
        return "shift"
    if op in ("vpmulhrsw", "vpmullw"):
        return "multiply"
    return "alu"


def dynamic(fn_rows, trips):
    """rows outside the single backward loop once, loop rows `trips` times."""
    branches = [(i, r) for i, r in enumerate(fn_rows) if r[1].startswith("j")]
    counts = Counter()
    mem = Counter()
    if not branches:
        loop = range(0)
    else:
        (bi, (_, _, operands)), = branches
        target = int(operands.split()[0], 16)
        ti = next(i for i, r in enumerate(fn_rows) if r[0] == target)
        loop = range(ti, bi + 1)
    for i, (_, op, operands) in enumerate(fn_rows):
        n = trips if i in loop else 1
        cls = classify(op, operands)
        counts[cls] += n
        counts["total"] += n
        if "(%rip)" in operands:
            mem["constant_memory_operands"] += n
    counts.update(mem)
    return dict(sorted(counts.items()))


def relocs(obj, symbol):
    return len(re.findall(r"R_X86_64_(?:PLT32|PC32)\s+" + re.escape(symbol) + r"(?:-0x4)?\s*$",
                          run("objdump", "-dr", str(obj)), re.M))


def stack_frame(fn_rows):
    subs = [int(m[1], 16) for _, op, o in fn_rows if op == "sub" and "%rsp" in o
            for m in [re.match(r"\$0x([0-9a-f]+),%rsp", o)] if m]
    return {"sub_rsp_bytes": subs, "rsp_or_rbp_rows": sum("%rsp" in o or "%rbp" in o for _, _, o in fn_rows)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.experiment.resolve()
    syms = symbols(args.elf)
    rows = disasm(args.elf)
    fns = {}
    for name in (TOB, FROMB):
        entries = syms.get(name, [])
        if len(entries) != 1 or entries[0][1] is None:
            raise ValueError(f"{name}: missing, ambiguous or unsized")
        start, size = entries[0]
        if start % 32:
            raise ValueError(f"{name}: not 32-byte aligned")
        fr = body(rows, start, start + size)
        bad = [r for r in fr if "%rsp" in r[2] or "%rbp" in r[2] or r[1].startswith("call")
               or r[1] in ("push", "pop", "leave", "vzeroupper", "vzeroall")]
        if bad:
            raise ValueError(f"{name}: stack/call/AVX-boundary rows {bad[:4]}")
        ops = Counter(r[1] for r in fr)
        if ops["ret"] != 1 or fr[-1][1] != "ret":
            raise ValueError(f"{name}: unexpected return structure")
        if sum(1 for r in fr if r[1].startswith("j")) != 1:
            raise ValueError(f"{name}: expected exactly one loop branch")
        fns[name] = {"address_mod_32": start % 32, "size_bytes": size, "instruction_rows": len(fr),
                     "stack_references": 0, "calls": 0, "vzeroupper": 0,
                     "dynamic_per_call": dynamic(fr, TRIPS[name]),
                     "opcode_counts": dict(sorted(ops.items()))}
    official = {}
    for name in ("poly_tobytes", "poly_frombytes", "poly_ntt_pack", "poly_ntt_unpack",
                 "poly_tobytes_raw", "poly_frombytes_raw"):
        entries = syms.get(name, [])
        if len(entries) != 1:
            raise ValueError(f"Official {name} not uniquely linked")
        start, size = entries[0]
        fr = body(rows, start, start + size if size else None)
        official[name] = {"address_mod_32": start % 32, "instruction_rows": len(fr),
                          "calls": [o for _, op, o in fr if op.startswith("call")],
                          "vzeroupper": sum(r[1] == "vzeroupper" for r in fr),
                          "stack": stack_frame(fr)}
        if name in TRIPS:
            official[name]["dynamic_per_call"] = dynamic(fr, TRIPS[name])

    def add(*names):
        total = Counter()
        for n in names:
            total.update(official[n]["dynamic_per_call"])
        return total
    comparison = {}
    for fused, parts, wrapper in ((TOB, ("poly_ntt_pack", "poly_tobytes_raw"), "poly_tobytes"),
                                  (FROMB, ("poly_frombytes_raw", "poly_ntt_unpack"), "poly_frombytes")):
        o = add(*parts)
        f = Counter(fns[fused]["dynamic_per_call"])
        keys = sorted(set(o) | set(f))
        comparison[fused] = {
            "official_kernels": list(parts),
            "official_wrapper_rows_not_counted": official[wrapper]["instruction_rows"],
            "official": {k: o[k] for k in keys}, "fused": {k: f[k] for k in keys},
            "fused_minus_official": {k: f[k] - o[k] for k in keys if f[k] != o[k]},
            "per_96_coefficients_fused_minus_official": {
                k: round((f[k] - o[k]) / 9, 2) for k in keys if f[k] != o[k]}}

    objs = {"kem_lazy_codec.o": root / "build/kem_lazy_codec.o", "kem_codec.o": root / "build/kem_codec.o",
            "kem_ref.o": root / "build/kem_ref.o"}
    calls = {f"{o}->{s}": relocs(p, s) for o, p in objs.items()
             for s in (TOB, FROMB, "poly_tobytes", "poly_frombytes", "poly_ntt", LAZY)}
    expect_zero = ["kem_lazy_codec.o->poly_tobytes", "kem_lazy_codec.o->poly_frombytes",
                   "kem_lazy_codec.o->poly_ntt", "kem_codec.o->poly_tobytes",
                   "kem_codec.o->poly_frombytes", f"kem_codec.o->{LAZY}",
                   f"kem_ref.o->{TOB}", f"kem_ref.o->{FROMB}", f"kem_ref.o->{LAZY}"]
    if any(calls[k] for k in expect_zero):
        raise ValueError(f"unexpected KEM call graph {calls}")
    for o in ("kem_lazy_codec.o", "kem_codec.o"):
        if calls[f"{o}->{TOB}"] != calls["kem_ref.o->poly_tobytes"] or \
           calls[f"{o}->{FROMB}"] != calls["kem_ref.o->poly_frombytes"]:
            raise ValueError(f"{o}: codec call-site count differs from Official {calls}")
    if calls[f"kem_lazy_codec.o->{LAZY}"] != 6 or calls["kem_codec.o->poly_ntt"] != 6:
        raise ValueError(f"unexpected Forward call graph {calls}")

    out = {
        "class": "linked ELF audit (codec Phase A, correctness only; no timing)",
        "parameter": "NTRU+864",
        "elf": str(args.elf), "elf_sha256": sha(args.elf),
        "asm_sha256": sha(root / "asm/ntruplus864_officialopt_codec_fused.s"),
        "compiler": run("cc", "--version").splitlines()[0],
        "fused": fns,
        "official": official,
        "dynamic_comparison": comparison,
        "stack_bytes": {"fused_tobytes": 0, "fused_frombytes": 0,
                        "official_poly_tobytes_frame": official["poly_tobytes"]["stack"]["sub_rsp_bytes"],
                        "official_poly_frombytes_frame": official["poly_frombytes"]["stack"]["sub_rsp_bytes"]},
        "vzeroupper_policy": "fused 0; Official pack.s kernels 0 (see official.*.vzeroupper)",
        "kem_call_relocations": calls,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"fused": {k: {x: v[x] for x in ("size_bytes", "instruction_rows")} for k, v in fns.items()},
                      "stack_bytes": out["stack_bytes"],
                      "delta_per_call": {k: v["fused_minus_official"] for k, v in comparison.items()},
                      "kem_call_relocations": {k: v for k, v in calls.items() if v}}, indent=1))


if __name__ == "__main__":
    main()
