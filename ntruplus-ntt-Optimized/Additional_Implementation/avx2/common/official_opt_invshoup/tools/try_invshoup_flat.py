#!/usr/bin/env python3
"""SUPERCOP do-part `try` emulation on installed campaign trees (no timing; nothing written to
the campaign).  Front end of common/official_opt_keccak/tools/export_keccak_flat.py try_tree()
(imported unchanged): every .c/.s of each tree compiled with each okc-amd64 line and do-part's
-DSUPERCOP / -DCRYPTO_NAMESPACE flags, try-small / try linked with knownrandombytes.o, checksums
compared with the pinned crypto_kem/ntruplus<N>/checksum{small,big}.  The same shape as the HT
flat-supercop-try.json records (which used a scratch script around the same function).

  try_invshoup_flat.py --param N --campaign-root C --tree NAME [--tree NAME ...] --output out.json
"""
import argparse
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "official_opt_keccak/tools"))
import export_keccak_flat as K  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--campaign-root", type=Path, required=True)
    ap.add_argument("--pristine", type=Path, default=Path("/home/nuc/src/supercop-pristine-20260831"))
    ap.add_argument("--machine", default="nucpromtlhcubinucai1ummsb209")
    ap.add_argument("--version", default="20260831")
    ap.add_argument("--tree", action="append", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    args.supercop = args.campaign_root.resolve()
    lines = K.compilers(args.supercop, args.machine)
    impl = args.supercop / f"crypto_kem/ntruplus{args.param}"
    out = {"campaign": str(args.supercop),
           "class": "SUPERCOP do-part try emulation (no timing, nothing written to the campaign)",
           "date": str(date.today()),
           "expected": {k: (args.pristine / f"crypto_kem/ntruplus{args.param}/checksum{k}").read_text().strip()
                        for k in ("small", "big")},
           "method": "common/official_opt_keccak/tools/export_keccak_flat.py try_tree() via "
                     "common/official_opt_invshoup/tools/try_invshoup_flat.py on each installed campaign tree",
           "okc_amd64": lines, "trees": {}}
    with tempfile.TemporaryDirectory() as tmp:
        for name in args.tree:
            res = K.try_tree(impl / name, name, args.param, args, lines, Path(tmp))
            out["trees"][name] = {"per_compiler": {
                e["compiler"].split()[3]: {"compile_errors": len(e["compile_errors"]), "warnings": len(e["warnings"]),
                                           "checksumsmall_ok": e["try"].get("small", {}).get("checksum") == out["expected"]["small"],
                                           "checksumbig_ok": e["try"].get("big", {}).get("checksum") == out["expected"]["big"],
                                           "pass": e["pass"]} for e in res}}
    out["pass"] = all(c["pass"] for t in out["trees"].values() for c in t["per_compiler"].values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: {c: v["pass"] for c, v in t["per_compiler"].items()} for k, t in out["trees"].items()}))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
