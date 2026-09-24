#!/usr/bin/env python3
"""SUPERCOP-flat qualification export of the NTRU+864 / NTRU+1152 HT candidates (Phase B).

Parameter-specific front end of export_ht_flat.py (the NTRU+768 exporter).
That file is left byte-identical because its own SHA-256 is part of the
committed NTRU+768 manifest, which `make ht-qualification-check` compares;
this tool imports it and rebinds its module constants and the two
parameter-dependent steps (kem.c construction, generator --check calls).
Every check of export_ht_flat.py applies unchanged (lock, base manifest and
tree, per-file hashes, Phase-A generation records, refuse-overwrite, --check
by regeneration into a temporary directory).

  864   candidate avx2-officialopt-lazy-codec-keccak-ht-864-exp001
        (src/kem_lazy_r2fold_codec_direct_keccak_ht.c) -> avx2-officialopt-lazy-codec-keccak-ht-qual001,
        base export avx2-officialopt-lazy-codec-keccak-qual001 (kem.c = src/kem_lazy_codec_direct.c
        with src/kem_lazy.c inlined)
  1152  candidate avx2-officialopt-lazy-freeze-keccak-ht-1152-exp001
        (src/kem_lazy_r2fold_freeze2op_keccak_ht.c) -> avx2-officialopt-lazy-freeze-keccak-ht-qual001,
        base export avx2-officialopt-lazy-freeze-keccak-qual001 (kem.c = src/kem_lazy_freeze2op.c
        with src/kem_lazy.c inlined)

Added files (exact Phase-A bytes, sha256 == results/ht-phase-a/*-generation.json):
ntt_ht.s, basemul_nor2.s, baseinv_r2fold.c.  No invntt_ht.s: the HT inverse is
not part of these candidates.  kem.c = the one Phase-A overlay head (HT Forward:
its comment and one #define) + the base kem.c with its verbatim src/kem_lazy.c
body replaced by the verbatim src/kem_lazy_r2fold.c.  This rebinds exactly what
the Phase-A chain rebinds: 6 Forwards -> HT, 2 keygen BaseInv -> fold, 2 keygen
BaseMul -> nor2; Encap/Decap BaseMul, the Decap inverse and everything else
unchanged.  The only chain lines not carried over are the repo-only Keccak
includes (util.h, fips202_mlkem.h, keccak_names.h) of the r2fold_only overlay;
its base #define lines (864: direct-codec tobytes/frombytes, 1152: freeze2op
tobytes) are already in the base kem.c.  The unified diff vs the base kem.c is in
the manifest.

  export_ht_flat_param.py --param N --experiment . --qualification-root qualification [--check]
"""

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import export_ht_flat as E  # noqa: E402

PLAIN = BASE_DEFINES = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def configure(param):
    """Rebind export_ht_flat's module constants for NTRU+864 / 1152."""
    global PLAIN, BASE_DEFINES
    P = f"ntruplus{param}_officialopt"
    if param == 864:
        name, base, stem = ("avx2-officialopt-lazy-codec-keccak-ht-qual001",
                            "avx2-officialopt-lazy-codec-keccak-qual001", "codec_direct")
        phase_a = "avx2-officialopt-lazy-codec-keccak-ht-864-exp001"
        BASE_DEFINES = [f"#define poly_tobytes {P}_tobytes_direct\n", f"#define poly_frombytes {P}_frombytes_direct\n"]
    else:
        name, base, stem = ("avx2-officialopt-lazy-freeze-keccak-ht-qual001",
                            "avx2-officialopt-lazy-freeze-keccak-qual001", "freeze2op")
        phase_a = "avx2-officialopt-lazy-freeze-keccak-ht-1152-exp001"
        BASE_DEFINES = [f"#define poly_tobytes {P}_tobytes_freeze2op\n"]
    PLAIN = f"src/kem_lazy_{stem}.c"
    E.PARAM, E.NAME, E.PHASE_A, E.BASE, E.P = param, name, phase_a, base, P
    E.ADDED = {
        "ntt_ht.s": (f"asm/{P}_ntt_ht.s", "results/ht-phase-a/ht-forward-generation.json", None),
        "basemul_nor2.s": (f"asm/{P}_basemul_nor2.s", "results/ht-phase-a/r2fold-generation.json",
                           f"asm/{P}_basemul_nor2.s"),
        "baseinv_r2fold.c": (f"src/{P}_baseinv_r2fold.c", "results/ht-phase-a/r2fold-generation.json",
                             f"src/{P}_baseinv_r2fold.c"),
    }
    E.R2K = f"src/kem_lazy_r2fold_{stem}_keccak.c"
    E.HEADS = (f"src/kem_lazy_r2fold_{stem}_keccak_ht.c",)
    E.HEAD_INCLUDES = (f'#include "kem_lazy_r2fold_{stem}_keccak.c"\n',)
    E.HEAD_DEFINES = (f"#define {P}_ntt_caller_lazy {P}_ntt_ht\n",)
    E.KEM_CALLS = {f"{P}_ntt_caller_lazy(": 7,  # 1 declaration + 6 calls, rebound to ntt_ht by the #define
                   "poly_invntt_scale(": 1, f"{P}_baseinv_r2fold(": 3, f"{P}_basemul_nor2(": 3,
                   "poly_baseinv(": 0, "poly_basemul(": 2, "poly_ntt(": 0}
    E.build_kem = build_kem
    E.generation_checks = generation_checks


def build_kem(root, base):
    """export_ht_flat.build_kem with the parameter's base overlay and #define lines."""
    fail = E.fail
    base_kem = (base / "kem.c").read_text()
    lazy = (root / "src/kem_lazy.c").read_text()
    r2fold = (root / "src/kem_lazy_r2fold.c").read_text()
    plain = (root / PLAIN).read_text()
    if plain.count(E.INCLUDE_LAZY) != 1 or base_kem != plain.replace(E.INCLUDE_LAZY, lazy):
        fail(f"base kem.c is not {PLAIN} with src/kem_lazy.c inlined")
    if base_kem.count(lazy) != 1:
        fail("src/kem_lazy.c body must occur exactly once in base kem.c")
    heads = []
    for path, inc, define in zip(E.HEADS, E.HEAD_INCLUDES, E.HEAD_DEFINES):
        text = (root / path).read_text()
        if text.count(inc) != 1 or not text.endswith(inc) or text.count(define) != 1:
            fail(f"{path}: unexpected overlay shape")
        head = text[:-len(inc)]
        body = [l for l in head.splitlines() if l.strip() and not l.lstrip().startswith(("/*", "*"))]
        if body != [define.rstrip("\n")]:
            fail(f"{path}: overlay head must be a comment plus exactly one #define, got {body}")
        heads.append(head)
    # The second link of the Phase-A chain: repo-only Keccak includes + the base #define lines + kem_lazy_r2fold.c.
    r2k = (root / E.R2K).read_text()
    if not r2k.endswith(E.INCLUDE_R2FOLD) or any(r2k.count(d) != 1 for d in BASE_DEFINES):
        fail(f"{E.R2K}: unexpected overlay shape")
    r2k_body = [l for l in r2k[:-len(E.INCLUDE_R2FOLD)].splitlines()
                if l.strip() and not l.lstrip().startswith(("/*", "*"))]
    if r2k_body != E.R2K_DROPPED + [d.rstrip("\n") for d in BASE_DEFINES]:
        fail(f"{E.R2K}: body {r2k_body} is not the expected Keccak includes + base #define lines")
    if any(d not in base_kem.split(lazy)[0] for d in BASE_DEFINES):
        fail("base kem.c prefix lacks the base #define lines")
    kem = "".join(heads) + base_kem.replace(lazy, r2fold)
    for call, n in E.KEM_CALLS.items():
        if kem.count(call) != n:
            fail(f"kem.c: {call} occurs {kem.count(call)} times, expected {n}")
    diff = list(difflib.unified_diff(base_kem.splitlines(), kem.splitlines(),
                                     f"{E.BASE}/kem.c", f"{E.NAME}/kem.c", lineterm="", n=0))
    info = {
        "construction": "overlay head (HT Forward; comment + one #define) + base export kem.c with its "
                        "verbatim src/kem_lazy.c body replaced by verbatim src/kem_lazy_r2fold.c",
        "overlay_heads": {p: {"sha256": sha(root / p), "define": d.rstrip("\n")}
                          for p, d in zip(E.HEADS, E.HEAD_DEFINES)},
        "base_kem_c": {"sha256": sha(base / "kem.c"), "equals": f"{PLAIN} with src/kem_lazy.c inlined"},
        "replaced_body": {"path": "src/kem_lazy.c", "sha256": sha(root / "src/kem_lazy.c")},
        "inserted_body": {"path": "src/kem_lazy_r2fold.c", "sha256": sha(root / "src/kem_lazy_r2fold.c")},
        "phase_a_chain": [*E.HEADS, E.R2K, "src/kem_lazy_r2fold.c"],
        "phase_a_chain_lines_not_carried": {
            "file": E.R2K, "lines": E.R2K_DROPPED,
            "reason": "repo-only mlkem-native binding; in the flat tree fips202.h is the mlkem-native adapter "
                      "and hash_f/g/h keep their Official names (same as the base export)"},
        "base_define_lines_already_in_base_kem_c": [d.rstrip("\n") for d in BASE_DEFINES],
        "textual_call_counts": E.KEM_CALLS,
        "unified_diff_vs_base": diff,
        "diff_lines_added": sum(1 for l in diff if l.startswith("+") and not l.startswith("+++")),
        "diff_lines_removed": sum(1 for l in diff if l.startswith("-") and not l.startswith("---")),
    }
    return kem, info


def generation_checks(root):
    """export_ht_flat.generation_checks with --param for the overlay / fold generators."""
    out = {}
    for flat, (src, record, key) in E.ADDED.items():
        rec = json.loads((root / record).read_text())
        expected = rec["output_sha256"] if key is None else rec["output_sha256"][key]
        actual = sha(root / src)
        if actual != expected:
            E.fail(f"{src} sha256 {actual} != Phase-A record {record}")
        out[flat] = {"from": src, "sha256": actual, "phase_a_record": record,
                     "phase_a_record_sha256": sha(root / record)}
    r2rec = json.loads((root / "results/ht-phase-a/r2fold-generation.json").read_text())
    if sha(root / "src/kem_lazy_r2fold.c") != r2rec["output_sha256"]["src/kem_lazy_r2fold.c"] or \
            sha(root / "src/kem_lazy.c") != r2rec["inputs_sha256"]["src/kem_lazy.c"]:
        E.fail("src/kem_lazy_r2fold.c / src/kem_lazy.c differ from the Phase-A r2fold generation record")
    for gen in ("generate_ht_overlays.py", "generate_keygen_r2fold.py"):
        r = subprocess.run([sys.executable, str(HERE.parent / gen), "--param", str(E.PARAM),
                            "--experiment", str(root), "--check"],
                           capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1"})
        if r.returncode:
            E.fail(f"{gen} --check failed:\n{r.stdout}{r.stderr}")
    return out


def export(root, qroot, base, lock, key):
    target, manifest_path = E.export(root, qroot, base, lock, key)
    m = json.loads(manifest_path.read_text())
    m["exporter"] = {"path": "common/official_opt_ht/tools/export_ht_flat_param.py", "sha256": sha(HERE),
                     "library": m["exporter"]}
    manifest_path.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    return target, manifest_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--base-qualification", type=Path, help="default qualification/<base export>")
    ap.add_argument("--qualification-root", type=Path, required=True)
    ap.add_argument("--check", action="store_true", help="verify the existing export instead of writing")
    args = ap.parse_args()
    configure(args.param)
    root = args.experiment.resolve()
    base = (root / (args.base_qualification or Path("qualification") / E.BASE)).resolve()
    lock = E.read_lock(E.REPO / "bench/supercop.lock")
    key = f"ntruplus{args.param}_avx2_tree_sha256"
    qroot = (root / args.qualification_root).resolve()
    if not args.check:
        target, _ = export(root, qroot, base, lock, key)
        print(target)
        print(f"tree_sha256 {E.sha256_tree(target)}")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        t, m = export(root, Path(tmp), base, lock, key)
        have, have_m = qroot / E.NAME, qroot / (E.NAME + ".json")
        if not have.is_dir() or not have_m.is_file():
            E.fail(f"--check: {have} or its manifest is missing")
        if sorted(p.name for p in have.iterdir()) != sorted(p.name for p in t.iterdir()):
            E.fail("--check: file set differs")
        for p in t.iterdir():
            if (have / p.name).read_bytes() != p.read_bytes():
                E.fail(f"--check: {p.name} differs")
        if json.loads(have_m.read_text()) != json.loads(m.read_text()):
            E.fail("--check: manifest differs")
        print(f"ok {have} tree_sha256 {E.sha256_tree(have)} (regenerated identical, manifest identical)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
