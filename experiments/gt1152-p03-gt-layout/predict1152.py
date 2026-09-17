"""Derive the predicted NTRU+1152 GT output layout from the measured 864 one.

probe864.py measured the real NTRU+864 GT forward on this host.  This script
carries that result to 1152 and states exactly what must still be verified once
the eight-bank forward exists.

Why the leaf ordering carries over
----------------------------------
The GT leaf ordering -- which of the 288 leaves lands at (top, row, halfcol,
lane) -- is fixed by .Lntt_one_bank plus the 9-row x 16-column enumeration.
Neither depends on the component count or on the leaf degree; component only
selects which branch of a leaf a slot holds.  The port copies .Lntt_one_bank
byte-identically, so the ordering is the same permutation.

What changes is only the address arithmetic: 3 components -> 4.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GT864 = REPO / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
REF = REPO / "ntruplus-ntt-Optimized/Reference_Implementation"

Q = 3457


def s16(x):
    x &= 0xFFFF
    return x - 0x10000 if x >= 0x8000 else x


def zetas(param):
    text = (REF / f"NTRU+{param}/ntt.c").read_text()
    body = re.search(r"const int16_t zetas\[288\]\s*=\s*\{(.*?)\};", text, re.S).group(1)
    return [int(t) for t in re.findall(r"-?\d+", body)]


def layout(n, deg, components):
    """int16 index of (top, row, halfcol, component, lane) for a GT output."""
    half = n // 2
    row_stride = deg * 16          # one row = 16 columns x deg branches
    halfcol_stride = deg * 8
    out = {}
    for top in range(2):
        for row in range(9):
            for halfcol in range(2):
                for component in range(components):
                    for lane in range(8):
                        idx = (top * half + row * row_stride
                               + halfcol * halfcol_stride + component * 8 + lane)
                        out[(top, row, halfcol, component, lane)] = idx
    return out


def main():
    perm = [int(x) for x in (HERE / "perm864.txt").read_text().split()]
    assert len(perm) == 288 and sorted(perm) == list(range(288))

    report = {"measured_864": {}, "predicted_1152": {}, "checks": []}

    def check(name, ok, detail):
        report["checks"].append({"check": name, "pass": bool(ok), "detail": detail})
        print(f"[{'pass' if ok else 'FAIL'}] {name}: {detail}")
        return ok

    # ---- 864, measured -----------------------------------------------------
    lay864 = layout(864, 3, 3)
    ok = sorted(lay864.values()) == list(range(864))
    check("864/layout_is_bijection", ok,
          "index = top*432 + row*48 + halfcol*24 + component*8 + lane covers "
          "0..863 exactly once")
    report["measured_864"] = {
        "formula": "top*432 + row*48 + halfcol*24 + component*8 + lane",
        "components": 3,
        "row_stride_int16": 48,
        "halfcol_stride_int16": 24,
        "top_stride_int16": 432,
        "store_stride_bytes": 96,
    }

    # ---- 1152, predicted ---------------------------------------------------
    lay1152 = layout(1152, 4, 4)
    ok = sorted(lay1152.values()) == list(range(1152))
    check("1152/layout_is_bijection", ok,
          "index = top*576 + row*64 + halfcol*32 + component*8 + lane covers "
          "0..1151 exactly once")
    report["predicted_1152"] = {
        "formula": "top*576 + row*64 + halfcol*32 + component*8 + lane",
        "components": 4,
        "row_stride_int16": 64,
        "halfcol_stride_int16": 32,
        "top_stride_int16": 576,
        "store_stride_bytes": 128,
        "banks": 8,
        "bank_base_bytes": [256 * b for b in range(8)],
        "tail_base_bytes": 2048,
        "scratch_bytes": 2304,
    }

    # ---- the leaf zeta table transfers ------------------------------------
    z864, z1152 = zetas(864), zetas(1152)
    check("zetas_identical", z864 == z1152,
          "reference zetas[288] agree between 864 and 1152")

    # leaf k uses zetas[144 + k//2], sign by k%2, in BOTH parameter sets:
    # 864 poly_basemul loops N/6=144 over blocks of 2 degree-3 leaves,
    # 1152 loops N/8=144 over blocks of 2 degree-4 leaves.
    def leaf_zeta(z, k):
        return z[144 + k // 2] if k % 2 == 0 else s16(-z[144 + k // 2])

    gt_order_864 = [leaf_zeta(z864, p) for p in perm]
    gt_order_1152 = [leaf_zeta(z1152, p) for p in perm]

    table = [int(t) for t in re.findall(
        r"-?\d+",
        re.search(r"basemul_zetas\[36\]\[8\]\s*=\s*\{(.*?)\};",
                  (GT864 / "base_tables.h").read_text(), re.S).group(1))]

    check("864/basemul_zetas_matches_measured_permutation",
          gt_order_864 == table,
          "base_tables.h equals the reference leaf zetas reordered by the "
          "measured GT permutation, an independent confirmation of both")
    check("1152/basemul_zetas_transfers_verbatim",
          gt_order_1152 == table,
          "the same table is correct for 1152, so base_tables.h is copied "
          "unchanged")

    # ---- what the pack has to do ------------------------------------------
    grp = perm[:8]
    scatter = {}
    for deg, n in ((3, 864), (4, 1152)):
        starts = sorted(deg * k for k in grp)
        gaps = sorted({b - a for a, b in zip(starts, starts[1:])})
        scatter[n] = {
            "leaf_indices": grp,
            "natural_coefficient_starts": starts,
            "gaps": gaps,
            "int16_per_leaf": deg,
            "bytes_per_leaf_stored": deg * 2,
            "bytes_per_leaf_packed_12bit": deg * 12 / 8,
        }
    report["pack_scatter"] = scatter

    print("\npack scatter for one GT vector (8 lanes = 8 leaves):")
    for n, s in scatter.items():
        print(f"  {n}: natural starts {s['natural_coefficient_starts']}  "
              f"gap {s['gaps']}  per-leaf {s['bytes_per_leaf_stored']} B stored / "
              f"{s['bytes_per_leaf_packed_12bit']} B packed")

    report["pass"] = all(c["pass"] for c in report["checks"])
    (HERE / "layout-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"\n{'PASS' if report['pass'] else 'FAIL'} -> layout-report.json")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
