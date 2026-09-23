#!/usr/bin/env python3
"""Create a flat Official-derived caller-lazy qualification source (864/1152).

Port of NTRU+768 avx2_official_opt_001/tools/export_caller_lazy_qualification.py.
The export is the pinned imported Official tree plus a fixed set of overlays.
It refuses to overwrite, verifies the pinned Official tree against
bench/supercop.lock and records every installed source hash in a sibling JSON
manifest.  This is a research export, not a clean-production promotion.

Variants:
  lazy (default)      avx2-officialopt-caller-lazy-qual001: `kem.c`
                      (src/kem_lazy.c) + `ntt_caller_lazy.s`.
  lazy-codec-direct   avx2-officialopt-lazy-codec-qual002 (NTRU+864 only,
                      candidate exp002): `kem.c` + `ntt_caller_lazy.s` +
                      `codec_direct.s` (asm/ntruplus864_officialopt_codec_direct.s).
                      `kem.c` is src/kem_lazy_codec_direct.c flattened: its one
                      `#include "kem_lazy.c"` line is replaced by the verbatim
                      src/kem_lazy.c, so SUPERCOP (which compiles every .c file)
                      sees one translation unit with the same preprocessed text.

Usage (from the experiment directory):
  export_caller_lazy_qualification.py --param 864 --experiment . \
      --output-root qualification [--variant lazy-codec-direct]
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, sha256_file, sha256_tree  # noqa: E402

NAMES = {"lazy": "avx2-officialopt-caller-lazy-qual001",
         "lazy-codec-direct": "avx2-officialopt-lazy-codec-qual002"}
INCLUDE_LINE = '#include "kem_lazy.c"\n'


def overlays(param: int, variant: str) -> dict:
    lays = {
        "kem.c": "src/kem_lazy.c",
        "ntt_caller_lazy.s": f"asm/ntruplus{param}_officialopt_ntt_caller_lazy.s",
    }
    if variant == "lazy-codec-direct":
        lays["kem.c"] = "src/kem_lazy_codec_direct.c"
        lays["codec_direct.s"] = f"asm/ntruplus{param}_officialopt_codec_direct.s"
    return lays


def flat_kem(root: Path, variant: str, lays: dict) -> str:
    text = (root / lays["kem.c"]).read_text()
    if variant == "lazy":
        return text
    if text.count(INCLUDE_LINE) != 1 or "#include" in text.replace(INCLUDE_LINE, ""):
        raise SystemExit("kem_lazy_codec_direct.c must have exactly one include (kem_lazy.c)")
    return text.replace(INCLUDE_LINE, (root / "src/kem_lazy.c").read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--param", type=int, choices=(864, 1152), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--variant", choices=tuple(NAMES), default="lazy")
    args = parser.parse_args()
    if args.variant == "lazy-codec-direct" and args.param != 864:
        raise SystemExit("the direct 12-bit codec exists only for NTRU+864")
    NAME = NAMES[args.variant]
    root = args.experiment.resolve()
    output_root = args.output_root.resolve()
    target = output_root / NAME
    manifest_path = output_root / (NAME + ".json")
    if target.exists() or manifest_path.exists():
        raise SystemExit("refusing to overwrite qualification export")

    lock = read_lock(REPO / "bench/supercop.lock")
    key = f"ntruplus{args.param}_avx2_tree_sha256"
    source = root / "upstream/supercop-avx2"
    if sha256_tree(source) != lock[key]:
        raise SystemExit("pinned Official import hash mismatch")
    record = json.loads((root / "upstream/UPSTREAM.json").read_text())
    if record.get("source_tree_sha256") != lock[key]:
        raise SystemExit("UPSTREAM.json does not match the lock")
    lays = overlays(args.param, args.variant)
    kem = flat_kem(root, args.variant, lays)
    symbol = f"ntruplus{args.param}_officialopt_ntt_caller_lazy"
    if symbol not in kem or f".global {symbol}" not in (root / lays["ntt_caller_lazy.s"]).read_text():
        raise SystemExit("overlay does not reference the namespaced lazy Forward")
    if args.variant == "lazy-codec-direct":
        asm = (root / lays["codec_direct.s"]).read_text()
        for op in ("tobytes", "frombytes"):
            codec = f"ntruplus{args.param}_officialopt_{op}_direct"
            if f"#define poly_{op} {codec}\n" not in kem or f".global {codec}" not in asm:
                raise SystemExit(f"overlay does not bind poly_{op} to {codec}")

    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=False)
    # The imported upstream copy is read-only; the export is a fresh writable
    # copy (content hashes, not modes, are what the manifest pins).
    for path in [target, *target.iterdir()]:
        path.chmod(path.stat().st_mode | 0o200)
    for destination, path in lays.items():
        shutil.copy2(root / path, target / destination)
    (target / "kem.c").write_text(kem)
    if "amd64" not in (target / "architectures").read_text().split():
        raise SystemExit("missing amd64 architecture")
    for goal in ("goal-constbranch", "goal-constindex"):
        if not (target / goal).is_file():
            raise SystemExit(f"missing {goal}")
    files = {str(path.relative_to(target)): sha256_file(path)
             for path in sorted(target.iterdir()) if path.is_file()}
    manifest = {
        "kind": "caller-lazy-qualification-source",
        "implementation": NAME,
        "variant": args.variant,
        "parameter": str(args.param),
        "supercop_version": lock["version"],
        "official_tree_sha256": lock[key],
        "tree_sha256": sha256_tree(target),
        "overlays": {destination: sha256_file(target / destination) for destination in lays},
        "overlay_sources": {destination: {"path": path, "sha256": sha256_file(root / path)}
                            for destination, path in lays.items()},
        **({"kem_c_flattened_include": {"path": "src/kem_lazy.c",
                                        "sha256": sha256_file(root / "src/kem_lazy.c")}}
           if args.variant != "lazy" else {}),
        "files_sha256": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(target)


if __name__ == "__main__":
    main()
