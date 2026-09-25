#!/usr/bin/env python3
"""Linked-ELF audit of the NTRU+768 / 864 / 1152 fused inverse (invntt_crep) and Shoup BaseMul.

  * invntt_crep entry: the HT audit's entry checks (common/official_opt_ht/tools/audit_ht_linked.py
    audit_entry, imported unchanged): unique, sized, 32-byte aligned, one ret, no stack
    (%rsp/%rbp/push/pop/leave), call or vzeroupper; linked stream == the .s assembled alone;
    rip symbols exactly the expected constants and its own tables (32-byte aligned);
  * basemul_shoup entry (gcc output): unique, sized, 32-byte aligned; linked stream == the .s
    assembled alone; exactly one ret, one vzeroupper, no call, one conditional branch (the loop
    back edge, target inside the function); only the audited opcode set; every stack reference
    is the fixed frame (push %rbp / mov %rsp,%rbp / and $-32,%rsp / sub $imm,%rsp / leave) or a
    constant-displacement %rsp operand; no memory operand has an index register and no GPR is
    loaded from memory, so no address depends on data; rip symbols: only its own zeta table;
  * KEM call relocations of every variant object (candidate and controls): the current-best
    (HT candidate) bindings of audit_ht_linked.EXPECT with exactly the intended changes:
      Inverse D: poly_invntt_scale (768: the HT inverse) and poly_crepmod3 1 -> 0, invntt_crep 0 -> 1;
      Shoup:     poly_basemul 2 -> 0, basemul_shoup 0 -> 2;
    and unchanged poly_basemul_scale 1, keygen nor2 2, fold BaseInv 2, Forward 6 x HT, codec,
    SHAKE256/hash bindings.

Flat mode (--flat-root DIR --flat-kem-obj OBJ, Phase B): the entry checks against the export's
invntt_crep.s / basemul_shoup.s, the flat kem.c relocations against the candidate bindings with
the Official hash_f/g/h names, and --phase-a-obj FLAT=PHASEA object identity (audit_ht_linked
compare_objects: identical up to the file symbol and the repo-only hash names).

  audit_invshoup_linked.py --param N --experiment . --elf ELF --output out.json [--candidate NAME]
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "official_opt_ht/tools"))
sys.path.insert(0, str(HERE.parents[2] / "official_opt_lazy/tools"))
import audit_ht_linked as H  # noqa: E402
from audit_forward_caller_lazy import PAD, disasm_rows, function_rows, normalise, relocs_to, run  # noqa: E402

SHOUP_OPS = {"push", "mov", "lea", "vmovd", "vpbroadcastd", "and", "sub", "vmovdqa", "vmovdqu", "vpsllw",
             "vpmulhuw", "vpmullw", "vpmulhrsw", "vpaddw", "vpsubw", "add", "cmp", "jne", "vzeroupper",
             "leave", "ret"}
STEM = {768: "freeze2op", 864: "codec_direct", 1152: "freeze2op"}


def expectations(n):
    """(TARGETS, {variant: expected relocation counts}, flat expected, HT candidate name)."""
    H.configure(n)
    p = f"ntruplus{n}_officialopt"
    inv, shoup = f"{p}_invntt_crep", f"{p}_basemul_shoup"
    stem = STEM[n]
    ht_cand = f"kem_lazy_r2fold_{stem}_keccak_ht" + ("_htinv" if n == 768 else "")
    base = dict(H.EXPECT[ht_cand])
    base.update({"poly_crepmod3": 1, "poly_basemul_scale": 1, inv: 0, shoup: 0})
    targets = list(H.TARGETS) + ["poly_crepmod3", "poly_basemul_scale", inv, shoup]
    old_inv = H.HTINV if n == 768 else "poly_invntt_scale"
    if base[old_inv] != 1 or base["poly_basemul"] != 2:
        raise ValueError("unexpected current-best bindings")

    def variant(invd, sh):
        e = dict(base)
        if invd:
            e.update({old_inv: 0, "poly_crepmod3": 0, inv: 1})
        if sh:
            e.update({"poly_basemul": 0, shoup: 2})
        return e
    exp = {f"kem_lazy_r2fold_invcrep_shoup_{stem}_keccak_ht": variant(True, True),
           f"kem_lazy_r2fold_invcrep_{stem}_keccak_ht": variant(True, False),
           f"kem_lazy_r2fold_shoup_{stem}_keccak_ht" + ("_htinv" if n == 768 else ""): variant(False, True)}
    hashes = [f"ntruplus{n}_keccak_hash_{x}" for x in "fgh"]
    return targets, exp, hashes, inv, shoup


def audit_shoup(nm, rows, name, asm, build):
    start, size = H.symbol(nm, name)
    if start % 32 or not size:
        raise ValueError(f"{name}: not 32-byte aligned or unsized")
    body = [r for r in function_rows(rows, start, start + size) if r[1] not in PAD]
    ops = Counter(r[1] for r in body)
    if set(ops) - SHOUP_OPS:
        raise ValueError(f"{name}: unexpected opcodes {sorted(set(ops) - SHOUP_OPS)}")
    if ops["ret"] != 1 or ops["vzeroupper"] != 1 or ops["jne"] != 1 or any(o.startswith("call") for o in ops):
        raise ValueError(f"{name}: ret/vzeroupper/branch/call counts {dict(ops)}")
    if [r[1] for r in body[-3:]] != ["vzeroupper", "leave", "ret"]:
        raise ValueError(f"{name}: epilogue {body[-3:]}")
    frame, stack_mem = [], []
    for addr, op, operands in body:
        mem = re.findall(r"(-?0x[0-9a-f]+|-?\d+)?\((%\w+)(?:,(%\w+)(?:,\d)?)?\)", operands)
        for disp, basereg, index in mem:
            if index:
                raise ValueError(f"{name}: index-register memory operand {operands}")
            if basereg in ("%rsp", "%rbp"):
                stack_mem.append((op, operands))
        if op in ("push", "leave") or (op in ("mov", "and", "sub") and ("%rsp" in operands or "%rbp" in operands)
                                       and not mem):
            frame.append((op, operands))
        if op in ("mov", "add", "sub", "cmp", "and") and mem:
            raise ValueError(f"{name}: scalar memory access {op} {operands}")
    want_frame = {("push", "%rbp"), ("mov", "%rsp,%rbp"), ("and", "$0xffffffffffffffe0,%rsp"), ("leave", "")}
    if not want_frame <= set(frame) or any(f not in want_frame and not (f[0] == "sub" and
                                                                        re.fullmatch(r"\$0x[0-9a-f]+,%rsp", f[1]))
                                           for f in frame):
        raise ValueError(f"{name}: unexpected frame {frame}")
    if any("%rbp" in o for _, o in stack_mem):
        raise ValueError(f"{name}: %rbp-relative data access")
    jne = [r for r in body if r[1] == "jne"][0]
    target = int(jne[2].split()[0], 16)
    if not (start <= target < jne[0]):
        raise ValueError(f"{name}: branch target outside the loop")
    obj = build / f"{name}.alone.o"
    subprocess.run(["cc", "-c", "-o", str(obj), str(asm)], check=True)
    onm = run("nm", "-S", str(obj))
    ostart, osize = H.symbol(onm, name)
    ob = function_rows(disasm_rows(obj), ostart, ostart + osize)
    ln, on = normalise(function_rows(rows, start, start + size)), normalise(ob)
    strip = [(op, v if op.startswith("j") else (v[0],)) for op, v in ln]
    ostrip = [(op, v if op.startswith("j") else (v[0],)) for op, v in on]
    if strip != ostrip:
        raise ValueError(f"{name}: linked stream differs from the assembled source")
    rip = sorted({v[1] for op, v in ln if not op.startswith("j") and v[1]})
    if rip != [f"{name}_zt"]:
        raise ValueError(f"{name}: rip symbols {rip}")
    return {"address_mod_32": start % 32, "size_bytes": size, "instruction_rows": sum(ops.values()),
            "opcode_counts": dict(sorted(ops.items())), "linked_stream_equals_assembled_source": True,
            "rip_symbols": rip, "calls": 0, "vzeroupper": 1, "conditional_branches": 1,
            "loop_back_edge_only": True, "index_register_operands": 0,
            "frame": sorted({f"{a} {b}".strip() for a, b in frame}),
            "stack_memory_operands": len(stack_mem),
            "stack_memory_operand_forms": sorted({o for _, o in stack_mem})}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--flat-root", type=Path)
    ap.add_argument("--flat-kem-obj", type=Path)
    ap.add_argument("--flat-candidate", help="variant whose bindings the flat kem.c must have")
    ap.add_argument("--flat-no-invcrep", action="store_true",
                    help="the flat export has no invntt_crep.s (NTRU+768 without the fused inverse)")
    ap.add_argument("--phase-a-obj", action="append", default=[], metavar="FLAT=PHASEA")
    args = ap.parse_args()
    n = args.param
    root = args.experiment.resolve()
    targets, exp, hashes, inv, shoup = expectations(n)
    flat = args.flat_root.resolve() if args.flat_root else None
    if (flat is None) != (args.flat_kem_obj is None) or (flat is not None) != (args.flat_candidate is not None):
        ap.error("--flat-root, --flat-kem-obj and --flat-candidate go together")
    has_inv = not (flat and args.flat_no_invcrep)
    src = {shoup: (flat / "basemul_shoup.s") if flat else root / f"asm/{shoup}.s"}
    if has_inv:
        src[inv] = (flat / "invntt_crep.s") if flat else root / f"asm/{inv}.s"
    nm = run("nm", "-S", str(args.elf))
    rows = disasm_rows(args.elf)
    entries = {}
    with tempfile.TemporaryDirectory() as tmp:
        if has_inv:
            entries[inv] = H.audit_entry(nm, rows, inv, src[inv], Path(tmp))
        entries[shoup] = audit_shoup(nm, rows, shoup, src[shoup], Path(tmp))
    if has_inv:
        p = f"ntruplus{n}_officialopt_invcrep"
        want = {"_16xq", "_16xv", "_16xw", "_16xwqinv", "zetas_inv", "_16xNinv_scale", "_16xNinv_scaleqinv",
                f"{p}_l1sigma", f"{p}_16x4853", f"{p}_16x128", f"{p}_16xinv3", f"{p}_16xm1"}
        if n == 768:
            want.add(f"{p}_zetas_b")
        if set(entries[inv]["rip_symbols"]) != want:
            raise ValueError(f"invntt_crep rip symbols {entries[inv]['rip_symbols']}")
        for t in sorted(want):
            if t.startswith(p):
                addr, _ = H.symbol(nm, t, sized=False)
                if addr % 32:
                    raise ValueError(f"{t} not 32-byte aligned")
    zt, _ = H.symbol(nm, f"{shoup}_zt", sized=False)
    if zt % 32:
        raise ValueError("Shoup zeta table not 32-byte aligned")
    relocs = {}
    if flat:
        fe = {**exp[args.flat_candidate], **{h: 0 for h in hashes}, "hash_f": 2, "hash_g": 2, "hash_h": 2}
        objects = {"flat kem.c": (args.flat_kem_obj, fe)}
    else:
        objects = {v: (root / f"build/{v}.o", e) for v, e in exp.items()}
    for v, (obj, e) in objects.items():
        got = {t: relocs_to(obj, t) for t in targets}
        if got != e:
            raise ValueError(f"{v}: call relocations {got} != {e}")
        relocs[v] = {k: c for k, c in got.items() if c}
    equivalence = {}
    for pair in args.phase_a_obj:
        f, pa = (Path(x) for x in pair.split("=", 1))
        equivalence[f.name] = H.compare_objects(f, pa, {h: f"hash_{x}" for h, x in zip(hashes, "fgh")})
    elf = args.elf.resolve()
    out = {"class": "linked ELF audit (Phase A, correctness only; no timing)" if not flat else
                    "linked ELF audit of the SUPERCOP-flat qualification export (Phase B, correctness only)",
           "parameter": f"NTRU+{n}",
           "elf": str(elf.relative_to(root) if elf.is_relative_to(root) else elf), "elf_sha256": H.sha(elf),
           "asm_sha256": {k: H.sha(v) for k, v in src.items()},
           "compiler": run("cc", "--version").splitlines()[0],
           "entries": entries, "kem_call_relocations": relocs,
           "shoup_stack_note": "gcc spills (fixed %rsp offsets, red zone / realigned frame): see the generator's "
                               "stack_slot_contents; data slots hold secret-derived intermediates and are not "
                               "cleared, as with compiler spills in the C KEM code"}
    if flat:
        out["flat_root"] = str(flat.relative_to(root) if flat.is_relative_to(root) else flat)
        out["flat_candidate"] = args.flat_candidate
        out["phase_a_object_equivalence"] = equivalence
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"entries": {k: {x: v[x] for x in ("size_bytes", "instruction_rows")} for k, v in entries.items()},
                      "kem_call_relocations": relocs}, indent=1))


if __name__ == "__main__":
    main()
