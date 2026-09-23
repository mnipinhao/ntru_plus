#!/usr/bin/env python3
"""SUPERCOP-flat feasibility of the mlkem-native-Keccak NTRU+ candidates (scratch only).

SUPERCOP compiles every .c/.s/.S of one implementation directory with each
okc-<abi> compiler line and no implementation-specific -D flags.  This tool:

1. flattens <base qualification tree> + the vendored mlkem-native x1 files +
   the adapter header into ONE directory (--out/<candidate>):
     - every base file except fips202.c, fips202.h, KeccakP-1600-AVX2.s,
       KeccakP-1600-SnP.h is copied unchanged (kem.c, symmetric.c, ... keep
       their base sha256; symmetric.c is the pinned Official one);
     - fips202.h := common/official_opt_keccak/src/fips202_mlkem.h;
     - third_party/mlkem-native-fips202-b3ba7b32/mlkem/src/{,fips202/}X ->
       mlk_X (flat names avoid params.h / fips202.h collisions with NTRU+),
       LICENSE -> LICENSE.mlkem-native;
     - common/official_opt_keccak/config/mlkem_native_config.h copied as is;
     - the ONLY edits are `#include "..."` lines rewritten to the flat names
       (every rewrite is recorded);
2. emulates SUPERCOP do-part for crypto_kem/ntruplus{N} in a scratch work
   directory, for the flat candidate, the unmodified base tree and the
   pinned Official avx2 tree: generated crypto_kem.h / crypto_kem_<p>.h from
   MACROS / PROTOTYPES.c / api.h, every file compiled with every compiler
   line of the (read-only) campaign's okc-amd64 with exactly do-part's flags
   (-DSUPERCOP -DCRYPTO_NAMESPACE... and includes, security model
   constbranchindex), ar into lib<op>.a, try-small / try linked with
   knownrandombytes.o + campaign libs, run, and checksums compared with the
   pinned crypto_kem/ntruplus{N}/checksum{small,big}.
Nothing is installed into any SUPERCOP tree; the campaign and pristine trees
are only read.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON = HERE.parents[1]
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
VENDOR = REPO / "third_party/mlkem-native-fips202-b3ba7b32"
DROP = {"fips202.c", "fips202.h", "KeccakP-1600-AVX2.s", "KeccakP-1600-SnP.h"}
MLK_FILES = {"mlkem/src/common.h": "mlk_common.h", "mlkem/src/sys.h": "mlk_sys.h",
             "mlkem/src/cbmc.h": "mlk_cbmc.h", "mlkem/src/params.h": "mlk_params.h",
             "mlkem/src/context.h": "mlk_context.h", "mlkem/src/verify.h": "mlk_verify.h",
             "mlkem/src/fips202/fips202.c": "mlk_fips202.c", "mlkem/src/fips202/fips202.h": "mlk_fips202.h",
             "mlkem/src/fips202/keccakf1600.c": "mlk_keccakf1600.c",
             "mlkem/src/fips202/keccakf1600.h": "mlk_keccakf1600.h"}
NAMES = {"candidate": {768: "avx2-officialopt-lazy-freeze-keccak-768-exp001",
                       864: "avx2-officialopt-lazy-codec-keccak-864-exp001",
                       1152: "avx2-officialopt-lazy-freeze-keccak-1152-exp001"}}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sh(cmd, cwd=None, timeout=3600):
    return subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout)


def rewrite_includes(text, mapping, rewrites, fname):
    def sub(m):
        target = m.group(2)
        key = target.split("/")[-1]
        if key in mapping and target != mapping[key]:
            rewrites.append({"file": fname, "from": target, "to": mapping[key]})
            return f'{m.group(1)}"{mapping[key]}"'
        return m.group(0)
    return re.sub(r'^(\s*#\s*include\s+)"([^"]+)"', sub, text, flags=re.M)


def flatten(base: Path, out: Path):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    kept = {}
    for f in sorted(base.iterdir()):
        if f.is_file() and f.name not in DROP:
            shutil.copy2(f, out / f.name)
            kept[f.name] = sha(f)
    mapping = {Path(k).name: v for k, v in MLK_FILES.items()}
    rewrites, added = [], {}
    for rel, flat in MLK_FILES.items():
        text = rewrite_includes((VENDOR / rel).read_text(), mapping, rewrites, flat)
        (out / flat).write_text(text)
        added[flat] = {"from": f"third_party/mlkem-native-fips202-b3ba7b32/{rel}", "source_sha256": sha(VENDOR / rel),
                       "flat_sha256": sha(out / flat)}
    hdr = (COMMON / "src/fips202_mlkem.h").read_text()
    new = hdr.replace('#include "mlkem/src/fips202/fips202.h"', '#include "mlk_fips202.h"')
    if new == hdr:
        raise ValueError("fips202_mlkem.h include anchor missing")
    rewrites.append({"file": "fips202.h", "from": "mlkem/src/fips202/fips202.h", "to": "mlk_fips202.h"})
    (out / "fips202.h").write_text(new)
    added["fips202.h"] = {"from": "common/official_opt_keccak/src/fips202_mlkem.h",
                          "source_sha256": sha(COMMON / "src/fips202_mlkem.h"), "flat_sha256": sha(out / "fips202.h")}
    shutil.copy2(COMMON / "config/mlkem_native_config.h", out / "mlkem_native_config.h")
    added["mlkem_native_config.h"] = {"from": "common/official_opt_keccak/config/mlkem_native_config.h",
                                      "flat_sha256": sha(out / "mlkem_native_config.h")}
    shutil.copy2(VENDOR / "LICENSE", out / "LICENSE.mlkem-native")
    # every remaining quoted include must resolve inside the flat directory or the SUPERCOP include dirs
    unresolved = []
    for f in sorted(out.iterdir()):
        if f.suffix in (".c", ".h", ".s", ".S"):
            for inc in re.findall(r'^\s*#\s*include\s+"([^"]+)"', f.read_text(), flags=re.M):
                if not (out / inc).exists() and not inc.startswith("crypto_") and inc not in ("randombytes.h",):
                    unresolved.append(f"{f.name}: {inc}")
    # mlk_common.h's two backend-API includes sit under MLK_CONFIG_USE_NATIVE_BACKEND_{ARITH,FIPS202}
    # && MLK_CHECK_APIS, never defined by the local config; any other unresolved include fails.
    inactive = {"mlk_common.h: native/api.h", "mlk_common.h: fips202/native/api.h"}
    return {"kept_from_base_sha256": kept, "dropped": sorted(DROP), "added": added,
            "include_rewrites": rewrites, "unresolved_quoted_includes": [u for u in unresolved if u not in inactive],
            "unresolved_inactive_includes": sorted(set(unresolved) & inactive)}


def compilers(campaign, machine):
    okc = campaign / "bench" / machine / "bin/okc-amd64"
    return [l.strip() for l in sh(["sh", str(okc)]).stdout.splitlines() if l.strip()]


def supercop_headers(pristine, work, o, p, op, opi, implementationdir):
    macros = (pristine / "MACROS").read_text().splitlines()
    protos = (pristine / "PROTOTYPES.c").read_text().splitlines()
    sel = lambda lines: [l for l in lines if re.search(rf"{o}$|{o}\(|{o}_", l)]
    lines = [f"#ifndef {o}_H", f"#define {o}_H", "", f'#include "{op}.h"', ""]
    lines += [f"#define {m} {m.replace(o, op, 1)}" for m in sel(macros)]
    lines += [f'#define {o}_PRIMITIVE "{p}"', f"#define {o}_IMPLEMENTATION {op}_IMPLEMENTATION",
              f"#define {o}_VERSION {op}_VERSION", "", "#endif"]
    (work / f"{o}.h").write_text("\n".join(lines) + "\n")
    api = (work / "api.h").read_text()
    for opp in (op, f"{op}_publicinputs"):
        body = [f"#ifndef {opp}_H", f"#define {opp}_H", ""]
        body += re.sub(r"[ \t]CRYPTO_", f" {opi}_", api).splitlines()
        body += [" ", "#ifdef __cplusplus", 'extern "C" {', "#endif"]
        body += [l.replace(o, opi, 1) for l in sel(protos)]
        body += ["#ifdef __cplusplus", "}", "#endif", ""]
        for m in sel(macros):
            mopi = m.replace(o, opi, 1)
            body.append(f"#define {mopi.replace(opi, opp, 1)} {mopi}")
        body += [f'#define {opp}_IMPLEMENTATION "{implementationdir}"', f"#ifndef {opi}_VERSION",
                 f'#define {opi}_VERSION "-"', "#endif", f"#define {opp}_VERSION {opi}_VERSION", "", "#endif"]
        (work / f"{opp}.h").write_text("\n".join(body) + "\n")


def try_tree(tree, label, param, args, compiler_lines, scratch):
    o, p = "crypto_kem", f"ntruplus{param}"
    op = f"{o}_{p}"
    security = "constbranchindex"
    implementationdir = f"{o}/{p}/{label}"
    opi = re.sub(r"[./-]", "_", f"{implementationdir}/{security}")
    bench = args.supercop / "bench" / args.machine
    inc, lib, abi = bench / "include", bench / "lib", "amd64"
    includes = f"-I. -I{inc} -I{inc}/nontimecop/{abi} -I{inc}/{abi} -I{inc}/{abi}/{security}"
    oklibs = sh(["sh", str(bench / "bin/oklibs-amd64")]).stdout.strip()
    libs = f"{lib}/{abi}/libsupercop.a {lib}/{abi}/kernelrandombytes.o {lib}/nontimecop/{abi}/libcpucycles.a {oklibs}"
    trylibs = f"{lib}/{abi}/knownrandombytes.o {libs}"
    expected = {k: (args.pristine / o / p / f"checksum{k}").read_text().strip() for k in ("small", "big")}
    results = []
    for compiler in compiler_lines:
        word = compiler.replace(" ", "_")
        work = scratch / label / word
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        for f in tree.iterdir():
            shutil.copy2(f, work / f.name)
        cfiles = sorted(f.name for f in work.iterdir() if f.suffix == ".c")
        sfiles = sorted(f.name for f in work.iterdir() if f.suffix in (".s", ".S"))
        for src in ("try.c", "measure.c"):
            shutil.copy2(args.pristine / o / src, work / src)
        for src in ("try-anything.c", "measure-anything.c", "MACROS", "PROTOTYPES.c"):
            shutil.copy2(args.pristine / src, work / src)
        (work / "try-small.c").write_text('#define SMALL\n#include "try.c"\n')
        for inc_name in ("test-more.inc", "test-loops.inc"):
            src = args.pristine / o / p / "supercop" / inc_name
            (work / inc_name).write_text(src.read_text() if src.exists() else "")
        supercop_headers(args.pristine, work, o, p, op, opi, implementationdir)
        defs = (f"-DSUPERCOP '-DCRYPTO_NAMESPACETOP={opi}' '-D_CRYPTO_NAMESPACETOP=_{opi}' "
                f"'-DCRYPTO_NAMESPACE(name)={opi}_##name' '-D_CRYPTO_NAMESPACE(name)=_{opi}_##name' "
                f"'-DCRYPTO_SHARED_NAMESPACE(name)={opi}_##name' '-D_CRYPTO_SHARED_NAMESPACE(name)=_{opi}_##name' "
                f"'-DCRYPTO_ALIGN(n)=__attribute__((aligned(n)))'")
        entry = {"compiler": compiler, "compile_errors": {}, "warnings": {}}
        ok = True
        for f in cfiles + sfiles:
            if f in ("try.c", "measure.c", "try-anything.c", "measure-anything.c", "try-small.c"):
                continue
            r = sh(f"{compiler} {defs} {includes} -c {f}", cwd=work)
            if r.returncode:
                entry["compile_errors"][f] = r.stderr.strip().splitlines()[:20]
                ok = False
            elif r.stderr.strip():
                entry["warnings"][f] = r.stderr.strip().splitlines()[:20]
        if ok:
            objs = " ".join(sorted(x.name for x in work.glob("*.o")))
            r = sh(f"ar cr lib{op}.a {objs} && ranlib lib{op}.a", cwd=work)
            ok = r.returncode == 0
            entry["library_globals"] = sorted(
                l.split()[-1] for l in sh(f"nm -g --defined-only lib{op}.a", cwd=work).stdout.splitlines()
                if len(l.split()) == 3)
        runs = {}
        for binary, src, key in (("try-small", "try-small.c", "small"), ("try", "try.c", "big")):
            if not ok:
                break
            r = sh(f"{compiler} -DSUPERCOP {includes} -o {binary} {src} try-anything.c lib{op}.a {trylibs}", cwd=work)
            if r.returncode:
                entry["compile_errors"][binary] = r.stderr.strip().splitlines()[:20]
                ok = False
                break
            r = sh(f"./{binary} {args.version} amd64 {implementationdir} {word}", cwd=work, timeout=3600)
            fields = r.stdout.split()
            runs[key] = {"exit": r.returncode, "checksum": fields[0] if fields else None,
                         "expected": expected[key], "stderr": r.stderr.strip().splitlines()[:5]}
            ok &= r.returncode == 0 and bool(fields) and fields[0] == expected[key]
        entry["try"] = runs
        entry["pass"] = bool(ok)
        results.append(entry)
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--base-qualification", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--supercop", type=Path, required=True, help="initialised SUPERCOP campaign (read only)")
    ap.add_argument("--pristine", type=Path, required=True, help="pristine SUPERCOP (read only)")
    ap.add_argument("--machine", required=True)
    ap.add_argument("--version", default="20260831")
    ap.add_argument("--summary", type=Path, help="also write the summary JSON here")
    args = ap.parse_args()
    root = args.experiment.resolve()
    out = args.out.resolve()
    if any(str(out).startswith(str(p.resolve())) for p in (args.supercop, args.pristine)):
        raise SystemExit("refusing to write inside a SUPERCOP tree")
    base = (root / args.base_qualification).resolve()
    name = NAMES["candidate"][args.param]
    flat = out / "implementations" / name
    meta = flatten(base, flat)
    lines = compilers(args.supercop, args.machine)
    scratch = out / "work"
    trees = {name: flat, base.name: base, "avx2": root / "upstream/supercop-avx2"}
    summary = {"class": "SUPERCOP-flat feasibility (scratch emulation of do-part; not installed, no timing)",
               "parameter": f"NTRU+{args.param}", "base_qualification": str(args.base_qualification),
               "flat_tree": str(flat), "flatten": meta,
               "flat_tree_sha256": {f.name: sha(f) for f in sorted(flat.iterdir())},
               "okc_amd64": lines, "trees": {}}
    for label, tree in trees.items():
        summary["trees"][label] = try_tree(tree, label, args.param, args, lines, scratch)
    summary["pass"] = bool(not meta["unresolved_quoted_includes"] and
                           all(e["pass"] for t in summary["trees"].values() for e in t))
    (out / "flat-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"pass": summary["pass"], "flat_tree": str(flat),
                      "trees": {k: [(e["compiler"].split()[3], e["pass"],
                                     {kk: vv["checksum"] == vv["expected"] for kk, vv in e.get("try", {}).items()},
                                     len(e["warnings"])) for e in v] for k, v in summary["trees"].items()}},
                     indent=1))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
