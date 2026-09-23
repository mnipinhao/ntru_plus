#!/usr/bin/env python3
"""Mutation check for the exp002 codec differential (gate 1).

Applies hand mutations, one at a time, to a scratch copy of
asm/ntruplus864_officialopt_codec_direct.s, links build/mutants/test_codec_direct
(tests/test_codec_direct.c, the unchanged test_codec_fused.c overlay) against
it and requires the differential to FAIL.  Mutants that pass are listed with
the reason they are equivalent.  The tracked asm is never modified.

  mutate_codec_direct.py --experiment . --output results/codec-direct-phase-a/mutation-check.json
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

ASM = "asm/ntruplus864_officialopt_codec_direct.s"
C = ".Lntruplus864_officialopt_direct_"


def nth_line_sub(pattern, repl, n=0):
    def f(text):
        lines = text.split("\n")
        hits = [i for i, l in enumerate(lines) if not l.startswith("#") and re.search(pattern, l)]
        if len(hits) <= n:
            raise ValueError(f"pattern {pattern!r} has {len(hits)} hits")
        i = hits[n]
        lines[i] = re.sub(pattern, repl, lines[i], count=1)
        return "\n".join(lines)
    return f


def delete_line(pattern, n=0):
    def f(text):
        lines = text.split("\n")
        hits = [i for i, l in enumerate(lines) if not l.startswith("#") and re.search(pattern, l)]
        del lines[hits[n]]
        return "\n".join(lines)
    return f


def swap_lines(p1, p2):
    def f(text):
        lines = text.split("\n")
        i = next(i for i, l in enumerate(lines) if re.search(p1, l))
        j = next(i for i, l in enumerate(lines) if re.search(p2, l))
        lines[i], lines[j] = lines[j], lines[i]
        return "\n".join(lines)
    return f


def move_after(p1, p2):
    """move the first line matching p1 to just after the first line matching p2"""
    def f(text):
        lines = text.split("\n")
        i = next(i for i, l in enumerate(lines) if re.search(p1, l))
        line = lines.pop(i)
        j = next(i for i, l in enumerate(lines) if re.search(p2, l))
        lines.insert(j + 1, line)
        return "\n".join(lines)
    return f


def table_byte(label, row, col, new):
    def f(text):
        lines = text.split("\n")
        i = lines.index(f"{C}{label}:") + 1 + row
        vals = lines[i][len(".byte "):].split(", ")
        vals[col] = new
        lines[i] = ".byte " + ", ".join(vals)
        return "\n".join(lines)
    return f


MUTANTS = [
    ("tobytes freeze: vpminuw -> vpminsw (signed min)", nth_line_sub(r"vpminuw", "vpminsw", 0), None),
    ("tobytes freeze: drop vpaddw q (min(b, b))", nth_line_sub(r"vpaddw %ymm14, (%ymm\d+), %ymm(\d+)",
                                                             r"vpor \1, \1, %ymm\2", 0), None),
    ("madd constant 4096 -> 2048", table_byte("madd", 0, 3, "0x08"), None),
    ("tobytes pshufb mask tb1: swap two bytes", table_byte("tb1", 0, 0, "0x09"), None),
    ("tobytes pshufb mask tb2 lane 1 only", table_byte("tb2", 1, 11, "0x0d"), None),
    ("tobytes interleave blend 0xCC -> 0xC0", nth_line_sub(r"vpblendd \$0xCC", "vpblendd $0xC0", 0), None),
    ("tobytes group store offset +1", nth_line_sub(r"vmovdqu (%xmm\d+), 12\(%rdi\)", r"vmovdqu \1, 13(%rdi)", 0), None),
    ("tobytes store order: group 0 stored after group 1", move_after(r"vmovdqu %xmm\d+, 0\(%rdi\)",
                                                                     r"vmovdqu %xmm\d+, 12\(%rdi\)"), None),
    ("tobytes last group: vpextrd $2 -> $1", nth_line_sub(r"vpextrd \$2", "vpextrd $1", 0), None),
    ("tobytes last group: vmovq offset 132 -> 128", nth_line_sub(r"vmovq (%xmm\d+), 132", r"vmovq \1, 128", 0), None),
    ("frombytes pshufb mask fb0: wrong byte", table_byte("fb0", 0, 4, "0x0a"), None),
    ("frombytes last group: fb2last -> fb2 (no 4-byte shift)",
     nth_line_sub(re.escape(C) + r"fb2last\(%rip\)", C + "fb2(%rip)", 0), None),
    ("frombytes low12 mask 0xfff -> 0x7ff", table_byte("low12", 0, 1, "0x07"), None),
    ("frombytes odd shift vpsrld 12 -> 11", nth_line_sub(r"vpsrld \$12", "vpsrld $11", 0), None),
    ("frombytes inverse blend 0xCC -> 0x0C", nth_line_sub(r"vpblendd \$0xCC", "vpblendd $0x0C", 6), None),  # 7th = first in frombytes
    ("frombytes load offset +1", nth_line_sub(r"vmovdqu 12\(%rsi\)", "vmovdqu 13(%rsi)", 0), None),
    ("frombytes canonical: drop one vpmaxuw", delete_line(r"vpmaxuw", 0), None),
    ("frombytes canonical: threshold q-1 -> q", nth_line_sub(r"_16xqm1", "_16xq", 0), None),
    ("frombytes pack: vpackusdw -> vpackssdw", nth_line_sub(r"vpackusdw", "vpackssdw", 0),
     "equivalent: packed values are <= 4095, so signed and unsigned saturation agree"),
    ("loop bound: 1536 -> 1152 (tobytes)", nth_line_sub(r"lea 1536\(%rsi\)", "lea 1152(%rsi)", 0), None),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()
    root = args.experiment.resolve()
    work = root / "build/mutants"
    work.mkdir(parents=True, exist_ok=True)
    src = (root / ASM).read_text()
    cmd = subprocess.run(["make", "-s", "-n", "-B", "build/test_codec_direct"], cwd=root, check=True,
                         capture_output=True, text=True).stdout.strip().splitlines()[-1]
    if ASM not in cmd:
        raise SystemExit("unexpected build command")
    results = []
    for name, mutate, equivalent in MUTANTS:
        text = mutate(src)
        if text == src:
            raise ValueError(f"mutation {name!r} changed nothing")
        m = work / "mutant.s"
        m.write_text(text)
        build = cmd.replace(ASM, str(m)).replace("-o build/test_codec_direct", f"-o {work}/test_codec_direct")
        subprocess.run(build, shell=True, cwd=root, check=True, capture_output=True, text=True)
        try:
            r = subprocess.run([str(work / "test_codec_direct")], capture_output=True, text=True,
                               timeout=args.timeout)
            caught, detail = r.returncode != 0, (r.stderr.strip().splitlines() or [""])[0]
        except subprocess.TimeoutExpired:
            caught, detail = False, "timeout"
        results.append({"mutation": name, "caught": caught, "first_error": detail,
                        "declared_equivalent": equivalent})
        print(f"{'caught ' if caught else 'SURVIVED'} {name}: {detail}")
    bad = [r for r in results if not r["caught"] and not r["declared_equivalent"]]
    wrong_equiv = [r for r in results if r["caught"] and r["declared_equivalent"]]
    out = {"class": "mutation check of tests/test_codec_direct.c against hand-mutated exp002 asm",
           "mutants": len(results), "caught": sum(r["caught"] for r in results),
           "survived_equivalent": [r["mutation"] for r in results if not r["caught"] and r["declared_equivalent"]],
           "survived_unexplained": [r["mutation"] for r in bad], "results": results,
           "pass": not bad and not wrong_equiv}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
