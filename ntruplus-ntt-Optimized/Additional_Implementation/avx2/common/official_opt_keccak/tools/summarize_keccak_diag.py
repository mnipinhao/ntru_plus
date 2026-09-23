#!/usr/bin/env python3
"""Tabulate the mlkem-native-Keccak same-ELF diagnostics of NTRU+768/864/1152.

Reads <experiment>/results/keccak-diag-{normal,reversed}-<tag>/summary.json
of the three experiments and prints Markdown tables (pooled StQ2 delta and
favourable launches, normal / reversed link order) plus the Official pooled
StQ2 per region; --json writes the same numbers.  supercop-derived, not Native.
"""

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve()
AVX2 = HERE.parents[3]
EXPERIMENTS = {768: AVX2 / "NTRU+768/experiments/avx2_official_opt_freeze_001",
               864: AVX2 / "NTRU+864/experiments/avx2_official_opt_001",
               1152: AVX2 / "NTRU+1152/experiments/avx2_official_opt_001"}
ROWS = [("permute", "mlkem_o3-official"), ("permute", "mlkem_o2-mlkem_o3"),
        ("hash_f", "mlkem_o3-official"), ("hash_f", "mlkem_o2-mlkem_o3"),
        ("hash_g", "mlkem_o3-official"), ("hash_g", "mlkem_o2-mlkem_o3"), ("hash_g", "mlkem_o2-official"),
        ("hash_h", "mlkem_o3-official"), ("hash_h", "mlkem_o2-mlkem_o3"),
        ("keypair", "base-official"), ("keypair", "base_keccak-official"), ("keypair", "base_keccak-base"),
        ("keypair", "keccak_only-official"),
        ("encap", "base-official"), ("encap", "base_keccak-official"), ("encap", "base_keccak-base"),
        ("encap", "keccak_only-official"),
        ("decap", "base-official"), ("decap", "base_keccak-official"), ("decap", "base_keccak-base"),
        ("decap", "keccak_only-official")]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", default="20260923")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    data, out = {}, {}
    for p, root in EXPERIMENTS.items():
        for order in ("normal", "reversed"):
            path = root / f"results/keccak-diag-{order}-{args.tag}/summary.json"
            data[p, order] = json.loads(path.read_text())
    lines = ["| Region | Delta | " + " | ".join(f"{p} normal | {p} reversed" for p in EXPERIMENTS) + " |",
             "| --- | --- | " + " | ".join("---: | ---:" for _ in EXPERIMENTS) + " |"]
    for region, delta in ROWS:
        cells = []
        for p in EXPERIMENTS:
            for order in ("normal", "reversed"):
                d = data[p, order]["regions"][region]["deltas"][delta]
                cells.append(f"{d['pooled_stq2_delta']:+.0f} ({d['favourable_launches']}/{d['launches']})")
                out.setdefault(str(p), {}).setdefault(region, {}).setdefault(delta, {})[order] = {
                    "pooled_stq2_delta": round(d["pooled_stq2_delta"], 1),
                    "favourable_launches": d["favourable_launches"], "launches": d["launches"],
                    "launch_delta_median": round(d["launch_delta_quartiles"]["median"], 1)}
        lines.append(f"| {region} | {delta} | " + " | ".join(cells) + " |")
    lines += ["", "| Region | Variant | " + " | ".join(f"{p} normal | {p} reversed" for p in EXPERIMENTS) + " |",
              "| --- | --- | " + " | ".join("---: | ---:" for _ in EXPERIMENTS) + " |"]
    for region in ("permute", "hash_f", "hash_g", "hash_h", "keypair", "encap", "decap"):
        names = list(data[768, "normal"]["regions"][region]["variants"])
        for v in names:
            cells = []
            for p in EXPERIMENTS:
                for order in ("normal", "reversed"):
                    s = data[p, order]["regions"][region]["variants"][v]["pooled_stq"][1]
                    cells.append(f"{s:.0f}")
                    out.setdefault(str(p), {}).setdefault(region, {}).setdefault("pooled_stq2", {}) \
                        .setdefault(v, {})[order] = round(s, 1)
            lines.append(f"| {region} | {v} | " + " | ".join(cells) + " |")
    print("\n".join(lines))
    if args.json:
        args.json.write_text(json.dumps({"class": "supercop-derived same-ELF diagnostic; not Native SUPERCOP",
                                         "tag": args.tag, "parameters": out}, indent=2) + "\n")


if __name__ == "__main__":
    main()
