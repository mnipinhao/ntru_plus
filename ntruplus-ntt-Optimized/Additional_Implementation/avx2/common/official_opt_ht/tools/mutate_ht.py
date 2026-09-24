#!/usr/bin/env python3
"""Mutation check: the HT/R^2-fold gates must reject one-line mutants.

Each mutant changes one line of a generated file (in a scratch copy); the
HT Forward / inverse mutants must be rejected both by the generator's symbolic
output-form proof and by tests/test_forward_ht.c / tests/test_invntt_ht.c, the
fold mutants by tests/test_keygen_r2fold.c.  The unmutated control must pass both.
--param 864 / 1152 (default 768): no HT inverse (no --inv-cmd, no inverse
mutants); the Forward mutants use the parameter's network (864 has no dword
unpacks, so the lo/hi swap is on vpunpcklwd) and add a pass-A pitfall mutant
(the ymm2 restore before the verbatim radix-3 level 2 dropped); the nor2
mutant changes the first zeta*qinv (864) or zeta (1152) load.
"""
import argparse
import json
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_forward_ht as G  # noqa: E402
from symexec import Forms, parse_consts  # noqa: E402

HT_MUTANTS = [
    ("block twiddle word", r"^(\.short )(-?\d+)(, .*)$", "ntruplus768_officialopt_ht_zetas_b", 3),
    ("pass-A radix-3 constant operand", r"^vpmulhw 64\(%rsi\)", None, 0),
    ("unpack lo/hi swap", r"^vpunpckldq ", None, 2),
    ("store row", r"^vmovdqa %ymm\d+, 64\(%rdi\)$", "#store", 0),
    ("level-2 twiddle offset", r"^vpbroadcastd 12\(%rdx\)", None, 0),
]
# (label, old, new, occurrence) on the HT inverse asm, rejected by symbolic proof + tests/test_invntt_ht.c
INV_MUTANTS = [
    ("inverse Barrett dropped", "vpsubw %ymm2, %ymm10, %ymm10\n", "", 0),
    ("inverse unpack lo/hi swap", "vpunpcklqdq ", "vpunpckhqdq ", 0),
    ("inverse twiddle slot", "vpmullw 96(%rsi)", "vpmullw 32(%rsi)", 0),
    ("inverse level-1 zeta offset", "vpbroadcastd 1160(%rdx)", "vpbroadcastd 1152(%rdx)", 0),
]
# NTRU+864 / 1152 Forward mutants: (label, old line, new line, occurrence) on the HT asm
HT_MUTANTS_P = {
    864: [("block twiddle word", None, None, 3),
          ("pass-A radix-3 constant operand", "vpmulhw 64(%rsi), %ymm3, %ymm3", "vpmulhw 0(%rsi), %ymm3, %ymm3", 0),
          ("unpack lo/hi swap", "vpunpcklwd %ymm10, %ymm7, %ymm13", "vpunpckhwd %ymm10, %ymm7, %ymm13", 0),
          ("store row", "vmovdqa %ymm13, 64(%rdi)", "vmovdqa %ymm13, 96(%rdi)", 0),
          ("level-2 twiddle offset", "vpbroadcastd 12(%rdx), %ymm6 #a", "vpbroadcastd 8(%rdx), %ymm6 #a", 0),
          ("pass-A w*qinv restore dropped", "vmovdqa %ymm14, %ymm2\n", "", 0)],
    1152: [("block twiddle word", None, None, 3),
           ("pass-A radix-3 constant operand", "vpmulhw 64(%rsi), %ymm3, %ymm3", "vpmulhw 0(%rsi), %ymm3, %ymm3", 0),
           ("unpack lo/hi swap", "vpunpckldq ", "vpunpckhdq ", 0),
           ("store row", "vmovdqa %ymm3, 64(%rdi)\n", "vmovdqa %ymm3, 96(%rdi)\n", 0),
           ("level-2 twiddle offset", "vpbroadcastd  12(%rdx), %ymm6 #a", "vpbroadcastd   8(%rdx), %ymm6 #a", 0),
           ("pass-A w*qinv restore dropped", "vmovdqa %ymm14, %ymm2\n", "", 0)],
}
FOLD_MUTANTS = [
    ("fold constant R2 -> R3", "src/ntruplus768_officialopt_baseinv_r2fold.c",
     "#define NTRUPLUS_R2FOLD       867", "#define NTRUPLUS_R2FOLD       460"),
    ("fold companion qinv", "src/ntruplus768_officialopt_baseinv_r2fold.c",
     "#define NTRUPLUS_R2FOLD_QINV  2787", "#define NTRUPLUS_R2FOLD_QINV  2786"),
    ("nor2 zeta load", "asm/ntruplus768_officialopt_basemul_nor2.s",
     "vmovdqa 32(%rcx), %ymm1", "vmovdqa (%rcx), %ymm1"),   # first of 2 zeta loads
]


def fold_mutants(param):
    if param == 768:
        return FOLD_MUTANTS
    p = f"ntruplus{param}_officialopt"
    load = ("vmovdqa 32(%rcx), %ymm2", "vmovdqa   (%rcx), %ymm2") if param == 864 else \
        ("vmovdqa 32(%rcx), %ymm1", "vmovdqa (%rcx), %ymm1")
    return [("fold constant R2 -> R3", f"src/{p}_baseinv_r2fold.c",
             "#define NTRUPLUS_R2FOLD       867", "#define NTRUPLUS_R2FOLD       460"),
            ("fold companion qinv", f"src/{p}_baseinv_r2fold.c",
             "#define NTRUPLUS_R2FOLD_QINV  2787", "#define NTRUPLUS_R2FOLD_QINV  2786"),
            ("nor2 zeta load", f"asm/{p}_basemul_nor2.s", *load)]   # first matching load


def mutate_line(text, old, new, nth, tab_b):
    """Replace occurrence nth of `old`; old None = bump the first word of line nth of the block table."""
    if old is None:
        lines = text.split("\n")
        start = next(i for i, l in enumerate(lines) if l.startswith(tab_b))
        i = [k for k in range(start, len(lines)) if lines[k].startswith(".short ")][nth]
        m = re.match(r"^(\.short )(-?\d+)(, .*)$", lines[i])
        lines[i] = f"{m[1]}{int(m[2]) + 1}{m[3]}"
        return "\n".join(lines)
    parts = text.split(old)
    if len(parts) < 2 + nth:
        raise SystemExit(f"mutant anchor {old!r}")
    out = old.join(parts[:nth + 1]) + new + old.join(parts[nth + 1:])
    if out == text:
        raise ValueError("mutation had no effect")
    return out


def mutate_ht(text, pattern, after, nth):
    lines = text.split("\n")
    start = 0
    if after:
        start = next(i for i, l in enumerate(lines) if l.startswith(after))
    hits = [i for i in range(start, len(lines)) if re.search(pattern, lines[i])]
    i = hits[nth]
    l = lines[i]
    if l.startswith(".short"):
        m = re.match(pattern, l)
        l = f"{m[1]}{int(m[2]) + 1}{m[3]}"
    elif "vpmulhw 64(%rsi)" in l:
        l = l.replace("vpmulhw 64(%rsi)", "vpmulhw 0(%rsi)")
    elif l.startswith("vpunpckldq"):
        l = l.replace("vpunpckldq", "vpunpckhdq")
    elif l.startswith("vpbroadcastd 12(%rdx)"):
        l = l.replace("12(%rdx)", "8(%rdx)")
    else:
        l = l.replace(", 64(%rdi)", ", 96(%rdi)")
    if l == lines[i]:
        raise ValueError("mutation had no effect")
    lines[i] = l
    return "\n".join(lines)


def symbolic_inv_ok(root, asm):
    import generate_inverse_ht as GI
    up = root / "upstream/supercop-avx2"
    syms = parse_consts((up / "consts.c").read_text())
    F = Forms()
    out_o = GI.run_official(F, (up / "invntt.s").read_text(), syms)[0]
    try:
        GI.verify(F, asm, syms, out_o, 6)
        return True
    except (ValueError, KeyError, IndexError):
        return False


def symbolic_ok(root, asm):
    """Symbolic output-form proof of a (mutated) HT Forward against the lazy Forward."""
    syms = parse_consts((root / "upstream/supercop-avx2/consts.c").read_text())
    F = Forms()
    out_l, _, _, _ = G.run_lazy(F, (root / f"asm/{G.LAZY}.s").read_text(), syms)
    try:
        G.verify(F, asm, syms, out_l)
        return True
    except (ValueError, KeyError, IndexError):
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), default=768)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--fwd-cmd", required=True, help="compile command of test_forward_ht with {HT} {OUT}")
    ap.add_argument("--kg-cmd", required=True, help="compile command of test_keygen_r2fold with {R2INV} {NOR2} {OUT}")
    ap.add_argument("--inv-cmd", help="compile command of test_invntt_ht with {HTINV} {OUT} (768 only)")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if (args.param == 768) != (args.inv_cmd is not None):
        ap.error("--inv-cmd is required for --param 768 and not accepted otherwise")
    G.configure(args.param)
    p = f"ntruplus{args.param}_officialopt"
    r2inv_src, nor2_src = (f"src/{p}_baseinv_r2fold.c", f"asm/{p}_basemul_nor2.s")
    root = args.experiment.resolve()
    ht_path = root / f"asm/{G.NAME}.s"
    ht = ht_path.read_text()
    res = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        def c_test(cmd, subst, name):
            out = tmp / name
            full = cmd.format(OUT=out, **subst)
            subprocess.run(shlex.split(full), cwd=root, check=True, capture_output=True)
            return subprocess.run([str(out)], cwd=root, capture_output=True).returncode == 0

        ctrl = {"symbolic": symbolic_ok(root, ht),
                "c_forward": c_test(args.fwd_cmd, {"HT": ht_path}, "fwd_ctrl"),
                "c_keygen": c_test(args.kg_cmd, {"R2INV": root / r2inv_src, "NOR2": root / nor2_src},
                                   "kg_ctrl")}
        if args.param == 768:
            inv_path = root / "asm/ntruplus768_officialopt_invntt_ht.s"
            inv = inv_path.read_text()
            ctrl["symbolic_inverse"] = symbolic_inv_ok(root, inv)
            ctrl["c_inverse"] = c_test(args.inv_cmd, {"HTINV": inv_path}, "inv_ctrl")
        if not all(ctrl.values()):
            raise SystemExit(f"unmutated control failed {ctrl}")
        for k, (label, old, new, nth) in enumerate(HT_MUTANTS_P.get(args.param, [])):
            m = mutate_line(ht, old, new, nth, G.TAB_B)
            p_m = tmp / f"ht_m{k}.s"
            p_m.write_text(m)
            res.append({"mutant": label, "file": ht_path.name,
                        "symbolic_rejects": not symbolic_ok(root, m),
                        "c_differential_rejects": not c_test(args.fwd_cmd, {"HT": p_m}, f"fwd_m{k}")})
        for k, (label, pat, after, nth) in enumerate(HT_MUTANTS if args.param == 768 else []):
            m = mutate_ht(ht, pat, after, nth)
            p = tmp / f"ht_m{k}.s"
            p.write_text(m)
            r = {"mutant": label, "file": ht_path.name,
                 "symbolic_rejects": not symbolic_ok(root, m),
                 "c_differential_rejects": not c_test(args.fwd_cmd, {"HT": p}, f"fwd_m{k}")}
            res.append(r)
        for k, (label, old, new, nth) in enumerate(INV_MUTANTS if args.param == 768 else []):
            parts = inv.split(old)
            if len(parts) < 2 + nth:
                raise SystemExit(f"mutant anchor {label}")
            m = old.join(parts[:nth + 1]) + new + old.join(parts[nth + 1:])
            p = tmp / f"inv_m{k}.s"
            p.write_text(m)
            res.append({"mutant": label, "file": inv_path.name,
                        "symbolic_rejects": not symbolic_inv_ok(root, m),
                        "c_differential_rejects": not c_test(args.inv_cmd, {"HTINV": p}, f"inv_m{k}")})
        for k, (label, rel, old, new) in enumerate(fold_mutants(args.param)):
            text = (root / rel).read_text()
            if old not in text:
                raise SystemExit(f"mutant anchor {label}")
            p = tmp / f"fold_m{k}{Path(rel).suffix}"
            p.write_text(text.replace(old, new, 1))   # first occurrence only
            subst = {"R2INV": root / r2inv_src, "NOR2": root / nor2_src}
            subst["R2INV" if rel.endswith(".c") else "NOR2"] = p
            res.append({"mutant": label, "file": Path(rel).name,
                        "c_differential_rejects": not c_test(args.kg_cmd, subst, f"kg_m{k}")})
    ok = all(all(v for k, v in r.items() if k.endswith("rejects")) for r in res)
    out = {"class": "mutation check (Phase A)", "verdict": "pass" if ok else "fail",
           "control_passes": ctrl, "mutants": res}
    if args.param != 768:
        out["parameter"] = f"NTRU+{args.param}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
