#!/usr/bin/env python3
"""Extract the in-repo SHAKE256 known-answer subset from NIST CAVP.

Source: NIST CAVP "SHA-3 / SHAKE byte-oriented test vectors" (FIPS 202),
  https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/documents/sha3/shakebytetestvectors.zip
  zip sha256 debfebc3157b3ceea002b84ca38476420389a3bf7e97dc5f53ea4689a16de4c7 (CAVS 19.0, generated 2016-01-28)
Only SHAKE256ShortMsg.rsp, SHAKE256LongMsg.rsp and SHAKE256VariableOut.rsp
are read (their sha256 are pinned below).  The subset keeps the lengths that
matter for a 136-byte-rate x1 SHAKE256 and the NTRU+ call shapes:

  ShortMsg  (256-bit output): message bytes 0..8, 16, 31..33, 63..65,
            127..129, 133..141, 176, 177, 255, 256, 268..272
  LongMsg   (256-bit output): the 1st, 2nd and 7th..12th messages
            (273, 410, 1095, 1232, 1369, 1506, 1643, 1780 bytes; they bracket
            the NTRU+ hash_f/g inputs 1153 / 1297 / 1729)
  VariableOut (32-byte message): the first vector of every output length in
            2, 3, 31..33, 64, 127, 128, 134..138, 191..193, 215..217,
            223..225, 247..250 bytes, and all six 250-byte vectors

Output: tests/vectors/shake256_cavp_subset.txt, one vector per line
  <inlen> <outlen> <msg hex, "-" if empty> <output hex>

  extract_shake256_vectors.py --zip shakebytetestvectors.zip           # write
  extract_shake256_vectors.py --zip shakebytetestvectors.zip --check   # verify
"""

import argparse
import hashlib
import io
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve()
OUT = HERE.parents[1] / "tests/vectors/shake256_cavp_subset.txt"
URL = ("https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/"
       "documents/sha3/shakebytetestvectors.zip")
ZIP_SHA256 = "debfebc3157b3ceea002b84ca38476420389a3bf7e97dc5f53ea4689a16de4c7"
RSP_SHA256 = {
    "SHAKE256ShortMsg.rsp": "a21dd9180a0f0139fa8d4056919f8194ddaca2f36dc5aafa70723682099d64f5",
    "SHAKE256LongMsg.rsp": "f7881838fa013853993bf7e0814de0ab53ee93a4dbc2b7bce5bed7cc81e6985f",
    "SHAKE256VariableOut.rsp": "90fb72336900b22284477b76d0868fc2822ae42a114079c6c8a7fbda12eb52ca",
}
SHORT = set(range(0, 9)) | {16, 31, 32, 33, 63, 64, 65, 127, 128, 129} | set(range(133, 142)) | \
    {176, 177, 255, 256} | set(range(268, 273))
LONG_INDEX = {0, 1, 6, 7, 8, 9, 10, 11}
VAROUT = {2, 3, 31, 32, 33, 64, 127, 128} | set(range(134, 139)) | set(range(191, 194)) | \
    set(range(215, 218)) | set(range(223, 226)) | set(range(247, 251))


def records(text):
    rec = {}
    for line in text.splitlines() + [""]:
        line = line.strip()
        if not line:
            if "Msg" in rec:
                yield rec
            rec = {}
        elif "=" in line and not line.startswith(("#", "[")):
            k, v = (s.strip() for s in line.split("=", 1))
            rec[k] = v


def build(zip_path: Path) -> str:
    blob = zip_path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != ZIP_SHA256:
        raise SystemExit("zip sha256 mismatch")
    z = zipfile.ZipFile(io.BytesIO(blob))
    texts = {}
    for name, digest in RSP_SHA256.items():
        member = next(n for n in z.namelist() if n.endswith(name))
        data = z.read(member)
        if hashlib.sha256(data).hexdigest() != digest:
            raise SystemExit(f"{name} sha256 mismatch")
        texts[name] = data.decode()
    rows = []
    for rec in records(texts["SHAKE256ShortMsg.rsp"]):
        n = int(rec["Len"]) // 8
        if n in SHORT:
            rows.append(("ShortMsg", n, 32, rec["Msg"][:2 * n], rec["Output"]))
    for i, rec in enumerate(records(texts["SHAKE256LongMsg.rsp"])):
        if i in LONG_INDEX:
            n = int(rec["Len"]) // 8
            rows.append(("LongMsg", n, 32, rec["Msg"], rec["Output"]))
    seen = set()
    for rec in records(texts["SHAKE256VariableOut.rsp"]):
        n = int(rec["Outputlen"]) // 8
        if n in VAROUT and (n not in seen or n == 250):
            seen.add(n)
            rows.append(("VariableOut", 32, n, rec["Msg"], rec["Output"]))
    for _, inlen, outlen, msg, out in rows:
        if len(msg) != 2 * inlen or len(out) != 2 * outlen:
            raise SystemExit("length mismatch in CAVP record")
    lines = ["# SHAKE256 known-answer subset (FIPS 202), extracted by",
             "# common/official_opt_keccak/tools/extract_shake256_vectors.py from NIST CAVP",
             f"# {URL}",
             f"# zip sha256 {ZIP_SHA256}"]
    lines += [f"# {name} sha256 {digest}" for name, digest in RSP_SHA256.items()]
    counts = {k: sum(r[0] == k for r in rows) for k in ("ShortMsg", "LongMsg", "VariableOut")}
    lines.append("# vectors: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    lines.append("# format: <inlen> <outlen> <msg hex or -> <output hex>")
    lines += [f"{inlen} {outlen} {msg or '-'} {out}" for _, inlen, outlen, msg, out in rows]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = build(args.zip)
    if args.check:
        if OUT.read_text() != text:
            print("MISMATCH vs regeneration", file=sys.stderr)
            return 1
        print(f"ok {OUT} sha256={hashlib.sha256(text.encode()).hexdigest()}")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT} ({len(text.splitlines())} lines) sha256={hashlib.sha256(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
