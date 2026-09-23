#!/usr/bin/env python3
"""Whole-vector Barrett repair control for the true-y CT prefix.

Uses the same physical owner routes and exact BaseMulScale input intervals as
the mixed-gauge candidate. Greedy stage-local choice is not globally optimal.
"""

import hashlib
import json
import ctypes
import subprocess
import tempfile
from pathlib import Path

from probe_inverse_ct_gauge import Q, ROOT, route
from prove_forward_lanes import barrett_word
from prove_inverse_ct_range import barrett_bound, mont_bound
from research_correlated_ct_butterfly import mont_factor
from research_mixed_gauge_vector_schedule import ownership
from research_mixed_gauge_full_tail import aligned_words, word_tail
from research_correlated_ct_butterfly import machine_base_mul_scale, WITNESS_C, WITNESS_F
from probe_inverse_ct_gauge import R, RINV, zetas_inv
from research_true_twist_repair_v2 import INPUT, FACTORS, TOWER, verified

RESULT = ROOT / 'results/yang-true-y-twist-selective-repair-20260923.json'


def stage_pairs(mem, stage, factors, plan=None):
    new = [None] * 48
    repairs = []
    for packet in range(6):
        base = 8 * packet
        upper, lower = [], []
        for pair in range(4):
            a, b = mem[base + pair], mem[base + pair + 4]
            vec = factors[str(stage)][packet * 4 + pair]['original_factors']
            if plan is None:
                options = []
                for ra, rb in ((False, False), (True, False),
                               (False, True), (True, True)):
                    aa = [barrett_bound(x) if ra else x for x in a]
                    bb = [barrett_bound(x) if rb else x for x in b]
                    t = [y if w == 1 else mont_bound(y, w)
                         for y, w in zip(bb, vec)]
                    outs = [x + y for x, y in zip(aa, t)]
                    if max(outs) <= 32767:
                        options.append((int(ra) + int(rb), max(outs),
                                        ra, rb, outs))
                assert options, (stage, packet, pair)
                _, _, ra, rb, output_bound = min(options)
                first = second = output_bound
            else:
                ra, rb = plan[packet * 4 + pair]
                aa = [barrett_word(x) if ra else x for x in a]
                bb = [barrett_word(x) if rb else x for x in b]
                t = [y if w == 1 else mont_factor(y, w)
                     for y, w in zip(bb, vec)]
                first = [x + y for x, y in zip(aa, t)]
                second = [x - y for x, y in zip(aa, t)]
                assert all(-32768 <= x <= 32767 for x in first + second)
            repairs.append((ra, rb))
            upper.append(first)
            lower.append(second)
        outputs = upper + lower
        if stage == 2:
            new[base:base + 8] = outputs
        else:
            for pair in range(4):
                lo, hi = route(stage, outputs[2 * pair],
                               outputs[2 * pair + 1])
                new[base + pair], new[base + pair + 4] = lo, hi
    return new, repairs


def naive_replay_diagnostic(factors, plans, owner_mem, alphas, cohort_xi):
    """Record, without promoting, where a direct physical top-tail replay fails."""
    source, _ = next(machine_base_mul_scale(
        [([WITNESS_C] * 768, [WITNESS_F] * 768)]))
    cells = [source[16 * v:16 * v + 16] for v in range(48)]
    for stage in (6, 5, 4, 3, 2):
        cells, _ = stage_pairs(cells, stage, factors, plans[str(stage)])
    z = zetas_inv()
    alpha_table = [[1, z[794 + 8 * b] * RINV % Q,
                    z[798 + 8 * b] * RINV % Q] for b in range(2)]
    phi = z[810] * RINV % Q
    omega = (-886) * RINV % Q
    nscale = R * pow(192, -1, Q) % Q
    candidate = [0] * 768
    for i in range(8):
        six_vectors = []
        for group, alpha in enumerate(alphas):
            vector_index = i + 8 * group
            six_vectors.append([mont_factor(value,
                pow(cohort_xi[alpha], -owner_mem[vector_index][lane][2], Q))
                for lane, value in enumerate(cells[vector_index])])
        for lane in range(16):
            outputs, _ = word_tail([v[lane] for v in six_vectors],
                                   alpha_table, omega, phi, nscale)
            for p, value in enumerate(outputs):
                candidate[16 * (i + 8 * p) + lane] = value
    sources = [ROOT / 'upstream/supercop-avx2/invntt.s',
               ROOT / 'upstream/supercop-avx2/consts.c']
    with tempfile.TemporaryDirectory(prefix='officialopt-selective-replay-') as td:
        binary = Path(td) / 'official-inverse.so'
        subprocess.run(['cc', '-shared', '-fPIC', '-mavx2', '-o', str(binary),
                        *map(str, sources)], check=True, capture_output=True)
        lib = ctypes.CDLL(str(binary))
        inverse = lib.poly_invntt_scale
        inverse.argtypes = [ctypes.c_void_p]
        backing, pointer, words = aligned_words()
        words[:] = source
        inverse(pointer)
        official = list(words)
    mismatches = [(i, a, b) for i, (a, b) in enumerate(zip(candidate, official))
                  if (a - b) % Q]
    return {'case': 'constant canonical c=3449,f=3349 through compiled BaseMulScale',
            'tested_naive_top_scale': nscale,
            'mismatch_count': len(mismatches),
            'first_mismatches': mismatches[:8],
            'interpretation': 'this physical owner/scale replay is not a semantic inverse; repair topology is not rejected'}


def main():
    closure, factor, tower = map(verified, (INPUT, FACTORS, TOWER))
    assert tower['materialized_leaf_gauge'] == 1
    owner_mem, _, factors = ownership()
    bounds = closure['BaseMulScale']['output_lane_bounds']
    mem = [[max(map(abs, bounds[16 * v + lane])) for lane in range(16)]
           for v in range(48)]
    plans, ledger = {}, []
    for stage in (6, 5, 4, 3, 2):
        mem, repairs = stage_pairs(mem, stage, factors)
        plans[str(stage)] = repairs
        ledger.append({'stage': stage,
                       'barrett_vectors': sum(a + b for a, b in repairs),
                       'max_output_abs_bound': max(max(vector)
                                                   for vector in mem)})
    assert all(max(vector) <= 32767 for vector in mem)
    # Every final y32 untwist is a full-vector Montgomery chain. This includes
    # identity lanes, whose raw representatives can still need reduction.
    alphas = [pow(factor['physical_owners'][16 * (8 * group)]['leaf'],
                  32, Q) for group in range(6)]
    cohort_xi = {}
    for row in factor['physical_owners']:
        alpha = pow(row['leaf'], 32, Q)
        cohort_xi[alpha] = min(cohort_xi.get(alpha, row['leaf']), row['leaf'])
    untwist = [None] * 48
    for i in range(8):
        for group, alpha in enumerate(alphas):
            untwist[i + 8 * group] = [mont_bound(value,
                pow(cohort_xi[alpha], -owner_mem[i + 8 * group][lane][2], Q))
                for lane, value in enumerate(mem[i + 8 * group])]
    assert max(max(v) for v in untwist) <= 32767
    result = {
        'evidence_class': 'stage_greedy_vector_Barrett_repair_interval_control_not_AVX2_lowering',
        'stage_ledger': ledger,
        'total_Barrett_vectors': sum(x['barrett_vectors'] for x in ledger),
        'plans': {stage: [{'packet': index // 4, 'pair': index % 4,
                           'reduce_a': a, 'reduce_b': b}
                          for index, (a, b) in enumerate(rows)]
                  for stage, rows in plans.items()},
        'max_after_mandatory_y32_untwist': max(max(v) for v in untwist),
        'naive_semantic_replay': naive_replay_diagnostic(
            factors, plans, owner_mem, alphas, cohort_xi),
        'scope_limits': ['greedy local choice not minimum complete schedule',
                         'no semantic top-tail closure, linked AVX2, or Decap timing yet'],
        'source_sha256': {str(path.relative_to(ROOT)):
                          hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__), INPUT, FACTORS, TOWER,
                                       ROOT / 'tools/research_mixed_gauge_vector_schedule.py',
                                       ROOT / 'tools/prove_inverse_ct_range.py',
                                       ROOT / 'tools/research_correlated_ct_butterfly.py',
                                       ROOT / 'tools/research_mixed_gauge_full_tail.py')},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('source_sha256', 'plans')}, indent=2))


if __name__ == '__main__':
    main()
