#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

PROFILES = ("A", "D", "S", "G", "DS", "DG", "SG", "DSG")
RANGES = {
    "D": ("ntruplus768_unpack_m_body_avx2", "ntruplus768_unpack_m_avx2"),
    "S": ("ntruplus768_basemul_scale_m_avx2",
          "ntruplus768_basemul_general_m_avx2"),
    "G": ("ntruplus768_basemul_general_m_avx2",
          "ntruplus768_basemul_f0_j1_avx2"),
}

def symbols(path: Path) -> dict[str, int]:
    text = subprocess.check_output(["nm", "-n", str(path)], text=True)
    return {f[2]: int(f[0], 16) for line in text.splitlines()
            if len((f := line.split())) == 3}

def digest(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--clean", type=Path, required=True)
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--base", choices=("clean", "db"), default="clean")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    a = p.parse_args()
    clean, db = a.clean.read_bytes(), a.db.read_bytes()
    cs, ds = symbols(a.clean), symbols(a.db)
    for start, end in RANGES.values():
        if (cs[start], cs[end]) != (ds[start], ds[end]):
            raise SystemExit(f"043 symbol mismatch: {start}")
    # In the frozen PIE the executable LOAD segment has file offset == VA.
    for name in {x for pair in RANGES.values() for x in pair}:
        if cs[name] >= len(clean): raise SystemExit("unexpected ELF mapping")
    a.output.mkdir(parents=True, exist_ok=True)
    images = {}
    for profile in PROFILES:
        image = bytearray(clean if a.base == "clean" else db)
        changed = []
        for factor, (start, end) in RANGES.items():
            enabled = factor in profile
            replacement = db if enabled else clean
            if (a.base == "clean" and enabled) or (a.base == "db" and not enabled):
                lo, hi = cs[start], cs[end]
                image[lo:hi] = replacement[lo:hi]
                changed.append({"factor": factor, "enabled": enabled,
                                "start": hex(lo), "end": hex(hi),
                                "bytes": hi - lo})
        path = a.output / f"measure-{profile}"
        path.write_bytes(image)
        path.chmod(0o755)
        images[profile] = {"sha256": digest(image), "changed_ranges": changed}
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps({
        "schema": "gt32-decap-ltc-044-patched-043-v1",
        "base": a.base,
        "clean_sha256": digest(clean), "db_sha256": digest(db),
        "symbol_addresses": {name: cs[name] for name in
            sorted({x for pair in RANGES.values() for x in pair})},
        "images": images}, indent=2) + "\n")

if __name__ == "__main__": main()
