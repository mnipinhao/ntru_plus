#!/usr/bin/env python3
"""SUPERCOP-flat qualification export of the Inverse D / Shoup candidates (Phase B).

Built from the installed current-best export (the HT export, kind ht-qualification-source):
  * every base file is copied unchanged except kem.c;
  * added, with the exact bytes of the Phase-A generated asm (each sha256 must equal its
    results/invshoup-phase-a/*-generation.json record):
        invntt_crep.s    <- asm/ntruplus<N>_officialopt_invntt_crep.s   (variants with the fused inverse)
        basemul_shoup.s  <- asm/ntruplus<N>_officialopt_basemul_shoup.s
    (the Shoup C source is its derivation input only, recorded in the manifest, not exported:
    SUPERCOP compiles every .c and .s of the directory);
  * kem.c = the base export kem.c with its verbatim src/kem_lazy_r2fold.c body replaced by the
    verbatim src/kem_lazy_r2fold_<X>.c body.  The base kem.c already carries the current-best
    overlay heads; the Phase-A chain of <X> is the current-best chain with only its #include
    lines rebound (checked here), so this rebinds exactly what Phase A rebinds: the Decap
    inverse pair -> invntt_crep, Encap BaseMul and second Decap BaseMul -> basemul_shoup.
    NTRU+768 with the fused inverse also drops the HT-inverse overlay head (its #define is dead
    once the Decap inverse call is gone) and the then unreferenced invntt_ht.s.
    The unified diff kem.c vs base kem.c is recorded in the manifest.

  864   avx2-officialopt-lazy-codec-keccak-ht-invd-shoup-qual001   X = invcrep_shoup
  1152  avx2-officialopt-lazy-freeze-keccak-ht-invd-shoup-qual001  X = invcrep_shoup
  768   avx2-officialopt-lazy-freeze-keccak-ht-shoup-qual001       X = shoup (default)
        avx2-officialopt-lazy-freeze-keccak-ht-invc-shoup-qual001  X = invcrep_shoup (--variant)

Modes (no compiler is run): write (refuses to overwrite), or --check (regenerate into a
temporary directory and require the existing export and manifest to be identical).  Research
export, not a clean-production promotion.  Install with official_opt_lazy/tools/install_qualification.py.

  export_invshoup_flat.py --param N --experiment . --qualification-root qualification [--variant X] [--check]
"""
import argparse
import difflib
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").exists())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, sha256_tree  # noqa: E402

BASES = {768: "avx2-officialopt-lazy-freeze-keccak-ht-qual001", 864: "avx2-officialopt-lazy-codec-keccak-ht-qual001",
         1152: "avx2-officialopt-lazy-freeze-keccak-ht-qual001"}
NAMES = {(768, "shoup"): "avx2-officialopt-lazy-freeze-keccak-ht-shoup-qual001",
         (768, "invcrep_shoup"): "avx2-officialopt-lazy-freeze-keccak-ht-invc-shoup-qual001",
         (864, "invcrep_shoup"): "avx2-officialopt-lazy-codec-keccak-ht-invd-shoup-qual001",
         (1152, "invcrep_shoup"): "avx2-officialopt-lazy-freeze-keccak-ht-invd-shoup-qual001"}
STEM = {768: "freeze2op", 864: "codec_direct", 1152: "freeze2op"}
INCLUDE_R2FOLD = '#include "kem_lazy_r2fold.c"\n'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fail(msg):
    raise SystemExit(f"export_invshoup_flat: {msg}")


def strip_head(text, path):
    if not text.startswith("/*\n") or text.count(" */\n") != 1:
        fail(f"{path}: unexpected comment shape")
    return text[text.index(" */\n") + 4:]


class Spec:
    def __init__(self, n, variant):
        self.n, self.variant = n, variant
        p = f"ntruplus{n}_officialopt"
        self.p = p
        self.name, self.base = NAMES[(n, variant)], BASES[n]
        self.inv = "invcrep" in variant
        self.added = {"basemul_shoup.s": (f"asm/{p}_basemul_shoup.s", "results/invshoup-phase-a/shoup-generation.json",
                                          f"asm/{p}_basemul_shoup.s")}
        if self.inv:
            self.added["invntt_crep.s"] = (f"asm/{p}_invntt_crep.s", "results/invshoup-phase-a/invcrep-generation.json",
                                           f"asm/{p}_invntt_crep.s")
        stem = STEM[n]
        self.ht_chain = [f"src/kem_lazy_r2fold_{stem}_keccak_ht.c", f"src/kem_lazy_r2fold_{stem}_keccak.c"]
        self.x_chain = [f"src/kem_lazy_r2fold_{variant}_{stem}_keccak_ht.c", f"src/kem_lazy_r2fold_{variant}_{stem}_keccak.c"]
        if n == 768:
            self.ht_chain.insert(0, f"src/kem_lazy_r2fold_{stem}_keccak_ht_htinv.c")
            if not self.inv:
                self.x_chain.insert(0, f"src/kem_lazy_r2fold_{variant}_{stem}_keccak_ht_htinv.c")
        self.drop_htinv = n == 768 and self.inv
        self.phase_a = self.x_chain[0][4:-2]


def check_base(spec, base, lock, key):
    m = json.loads(base.with_suffix(".json").read_text())
    if (m.get("kind") != "ht-qualification-source" or m.get("parameter") != str(spec.n) or
            m.get("supercop_version") != lock["version"] or m.get("official_tree_sha256") != lock[key] or
            m.get("implementation") != base.name or base.name != spec.base):
        fail("base qualification manifest does not match the lock / parameter / name")
    if sha256_tree(base) != m["tree_sha256"]:
        fail("base qualification tree hash mismatch")
    if {f.name for f in base.iterdir()} != set(m["files_sha256"]):
        fail("base qualification file set differs from its manifest")
    for fname, expected in m["files_sha256"].items():
        if sha(base / fname) != expected:
            fail(f"base qualification file mismatch: {fname}")
    for fname in spec.added:
        if fname in m["files_sha256"]:
            fail(f"{fname} already exists in the base export")
    return m


def build_kem(spec, root, base):
    base_kem = (base / "kem.c").read_text()
    r2 = (root / "src/kem_lazy_r2fold.c").read_text()
    x = (root / f"src/kem_lazy_r2fold_{spec.variant}.c").read_text()
    if base_kem.count(r2) != 1:
        fail("src/kem_lazy_r2fold.c body must occur exactly once in the base kem.c")
    # the variant chain is the current-best chain with only the #include lines rebound
    ht = [strip_head((root / p).read_text(), p) for p in spec.ht_chain]
    xc = [strip_head((root / p).read_text(), p) for p in spec.x_chain]
    if spec.drop_htinv:
        ht = ht[1:]
    ht_inc = [f'#include "{Path(p).name}"\n' for p in spec.ht_chain[1:]] + [INCLUDE_R2FOLD]
    x_inc = [f'#include "{Path(p).name}"\n' for p in spec.x_chain[1:]] + [f'#include "kem_lazy_r2fold_{spec.variant}.c"\n']
    if spec.drop_htinv:
        ht_inc = ht_inc[1:]
    for a, b, ia, ib, p in zip(ht, xc, ht_inc, x_inc, spec.x_chain):
        if not a.endswith(ia) or not b.endswith(ib) or a[:-len(ia)] != b[:-len(ib)]:
            fail(f"{p}: not the current-best chain file with its #include rebound")
    kem = base_kem.replace(r2, x)
    info_drop = None
    if spec.drop_htinv:
        head = strip_head((root / spec.ht_chain[0]).read_text(), spec.ht_chain[0])
        define = f"#define poly_invntt_scale {spec.p}_invntt_ht\n"
        if head != define + f'#include "{Path(spec.ht_chain[1]).name}"\n':
            fail("unexpected HT-inverse overlay head")
        full = (root / spec.ht_chain[0]).read_text()
        comment = full[:full.index(" */\n") + 4]
        if kem.count(comment + define) != 1:
            fail("HT-inverse head not found in the base kem.c")
        kem = kem.replace(comment + define, "")
        info_drop = {"removed_overlay_head": spec.ht_chain[0], "define": define.rstrip("\n")}
    calls = {"poly_invntt_scale(": 0 if spec.inv else 1, "poly_crepmod3(": 0 if spec.inv else 1,
             f"{spec.p}_invntt_crep(": 2 if spec.inv else 0, "poly_basemul(": 0, "poly_basemul_scale(": 1,
             f"{spec.p}_basemul_shoup(": 3, f"{spec.p}_basemul_nor2(": 3, f"{spec.p}_baseinv_r2fold(": 3,
             f"{spec.p}_ntt_caller_lazy(": 7, "poly_ntt(": 0, "poly_baseinv(": 0}
    if spec.n == 768:
        calls[f"{spec.p}_invntt_ht"] = 0 if spec.inv else 1
    for c, k in calls.items():
        if kem.count(c) != k:
            fail(f"kem.c: {c} occurs {kem.count(c)} times, expected {k}")
    diff = list(difflib.unified_diff(base_kem.splitlines(), kem.splitlines(), f"{spec.base}/kem.c",
                                     f"{spec.name}/kem.c", lineterm="", n=0))
    info = {"construction": "base export kem.c with its verbatim src/kem_lazy_r2fold.c body replaced by the "
                            f"verbatim src/kem_lazy_r2fold_{spec.variant}.c body"
                            + ("; HT-inverse overlay head removed" if spec.drop_htinv else ""),
            "base_kem_c_sha256": sha(base / "kem.c"),
            "replaced_body": {"path": "src/kem_lazy_r2fold.c", "sha256": sha(root / "src/kem_lazy_r2fold.c")},
            "inserted_body": {"path": f"src/kem_lazy_r2fold_{spec.variant}.c",
                              "sha256": sha(root / f"src/kem_lazy_r2fold_{spec.variant}.c")},
            "phase_a_chain": [*spec.x_chain, f"src/kem_lazy_r2fold_{spec.variant}.c"],
            "phase_a_chain_equals_current_best_chain_with_includes_rebound": True,
            "textual_call_counts": calls, "unified_diff_vs_base": diff,
            "diff_lines_added": sum(1 for l in diff if l.startswith("+") and not l.startswith("+++")),
            "diff_lines_removed": sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))}
    if info_drop:
        info["dropped"] = info_drop
    return kem, info


def generation_checks(spec, root):
    out = {}
    for flat, (src, record, key) in spec.added.items():
        rec = json.loads((root / record).read_text())
        expected = rec["output_sha256"][key]
        if sha(root / src) != expected:
            fail(f"{src} sha256 differs from the Phase-A record {record}")
        out[flat] = {"from": src, "sha256": expected, "phase_a_record": record,
                     "phase_a_record_sha256": sha(root / record)}
    rec = json.loads((root / "results/invshoup-phase-a/shoup-generation.json").read_text())
    c = f"src/{spec.p}_basemul_shoup.c"
    if sha(root / c) != rec["output_sha256"][c]:
        fail(f"{c} differs from the Phase-A record")
    krec = json.loads((root / "results/invshoup-phase-a/invshoup-kems-generation.json").read_text())
    for p in [*spec.x_chain, f"src/kem_lazy_r2fold_{spec.variant}.c"]:
        if sha(root / p) != krec["output_sha256"][p]:
            fail(f"{p} differs from the Phase-A KEM generation record")
    if sha(root / "src/kem_lazy_r2fold.c") != krec["inputs_sha256"]["src/kem_lazy_r2fold.c"]:
        fail("src/kem_lazy_r2fold.c differs from the Phase-A KEM generation record")
    return out, {"path": c, "sha256": sha(root / c), "compiler": rec["compiler"]}


def export(spec, root, qroot, base, lock, key):
    target, manifest_path = qroot / spec.name, qroot / (spec.name + ".json")
    if target.exists() or manifest_path.exists():
        fail(f"refusing to overwrite {target} / {manifest_path}")
    bm = check_base(spec, base, lock, key)
    added, shoup_c = generation_checks(spec, root)
    kem, kem_info = build_kem(spec, root, base)
    qroot.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    kept, dropped = {}, []
    for f in sorted(base.iterdir()):
        if f.name == "kem.c":
            continue
        if spec.drop_htinv and f.name == "invntt_ht.s":
            dropped.append(f.name)
            continue
        shutil.copy2(f, target / f.name)
        kept[f.name] = sha(f)
    for flat, (src, _, _) in spec.added.items():
        shutil.copy2(root / src, target / flat)
    (target / "kem.c").write_text(kem)
    for f in [target, *target.iterdir()]:
        f.chmod(f.stat().st_mode | 0o200)
    files = {f.name: sha(f) for f in sorted(target.iterdir()) if f.is_file()}
    manifest = {
        "kind": "invshoup-qualification-source", "implementation": spec.name,
        "phase_a_candidate": spec.phase_a, "parameter": str(spec.n), "variant": spec.variant,
        "supercop_version": lock["version"], "official_tree_sha256": lock[key],
        "tree_sha256": sha256_tree(target), "files_sha256": files,
        "base": {"implementation": base.name, "kind": bm["kind"], "tree_sha256": bm["tree_sha256"],
                 "manifest": str(base.with_suffix(".json").relative_to(root)),
                 "manifest_sha256": sha(base.with_suffix(".json"))},
        "kept_from_base_sha256": kept, "dropped_from_base": dropped,
        "replaced_from_base": {"kem.c": {"base_sha256": bm["files_sha256"]["kem.c"], "sha256": files["kem.c"]}},
        "added": added, "shoup_derivation_source": shoup_c, "kem_c": kem_info,
        "exporter": {"path": "common/official_opt_invshoup/tools/export_invshoup_flat.py", "sha256": sha(HERE)},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return target, manifest_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--variant", choices=("shoup", "invcrep_shoup"))
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--qualification-root", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    variant = args.variant or ("shoup" if args.param == 768 else "invcrep_shoup")
    if (args.param, variant) not in NAMES:
        ap.error("no such export")
    spec = Spec(args.param, variant)
    root = args.experiment.resolve()
    base = (root / "qualification" / spec.base).resolve()
    lock = read_lock(REPO / "bench/supercop.lock")
    key = f"ntruplus{args.param}_avx2_tree_sha256"
    qroot = (root / args.qualification_root).resolve()
    if not args.check:
        target, _ = export(spec, root, qroot, base, lock, key)
        print(target)
        print(f"tree_sha256 {sha256_tree(target)}")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        t, m = export(spec, root, Path(tmp), base, lock, key)
        have, have_m = qroot / spec.name, qroot / (spec.name + ".json")
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
