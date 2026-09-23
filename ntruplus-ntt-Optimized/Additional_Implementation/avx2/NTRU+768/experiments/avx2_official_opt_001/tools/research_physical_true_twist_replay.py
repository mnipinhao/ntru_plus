#!/usr/bin/env python3
"""Derive the true-y CT tree from physical AVX2 input and route order."""

from dataclasses import dataclass

from probe_inverse_ct_gauge import Q, route
from research_true_twist_repair_v2 import FACTORS, verified


@dataclass(frozen=True)
class Node:
    leaves: frozenset
    degree: int
    n: int
    xi: int
    zeta: int
    k: int


def build():
    owners = verified(FACTORS)['physical_owners']
    mem = [[Node(frozenset((row['leaf'],)), row['degree'], 1,
                 row['leaf'], 1, 0)
            for row in owners[16 * vec:16 * vec + 16]]
           for vec in range(48)]
    ledger = []
    tree = {}
    for stage in (6, 5, 4, 3, 2):
        new = [None] * 48
        stage_rows = []
        for packet in range(6):
            upper, lower = [], []
            for pair in range(4):
                a = mem[8 * packet + pair]
                b = mem[8 * packet + pair + 4]
                high, low, rows = [], [], []
                for aa, bb in zip(a, b):
                    assert aa.degree == bb.degree and aa.k == bb.k
                    assert aa.n == bb.n and aa.leaves.isdisjoint(bb.leaves)
                    n = 2 * aa.n
                    zeta = bb.xi * pow(aa.xi, -1, Q) % Q
                    assert pow(zeta, n, Q) == 1 and pow(zeta, n // 2, Q) == Q - 1, (
                        stage, packet, pair, aa, bb, zeta)
                    if aa.n > 1:
                        assert zeta * zeta % Q == aa.zeta == bb.zeta, (
                            stage, packet, pair, aa, bb, zeta)
                    node = Node(aa.leaves | bb.leaves, aa.degree, n,
                                aa.xi, zeta, aa.k)
                    prior = tree.setdefault(node.leaves,
                                            (aa.leaves, bb.leaves))
                    assert prior == (aa.leaves, bb.leaves)
                    high.append(node)
                    low.append(Node(node.leaves, node.degree, n,
                                    node.xi, zeta, aa.k + n // 2))
                    rows.append({'xi': node.xi, 'zeta': zeta, 'k': aa.k,
                                 'twiddle': pow(zeta, -aa.k, Q),
                                 'leaves': node.leaves})
                upper.append(high)
                lower.append(low)
                stage_rows.append(rows)
            outputs = upper + lower
            if stage == 2:
                new[8 * packet:8 * packet + 8] = outputs
            else:
                for pair in range(4):
                    lo, hi = route(stage, outputs[2 * pair], outputs[2 * pair + 1])
                    new[8 * packet + pair] = lo
                    new[8 * packet + pair + 4] = hi
        mem = new
        ledger.append(stage_rows)
    return mem, ledger, tree


def assign_kinds(mem, tree):
    """Lay the mixed recipe onto physical upper/lower child ownership."""
    from research_twiddle_half_absorption import RECIPE

    kinds = {}

    def visit(leaves, kind):
        old = kinds.setdefault(leaves, kind)
        assert old == kind
        if kind == 'U1':
            assert len(leaves) == 1
            return
        upper, lower, _, _ = RECIPE[kind]
        a, b = tree[leaves]
        visit(a, upper)
        visit(b, lower)

    roots = {node.leaves for vector in mem for node in vector}
    assert len(roots) == 6 and all(len(group) == 32 for group in roots)
    for group in roots:
        visit(group, 'H32')
    assert len(kinds) == len(tree) + 192
    return kinds


if __name__ == '__main__':
    mem, stages, tree = build()
    kinds = assign_kinds(mem, tree)
    print({'stages': [len(stage) for stage in stages],
           'final_n': sorted({node.n for vector in mem for node in vector}),
           'distinct_final_xi': len({node.xi for vector in mem for node in vector}),
           'kinded_nodes': len(kinds)})
