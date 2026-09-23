#!/usr/bin/env python3
"""Derive the 2-op-freeze poly_tobytes from pinned Official pack.s (768/1152).

Official NTRU+768 / NTRU+1152 AVX2 poly_tobytes (pack.s:1-144) freezes every
coefficient register X (8 per iteration) with the Barrett reduction

    vpmulhrsw _16xv, X, T;  vpmullw _16xq, T, T;  vpsubw T, X, X

followed by the 3-op conditional add of q

    vpsraw $15, X, T;  vpand _16xq, T, T;  vpaddw T, X, X

The only change is that every 3-op add of q is replaced by the 2-op
canonicalisation (proof: tools/prove_freeze_2op.py, tests/test_freeze_2op.c)

    vpaddw _16xq, X, T;  vpminuw T, X, X

in the same register allocation and the same grouping (4 vpaddw then 4
vpminuw where Official has 4 vpsraw, 4 vpand, 4 vpaddw).  Every other line of
the pinned function (loads, Barrett, packing, stores, loop control) is kept in
order; the entry and its loop label are namespaced and the entry gets
.p2align 5 / .type / .size.  poly_frombytes and the rest of pack.s are not
copied (the Official ones stay linked).

The generator also writes two KEM overlays (preprocessor rebinding of every
poly_tobytes call; kem.c has 7: 3 in keypair, 2 in enc, 2 in dec, and none
of poly.c / poly.h's other helpers call it):
  src/kem_lazy_freeze2op.c  candidate  = src/kem_lazy.c (lazy Forward) + 2-op tobytes
  src/kem_freeze2op.c       control    = Official kem.c + 2-op tobytes

Gates enforced here: pinned pack.s / kem.c sha256; exactly 8 sites per loop
iteration, each the exact 3-op sequence on the _16xq register, each on a
register that a Barrett vpsubw produced and that is not touched in between;
the temporary T of every site is dead afterwards (next access is a pure
write before the loop branch); a line diff old -> new consisting only of
24 removed 3-op lines and 16 added 2-op lines; deterministic regeneration.

  generate_tobytes_freeze2op.py --param 768 --experiment .           # write
  generate_tobytes_freeze2op.py --param 768 --experiment . --check   # verify
"""

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

# sha256 of the imported (never edited) SUPERCOP 20260831 crypto_kem/ntruplus{N}/avx2 files
PARAMS = {
    768: {"pack_sha256": "dd1d2b9690de0780d68cd6ab0902190c559b1e661aca9735312eaeb845a1a3c6",
          "kem_sha256": "368bb8f799566cf199960ffdc80e33acce0da5cfe141fffa248a21f221ae7f3f",
          "iterations": 6},
    1152: {"pack_sha256": "406e0d9cff4af069d8b8cc3cb028d11898a61f86d86cece9280fa81dafb11732",
           "kem_sha256": "368bb8f799566cf199960ffdc80e33acce0da5cfe141fffa248a21f221ae7f3f",
           "iterations": 9},
}
SITES = 8
TOBYTES_CALLS = 7   # kem.c poly_tobytes call sites (keypair 3, enc 2, dec 2)
STRIDE_IN = 256     # coefficient bytes consumed per iteration


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def name_for(n: int) -> str:
    return f"ntruplus{n}_officialopt_tobytes_freeze2op"


def parse(line):
    """(opcode, [operands]) of an instruction line, else None."""
    code = line.split("#")[0].strip()
    m = re.fullmatch(r"([a-z][a-z0-9]*)\s+(.*)", code)
    if not m:
        return None
    return m[1], [o.strip() for o in m[2].split(",")]


def extract_official(n: int, upstream: Path) -> list:
    raw = (upstream / "pack.s").read_bytes()
    if sha256(raw) != PARAMS[n]["pack_sha256"]:
        raise ValueError("pinned Official pack.s changed")
    lines = raw.decode().split("\n")
    if lines[:2] != [".global poly_tobytes", "poly_tobytes:"]:
        raise ValueError("unexpected Official poly_tobytes entry")
    end = lines.index("ret")
    if lines[end + 1:end + 4] != ["", ".global poly_frombytes", "poly_frombytes:"]:
        raise ValueError("poly_tobytes is not followed by poly_frombytes")
    return lines[:end + 1]


def find_sites(body):
    """Indices (i_sraw, i_and, i_add, X, T) of every 3-op add of q."""
    ins = {i: parse(l) for i, l in enumerate(body) if parse(l)}
    consts = {ops[0]: ops[1] for i, (op, ops) in ins.items()
              if op == "vmovdqa" and ops[0] in ("_16xv(%rip)", "_16xq(%rip)")}
    q, v = consts.get("_16xq(%rip)"), consts.get("_16xv(%rip)")
    if q is None or v is None:
        raise ValueError("_16xq/_16xv not loaded")
    for i, (op, ops) in ins.items():   # constant registers are never redefined
        if ops[-1] in (q, v) and not (op == "vmovdqa" and ops[0] in consts):
            raise ValueError(f"constant register redefined at line {i + 1}")
    order = sorted(ins)
    sites = []
    for k, i in enumerate(order):
        op, ops = ins[i]
        if op != "vpsraw":
            continue
        if ops[0] != "$15" or len(ops) != 3:
            raise ValueError(f"line {i + 1}: unexpected vpsraw")
        x, t = ops[1], ops[2]
        rest = order[k + 1:]
        a = next(j for j in rest if t in ins[j][1])
        if ins[a] != ("vpand", [q, t, t]):
            raise ValueError(f"line {a + 1}: next use of {t} is not vpand q")
        b = next(j for j in rest if j > a and t in ins[j][1])
        if ins[b] != ("vpaddw", [t, x, x]):
            raise ValueError(f"line {b + 1}: next use of {t} is not vpaddw into {x}")
        # X untouched between the Barrett vpsubw that produced it and the add
        prev = [j for j in order if j < i and x == ins[j][1][-1]]
        if not prev or ins[prev[-1]][0] != "vpsubw" or ins[prev[-1]][1][1:] != [x, x]:
            raise ValueError(f"line {i + 1}: {x} not produced by a Barrett vpsubw")
        tq = ins[prev[-1]][1][0]
        mul = [j for j in order if j < prev[-1] and ins[j][1][-1] == tq]
        if not mul or ins[mul[-1]] != ("vpmullw", [q, tq, tq]):
            raise ValueError(f"line {prev[-1] + 1}: Barrett vpsubw not by q*quotient")
        rs = [j for j in order if j < mul[-1] and ins[j][1][-1] == tq]
        if not rs or ins[rs[-1]] != ("vpmulhrsw", [v, x, tq]):
            raise ValueError(f"line {mul[-1] + 1}: Barrett quotient not vpmulhrsw(_16xv, {x})")
        if any(x in ins[j][1] for j in order if prev[-1] < j < i):
            raise ValueError(f"{x} touched between Barrett and add of q")
        if any(ins[j][1][-1] == x for j in order if i <= j < b):
            raise ValueError(f"{x} redefined inside the add of q")
        sites.append((i, a, b, x, t))
    return sites, ins, q


def check_dead(t, after, body, ins):
    """T must be written (not read) by its next access before the loop branch."""
    for j in range(after + 1, len(body)):
        if j not in ins:
            continue
        op, ops = ins[j]
        if op.startswith("j"):
            break
        if t in ops[:-1]:
            raise ValueError(f"temporary {t} read at line {j + 1} after the freeze")
        if ops[-1] == t:
            return j
    raise ValueError(f"temporary {t} not overwritten before the loop branch")


def generate_asm(n: int, upstream: Path):
    body = extract_official(n, upstream)
    name = name_for(n)
    loop = "_looptop_poly_tobytes"
    if sum(loop in l for l in body) != 2 or f"{loop}:" not in body or f"jb  {loop}" not in body:
        raise ValueError("unexpected Official loop label use")
    bound = [l for l in body if re.fullmatch(r"lea \d+\(%rsi\), %r8", l)]
    if bound != [f"lea {2 * n}(%rsi), %r8"] or f"add ${STRIDE_IN}, %rsi" not in body \
            or 2 * n // STRIDE_IN != PARAMS[n]["iterations"] or (2 * n) % STRIDE_IN:
        raise ValueError("loop bound / stride / trip count changed")
    sites, ins, q = find_sites(body)
    if len(sites) != SITES:
        raise ValueError(f"{len(sites)} freeze sites, expected {SITES}")
    if len({s[3] for s in sites}) != SITES:
        raise ValueError("freeze sites do not cover 8 distinct coefficient registers")
    dead = {s[4]: check_dead(s[4], s[2], body, ins) for s in sites}
    # Replacement, per group of consecutive sites: the vpsraw lines become the
    # vpaddw q lines and the vpaddw lines become the vpminuw lines; the vpand
    # lines are dropped.  Operand spacing follows the Official vpaddw lines.
    new = list(body)
    removed, added = [], []
    for i, a, b, x, t in sites:
        removed += [body[i], body[a], body[b]]
        new[i] = f"vpaddw {q}, {x}, {t}"
        new[b] = f"vpminuw {t}, {x}, {x}"
        new[a] = None
        added += [new[i], new[b]]
    new = [l for l in new if l is not None]
    # structural diff gate: only the 24 -> 16 replacement
    sm = difflib.SequenceMatcher(a=body, b=new, autojunk=False)
    old_changed, new_changed = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            old_changed += body[i1:i2]
            new_changed += new[j1:j2]
    if sorted(old_changed) != sorted(removed) or sorted(new_changed) != sorted(added) \
            or len(removed) != 3 * SITES or len(added) != 2 * SITES:
        raise ValueError("diff is not exactly the 8 x 3 -> 8 x 2 freeze replacement")
    kept_old = [l for k, l in enumerate(body) if k not in {s for site in sites for s in site[:3]}]
    kept_new = [l for l in new if l not in added]
    if kept_old != kept_new:
        raise ValueError("non-freeze lines changed or reordered")
    # namespacing (after the diff gate so that the gate sees Official text)
    if new[:2] != [".global poly_tobytes", "poly_tobytes:"]:
        raise ValueError("entry lost")
    lab = f"{name}_looptop"
    out = [f"# GENERATED by common/official_opt_lazy/tools/generate_tobytes_freeze2op.py -- do not edit.",
           f"# Official NTRU+{n} AVX2 poly_tobytes (upstream/supercop-avx2/pack.s sha256",
           f"# {PARAMS[n]['pack_sha256']}) with each of its 8 per-iteration",
           "# `vpsraw $15; vpand q; vpaddw` add-of-q sequences replaced by `vpaddw q; vpminuw`.",
           ".text", ".p2align 5", f".global {name}", f".type {name},@function", f"{name}:"]
    for l in new[2:]:
        out.append(l.replace(loop, lab))
    out += [f".size {name},.-{name}", "",
            ".ifndef no_gnu_stack", '.section .note.GNU-stack,"",@progbits', ".endif", ""]
    meta = {"sites_per_iteration": SITES, "iterations": PARAMS[n]["iterations"],
            "removed_per_iteration": {"vpsraw": 8, "vpand": 8, "vpaddw": 8},
            "added_per_iteration": {"vpaddw": 8, "vpminuw": 8},
            "net_instructions_saved_per_call": SITES * PARAMS[n]["iterations"],
            "official_site_lines": [[i + 1, a + 1, b + 1] for i, a, b, _, _ in sites],
            "temporaries_next_written_at_line": {t: j + 1 for t, j in sorted(dead.items())}}
    return "\n".join(out), meta


def generate_kems(n: int, upstream: Path) -> dict:
    kem = (upstream / "kem.c").read_bytes()
    if sha256(kem) != PARAMS[n]["kem_sha256"]:
        raise ValueError("pinned Official kem.c changed")
    text = kem.decode()
    if text.count("poly_tobytes(") != TOBYTES_CALLS:
        raise ValueError("Official KEM tobytes call graph changed")
    for f in ("poly.c", "symmetric.c", "fips202.c", "consts.c"):
        if "poly_tobytes" in (upstream / f).read_text():
            raise ValueError(f"{f} calls poly_tobytes; overlay would miss it")
    name = name_for(n)
    head = ("/*\n * GENERATED by common/official_opt_lazy/tools/generate_tobytes_freeze2op.py"
            " -- do not edit.\n")
    lazy = (head + f" * NTRU+{n} AVX2 candidate avx2-officialopt-lazy-freeze-{n}-exp001: the caller-lazy\n"
            " * KEM (generated src/kem_lazy.c, 6 poly_ntt call sites -> lazy Forward) with all\n"
            f" * {TOBYTES_CALLS} poly_tobytes calls bound to asm/{name}.s.\n"
            " * Preprocessor overlay; kem_lazy.c is unchanged, so the lazy-only candidate\n"
            " * stays intact and both can be linked into one ELF.\n */\n"
            f"#define poly_tobytes {name}\n#include \"kem_lazy.c\"\n")
    ctrl = (head + f" * NTRU+{n} AVX2 freeze-only control: the pinned Official kem.c (Official\n"
            f" * Forward) with all {TOBYTES_CALLS} poly_tobytes calls bound to asm/{name}.s.\n"
            " * Diagnostic only.\n */\n"
            f"#define poly_tobytes {name}\n#include \"../upstream/supercop-avx2/kem.c\"\n")
    return {"src/kem_lazy_freeze2op.c": lazy, "src/kem_freeze2op.c": ctrl}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=sorted(PARAMS), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true",
                    help="verify committed outputs equal regeneration; write nothing")
    ap.add_argument("--meta", type=Path, help="write the generation record (JSON) here")
    args = ap.parse_args()
    root = args.experiment.resolve()
    upstream = root / "upstream/supercop-avx2"
    asm, meta = generate_asm(args.param, upstream)
    kems = generate_kems(args.param, upstream)
    if (asm, meta) != generate_asm(args.param, upstream) or kems != generate_kems(args.param, upstream):
        raise ValueError("non-deterministic generation")
    outputs = {root / f"asm/{name_for(args.param)}.s": asm}
    outputs.update({root / k: v for k, v in kems.items()})
    meta["outputs_sha256"] = {str(p.relative_to(root)): sha256(t.encode()) for p, t in outputs.items()}
    meta["pack_s_sha256"] = PARAMS[args.param]["pack_sha256"]
    meta["generator_sha256"] = sha256(Path(__file__).read_bytes())
    if args.check:
        bad = [str(p) for p, t in outputs.items() if not p.exists() or p.read_text() != t]
        if bad:
            print("MISMATCH vs regeneration: " + ", ".join(bad), file=sys.stderr)
            return 1
        verb = "ok"
    else:
        for p, t in outputs.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(t)
        verb = "wrote"
    for p, t in outputs.items():
        print(f"{verb} {p.relative_to(root)} sha256={sha256(t.encode())}")
    print("freeze replacement: " + json.dumps({k: meta[k] for k in (
        "sites_per_iteration", "iterations", "net_instructions_saved_per_call", "official_site_lines")}))
    if args.meta:
        args.meta.parent.mkdir(parents=True, exist_ok=True)
        args.meta.write_text(json.dumps(meta, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
