#!/usr/bin/env python3
"""SUPERCOP-flat qualification export of the NTRU+768 HT candidate (Phase B).

Candidate avx2-officialopt-lazy-freeze-keccak-ht-768-exp001 (Phase A overlay
src/kem_lazy_r2fold_freeze2op_keccak_ht_htinv.c) as the flat implementation
directory avx2-officialopt-lazy-freeze-keccak-ht-qual001, built from the
installed base export avx2-officialopt-lazy-freeze-keccak-qual001:

  * every base file is copied unchanged except kem.c;
  * added, with the exact bytes of the Phase-A generated files (each sha256
    must equal its results/ht-phase-a/*-generation.json record):
        ntt_ht.s          <- asm/ntruplus768_officialopt_ntt_ht.s
        invntt_ht.s       <- asm/ntruplus768_officialopt_invntt_ht.s
        basemul_nor2.s    <- asm/ntruplus768_officialopt_basemul_nor2.s
        baseinv_r2fold.c  <- src/ntruplus768_officialopt_baseinv_r2fold.c
  * kem.c = the two Phase-A overlay heads (HT inverse, then HT Forward: their
    comment and one #define each, i.e. the overlay files without their
    #include line) + the base export kem.c with its verbatim src/kem_lazy.c
    body replaced by the verbatim src/kem_lazy_r2fold.c body.  This rebinds
    exactly what the Phase-A overlay chain rebinds: 6 Forwards -> HT, the
    Decap inverse -> HT inverse, 2 keygen BaseInv -> fold, 2 keygen BaseMul
    -> nor2; Encap/Decap BaseMul and everything else unchanged.  The only
    Phase-A chain lines not carried over are the repo-only Keccak includes of
    src/kem_lazy_r2fold_freeze2op_keccak.c (util.h, fips202_mlkem.h,
    keccak_names.h): in the flat tree fips202.h *is* the mlkem-native adapter
    and hash_f/g/h keep their Official names, exactly as in the base export.
    The unified diff kem.c vs base kem.c is recorded in the manifest.

Modes (no compiler is run):
  --qualification-root DIR          write DIR/<name> + DIR/<name>.json; refuses
                                    to overwrite either path.
  --qualification-root DIR --check  regenerate into a temporary directory and
                                    require the existing export and manifest
                                    to be identical (file set, bytes, JSON).
Both modes verify bench/supercop.lock against the base export's manifest, the
base tree against that manifest (tree hash and every file hash), the base
kem.c construction (src/kem_lazy_freeze2op.c with src/kem_lazy.c inlined),
the Phase-A generation records and the cheap overlay/fold generators --check.
Research export, not a clean-production promotion.  Install with
common/official_opt_lazy/tools/install_qualification.py.
"""

import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, sha256_tree  # noqa: E402

PARAM = 768
NAME = "avx2-officialopt-lazy-freeze-keccak-ht-qual001"
PHASE_A = "avx2-officialopt-lazy-freeze-keccak-ht-768-exp001"
BASE = "avx2-officialopt-lazy-freeze-keccak-qual001"
P = f"ntruplus{PARAM}_officialopt"
ADDED = {  # flat name -> (experiment source, Phase-A generation record, key or None)
    "ntt_ht.s": (f"asm/{P}_ntt_ht.s", "results/ht-phase-a/ht-forward-generation.json", None),
    "invntt_ht.s": (f"asm/{P}_invntt_ht.s", "results/ht-phase-a/ht-inverse-generation.json", None),
    "basemul_nor2.s": (f"asm/{P}_basemul_nor2.s", "results/ht-phase-a/r2fold-generation.json",
                       f"asm/{P}_basemul_nor2.s"),
    "baseinv_r2fold.c": (f"src/{P}_baseinv_r2fold.c", "results/ht-phase-a/r2fold-generation.json",
                         f"src/{P}_baseinv_r2fold.c"),
}
HEADS = ("src/kem_lazy_r2fold_freeze2op_keccak_ht_htinv.c", "src/kem_lazy_r2fold_freeze2op_keccak_ht.c")
HEAD_INCLUDES = ('#include "kem_lazy_r2fold_freeze2op_keccak_ht.c"\n', '#include "kem_lazy_r2fold_freeze2op_keccak.c"\n')
HEAD_DEFINES = (f"#define poly_invntt_scale {P}_invntt_ht\n",
                f"#define {P}_ntt_caller_lazy {P}_ntt_ht\n")
R2K = "src/kem_lazy_r2fold_freeze2op_keccak.c"
R2K_DROPPED = ['#include "util.h"', '#include "fips202_mlkem.h"', '#include "keccak_names.h"']
FREEZE_DEFINE = f"#define poly_tobytes {P}_tobytes_freeze2op\n"
INCLUDE_LAZY = '#include "kem_lazy.c"\n'
INCLUDE_R2FOLD = '#include "kem_lazy_r2fold.c"\n'
# kem.c call bindings (textual, after the #define rebinds): name -> count
KEM_CALLS = {f"{P}_ntt_caller_lazy(": 7,  # 1 declaration + 6 calls, rebound to ntt_ht by the #define
             "poly_invntt_scale(": 1, f"{P}_baseinv_r2fold(": 3, f"{P}_basemul_nor2(": 3,
             "poly_baseinv(": 0, "poly_basemul(": 2, "poly_ntt(": 0}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def fail(msg):
    raise SystemExit(f"export_ht_flat: {msg}")


def check_base(root, base, lock, key):
    manifest_path = base.with_suffix(".json")
    m = json.loads(manifest_path.read_text())
    if (m.get("kind") != "keccak-qualification-source" or m.get("parameter") != str(PARAM) or
            m.get("supercop_version") != lock["version"] or m.get("official_tree_sha256") != lock[key] or
            m.get("implementation") != base.name or base.name != BASE):
        fail("base qualification manifest does not match the lock / parameter / name")
    if sha256_tree(base) != m["tree_sha256"]:
        fail("base qualification tree hash mismatch")
    if {f.name for f in base.iterdir()} != set(m["files_sha256"]):
        fail("base qualification file set differs from its manifest")
    for fname, expected in m["files_sha256"].items():
        if sha(base / fname) != expected:
            fail(f"base qualification file mismatch: {fname}")
    for fname in ADDED:
        if fname in m["files_sha256"]:
            fail(f"{fname} already exists in the base export")
    return m, manifest_path


def build_kem(root, base):
    base_kem = (base / "kem.c").read_text()
    lazy = (root / "src/kem_lazy.c").read_text()
    r2fold = (root / "src/kem_lazy_r2fold.c").read_text()
    freeze = (root / "src/kem_lazy_freeze2op.c").read_text()
    if freeze.count(INCLUDE_LAZY) != 1 or base_kem != freeze.replace(INCLUDE_LAZY, lazy):
        fail("base kem.c is not src/kem_lazy_freeze2op.c with src/kem_lazy.c inlined")
    if base_kem.count(lazy) != 1:
        fail("src/kem_lazy.c body must occur exactly once in base kem.c")
    heads = []
    for path, inc, define in zip(HEADS, HEAD_INCLUDES, HEAD_DEFINES):
        text = (root / path).read_text()
        if text.count(inc) != 1 or not text.endswith(inc) or text.count(define) != 1:
            fail(f"{path}: unexpected overlay shape")
        head = text[:-len(inc)]
        body = [l for l in head.splitlines() if l.strip() and not l.lstrip().startswith(("/*", "*"))]
        if body != [define.rstrip("\n")]:
            fail(f"{path}: overlay head must be a comment plus exactly one #define, got {body}")
        heads.append(head)
    # The third link of the Phase-A chain: repo-only Keccak includes + the freeze2op #define + kem_lazy_r2fold.c.
    r2k = (root / R2K).read_text()
    if not r2k.endswith(INCLUDE_R2FOLD) or r2k.count(FREEZE_DEFINE) != 1:
        fail(f"{R2K}: unexpected overlay shape")
    r2k_body = [l for l in r2k[:-len(INCLUDE_R2FOLD)].splitlines()
                if l.strip() and not l.lstrip().startswith(("/*", "*"))]
    if r2k_body != R2K_DROPPED + [FREEZE_DEFINE.rstrip("\n")]:
        fail(f"{R2K}: body {r2k_body} is not the expected Keccak includes + freeze2op #define")
    if FREEZE_DEFINE not in base_kem.split(lazy)[0]:
        fail("base kem.c prefix lacks the freeze2op #define")
    kem = "".join(heads) + base_kem.replace(lazy, r2fold)
    for call, n in KEM_CALLS.items():
        if kem.count(call) != n:
            fail(f"kem.c: {call} occurs {kem.count(call)} times, expected {n}")
    diff = list(difflib.unified_diff(base_kem.splitlines(), kem.splitlines(),
                                     f"{BASE}/kem.c", f"{NAME}/kem.c", lineterm="", n=0))
    info = {
        "construction": "overlay heads (HT inverse, HT Forward; comment + one #define each) + base export "
                        "kem.c with its verbatim src/kem_lazy.c body replaced by verbatim src/kem_lazy_r2fold.c",
        "overlay_heads": {p: {"sha256": sha(root / p), "define": d.rstrip("\n")} for p, d in zip(HEADS, HEAD_DEFINES)},
        "base_kem_c": {"sha256": sha(base / "kem.c"), "equals": "src/kem_lazy_freeze2op.c with src/kem_lazy.c inlined"},
        "replaced_body": {"path": "src/kem_lazy.c", "sha256": sha(root / "src/kem_lazy.c")},
        "inserted_body": {"path": "src/kem_lazy_r2fold.c", "sha256": sha(root / "src/kem_lazy_r2fold.c")},
        "phase_a_chain": [*HEADS, R2K, "src/kem_lazy_r2fold.c"],
        "phase_a_chain_lines_not_carried": {
            "file": R2K, "lines": R2K_DROPPED,
            "reason": "repo-only mlkem-native binding; in the flat tree fips202.h is the mlkem-native adapter "
                      "and hash_f/g/h keep their Official names (same as the base export)"},
        "textual_call_counts": KEM_CALLS,
        "unified_diff_vs_base": diff,
        "diff_lines_added": sum(1 for l in diff if l.startswith("+") and not l.startswith("+++")),
        "diff_lines_removed": sum(1 for l in diff if l.startswith("-") and not l.startswith("---")),
    }
    return kem, info


def generation_checks(root):
    out = {}
    for flat, (src, record, key) in ADDED.items():
        rec = json.loads((root / record).read_text())
        expected = rec["output_sha256"] if key is None else rec["output_sha256"][key]
        actual = sha(root / src)
        if actual != expected:
            fail(f"{src} sha256 {actual} != Phase-A record {record}")
        out[flat] = {"from": src, "sha256": actual, "phase_a_record": record,
                     "phase_a_record_sha256": sha(root / record)}
    r2rec = json.loads((root / "results/ht-phase-a/r2fold-generation.json").read_text())
    if sha(root / "src/kem_lazy_r2fold.c") != r2rec["output_sha256"]["src/kem_lazy_r2fold.c"] or \
            sha(root / "src/kem_lazy.c") != r2rec["inputs_sha256"]["src/kem_lazy.c"]:
        fail("src/kem_lazy_r2fold.c / src/kem_lazy.c differ from the Phase-A r2fold generation record")
    tools = HERE.parent
    for gen in ("generate_ht_overlays.py", "generate_keygen_r2fold.py"):
        r = subprocess.run([sys.executable, str(tools / gen), "--experiment", str(root), "--check"],
                           capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1"})
        if r.returncode:
            fail(f"{gen} --check failed:\n{r.stdout}{r.stderr}")
    return out


def export(root, qroot, base, lock, key):
    target, manifest_path = qroot / NAME, qroot / (NAME + ".json")
    if target.exists() or manifest_path.exists():
        fail(f"refusing to overwrite {target} / {manifest_path}")
    base_manifest, base_manifest_path = check_base(root, base, lock, key)
    added = generation_checks(root)
    kem, kem_info = build_kem(root, base)
    for flat, (src, _, _) in ADDED.items():
        text = (root / src).read_text()
        symbol = {"ntt_ht.s": f"{P}_ntt_ht", "invntt_ht.s": f"{P}_invntt_ht",
                  "basemul_nor2.s": f"{P}_basemul_nor2", "baseinv_r2fold.c": f"{P}_baseinv_r2fold"}[flat]
        if (flat.endswith(".s") and f".global {symbol}\n" not in text) or \
                (flat.endswith(".c") and f"int {symbol}(" not in text) or symbol not in kem:
            fail(f"{flat}: {symbol} not defined there or not referenced by kem.c")
    qroot.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    kept = {}
    for f in sorted(base.iterdir()):
        if f.name != "kem.c":
            shutil.copy2(f, target / f.name)
            kept[f.name] = sha(f)
    for flat, (src, _, _) in ADDED.items():
        shutil.copy2(root / src, target / flat)
    (target / "kem.c").write_text(kem)
    for f in [target, *target.iterdir()]:
        f.chmod(f.stat().st_mode | 0o200)
    files = {f.name: sha(f) for f in sorted(target.iterdir()) if f.is_file()}
    for flat, entry in added.items():
        if files[flat] != entry["sha256"]:
            fail(f"{flat}: exported bytes differ from the Phase-A file")
    manifest = {
        "kind": "ht-qualification-source",
        "implementation": NAME,
        "phase_a_candidate": PHASE_A,
        "parameter": str(PARAM),
        "supercop_version": lock["version"],
        "official_tree_sha256": lock[key],
        "tree_sha256": sha256_tree(target),
        "files_sha256": files,
        "base": {"implementation": base.name, "kind": base_manifest["kind"],
                 "tree_sha256": base_manifest["tree_sha256"],
                 "manifest": str(base_manifest_path.relative_to(root)),
                 "manifest_sha256": sha(base_manifest_path)},
        "kept_from_base_sha256": kept,
        "replaced_from_base": {"kem.c": {"base_sha256": base_manifest["files_sha256"]["kem.c"],
                                         "sha256": files["kem.c"]}},
        "added": added,
        "kem_c": kem_info,
        "exporter": {"path": "common/official_opt_ht/tools/export_ht_flat.py", "sha256": sha(HERE)},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return target, manifest_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--base-qualification", type=Path, default=Path("qualification") / BASE)
    ap.add_argument("--qualification-root", type=Path, required=True)
    ap.add_argument("--check", action="store_true", help="verify the existing export instead of writing")
    args = ap.parse_args()
    root = args.experiment.resolve()
    base = (root / args.base_qualification).resolve()
    lock = read_lock(REPO / "bench/supercop.lock")
    key = f"ntruplus{PARAM}_avx2_tree_sha256"
    qroot = (root / args.qualification_root).resolve()
    if not args.check:
        target, _ = export(root, qroot, base, lock, key)
        print(target)
        print(f"tree_sha256 {sha256_tree(target)}")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        t, m = export(root, Path(tmp), base, lock, key)
        have, have_m = qroot / NAME, qroot / (NAME + ".json")
        if not have.is_dir() or not have_m.is_file():
            fail(f"--check: {have} or its manifest is missing")
        if sorted(p.name for p in have.iterdir()) != sorted(p.name for p in t.iterdir()):
            fail("--check: file set differs")
        for p in t.iterdir():
            if (have / p.name).read_bytes() != p.read_bytes():
                fail(f"--check: {p.name} differs")
        if json.loads(have_m.read_text()) != json.loads(m.read_text()):
            fail("--check: manifest differs")
        print(f"ok {have} tree_sha256 {sha256_tree(have)} (regenerated identical, manifest identical)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
