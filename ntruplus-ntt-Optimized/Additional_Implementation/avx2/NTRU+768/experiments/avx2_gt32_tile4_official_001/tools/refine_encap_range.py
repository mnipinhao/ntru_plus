#!/usr/bin/env python3
"""Exact marginal reachability for small-input forward; not a binary proof.

Independent input support justifies Cartesian products at each butterfly.
Outputs of the SAME butterfly remain correlated and are never combined again
as independent inputs. Different k3 rows are not claimed independent.
"""
import hashlib
import itertools
import json
from pathlib import Path

import generate_encap_range_wavefront as old

gt = old.gt
ROOT = old.ROOT
Q = old.Q


def minkowski(a, b):
    """Exact integer sumset using arbitrary-width bitsets (no FFT rounding)."""
    if len(a) < len(b):
        a, b = b, a
    amin, bmin = min(a), min(b)
    bits = 0
    for x in a:
        bits |= 1 << (x - amin)
    result = 0
    for x in b:
        result |= bits << (x - bmin)
    out = set()
    while result:
        bit = result & -result
        out.add(bit.bit_length() - 1 + amin + bmin)
        result ^= bit
    return out


def main():
    ledger = []
    constants = {str(-886): gt.signed16(-886 * gt.QINV)}
    for a, b in (({-3, 0, 7}, {-4, 1}), ({0}, {-32768, 32767}),
                 (set(range(-9, 10, 2)), set(range(-7, 8, 3)))):
        assert minkowski(a, b) == {x+y for x in a for y in b}

    def record(node, values, method, **extra):
        lo, hi = min(values), max(values)
        if not -32768 <= lo <= hi <= 32767:
            raise ArithmeticError((node, lo, hi))
        ledger.append(dict(node=node, integer_pre_wrap=[lo, hi],
                           cardinality=len(values), method=method,
                           status="proved-safe", **extra))

    rows = [[None] * 32 for _ in range(6)]
    for branch, t in itertools.product(range(2), range(32)):
        streams = []
        for n3 in range(3):
            n = (64*n3 + 33*t) % 96
            w = gt.centered(pow(gt.BRANCH_SCALE[branch], -n, Q) * gt.R)
            constants[str(w)] = gt.signed16(w * gt.QINV)
            split = {l - 722*h if branch == 0 else l + 723*h
                     for l, h in itertools.product((-1, 0, 1), repeat=2)}
            streams.append({old.mont(x, w) for x in split})
        outs = [set(), set(), set()]
        for x, y, z in itertools.product(*streams):
            d = y-z
            assert -32768 <= d <= 32767
            w = old.mont(d, -886)
            assert all(-32768 <= v <= 32767 for v in (x+y, x-z, x-y))
            for dest, value in zip(outs, (x+y+z, x-z+w, x-y-w)):
                dest.add(value)
        for k3, values in enumerate(outs):
            rows[2*k3+branch][t] = values
            record(f"frontend/b{branch}/k{k3}/q{t}", values,
                   "exact independent six-coefficient enumeration", scale=0)

    stages = [0]*5
    terminal = []
    for tile, row in enumerate(rows):
        support = [{t} for t in range(32)]
        for stage in range(1, 6):
            distance = 32 >> stage
            for base in range(0, 32, 2*distance):
                factor = gt.mont_root(gt.forward_power(stage, base))
                for j in range(distance):
                    a, b = base+j, base+j+distance
                    assert support[a].isdisjoint(support[b])
                    rhs = row[b] if stage == 1 else {old.mont(v, factor) for v in row[b]}
                    name = f"tile{tile}/D{distance}/q{a},{b}"
                    record(name+"/multiply", rhs, "exact fixed-constant image",
                           constant_R=factor if stage != 1 else None,
                           input_interval=[min(row[b]), max(row[b])], scale=0)
                    plus = minkowski(row[a], rhs)
                    minus = minkowski(row[a], {-v for v in rhs})
                    for suffix, values in (("plus", plus), ("minus", minus)):
                        record(name+"/"+suffix, values, "exact disjoint-support sumset",
                               independent_support=[sorted(support[a]), sorted(support[b])],
                               scale=0)
                        stages[stage-1] = max(stages[stage-1], abs(min(values)), abs(max(values)))
                    row[a], row[b] = plus, minus
                    support[a] = support[b] = support[a] | support[b]
                    if stage != 1:
                        constants[str(factor)] = gt.signed16(factor * gt.QINV)
        terminal.append([max(abs(min(v)), abs(max(v))) for v in row])

    old.LEDGER.clear()
    leaves = old.consumers(terminal)
    for leaf in leaves:
        factor = leaf['lambda_R']
        constants[str(factor)] = gt.signed16(factor * gt.QINV)
    factor = gt.centered(gt.R*gt.R)
    constants[str(factor)] = gt.signed16(factor * gt.QINV)
    # Full signed-domain macro identity checks for all encountered constants.
    for factor in map(int, constants):
        for x in range(-32768, 32768):
            old.mont(x, factor)
    serializer = []
    for x in range(-32768, 32768):
        quotient = (9*x + 16384) >> 15
        y = gt.signed16(x - gt.signed16(quotient*Q))
        assert -Q < y < Q
        z = y + (Q if y < 0 else 0)
        assert z == x % Q
        serializer.append(y)
    sources = [Path(__file__), Path(old.__file__), Path(gt.__file__)]
    sources += [old.CLEAN / s for s in ('ntt.s', 'ntt_m.s', 'basemul.s', 'pack.s', 'encap.c')]
    report = dict(schema="encap-range-refinement-v1", status="proved-safe-model",
                  scope="768 Encap independent ternary coefficients; no new ASM",
                  source_sha256={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):
                                 hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                  stage_exact_marginal_maxima=stages, old_conservative_maxima=[9844,11478,12674,14398,15605],
                  constants_QINV=constants, full_domain_constant_checks=len(constants)*65536,
                  terminal_bounds=terminal, ledger=ledger,
                  consumer_method="conservative asymmetric h*r interval; not exact reachability",
                  consumer_ledger=old.LEDGER, consumer_leaves=leaves,
                  post_add_bound=max(max(x['plus_m']) for x in leaves),
                  serializer=dict(inputs=65536, image=[min(serializer),max(serializer)], exact_mod_q=True),
                  limitations=["Not Isabelle/SMT certified; Python assertions must be enabled",
                               "Exact marginals over independent ternary input superset, not joint output reachability",
                               "No full machine/linked-binary conformance proof",
                               "Consumer interval endpoints need not be reachable"])
    (ROOT/'generated/tile4_encap_range_refined.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','stage_exact_marginal_maxima','post_add_bound','full_domain_constant_checks')}))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Proof checks require Python without -O')
    main()
