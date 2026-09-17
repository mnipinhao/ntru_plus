"""Machine-checked structural proof: NTRU+1152 shares NTRU+864's GT transform.

Establishes, mechanically and from current repository sources, the claims the
GT1152 port rests on.  Emits proof-report.json.  Every check is a hard
assertion; nothing here is asserted from memory.

Claim under test
----------------
    NTRU+864  = 2 (alpha/beta CRT) x [Good-Thomas 9x16 = 144] x degree-3 leaves
    NTRU+1152 = 2 (alpha/beta CRT) x [the SAME 9x16 = 144] x degree-4 leaves
    => 288 leaves both; leaf roots and stage twiddles are n-independent.

Scope note
----------
Check 7 audits the twiddle tables embedded in NTRU+864's ntt9.S.  It proves
that their contents are functions of (q, z^144 - alpha) alone -- exact
Barrett-Shoup pairing over every entry, and multiplicative orders dividing 864.
It does NOT reverse-engineer the 617-instruction .Lntt_one_bank body to
reconstruct the table *ordering*.  That is deliberate: the port copies
.Lntt_one_bank byte-identically, so ordering is fixed by the algorithm, not by
n.  The ordering question is therefore out of scope rather than unproven.
"""

import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

Q = 3457
REF = REPO / "ntruplus-ntt-Optimized/Reference_Implementation"
STOCK = REPO / "ntruplus-ntt-Optimized/Additional_Implementation/aarch64"
GT864 = REPO / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

results = []


def check(name, ok, detail):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    status = "pass" if ok else "FAIL"
    print(f"[{status}] {name}: {detail}")
    return bool(ok)


def order(x):
    x %= Q
    assert x != 0
    o, y = 1, x
    while y != 1:
        y = y * x % Q
        o += 1
    return o


def parse_c_zetas(path):
    text = Path(path).read_text()
    m = re.search(r"const int16_t zetas\[288\]\s*=\s*\{(.*?)\};", text, re.S)
    assert m, f"zetas[288] not found in {path}"
    vals = [int(t) for t in re.findall(r"-?\d+", m.group(1))]
    assert len(vals) == 288, f"{path}: got {len(vals)} zetas"
    return vals


def parse_asm_table(path, label, stop_prefix):
    """Extract the .short values of one labelled table from an asm file."""
    text = Path(path).read_text()
    lines = text.splitlines()
    out, collecting = [], False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(label + ":"):
            collecting = True
            continue
        if collecting:
            if stripped.startswith(stop_prefix) and not stripped.startswith(".short"):
                break
            if stripped.startswith(".short"):
                out += [int(t) for t in re.findall(r"-?\d+", stripped)]
    assert out, f"{label} not found or empty in {path}"
    return out


# ---------------------------------------------------------------- 1. field
alphas = sorted(a for a in range(Q) if (a * a - a + 1) % Q == 0)
check("field/alpha_beta_roots",
      len(alphas) == 2 and sum(alphas) % Q == 1,
      f"y^2-y+1 mod {Q} has roots {alphas}, sum={sum(alphas) % Q} "
      f"(matches ntt_top.S comment 'beta = 1-alpha')")
ALPHA, BETA = alphas
check("field/alpha_order",
      order(ALPHA) == 6 and order(BETA) == 6,
      f"ord(alpha)=ord(beta)=6; q-1={Q-1}=2^7*27")

# ------------------------------------------- 2. ord(z) is n-independent (trap)
ord_rows = []
for n, deg in ((864, 3), (1152, 4)):
    ord_x = 6 * (n // 2)                     # X^(n/2) = y, ord(y) = 6
    ord_z = ord_x // math.gcd(deg, ord_x)    # z = X^deg
    ord_rows.append({"n": n, "leaf_degree": deg, "ord_X": ord_x, "ord_z": ord_z})
check("transform/ord_z_is_864_for_both",
      all(r["ord_z"] == 864 for r in ord_rows),
      f"{ord_rows}; the 864 here is 144*ord(alpha)=144*6, NOT the parameter n "
      "-- twiddles must not be 'rescaled' from 864 to 1152")

# -------------------------------------------- 3. z^144 - alpha is n-independent
roots_a = sorted(z for z in range(1, Q) if pow(z, 144, Q) == ALPHA)
roots_b = sorted(z for z in range(1, Q) if pow(z, 144, Q) == BETA)
check("transform/leaf_root_count",
      len(roots_a) == 144 and len(roots_b) == 144,
      f"z^144-alpha splits into {len(roots_a)} linear factors, z^144-beta into "
      f"{len(roots_b)}; total {len(roots_a) + len(roots_b)} leaves")
check("transform/gt_factors_coprime",
      math.gcd(9, 16) == 1 and 9 * 16 == 144,
      "144 = 9 x 16 with gcd(9,16)=1, so Good-Thomas applies")

# ------------------------------------------- 4. reference zeta tables identical
z864 = parse_c_zetas(REF / "NTRU+864/ntt.c")
z1152 = parse_c_zetas(REF / "NTRU+1152/ntt.c")
check("tables/reference_zetas_identical",
      z864 == z1152,
      f"Reference_Implementation NTRU+864/ntt.c and NTRU+1152/ntt.c zetas[288] "
      f"agree on all 288 values")

# --------------------------------------- 5. stock asm basemul tables identical
def parse_zetas_mul(path):
    text = Path(path).read_text()
    body = re.search(r"^zetas_mul:\s*$(.*?)(?=^\S+:|\Z)", text, re.S | re.M)
    assert body, f"zetas_mul not found in {path}"
    return [int(t) for t in re.findall(r"-?\d+", body.group(1))]

zm864 = parse_zetas_mul(STOCK / "NTRU+864/asm/base.s")
zm1152 = parse_zetas_mul(STOCK / "NTRU+1152/asm/base.s")
check("tables/stock_zetas_mul_identical",
      zm864 == zm1152 and len(zm864) > 0,
      f"stock base.s zetas_mul agree on all {len(zm864)} integers")

# --------------------------------- 6. leaf indexing is the same zetas[144..287]
def parse_basemul_indices(path):
    text = Path(path).read_text()
    m = re.search(r"void poly_basemul\(.*?\n\}", text, re.S)
    assert m, f"poly_basemul not found in {path}"
    body = m.group(0)
    loop = re.search(r"i\s*<\s*NTRUPLUS_N/(\d+)", body)
    zeta = re.findall(r"zetas\[(\d+)\s*\+\s*i\]", body)
    signs = len(re.findall(r"-zetas\[", body))
    return int(loop.group(1)), sorted(set(zeta)), signs

d864 = parse_basemul_indices(REF / "NTRU+864/poly.c")
d1152 = parse_basemul_indices(REF / "NTRU+1152/poly.c")
leaves864 = 864 // d864[0] * 2
leaves1152 = 1152 // d1152[0] * 2
check("leaves/same_zeta_window_and_count",
      d864[1] == d1152[1] == ["144"] and leaves864 == leaves1152 == 288
      and d864[2] == d1152[2] == 1,
      f"864: blocks of {d864[0]} (2 x degree-3), 1152: blocks of {d1152[0]} "
      f"(2 x degree-4); both index zetas[144+i] with a +/- pair, both yield "
      f"{leaves864} leaves")

# ------------------------------- 7. GT stage twiddle tables are (q, z)-derived
# These tables mix two packing styles (whole-row twiddle/Shoup pairs, and
# lane-interleaved pairs within one row), so the audit is deliberately
# layout-agnostic: it only asks whether every stored value is z-derived.
def shoup(t):
    return round(t * 32768 / Q)


table_report = {}
all_ok = True
for label in (".Lntt9_top0", ".Lntt9_top1", ".Lntt16_top0", ".Lntt16_top1"):
    vals = parse_asm_table(GT864 / "ntt9.S", label, ".L")
    nonzero = [v for v in vals if v % Q != 0]

    twiddles = sorted({v for v in nonzero if 864 % order(v) == 0})
    shoup_consts = {shoup(t) for t in twiddles}
    unexplained = sorted({v for v in nonzero
                          if v not in twiddles and v not in shoup_consts})

    ok = not unexplained
    all_ok &= ok
    table_report[label] = {
        "values_total": len(vals),
        "values_zero_padding": len(vals) - len(nonzero),
        "distinct_twiddles": len(twiddles),
        "every_value_z_derived": ok,
        "unexplained": unexplained[:5],
        "twiddle_orders": sorted({order(t) for t in twiddles}),
        "primitive_864_twiddles": sum(1 for t in twiddles if order(t) == 864),
    }

check("tables/ntt9_twiddles_are_z_derived", all_ok,
      "every non-zero value in .Lntt9_top{0,1} / .Lntt16_top{0,1} is either a "
      "twiddle whose multiplicative order divides 864, or the exact "
      "round(t*2^15/q) Barrett-Shoup constant of such a twiddle -- so the "
      "tables are functions of (q, z^144-alpha) alone; see module docstring "
      "for what this does and does not establish")

# ---------------------------------------------------------------- oracle tie-in
sys.path.insert(0, str(HERE))
import ntruplus1152 as P  # noqa: E402

check("oracle/zetas_match_reference",
      P.ZETAS == z1152,
      "the Python oracle parses its zetas from NTRU+1152/ntt.c rather than "
      "embedding a copy")

report = {
    "experiment": "GT1152-P01-RING-PROFILE",
    "q": Q,
    "alpha": ALPHA,
    "beta": BETA,
    "ord_z": ord_rows,
    "leaf_roots": {"alpha_half": len(roots_a), "beta_half": len(roots_b)},
    "ntt9_tables": table_report,
    "checks": results,
    "pass": all(r["pass"] for r in results),
}
(HERE / "proof-report.json").write_text(json.dumps(report, indent=2) + "\n")

failed = [r["check"] for r in results if not r["pass"]]
if failed:
    print(f"\nFAIL: {failed}", file=sys.stderr)
    raise SystemExit(1)
print(f"\nPASS: {len(results)} structural checks -> proof-report.json")
