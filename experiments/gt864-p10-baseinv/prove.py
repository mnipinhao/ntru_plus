#!/usr/bin/env python3
"""P10 algebra, scale, range, and scalar batch-inversion hard gate."""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
Q = 3457
R = 1 << 16
R_MOD = R % Q
R_INV = pow(R, -1, Q)
QI = -12929
SCALE = -1571
SCALE_HAT = -14891
INPUT_BOUND = 28765
Z_BOUND = 1728


def s16(x: int) -> int:
    return (x + (1 << 15)) % (1 << 16) - (1 << 15)


def redc(x: int) -> int:
    """Exact signed-halfword Montgomery REDC used by the Neon DAG."""
    t = s16(s16(x) * QI)
    numerator = x + t * Q
    assert numerator % R == 0
    y = numerator // R
    assert -(1 << 15) <= y < (1 << 15)
    return y


def mm(a: int, b: int) -> int:
    return redc(a * b)


def sqrdmulh_s16(a: int, b: int) -> int:
    y = (a * b + (1 << 14)) // (1 << 15)
    return max(-(1 << 15), min((1 << 15) - 1, y))


def fixed_scale(a: int) -> int:
    z = s16(a * SCALE)
    t = sqrdmulh_s16(a, SCALE_HAT)
    return s16(z - t * Q)


def redc_bound(abs_x: int) -> int:
    return (abs_x + (1 << 15) * Q + R - 1) // R


def parse_zetas() -> list[list[int]]:
    text = (PROD / "gt864_fr0_basemul_tables.h").read_text()
    body = text.split("gt864_fr0_zetas_mul[36][8] = {", 1)[1].split("};", 1)[0]
    rows = []
    for row in re.findall(r"\{([^{}]+)\}", body):
        values = [int(x) for x in re.findall(r"-?\d+", row)]
        if len(values) == 8:
            rows.append(values)
    assert len(rows) == 36
    return rows


def direct_num(a: int, b: int, c: int, zr: int) -> tuple[tuple[int, int, int], int]:
    u = mm(b, c)
    w = mm(c, c)
    n0 = redc(a * a - u * zr)
    n1 = redc(w * zr - a * b)
    n2 = redc(b * b - a * c)
    h = redc(n2 * b + n1 * c)
    den = redc(h * zr + n0 * a)
    return (n0, n1, n2), den


def mul_cubic(a: tuple[int, int, int], b: tuple[int, int, int], z: int) -> tuple[int, int, int]:
    a0, a1, a2 = a
    b0, b1, b2 = b
    return (
        (a0 * b0 + z * (a1 * b2 + a2 * b1)) % Q,
        (a0 * b1 + a1 * b0 + z * a2 * b2) % Q,
        (a0 * b2 + a1 * b1 + a2 * b0) % Q,
    )


def run_batch(values: list[tuple[int, int, int]], zrs: list[int]) -> tuple[list[tuple[int, int, int]], list[int]]:
    nums: list[tuple[int, int, int]] = []
    den_step_chain = [[0] * 3 for _ in range(12)]
    for tile, ((a, b, c), zr) in enumerate(zip(values, zrs)):
        num, den = direct_num(a, b, c, zr)
        nums.append(num)
        chain, step = divmod(tile, 12)
        den_step_chain[step][chain] = den

    prefix = [[0] * 3 for _ in range(12)]
    prefix[0] = den_step_chain[0][:]
    for step in range(1, 12):
        for chain in range(3):
            prefix[step][chain] = mm(prefix[step - 1][chain], den_step_chain[step][chain])

    if any(x % Q == 0 for x in prefix[11]):
        return [], [x % Q for x in prefix[11]]

    # Corrected inverse3 output has scale R^-1.  Numerically it is exactly
    # the modular inverse of the stored final-prefix value.
    running = [pow(x, -1, Q) for x in prefix[11]]
    assert all(fixed_scale(s16(pow((x * R_INV) % Q, -1, Q) * R % Q)) % Q == y for x, y in zip(prefix[11], running))
    inv_den = [[0] * 3 for _ in range(12)]
    for step in range(11, 0, -1):
        for chain in range(3):
            inv_den[step][chain] = mm(prefix[step - 1][chain], running[chain])
            running[chain] = mm(running[chain], den_step_chain[step][chain])
    inv_den[0] = running

    output: list[tuple[int, int, int]] = []
    for tile, num in enumerate(nums):
        chain, step = divmod(tile, 12)
        di = inv_den[step][chain]
        output.append(tuple(mm(x, di) for x in num))
    return output, [x % Q for x in prefix[11]]


def main() -> None:
    caller = json.loads((PROD / "evidence/caller-range-proof.json").read_text())
    k1 = next(x for x in caller["results"] if x["extra"] == ["main.stage1.node0"])
    assert k1["all_callers_closed"]
    assert k1["forward"]["f"]["abs_peak"] == 28765
    assert k1["forward"]["g"]["abs_peak"] == 26930

    assert R_MOD == Q - 147
    assert R_INV == Q - 682
    assert SCALE % Q == pow(R, -2, Q)
    assert SCALE_HAT == round(SCALE * (1 << 15) / Q)
    order = next(k for k in range(1, Q) if pow(R, k, Q) == 1)
    assert order == 36

    # Scales are exponents of R modulo ord_q(R).
    prefix_scales = [-2]
    for _ in range(1, 12):
        prefix_scales.append((prefix_scales[-1] - 2 - 1) % order)
    assert prefix_scales[-1] == 1
    corrected_chain_inverse_scale = (-1) % order
    for step in range(11, 0, -1):
        assert (prefix_scales[step - 1] + corrected_chain_inverse_scale - 1) % order == 2
        corrected_chain_inverse_scale = (corrected_chain_inverse_scale - 2 - 1) % order
    assert corrected_chain_inverse_scale == 2
    assert (-1 + 2 - 1) % order == 0

    u = redc_bound(INPUT_BOUND * INPUT_BOUND)
    w = u
    n0 = redc_bound(INPUT_BOUND * INPUT_BOUND + u * Z_BOUND)
    n1 = redc_bound(w * Z_BOUND + INPUT_BOUND * INPUT_BOUND)
    n2 = redc_bound(2 * INPUT_BOUND * INPUT_BOUND)
    h = redc_bound((n2 + n1) * INPUT_BOUND)
    den = redc_bound(h * Z_BOUND + n0 * INPUT_BOUND)
    prefix_bounds = [den]
    for _ in range(1, 12):
        prefix_bounds.append(redc_bound(prefix_bounds[-1] * den))
    corrected_inverse = max(abs(fixed_scale(x)) for x in range(-prefix_bounds[-1], prefix_bounds[-1] + 1))
    running = corrected_inverse
    recovered = []
    for step in range(11, 0, -1):
        recovered.append(redc_bound(prefix_bounds[step - 1] * running))
        running = redc_bound(running * den)
    recovered.append(running)
    finish = redc_bound(max(n0, n1, n2) * max(recovered))
    bounds = {
        "input": INPUT_BOUND,
        "u_w": u,
        "n0_n1": max(n0, n1),
        "n2": n2,
        "h": h,
        "determinant": den,
        "prefix": prefix_bounds,
        "corrected_global_inverse": corrected_inverse,
        "recovered_inverse": max(recovered),
        "finish": finish,
    }
    assert bounds == {
        "input": 28765,
        "u_w": 14355,
        "n0_n1": 14733,
        "n2": 26980,
        "h": 20038,
        "determinant": 8724,
        "prefix": [8724, 2890, 2114, 2010, 1997, 1995, 1995, 1995, 1995, 1995, 1995, 1995],
        "corrected_global_inverse": 1741,
        "recovered_inverse": 1994,
        "finish": 2550,
    }
    wide_bounds = {
        "bc": INPUT_BOUND * INPUT_BOUND,
        "n0": INPUT_BOUND * INPUT_BOUND + u * Z_BOUND,
        "n1": w * Z_BOUND + INPUT_BOUND * INPUT_BOUND,
        "n2": 2 * INPUT_BOUND * INPUT_BOUND,
        "h": (n2 + n1) * INPUT_BOUND,
        "determinant": h * Z_BOUND + n0 * INPUT_BOUND,
        "finish": max(n0, n1, n2) * max(recovered),
    }
    correction = (1 << 15) * Q
    assert all(v + correction < (1 << 31) for v in wide_bounds.values())
    assert all(v < (1 << 15) for k, v in bounds.items() if isinstance(v, int))

    # Close the only BaseInv consumers in production Keygen.  finv is paired
    # with Forward(g), and ginv with Forward(f); 28765 is the larger producer
    # bound.  D1 takes two early Montgomery reductions and then a signed-32
    # Barrett reduction.  A 2550 BaseInv representative remains safe and the
    # final D1 value is still strictly inside (-q,q), as required by small
    # ToBytes.
    consumer_product = 28765 * finish
    early0 = redc_bound(2 * consumer_product)
    early1 = redc_bound(consumer_product)
    d1_wide = [
        early0 * Z_BOUND + consumer_product,
        early1 * Z_BOUND + 2 * consumer_product,
        3 * consumer_product,
    ]
    assert max(early0, early1) < (1 << 15)
    assert max(d1_wide) < (1 << 31)
    recip = 621199
    half = 1 << 30
    denominator = 1 << 31
    lo, hi = -max(d1_wide), max(d1_wide)
    d1_min, d1_max, covered = Q, -Q, 0
    first_qhat = (lo * recip + half) // denominator
    last_qhat = (hi * recip + half) // denominator
    for qhat in range(first_qhat, last_qhat + 1):
        bucket_lo = max(lo, -((-qhat * denominator + half - 1) // recip))
        bucket_hi = min(hi, ((qhat + 1) * denominator - half - 1) // recip)
        if bucket_lo > bucket_hi:
            continue
        d1_min = min(d1_min, bucket_lo - qhat * Q)
        d1_max = max(d1_max, bucket_hi - qhat * Q)
        covered += bucket_hi - bucket_lo + 1
    assert covered == hi - lo + 1
    assert -Q < d1_min <= d1_max < Q
    consumer = {
        "other_forward_bound": 28765,
        "baseinv_bound": finish,
        "product": consumer_product,
        "early_REDC": [early0, early1],
        "final_wide": d1_wide,
        "exact_barrett_output": [d1_min, d1_max],
        "exact_integer_inputs_covered": covered,
        "small_tobytes_contract": "pass: output remains strictly inside (-q,q)",
    }

    # Exhaustively establish the fixed multiplication for all signed int16.
    fixed_max = 0
    for a in range(-(1 << 15), 1 << 15):
        y = fixed_scale(a)
        assert (y - a * SCALE) % Q == 0
        fixed_max = max(fixed_max, abs(y))
    assert fixed_max == 2064

    zeta_rows = parse_zetas()
    rng = random.Random(0x503130)
    successful = 0
    failed = 0
    cases = 2000
    for case in range(cases):
        lane = case & 7
        zrs = [row[lane] for row in zeta_rows]
        values = []
        for tile in range(36):
            if case < 8:
                pool = [-INPUT_BOUND, -26930, -1, 0, 1, 26930, INPUT_BOUND]
                values.append(tuple(pool[(case + tile + j) % len(pool)] for j in range(3)))
            else:
                values.append(tuple(rng.randint(-INPUT_BOUND, INPUT_BOUND) for _ in range(3)))
        output, terminal = run_batch(values, zrs)
        if not output:
            failed += 1
            continue
        successful += 1
        for value, inv, zr in zip(values, output, zrs):
            z = (zr * R_INV) % Q
            assert mul_cubic(tuple(x % Q for x in value), tuple(x % Q for x in inv), z) == (1, 0, 0)

    # A forced singular leaf must cause the fixed final-prefix zero test to fail.
    singular = [(1, 0, 0)] * 36
    singular[0] = (0, 0, 0)
    out, terminal = run_batch(singular, [row[0] for row in zeta_rows])
    assert not out and 0 in terminal
    assert successful > 0 and failed >= 0

    result = {
        "gate": "P10 direct-FR0 BaseInv algebra/range",
        "status": "pass",
        "q": Q,
        "montgomery_order": order,
        "scale_ledger": {
            "cofactor": "R^-1",
            "determinant": "R^-2",
            "prefix_after_12": "R^1",
            "inverse3_after_global_correction": "R^-1",
            "recovered_inverse": "R^2",
            "finish": "R0",
        },
        "bounds": bounds,
        "wide_bounds": wide_bounds,
        "D1_consumer_closure": consumer,
        "wide_correction_margin": {k: (1 << 31) - (v + correction) for k, v in wide_bounds.items()},
        "fixed_scale_full_int16_max": fixed_max,
        "random_batches": cases,
        "successful_batches": successful,
        "singular_or_accidentally_singular_batches": failed + 1,
        "producer_evidence": str(PROD / "evidence/caller-range-proof.json"),
    }
    (HERE / "proof-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
