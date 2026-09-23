#!/usr/bin/env python3
"""Gate: generated lazy Forward == a reference lazy Forward, instruction by instruction.

Used for NTRU+768: the common generator's output
(asm/ntruplus768_officialopt_ntt_caller_lazy.s) must carry the same
instruction stream as the NTRU+768 qual001 caller-lazy Forward
(NTRU+768/experiments/avx2_official_opt_001/asm/ntruplus768_officialopt_ntt_caller_lazy.s,
read only), which differs only in local loop-label names.

Two independent checks:
  1. text: comments and blank lines dropped, whitespace collapsed, every
     label defined in the file renamed to L<k> by order of definition and
     the entry symbol renamed to FUNC; the two line lists must be equal;
  2. object: both files assembled alone with `cc -c`; the .text section
     bytes and the relocation lists (offset, type, symbol+addend) must be
     equal, and the only symbol-table differences are the local labels.

  check_lazy_stream_equal.py --candidate A.s --reference B.s [--output FILE]
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def normalised_lines(path):
    lines = []
    for raw in Path(path).read_text().splitlines():
        code = raw.split("#")[0].strip()
        if code:
            lines.append(re.sub(r"\s+", " ", code))
    globals_ = [l.split()[1] for l in lines if l.startswith(".global ")]
    if len(globals_) != 1:
        raise ValueError(f"{path}: expected one global entry, got {globals_}")
    entry = globals_[0]
    labels = [l[:-1] for l in lines if re.fullmatch(r"[A-Za-z_.][A-Za-z0-9_.$]*:", l)]
    rename = {entry: "FUNC"}
    k = 0
    for lab in labels:
        if lab not in rename:
            rename[lab] = f"L{k}"
            k += 1
    pat = re.compile(r"(?<![A-Za-z0-9_.$])(" + "|".join(map(re.escape, sorted(rename, key=len, reverse=True)))
                     + r")(?![A-Za-z0-9_.$])")
    return [pat.sub(lambda m: rename[m[1]], l) for l in lines], rename


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def object_view(path, tmp):
    obj = Path(tmp) / (Path(path).stem + ".o")
    run("cc", "-c", "-o", str(obj), str(path))
    text = subprocess.run(["objcopy", "-O", "binary", "--only-section=.text", str(obj), "/dev/stdout"],
                          check=True, capture_output=True).stdout
    relocs = []
    for line in run("objdump", "-r", "-j", ".text", str(obj)).splitlines():
        m = re.match(r"^([0-9a-f]+)\s+(R_X86_64_\w+)\s+(\S+)$", line.strip())
        if m:
            relocs.append([int(m[1], 16), m[2], m[3]])
    syms = sorted(l.split()[-1] for l in run("nm", str(obj)).splitlines() if l.split()[-2] in "tT")
    return {"text_sha256": hashlib.sha256(text).hexdigest(), "text_bytes": len(text),
            "relocations": relocs, "text_symbols": syms}, text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    cl, crename = normalised_lines(args.candidate)
    rl, rrename = normalised_lines(args.reference)
    if cl != rl:
        for i, (a, b) in enumerate(zip(cl, rl)):
            if a != b:
                raise SystemExit(f"FAIL text line {i}: {a!r} != {b!r}")
        raise SystemExit(f"FAIL text length {len(cl)} != {len(rl)}")
    with tempfile.TemporaryDirectory() as tmp:
        cv, ct = object_view(args.candidate, tmp)
        rv, rt = object_view(args.reference, tmp)
    if ct != rt:
        raise SystemExit("FAIL assembled .text bytes differ")
    if cv["relocations"] != rv["relocations"]:
        raise SystemExit("FAIL relocations differ")
    ren_c = {crename.get(s, s) for s in cv["text_symbols"]}
    ren_r = {rrename.get(s, s) for s in rv["text_symbols"]}
    if ren_c != ren_r:
        raise SystemExit(f"FAIL symbol sets differ after label normalisation: {ren_c ^ ren_r}")
    instr = [l for l in cl if not l.startswith(".") and not l.endswith(":")]
    record = {
        "class": "instruction-stream equality gate (label/symbol-name normalised)",
        "candidate": str(args.candidate), "candidate_sha256": sha(args.candidate),
        "reference": str(args.reference), "reference_sha256": sha(args.reference),
        "normalised_lines": len(cl), "instructions": len(instr),
        "label_map_candidate": crename, "label_map_reference": rrename,
        "assembled_text_sha256": cv["text_sha256"], "assembled_text_bytes": cv["text_bytes"],
        "relocations": len(cv["relocations"]),
        "text_equal": True, "object_text_bytes_equal": True, "relocations_equal": True,
        "pass": True,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2) + "\n")
    print(f"lazy stream equality PASS: {len(instr)} instructions, {len(cl)} normalised lines, "
          f".text {cv['text_bytes']} bytes sha256={cv['text_sha256'][:16]}.., "
          f"{len(cv['relocations'])} relocations equal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
