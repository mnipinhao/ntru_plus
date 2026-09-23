#!/usr/bin/env python3
"""Replay Official CT data routes as ownership and price a conservative tail.

This is an instruction/dataflow model, not a linked full inverse kernel.
"""

import hashlib
import json
from pathlib import Path

from probe_inverse_ct_gauge import Q, ROOT, route
from research_full_twisted_pairings import children
from research_twiddle_half_absorption import RECIPE
from research_yang_true_twist import ZETA32
from research_true_twist_repair_v2 import FACTORS, verified

RESULT = ROOT / 'results/yang-true-y-twist-mixed-gauge-vector-schedule-20260923.json'


def ownership():
    factor = verified(FACTORS)
    owners = factor['physical_owners']
    mem = [[(frozenset((row['leaf'],)), row['degree'], 0)
            for row in owners[16 * vector:16 * vector + 16]]
           for vector in range(48)]
    roots = sorted({row['leaf'] for row in owners})
    cohorts = [group for _, top in children(roots, 192)
               for _, group in children(top, 96)]
    subtree_kinds = {}

    def assign(kind, xi, zeta):
        if kind == 'U1':
            return
        n = int(kind[1:])
        members = frozenset(xi * pow(zeta, j, Q) % Q for j in range(n))
        prior = subtree_kinds.setdefault(members, (kind, zeta))
        assert prior == (kind, zeta)
        upper, lower, _, _ = RECIPE[kind]
        assign(upper, xi, zeta * zeta % Q)
        assign(lower, xi * zeta % Q, zeta * zeta % Q)

    for group in cohorts:
        assign('H32', min(group), ZETA32)
    route_ops = {6: 0, 5: 0, 4: 0, 3: 0, 2: 0}
    vector_modes = {str(stage): [] for stage in (6, 5, 4, 3, 2)}
    for stage in (6, 5, 4, 3, 2):
        n = 1 << (7 - stage)
        new = [None] * 48
        for packet in range(6):
            base = packet * 8
            upper, lower = [], []
            for pair in range(4):
                out_a, out_b = [], []
                lane_modes = []
                original_factors, candidate_factors = [], []
                for a, b in zip(mem[base + pair], mem[base + pair + 4]):
                    leaves_a, degree_a, k_a = a
                    leaves_b, degree_b, k_b = b
                    assert degree_a == degree_b and k_a == k_b
                    assert leaves_a.isdisjoint(leaves_b)
                    union = leaves_a | leaves_b
                    assert len(union) == n
                    kind, zeta = subtree_kinds[union]
                    lane_modes.append(kind)
                    original = pow(zeta, -k_a, Q)
                    upper_kind, lower_kind, _, _ = RECIPE[kind]
                    scale = lambda child: 0 if child == 'U1' else RECIPE[child][3]
                    combined = original * pow(2,
                        scale(lower_kind) - scale(upper_kind), Q) % Q
                    original_factors.append(original)
                    candidate_factors.append(combined)
                    out_a.append((union, degree_a, k_a))
                    out_b.append((union, degree_a, k_a + n // 2))
                upper.append(out_a)
                lower.append(out_b)
                vector_modes[str(stage)].append({'packet': packet,
                                                   'pair': pair,
                                                   'lane_kinds': lane_modes,
                                                   'original_factors': original_factors,
                                                   'candidate_factors': candidate_factors,
                                                   'original_has_vector_multiply':
                                                   any(x != 1 for x in original_factors),
                                                   'candidate_has_vector_multiply':
                                                   any(x != 1 for x in candidate_factors),
                                                   'homogeneous':
                                                   len(set(lane_modes)) == 1})
            outputs = upper + lower
            if stage == 2:
                new[base:base + 8] = outputs
            else:
                for pair in range(4):
                    lo, hi = route(stage, outputs[2 * pair],
                                   outputs[2 * pair + 1])
                    new[base + pair], new[base + pair + 4] = lo, hi
                    route_ops[stage] += 1
        mem = new
    return mem, route_ops, vector_modes


def main():
    mem, route_ops, vector_modes = ownership()
    grouped = {}
    for i in range(8):
        vectors = [mem[i + 8 * group] for group in range(6)]
        for lane in range(16):
            row = [v[lane] for v in vectors]
            key = (row[0][1], row[0][2])
            assert all((x[1], x[2]) == key for x in row)
            assert len({next(iter({pow(lam, 32, Q) for lam in x[0]}))
                        for x in row}) == 6
            grouped[i, lane] = key
    assert set(grouped.values()) == {(degree, k)
                                     for degree in range(4) for k in range(32)}
    sample = {str(i): [grouped[i, lane] for lane in range(16)]
              for i in range(8)}
    # The inherited CT routes already create quartic AoS: four degrees for
    # each of four consecutive k values. Level-0 can store its six outputs
    # back to the six physical vector slots without another transpose.
    shape = []
    for i in range(8):
        expected = [(lane % 4, 4 * i + lane // 4) for lane in range(16)]
        assert sample[str(i)] == expected, (i, sample[str(i)], expected)
        shape.append({'tile': i, 'lane_degree_k': sample[str(i)],
                      'quartic_AoS_exact': True,
                      'coefficient_store_offsets_bytes':
                      [32 * (i + 8 * p) for p in range(6)]})
    result = {
        'evidence_class': 'exact_owner_route_replay_and_conservative_tail_packet_ledger_not_linked_ASM',
        'stage_route_pairs_per_polynomial': route_ops,
        'stage_vector_modes': vector_modes,
        'mixed_mode_vector_pairs': {
            stage: sum(not row['homogeneous'] for row in rows)
            for stage, rows in vector_modes.items()},
        'vector_montgomery_ledger': {
            stage: {
                'original': sum(row['original_has_vector_multiply']
                                for row in rows),
                'candidate': sum(row['candidate_has_vector_multiply']
                                 for row in rows),
                'new': sum(row['candidate_has_vector_multiply'] and not
                           row['original_has_vector_multiply'] for row in rows),
                'changed_constant_vectors': sum(
                    row['original_factors'] != row['candidate_factors']
                    for row in rows),
                'distinct_original_factor_vectors': len({tuple(
                    row['original_factors']) for row in rows}),
                'distinct_candidate_factor_vectors': len({tuple(
                    row['candidate_factors']) for row in rows}),
            } for stage, rows in vector_modes.items()},
        'tail_eight_tiles': shape,
        'same_k_degree_across_six_cohorts': True,
        'full_128_degree_k_owners_unique': True,
        'tail_arithmetic_packets': 8,
        'per_tail_packet': {'radix3_triples': 2,
                            'level0_pairs': 3,
                            'data_loads_if_materialized_between_stages': 12,
                            'data_stores_if_materialized_between_stages': 12,
                            'omega_montgomery': 2,
                            'alpha_montgomery': 4,
                            'phi_montgomery': 3,
                            'final_montgomery': 6,
                            'barrett': 2},
        'per_full_polynomial': {
            'mandatory_y32_untwist_montgomery_vectors': 48,
            'factored_radix3_montgomery_vectors': 48,
            'factored_level0_montgomery_vectors': 72,
            'factored_tail_montgomery_including_untwist': 168,
            'top_tail_data_loads_if_materialized': 96,
            'top_tail_data_stores_if_materialized': 96,
            'top_tail_barrett_vectors': 16,
        },
        'output_geometry': 'exact coefficient-domain quartic AoS already formed by inherited radix2 routes; six tail outputs store to vector slots i+8p with no extra transpose',
        'source_sha256': {str(path.relative_to(ROOT)):
                          hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__), FACTORS,
                                       ROOT / 'tools/probe_inverse_ct_gauge.py',
                                       ROOT / 'tools/research_twiddle_half_absorption.py')},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('source_sha256', 'tail_eight_tiles',
                                     'stage_vector_modes')},
                     indent=2))


if __name__ == '__main__':
    main()
