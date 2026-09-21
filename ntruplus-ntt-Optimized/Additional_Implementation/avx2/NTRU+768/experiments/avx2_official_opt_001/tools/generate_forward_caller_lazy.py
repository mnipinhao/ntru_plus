#!/usr/bin/env python3
"""Derive a caller-bounded Forward entry from pinned Official ntt.s.

The only arithmetic deletion is the terminal 48-vector Barrett block.
This is not a replacement for the general-input poly_ntt entry.
"""

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream/supercop-avx2"
NAME = "ntruplus768_officialopt_ntt_caller_lazy"
EXPECTED_NTT_SHA256 = "992b613701be5988e83798a4a8f56a798c7e47e4616db70e65eee7feb75332f4"


def generate_asm() -> str:
    source = (UPSTREAM / "ntt.s").read_bytes()
    if hashlib.sha256(source).hexdigest() != EXPECTED_NTT_SHA256:
        raise ValueError("pinned Official ntt.s changed")
    body = source.decode()
    if body.count(".global poly_ntt\npoly_ntt:") != 1:
        raise ValueError("unexpected Official entry")
    body = body.replace(".global poly_ntt\npoly_ntt:",
                        f".text\n.p2align 5\n.global {NAME}\n.type {NAME},@function\n{NAME}:", 1)
    body = re.sub(r"\b(_looptop_[A-Za-z0-9_]+)\b", r"officialopt_lazy_\1", body)
    load_v = "vmovdqa _16xv(%rip), %ymm1\n"
    if body.count(load_v) != 1:
        raise ValueError("unexpected terminal Barrett constant load")
    body = body.replace(load_v, "", 1)
    start, end = body.split("#reduce2\n", 1)
    reduction, suffix = end.split("#store\n", 1)
    lines = [line.strip() for line in reduction.splitlines() if line.strip()]
    opcodes = [line.split()[0] for line in lines]
    if len(lines) != 24 or sorted(set(opcodes)) != ["vpmulhrsw", "vpmullw", "vpsubw"]:
        raise ValueError("unexpected terminal Barrett block")
    if {opcode: opcodes.count(opcode) for opcode in set(opcodes)} != {
            "vpmulhrsw": 8, "vpmullw": 8, "vpsubw": 8}:
        raise ValueError("unexpected terminal Barrett operation count")
    if body.count("#reduce2\n") != 1 or end.count("#store\n") != 1:
        raise ValueError("unexpected terminal block multiplicity")
    body = start + "#store\n" + suffix
    marker = ".ifndef no_gnu_stack"
    if body.count(marker) != 1:
        raise ValueError("unexpected Official NTT footer")
    return body.replace(marker, f".size {NAME},.-{NAME}\n\n{marker}", 1)


def generate_kem() -> str:
    body = (UPSTREAM / "kem.c").read_text()
    if body.count("poly_ntt(") != 6 or body.count("#ifdef SUPERCOP\n") != 1:
        raise ValueError("Official KEM Forward call graph changed")
    body = body.replace("poly_ntt(", NAME + "(")
    return body.replace("#ifdef SUPERCOP\n",
                        f"void {NAME}(poly *);\n\n#ifdef SUPERCOP\n", 1)


if __name__ == "__main__":
    (ROOT / "asm/ntruplus768_officialopt_ntt_caller_lazy.s").write_text(generate_asm())
    (ROOT / "src/kem_lazy.c").write_text(generate_kem())
