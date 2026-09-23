#!/usr/bin/env python3
"""Constant-time review of the mlkem-native-Keccak NTRU+ hash path (768/864/1152).

Two complementary checks on the release-flag objects (build/mlk_fips202.o,
build/mlk_keccakf1600.o, build/symmetric_keccak.o):

1. Static (objdump of the linked candidate KEM ELF): for every function of
   the new hash path -- ntruplus{N}_keccak_hash_{f,g,h}, mlk shake256,
   absorb_once, keccakf1600_{permute,xor_bytes,extract_bytes},
   mlk_keccakf1600_permute_c -- list every conditional branch with the
   instruction that set its flags, every cmov/setcc, every
   division / variable-latency candidate (div, idiv, bsf, bsr, tzcnt, lzcnt,
   popcnt are listed) and every memory operand that uses an index register.
   Each branch is classified by hand in docs (loop counters and the public
   lengths inlen/outlen/offset/length, and the stack-protector check).

2. Dynamic (tests/ct_trace.c, ptrace single-step): the same code linked into
   a tracer runs each target -- SHAKE256 32->N/4 (keypair), 1+POLYBYTES->N/4,
   hash_f, hash_g, hash_h, one x1 permutation -- on --trials secret inputs
   (all-zero, all-0xff, pseudo-random) with fixed public lengths/pointers
   (linked -no-pie -z now, one untraced warm-up call: no lazy PLT binding).
   For every executed instruction the tracer records rip and the effective
   address of its explicit memory operand (table derived here from objdump;
   glibc memcpy / explicit_bzero record rip only).  Gate: per target all
   traces byte-identical (same instruction sequence, same addresses); a
   negative control (secret-indexed table lookup) must produce differing
   traces, showing the address check is live.

This is evidence for the compiled code on this toolchain, not a proof.
mlkem-native's own claim (README/SOUNDNESS.md at the pinned commit): C code
is CBMC-proved memory/type safe; constant-time for C is NOT formally proved,
it is tested with valgrind across compilers/flags; only its assembly is
HOL-Light proved constant-time (the x1 path here has no assembly).
"""

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

REGS = ["r15", "r14", "r13", "r12", "rbp", "rbx", "r11", "r10", "r9", "r8", "rax", "rcx", "rdx",
        "rsi", "rdi", "orig_rax", "rip", "cs", "eflags", "rsp", "ss", "fs_base", "gs_base"]
ALIAS = {"eax": "rax", "ebx": "rbx", "ecx": "rcx", "edx": "rdx", "esi": "rsi", "edi": "rdi",
         "ebp": "rbp", "esp": "rsp", **{f"r{i}d": f"r{i}" for i in range(8, 16)}}
MEM = re.compile(r"(?:(%[a-z]s):)?(-?0x[0-9a-f]+|-?\d+)?\((%[a-z0-9]+)?(?:,(%[a-z0-9]+)(?:,([1248]))?)?\)")
FLAG_SETTERS = ("cmp", "test", "sub", "add", "dec", "inc", "and", "or", "xor", "neg", "sbb", "adc", "bt",
                "shl", "shr", "sar", "vptest")
VARLAT = ("div", "idiv", "bsf", "bsr", "tzcnt", "lzcnt", "popcnt")
MLK = "ntruplus_mlkfips202_"


def run(*args, **kw):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True, **kw).stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def disassemble(elf):
    """{function name: [(addr, mnemonic, operands)]} of an ELF."""
    funcs, cur = {}, None
    for line in run("objdump", "-d", "--no-show-raw-insn", "-M", "att", elf).splitlines():
        head = re.match(r"^([0-9a-f]+) <([^>]+)>:$", line)
        if head:
            cur = funcs.setdefault(head[2], [])
            continue
        m = re.match(r"^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$", line)
        if m and cur is not None:
            op, operands = m[2], m[3]
            if op in ("rep", "repz", "repnz", "bnd", "notrack", "lock", "data16", "cs") and operands:
                op2, _, rest = operands.partition(" ")
                op, operands = f"{op} {op2}", rest
            cur.append((int(m[1], 16), op, operands.split("#")[0].strip()))
    return funcs


def reg_id(name):
    if name is None:
        return -1
    name = ALIAS.get(name[1:], name[1:])
    return REGS.index(name)


def table(funcs):
    rows = []
    for insns in funcs.values():
        for addr, op, operands in insns:
            base_op = op.split()[-1]
            if base_op.startswith(("lea", "nop")) or base_op in ("endbr64",):
                continue
            m = MEM.search(operands)
            if not m:
                continue
            seg, disp, base, index, scale = m.groups()
            if base == "%rip" or seg in ("%fs", "%gs"):
                continue
            rows.append((addr, reg_id(base), reg_id(index), int(scale or 1), int(disp or "0", 0)))
    return rows


def static_review(funcs, names):
    out = {}
    for name in names:
        insns = funcs[name]
        branches, cmovs, varlat, indexed = [], [], [], []
        for i, (addr, op, operands) in enumerate(insns):
            base = op.split()[-1]
            if base.startswith("j") and base != "jmp":
                setter = next(((a, o, x) for a, o, x in reversed(insns[max(0, i - 8):i])
                               if o.split()[-1].startswith(FLAG_SETTERS)), None)
                branches.append({"addr": hex(addr), "insn": f"{op} {operands}",
                                 "flags_from": f"{setter[1]} {setter[2]}" if setter else None})
            if base.startswith(("cmov", "set")):
                cmovs.append(f"{hex(addr)} {op} {operands}")
            if base.startswith(VARLAT):
                varlat.append(f"{hex(addr)} {op} {operands}")
            m = MEM.search(operands)
            if m and m.group(4) and not base.startswith(("lea", "nop")):
                indexed.append(f"{hex(addr)} {op} {operands}")
        out[name] = {"instructions": len(insns), "conditional_branches": branches, "cmov_setcc": cmovs,
                     "variable_latency_candidates": varlat, "indexed_memory_operands": indexed,
                     "calls": sorted({x for _, o, x in insns if o.split()[-1] in ("call", "jmp") and "<" in x
                                      and name not in x})}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True, help="linked candidate KEM test ELF (static review)")
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--trials", type=int, default=12)
    ap.add_argument("--cc", default="cc")
    ap.add_argument("--cflags", default="-O3 -mavx2 -march=native -mtune=native -fPIE -Wall -Wextra -Werror")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.experiment.resolve()
    n = args.param
    here = Path(__file__).resolve()
    common = here.parents[1]
    build = args.build.resolve()
    traces = build / "traces"
    traces.mkdir(parents=True, exist_ok=True)
    for old in traces.glob("*.trace"):
        old.unlink()
    objs = [root / "build/mlk_fips202.o", root / "build/mlk_keccakf1600.o", root / "build/symmetric_keccak.o"]
    tracer = build / "ct_trace"
    run(args.cc, *args.cflags.split(), "-no-pie", "-Wl,-z,now", f"-I{root / 'upstream/supercop-avx2'}", "-o", tracer,
        common / "tests/ct_trace.c", *objs)
    funcs = disassemble(tracer)
    rows = table(funcs)
    (build / "ea-table.txt").write_text("".join(f"{a:x} {b} {i} {s} {d}\n" for a, b, i, s, d in rows))
    log = run(tracer, build / "ea-table.txt", traces, args.trials)
    (build / "ct_trace.log").write_text(log)
    text_lo = min(a for insns in funcs.values() for a, _, _ in insns)
    text_hi = max(a for insns in funcs.values() for a, _, _ in insns)
    dynamic, ok = {}, True
    for target in ("shake_keypair", "shake_hash_g_shape", "hash_f", "hash_g", "hash_h", "permute",
                   "negative_control"):
        files = [traces / f"{target}-{k}.trace" for k in range(args.trials)]
        blobs = [f.read_bytes() for f in files]
        recs = [(int.from_bytes(blobs[0][i:i + 8], "little"), int.from_bytes(blobs[0][i + 8:i + 16], "little"))
                for i in range(0, len(blobs[0]), 16)]
        in_elf = [r for r in recs if text_lo <= r[0] <= text_hi]
        identical = all(b == blobs[0] for b in blobs)
        first_diff = None
        if not identical:
            for k, b in enumerate(blobs):
                if b != blobs[0]:
                    pos = next((i for i in range(0, min(len(b), len(blobs[0])), 16) if b[i:i + 16] != blobs[0][i:i + 16]),
                               min(len(b), len(blobs[0])))
                    first_diff = {"trial": k, "step": pos // 16, "len": [len(blobs[0]) // 16, len(b) // 16]}
                    break
        dynamic[target] = {"trials": args.trials, "steps": len(recs), "identical_rip_and_address_traces": identical,
                           "steps_in_elf": len(in_elf), "steps_in_libc_rip_only": len(recs) - len(in_elf),
                           "memory_operand_addresses_checked": sum(1 for r in in_elf if r[1]),
                           "unique_rips": len({r[0] for r in recs}),
                           "trace_sha256": hashlib.sha256(blobs[0]).hexdigest(), "first_difference": first_diff}
        ok &= identical if target != "negative_control" else not identical
    names = [f"ntruplus{n}_keccak_hash_{x}" for x in "fgh"] + [
        MLK + "shake256", MLK + "keccakf1600_permute", MLK + "keccakf1600_xor_bytes",
        MLK + "keccakf1600_extract_bytes", "mlk_keccakf1600_permute_c"]
    elf_funcs = disassemble(args.elf)
    names += sorted(f for f in elf_funcs if f.startswith("mlk_keccak_absorb_once"))
    review = static_review(elf_funcs, names)
    total = Counter()
    for r in review.values():
        total["conditional_branches"] += len(r["conditional_branches"])
        total["cmov_setcc"] += len(r["cmov_setcc"])
        total["variable_latency_candidates"] += len(r["variable_latency_candidates"])
    perm = review["mlk_keccakf1600_permute_c"]
    static_ok = total["variable_latency_candidates"] == 0 and len(perm["conditional_branches"]) == 1 \
        and not perm["indexed_memory_operands"]
    summary = {
        "class": "Phase-A constant-time review (no timing)", "parameter": f"NTRU+{n}", "pass": bool(ok and static_ok),
        "dynamic": {"method": "ptrace single-step; per executed instruction (rip, explicit memory operand "
                              "effective address); traces compared byte-for-byte across secret inputs",
                    "tracer_sha256": sha(tracer), "objects_sha256": {o.name: sha(o) for o in objs},
                    "ea_table_rows": len(rows), "targets": dynamic, "pass": bool(ok)},
        "static": {"elf": str(args.elf), "elf_sha256": sha(args.elf), "totals": dict(total),
                   "permute_c_single_loop_branch_no_indexed_access": bool(static_ok), "functions": review},
        "mlkem_native_claims": {
            "source": "mlkem-native b3ba7b32 README.md 'Formal Verification'/'Security', SOUNDNESS.md A2",
            "c_code": "CBMC-proved memory safety and type safety (no overflow); constant-time NOT formally "
                      "proved for C, tested empirically with valgrind across compilers/options; value barriers "
                      "against compiler-introduced leaks",
            "assembly": "HOL-Light proved constant-time; not used here (x1 path is pure C)"},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"pass": summary["pass"], "totals": dict(total),
                      "dynamic": {t: [d["steps"], d["identical_rip_and_address_traces"],
                                      d["memory_operand_addresses_checked"]] for t, d in dynamic.items()}}, indent=1))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
