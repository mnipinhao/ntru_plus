#!/usr/bin/env python3
"""Provenance + configuration equivalence of the vendored mlkem-native x1 Keccak.

Given a clean mlkem-native checkout (--mlk-root) at the pinned commit
b3ba7b32773e657dd37f6f87bce82528459ad8a4:

1. every file of third_party/mlkem-native-fips202-b3ba7b32 (except README.md)
   is byte-identical to the checkout's file at the same path, and the
   README's per-file sha256 table matches;
2. fips202.c and keccakf1600.c are compiled with the release CFLAGS in
   (a) the vendored configuration (common/official_opt_keccak/config: no
       native backend, prefix ntruplus_mlkfips202) and
   (b) the configuration of the component comparison that motivated this
       backend (avx2_keccak_compare_001: -DMLK_CONFIG_USE_NATIVE_BACKEND_FIPS202
       -DMLK_CONFIG_PARAMETER_SET=768, upstream mlkem_native_config.h),
   and the x1 functions' instruction streams are compared after removing
   alignment padding and normalising symbol prefixes and branch targets
   (-> instruction index).  The x86_64 native FIPS202 backend is x4-only,
   so the x1 permutation is C in both; the expected difference is that in
   (a) mlk_keccakf1600_permute is `endbr64; jmp mlk_keccakf1600_permute_c`
   (the C permutation is shared with the unused x4 C fallback), whereas in
   (b) the same body is inlined into mlk_keccakf1600_permute.
"""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON = HERE.parents[1]
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
VENDOR = REPO / "third_party/mlkem-native-fips202-b3ba7b32"
COMMIT = "b3ba7b32773e657dd37f6f87bce82528459ad8a4"
CFLAGS = "-O3 -mavx2 -march=native -mtune=native -fPIE -Wall -Wextra -Werror".split()
PAD = ("nop", "nopw", "nopl", "xchg", "data16", "cs")


def run(*args, **kw):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True, **kw).stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def functions(obj, prefix):
    out, cur = {}, None
    for line in run("objdump", "-d", "--no-show-raw-insn", "-M", "att", obj).splitlines():
        head = re.match(r"^([0-9a-f]+) <([^>]+)>:$", line)
        if head:
            cur = out.setdefault(head[2].replace(prefix, "NS_"), [])
            continue
        m = re.match(r"^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$", line)
        if m and cur is not None and m[2] not in PAD:
            cur.append((int(m[1], 16), m[2], m[3].split("#")[0].strip().replace(prefix, "NS_")))
    return out


def normalise(insns):
    index = {a: i for i, (a, _, _) in enumerate(insns)}
    rows = []
    for a, op, operands in insns:
        t = re.match(r"^([0-9a-f]+) <([^>]+)>$", operands)
        if op.startswith("j") and t and int(t[1], 16) in index:
            rows.append(f"{op} ->{index[int(t[1], 16)]}")
        elif t:
            rows.append(f"{op} <{t[2].split('+')[0]}>")
        else:
            rows.append(f"{op} {operands}")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mlk-root", type=Path, required=True)
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.mlk_root.resolve()
    head = run("git", "-C", root, "rev-parse", "HEAD").strip()
    dirty = run("git", "-C", root, "status", "--porcelain").strip()
    if head != COMMIT or dirty:
        raise SystemExit(f"mlkem-native checkout must be clean at {COMMIT} (HEAD {head}, dirty={bool(dirty)})")
    vendored = sorted(p for p in VENDOR.rglob("*") if p.is_file() and p.name != "README.md")
    identical = {str(p.relative_to(VENDOR)): sha(p) == sha(root / p.relative_to(VENDOR)) for p in vendored}
    readme = (VENDOR / "README.md").read_text()
    readme_ok = all(f"`{sha(p)}`" in readme and str(p.relative_to(VENDOR)) in readme for p in vendored)
    build = args.build.resolve()
    build.mkdir(parents=True, exist_ok=True)
    objs = {}
    for cfg, flags, src_root, prefix in (
            ("vendored", [f"-I{COMMON / 'config'}"], VENDOR, "ntruplus_mlkfips202_"),
            ("native768", ["-DMLK_CONFIG_USE_NATIVE_BACKEND_FIPS202", "-DMLK_CONFIG_PARAMETER_SET=768",
                           f"-I{root / 'mlkem/src'}", f"-I{root / 'mlkem'}"], root, "PQCP_MLKEM_NATIVE_MLKEM768_")):
        funcs = {}
        for name in ("fips202", "keccakf1600"):
            o = build / f"{cfg}_{name}.o"
            run("cc", *CFLAGS, *flags, "-c", "-o", o, src_root / f"mlkem/src/fips202/{name}.c")
            funcs.update(functions(o, prefix))
            objs[f"{cfg}_{name}.o"] = sha(o)
        objs[cfg] = funcs
    a, b = objs.pop("vendored"), objs.pop("native768")
    compare = {}
    for fn in ("NS_shake256", "NS_keccakf1600_xor_bytes", "NS_keccakf1600_extract_bytes"):
        compare[fn] = normalise(a[fn]) == normalise(b[fn])
    absorb = [f for f in a if f.startswith("mlk_keccak_absorb_once")]
    compare["mlk_keccak_absorb_once"] = len(absorb) == 1 and normalise(a[absorb[0]]) == normalise(
        b[[f for f in b if f.startswith("mlk_keccak_absorb_once")][0]])
    wrapper = [f"{op} {x}" for _, op, x in a["NS_keccakf1600_permute"]]
    body_a = normalise(a["mlk_keccakf1600_permute_c"])
    # the exported function starts with endbr64 (CET); the static permute_c does not
    body_b = normalise([r for r in b["NS_keccakf1600_permute"] if r[1] != "endbr64"])
    compare["permutation_body (vendored permute_c == native768 inlined permute)"] = body_a == body_b
    ok = all(identical.values()) and readme_ok and all(compare.values()) and len(wrapper) == 2 \
        and wrapper[0].startswith("endbr64") and wrapper[1].startswith("jmp") and "permute_c" in wrapper[1]
    summary = {"mlkem_native_commit": head, "checkout_clean": not dirty,
               "vendored_files_identical_to_checkout": identical, "readme_sha256_table_matches": readme_ok,
               "cflags": CFLAGS, "object_sha256": objs,
               "x1_instruction_streams_equal": compare,
               "vendored_permute_wrapper": wrapper,
               "permutation_body_instructions": len(body_a),
               "pass": bool(ok)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("pass", "x1_instruction_streams_equal", "vendored_permute_wrapper",
                                              "readme_sha256_table_matches")}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
