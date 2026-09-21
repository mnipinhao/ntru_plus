#!/usr/bin/env python3
"""Caller-specific, pre-wrap range proof. No production sources are modified.

Exact frontend enumeration; conservative interval propagation thereafter.
An interval bound is not a claim that its endpoint is reachable.
"""
import functools
import hashlib
import itertools
import json
from pathlib import Path

import generate_tile4 as gt

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean/avx2-gt32-clean"
Q = 3457
LEDGER = []


def checked(name, values):
    values = tuple(values)
    lo, hi = min(values), max(values)
    if not -32768 <= lo <= hi <= 32767:
        raise ArithmeticError(f"proof insufficient, not an overflow witness: {name}: {lo, hi}")
    LEDGER.append({"operation": name, "interval": [lo, hi], "i16_safe": True})
    return max(abs(lo), abs(hi))


def mont(x, w):
    """VPMULLW intentional wrap, signed VPMULHW, unwrapped VPSUBW."""
    assert -32768 <= x <= 32767 and -32768 <= w <= 32767
    low = gt.signed16(x * gt.signed16(w * gt.QINV))
    result = (x * w >> 16) - (low * Q >> 16)
    assert -32768 <= result <= 32767, (x, w, result)
    assert (result * 65536 - x * w) % Q == 0
    return result


@functools.lru_cache(None)
def mont_bound(bound, factor):
    return max(abs(mont(x, factor)) for x in range(-bound, bound + 1))


def frontend():
    rows = [[0] * 32 for _ in range(6)]
    for branch, t in itertools.product(range(2), range(32)):
        streams = []
        for n3 in range(3):
            n = (64*n3 + 33*t) % 96
            w = gt.centered(pow(gt.BRANCH_SCALE[branch], -n, Q) * gt.R)
            splits = [l - 722*h if branch == 0 else l + 723*h
                      for l, h in itertools.product(range(-1, 2), repeat=2)]
            checked(f"frontend/b{branch}/q{t}/n3{n3}/top", splits)
            streams.append(sorted({mont(x, w) for x in splits}))
        operations = {name: [] for name in ("x1-x2", "omega", "x0+x1", "sum",
                                            "x0-x2", "plus", "x0-x1", "minus")}
        for x0, x1, x2 in itertools.product(*streams):
            d = x1-x2
            assert -32768 <= d <= 32767
            omega = mont(d, -886)
            vals = (d, omega, x0+x1, x0+x1+x2, x0-x2,
                    x0-x2+omega, x0-x1, x0-x1-omega)
            for name, value in zip(operations, vals):
                operations[name].append(value)
        for name, values in operations.items():
            checked(f"frontend/b{branch}/q{t}/{name}", values)
        for k3, name in enumerate(("sum", "plus", "minus")):
            rows[2*k3+branch][t] = max(map(abs, operations[name]))
    return rows


def forward(rows):
    result, stages = [], []
    for tile, row in enumerate(rows):
        row = row[:]
        tile_stages = []
        for stage in range(1, 6):
            distance = 32 >> stage
            for base in range(0, 32, 2*distance):
                factor = gt.mont_root(gt.forward_power(stage, base))
                for j in range(distance):
                    a, b = base+j, base+j+distance
                    product = row[b] if stage == 1 else mont_bound(row[b], factor)
                    checked(f"tile{tile}/D{distance}/q{b}/product", [-product, product])
                    bound = row[a] + product
                    checked(f"tile{tile}/D{distance}/q{a},{b}/add-sub", [-bound, bound])
                    row[a] = row[b] = bound
            tile_stages.append(row[:])
        result.append(row)
        stages.append(tile_stages)
    return result, stages


def consumers(rows):
    leaves = []
    for tile, row in enumerate(rows):
        for q, bound in enumerate(row):
            # a=h is unsigned canonical but carried in signed i16; b=r lazy.
            # Signed high(product) and signed high(low*q) bounded separately.
            product = (3456*bound + 65535)//65536 + 1729
            checked(f"B3/t{tile}/q{q}/h*r", [-product, product])
            lam = gt.lambda_montgomery(tile//2, q, tile%2)
            raw, normalized = [], []
            for c in range(4):
                wrapped, direct = 3-c, c+1
                acc = 0
                for k in range(wrapped):
                    acc += product
                    checked(f"B3/t{tile}/q{q}/c{c}/wrapped{k}", [-acc, acc])
                if wrapped:
                    acc = mont_bound(acc, lam)
                    checked(f"B3/t{tile}/q{q}/c{c}/lambda", [-acc, acc])
                for k in range(direct):
                    acc += product
                    checked(f"B3/t{tile}/q{q}/c{c}/direct{k}", [-acc, acc])
                raw.append(acc)
                out = mont_bound(acc, gt.centered(gt.R*gt.R))
                normalized.append(out)
                checked(f"B3/t{tile}/q{q}/c{c}/R2", [-out, out])
                checked(f"add-m/t{tile}/q{q}/c{c}", [-out-bound, out+bound])
            leaves.append({"tile": tile, "physical_q": q, "r_m_bound": bound,
                           "h_range": [0,3456], "product_bound": product,
                           "lambda_R": lam, "raw_e_minus1": raw,
                           "e0": normalized, "plus_m": [x+bound for x in normalized]})
    return leaves


def main():
    LEDGER.clear()
    f = frontend()
    terminal, stages = forward(f)
    leaves = consumers(terminal)
    reduced = []
    for x in range(-32768, 32768):
        t = (9*x + 16384) >> 15
        y = x - t*Q  # VPSUBW is intentionally modulo 2^16 if t*q overflows.
        assert -32768 <= y <= 32767
        z = y + (Q if y < 0 else 0)
        assert 0 <= z < Q and z == x % Q
        reduced.append(y)
    source_files = ["encap.c", "ntt.s", "ntt_m.s", "basemul.s", "pack.s"]
    report = {
        "schema": "ntruplus768-encap-range-v1", "status": "proved-safe",
        "scope": "Encap only; no inverse, keygen or arbitrary general forward claim",
        "source_sha256": {p: hashlib.sha256((CLEAN/p).read_bytes()).hexdigest() for p in source_files},
        "input": {"r": [-1,1], "m": [-1,1], "valid_decoded_h": [0,3456]},
        "output_montgomery_exponent": 0,
        "proof_kind": "exact frontend sets; conservative symmetric intervals downstream",
        "frontend_bounds": f, "stage_bounds": stages, "terminal_bounds": terminal,
        "stage_maxima": [max(max(tile[s]) for tile in stages) for s in range(5)],
        "forward_max_abs": max(map(max, terminal)), "consumer_leaves": leaves,
        "basemul_e0_max_abs": max(max(x["e0"]) for x in leaves),
        "post_add_max_abs": max(max(x["plus_m"]) for x in leaves),
        "serializer": {"tested_inputs": 65536, "input": [-32768,32767],
                       "centered_image": [min(reduced),max(reduced)], "canonical": [0,3456]},
        "ledger": LEDGER,
        "raw_representative_equality_required_for_wavefront": True,
        "new_reductions": 0,
        "limitations": ["bounds are not reachable endpoint witnesses",
                        "source-shaped proof; linked differential is a separate gate"]}
    out = ROOT/"generated/tile4_encap_range_closure.json"
    out.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k: report[k] for k in ("status", "stage_maxima", "forward_max_abs",
                                            "basemul_e0_max_abs", "post_add_max_abs")}))


if __name__ == "__main__":
    main()
