#!/usr/bin/env python3
"""Mutation check: the Inverse D / Shoup gates must reject one-line mutants.

Each mutant changes one line of a committed generated asm (in a scratch copy) and must be
rejected by BOTH
  * the symbolic check: fused inverse -- every output word keeps the interned form of the
    generator's candidate (generate_invntt_crep.run_variant); Shoup -- every output word keeps
    the form of the reference formula (generate_basemul_shoup.symbolic_check);
  * the C differential (tests/test_invntt_crep.c / tests/test_basemul_shoup.c, compiled with
    the mutant through --inv-cmd / --shoup-cmd with {ASM} and {OUT}).
The unmutated files must pass both.  Shoup mutants are chosen to be wrong mod q or to leave
the proven range (a companion change alone keeps a*b mod q and is caught only symbolically,
so it is not used as a C-differential mutant).
"""
import argparse
import json
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "official_opt_ht/tools"))
import generate_invntt_crep as GI  # noqa: E402
import generate_basemul_shoup as GS  # noqa: E402
from symexec import parse_consts  # noqa: E402
from symexec_ext import FormsX  # noqa: E402


def inv_mutants(n):
    p = f"ntruplus{n}_officialopt_invcrep"
    m = [("sigma table word", f"{p}_l1sigma:", "BUMP", 0),
         ("level-1 Montgomery companion", "vpmullw _16xNinv_scaleqinv(%rip), %ymm11, %ymm14",
          "vpmullw _16xNinv_scale(%rip), %ymm11, %ymm14", 0),
         ("level-1 sigma pointer advance dropped", "add $16,  %rcx\n", "", 0),
         ("level-0 out_b = 2t -> t", "vpaddw %ymm13, %ymm13, %ymm13\n", "", 0),
         ("crep5 constant operand", f"vmovdqa {p}_16x4853(%rip), %ymm3", f"vmovdqa {p}_16x128(%rip), %ymm3", 0)]
    if n != 768:
        m += [("split reload dropped", f"{p}_looptop_43:\nvmovdqa 0(%rdi), ", f"{p}_looptop_43:\nvmovdqa 32(%rdi), ", 0),
              ("split zeta rewind", "sub $576, %rdx", "sub $512, %rdx", 0)]
    return m


def shoup_mutants(n):
    fn = f"ntruplus{n}_officialopt_basemul_shoup"
    if n == 864:
        return [("zeta table word", f"{fn}_zt:", "BUMP", 0),
                ("b row load offset", "\tvmovdqa\t64(%rdx), %ymm12", "\tvmovdqa\t32(%rdx), %ymm12", 0),
                ("final q*h multiply dropped", "\tvpmullw\t%ymm15, %ymm2, %ymm2\n", "", 0),
                ("spill reload slot", "\tvpaddw\t-32(%rsp), %ymm7, %ymm7", "\tvpaddw\t-64(%rsp), %ymm7, %ymm7", 0)]
    return [("zeta table word", f"{fn}_zt:", "BUMP", 0),
            ("b row load offset", "\tvmovdqa\t96(%rdx), %ymm11", "\tvmovdqa\t64(%rdx), %ymm11", 0),
            ("final q*h multiply dropped", "\tvpmullw\t%ymm10, %ymm14, %ymm14\n", "", 0),
            ("spill reload slot", "\tvpaddw\t-24(%rsp), %ymm11, %ymm11", "\tvpaddw\t-56(%rsp), %ymm11, %ymm11", 0)]


def mutate(text, old, new, nth):
    if new == "BUMP":        # bump the first table word after the label `old`
        i = text.index("\n", text.index("\n" + old) + 1) + 1
        line_end = text.index("\n", i)
        line = text[i:line_end]
        for d in (".short ", "\t.value\t"):
            if line.startswith(d):
                vals = line[len(d):].split(",")
                vals[0] = str(int(vals[0]) + 1)
                return text[:i] + d + ",".join(vals) + text[line_end:]
        raise ValueError(f"no table line after {old}")
    if new is None:          # drop the whole line starting with `old`
        i = text.index(old)
        return text[:i] + text[text.index("\n", i) + 1:]
    parts = text.split(old)
    if len(parts) < 2 + nth:
        raise SystemExit(f"mutant anchor {old!r}")
    return old.join(parts[:nth + 1]) + new + old.join(parts[nth + 1:])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--inv-cmd", required=True)
    ap.add_argument("--shoup-cmd", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    n = args.param
    root = args.experiment.resolve()
    nm = GI.Names(n)
    inv_path = root / f"asm/{nm.entry}.s"
    sh_path = root / f"asm/ntruplus{n}_officialopt_basemul_shoup.s"
    inv, sh = inv_path.read_text(), sh_path.read_text()
    syms = parse_consts((root / "upstream/supercop-avx2/consts.c").read_text())
    F = FormsX()
    ref_inv = GI.run_variant(F, inv, syms, n, nm.entry)[0]
    _, tab = GS.zeta_table(n, root)

    def sym_inv(text):
        try:
            return GI.run_variant(F, text, syms, n, nm.entry)[0] == ref_inv
        except (ValueError, KeyError, IndexError, RuntimeError):
            return False

    def sym_shoup(text):
        try:
            GS.symbolic_check(n, text, tab)
            return True
        except (ValueError, KeyError, IndexError, RuntimeError):
            return False
    res = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        def c_test(cmd, asm, name):
            out = tmp / name
            subprocess.run(shlex.split(cmd.format(OUT=out, ASM=asm)), cwd=root, check=True, capture_output=True)
            return subprocess.run([str(out)], cwd=root, capture_output=True).returncode == 0
        ctrl = {"symbolic_inverse": sym_inv(inv), "c_inverse": c_test(args.inv_cmd, inv_path, "inv_ctrl"),
                "symbolic_shoup": sym_shoup(sh), "c_shoup": c_test(args.shoup_cmd, sh_path, "sh_ctrl")}
        if not all(ctrl.values()):
            raise SystemExit(f"unmutated control failed {ctrl}")
        for k, (label, old, new, nth) in enumerate(inv_mutants(n)):
            m = mutate(inv, old, new, nth)
            if m == inv:
                raise SystemExit(f"mutant {label} had no effect")
            pm = tmp / f"inv_m{k}.s"
            pm.write_text(m)
            res.append({"mutant": label, "file": inv_path.name, "symbolic_rejects": not sym_inv(m),
                        "c_differential_rejects": not c_test(args.inv_cmd, pm, f"inv_m{k}")})
        for k, (label, old, new, nth) in enumerate(shoup_mutants(n)):
            m = mutate(sh, old, new, nth)
            if m == sh:
                raise SystemExit(f"mutant {label} had no effect")
            pm = tmp / f"sh_m{k}.s"
            pm.write_text(m)
            res.append({"mutant": label, "file": sh_path.name, "symbolic_rejects": not sym_shoup(m),
                        "c_differential_rejects": not c_test(args.shoup_cmd, pm, f"sh_m{k}")})
    ok = all(r["symbolic_rejects"] and r["c_differential_rejects"] for r in res)
    out = {"class": "mutation check (Phase A)", "parameter": f"NTRU+{n}", "verdict": "pass" if ok else "fail",
           "control_passes": ctrl, "mutants": res}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
