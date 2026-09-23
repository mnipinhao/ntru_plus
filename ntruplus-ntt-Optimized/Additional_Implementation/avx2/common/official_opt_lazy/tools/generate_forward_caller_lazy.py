#!/usr/bin/env python3
"""Derive a caller-bounded Forward entry from pinned Official ntt.s (864/1152).

Port of NTRU+768 avx2_official_opt_001/tools/generate_forward_caller_lazy.py.
The only arithmetic deletion is the single terminal Barrett block
(`#reduce2` ... `#store`) and its `_16xv` constant load.  Every other
instruction of the pinned Official poly_ntt is kept in order.  This is not a
replacement for the general-input poly_ntt entry, which stays linked.

Usage (from the experiment directory, normally via `make generate`):
  generate_forward_caller_lazy.py --param 864 --experiment .           # write
  generate_forward_caller_lazy.py --param 864 --experiment . --check   # verify
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

# Per-parameter pins.  Hashes are of the imported (never edited) upstream copy
# of SUPERCOP 20260831 crypto_kem/ntruplus{N}/avx2.
PARAMS = {
    864: {
        "ntt_sha256": "980cad5ef69a78f9ed1f2f45fc5dcaa0a04cc07693cf65ea108acc41c547db92",
        "kem_sha256": "368bb8f799566cf199960ffdc80e33acce0da5cfe141fffa248a21f221ae7f3f",
        # registers per iteration in the terminal block, loop stride (bytes)
        "regs": 6, "stride": 192,
    },
    1152: {
        "ntt_sha256": "23c851702f9ca399945c71ee90d6f26d0e6ebf6c602f4d1a7e09c4761bf1ede5",
        "kem_sha256": "368bb8f799566cf199960ffdc80e33acce0da5cfe141fffa248a21f221ae7f3f",
        "regs": 8, "stride": 256,
    },
}
ITERATIONS = 9  # terminal loop trip count for both parameters (asserted below)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def name_for(n: int) -> str:
    return f"ntruplus{n}_officialopt_ntt_caller_lazy"


def generate_asm(n: int, upstream: Path):
    p = PARAMS[n]
    name = name_for(n)
    source = (upstream / "ntt.s").read_bytes()
    if sha256(source) != p["ntt_sha256"]:
        raise ValueError("pinned Official ntt.s changed")
    body = source.decode()
    entry = ".global poly_ntt\npoly_ntt:"
    if body.count(entry) != 1 or body.count("poly_ntt") != 2:
        raise ValueError("unexpected Official entry")
    body = body.replace(entry, f".text\n.p2align 5\n.global {name}\n"
                        f".type {name},@function\n{name}:", 1)
    labels = set(re.findall(r"\b(_looptop_[A-Za-z0-9_]+):", body))
    if labels != {"_looptop_j_0", "_looptop_start_1", "_looptop_j_1",
                  "_looptop_start_2", "_looptop_j_2", "_looptop_start_3456"}:
        raise ValueError(f"unexpected Official local labels {sorted(labels)}")
    body = re.sub(r"\b(_looptop_[A-Za-z0-9_]+)\b",
                  rf"ntruplus{n}_officialopt_lazy\1", body)
    load_v = "vmovdqa _16xv(%rip), %ymm1\n"
    if body.count(load_v) != 1 or body.count("_16xv") != 1:
        raise ValueError("unexpected terminal Barrett constant load")
    body = body.replace(load_v, "", 1)
    if body.count("#reduce2\n") != 1:
        raise ValueError("unexpected terminal block multiplicity")
    start, end = body.split("#reduce2\n", 1)
    if end.count("#store\n") != 1:
        raise ValueError("unexpected terminal store multiplicity")
    reduction, suffix = end.split("#store\n", 1)
    lines = [line.strip() for line in reduction.splitlines() if line.strip()]
    if any(line.startswith("#") or line.endswith(":") for line in lines):
        raise ValueError("comment or label inside terminal Barrett block")
    parsed = [re.fullmatch(r"(\w+)\s+(%ymm\d+),\s*(%ymm\d+),\s*(%ymm\d+)", line)
              for line in lines]
    if not all(parsed):
        raise ValueError("unexpected operand form in terminal Barrett block")
    opcodes = [m[1] for m in parsed]
    regs = p["regs"]
    counts = {op: opcodes.count(op) for op in sorted(set(opcodes))}
    if counts != {"vpmulhrsw": regs, "vpmullw": regs, "vpsubw": regs}:
        raise ValueError(f"unexpected terminal Barrett operation count {counts}")
    # Structural check: every vpsubw subtracts a vpmullw(q, vpmulhrsw(v, x))
    # of the same x back into x, i.e. x -= q*round(x*v/2^15) exactly.
    rs, ql = {}, {}
    reduced = []
    for op, src, a, dst in (m.groups()[:4] for m in parsed):
        if op == "vpmulhrsw":
            if src != "%ymm1":
                raise ValueError("vpmulhrsw not by the _16xv register")
            rs[dst] = a
        elif op == "vpmullw":
            if src != "%ymm0" or a not in rs:
                raise ValueError("vpmullw not q * Barrett quotient")
            ql[dst] = rs.pop(a)
        else:
            if src not in ql or ql[src] != a or dst != a:
                raise ValueError("vpsubw does not close a Barrett reduction")
            reduced.append(a)
            del ql[src]
    if len(set(reduced)) != regs or rs or ql:
        raise ValueError("terminal block does not reduce each register exactly once")
    if re.search(r"%ymm1(?!\d)", start + suffix):
        raise ValueError("%ymm1 (_16xv) used outside the removed block")
    # Terminal loop trip count: `lea 2N(%rdi), %r8` ... `add $stride, %rdi`.
    head = start.split(f"ntruplus{n}_officialopt_lazy_looptop_start_3456:")
    if len(head) != 2:
        raise ValueError("terminal loop label not found")
    bounds = re.findall(r"lea\s+(\d+)\(%rdi\),\s*%r8", head[0])
    if not bounds or int(bounds[-1]) != 2 * n:
        raise ValueError("terminal loop bound changed")
    if f"add ${p['stride']}, %rdi" not in suffix or 2 * n // p["stride"] != ITERATIONS:
        raise ValueError("terminal loop stride/trip count changed")
    stores = re.findall(r"vmovdqa %ymm(\d+),\s*\d*\(%rdi\)", suffix)
    if sorted(f"%ymm{r}" for r in stores) != sorted(reduced):
        raise ValueError("stored registers differ from reduced registers")
    body = start + "#store\n" + suffix
    marker = ".ifndef no_gnu_stack"
    if body.count(marker) != 1:
        raise ValueError("unexpected Official NTT footer")
    body = body.replace(marker, f".size {name},.-{name}\n\n{marker}", 1)
    meta = {"removed_per_iteration": counts, "iterations": ITERATIONS,
            "removed_vectors_per_forward": regs * ITERATIONS,
            "removed_constant_loads": 1}
    return body, meta


def generate_kem(n: int, upstream: Path) -> str:
    name = name_for(n)
    raw = (upstream / "kem.c").read_bytes()
    if sha256(raw) != PARAMS[n]["kem_sha256"]:
        raise ValueError("pinned Official kem.c changed")
    body = raw.decode()
    if body.count("poly_ntt(") != 6 or body.count("#ifdef SUPERCOP\n") != 1:
        raise ValueError("Official KEM Forward call graph changed")
    body = body.replace("poly_ntt(", name + "(")
    return body.replace("#ifdef SUPERCOP\n",
                        f"void {name}(poly *);\n\n#ifdef SUPERCOP\n", 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--param", type=int, choices=sorted(PARAMS), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true",
                    help="verify committed outputs equal regeneration; write nothing")
    args = ap.parse_args()
    root = args.experiment.resolve()
    upstream = root / "upstream/supercop-avx2"
    asm, meta = generate_asm(args.param, upstream)
    kem = generate_kem(args.param, upstream)
    # determinism: a second derivation must be byte-identical
    if (asm, meta) != generate_asm(args.param, upstream) or kem != generate_kem(args.param, upstream):
        raise ValueError("non-deterministic generation")
    outputs = {root / f"asm/{name_for(args.param)}.s": asm, root / "src/kem_lazy.c": kem}
    if args.check:
        bad = [str(path) for path, text in outputs.items()
               if not path.exists() or path.read_text() != text]
        if bad:
            print("MISMATCH vs regeneration: " + ", ".join(bad), file=sys.stderr)
            return 1
        for path, text in outputs.items():
            print(f"ok {path.relative_to(root)} sha256={sha256(text.encode())}")
        print(f"removed per Forward: {meta}")
        return 0
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print(f"wrote {path.relative_to(root)} sha256={sha256(text.encode())}")
    print(f"removed per Forward: {meta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
