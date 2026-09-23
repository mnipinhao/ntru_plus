#!/usr/bin/env python3
"""Close mixed-gauge CT top algebra/range against independent six-root CRT.

The first gate is a semantic matrix comparison. Machine allocation and linked
costs are deliberately not inferred from that comparison.
"""

import ctypes
import hashlib
import json
import random
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import Q, R, RINV, ROOT, zetas_inv
from prove_forward_lanes import barrett_word
from prove_inverse_ct_range import barrett_bound, mont_bound
from research_correlated_ct_butterfly import machine_base_mul_scale, mont_factor
from research_full_twisted_pairings import children, invert_matrix
from research_twiddle_half_absorption import evaluate, WITNESS_C, WITNESS_F
from research_yang_true_twist import ZETA32, reconstruct
from research_true_twist_repair_v2 import FACTORS, INPUT, TOWER, verified
from research_mixed_gauge_vector_schedule import ownership, stage_values

FACTOR = ROOT / 'results/yang-full-twisted-tower-factor-20260923.json'
RESULT = ROOT / 'results/yang-true-y-twist-mixed-gauge-full-tail-20260923.json'


def aligned_words():
    backing = ctypes.create_string_buffer(1536 + 31)
    pointer = (ctypes.addressof(backing) + 31) & ~31
    return backing, pointer, (ctypes.c_int16 * 768).from_address(pointer)


def word_tail(v, alphas, omega, phi, nscale):
    triples, maximum = [], 0
    for b in range(2):
        x, y, zz = v[3 * b:3 * b + 3]
        diff = y - zz
        t = mont_factor(diff, omega)
        s0 = x + y + zz
        s1 = x - y - t
        s2 = x - zz + t
        maximum = max(maximum, abs(diff), abs(s0), abs(s1), abs(s2))
        assert maximum <= 32767
        triples.append([barrett_word(s0),
                        mont_factor(s1, alphas[b][1]),
                        mont_factor(s2, alphas[b][2])])
    upper, lower = [], []
    for j in range(3):
        u, vv = triples[0][j], triples[1][j]
        diff = u - vv
        t = mont_factor(diff, phi)
        hi_input = u + vv - t
        maximum = max(maximum, abs(diff), abs(hi_input))
        assert maximum <= 32767
        upper.append(mont_factor(hi_input, nscale))
        lower.append(mont_factor(t, 2 * nscale % Q))
    return upper + lower, maximum


def bound_tail(v, alphas, omega, phi, nscale):
    triples, maximum = [], 0
    for b in range(2):
        x, y, zz = v[3 * b:3 * b + 3]
        diff = y + zz
        t = mont_bound(diff, omega)
        s0 = x + y + zz
        s1 = x + y + t
        s2 = x + zz + t
        maximum = max(maximum, diff, s0, s1, s2)
        assert maximum <= 32767, ('radix3', b, maximum)
        triples.append([barrett_bound(s0),
                        mont_bound(s1, alphas[b][1]),
                        mont_bound(s2, alphas[b][2])])
    outputs = []
    for j in range(3):
        u, vv = triples[0][j], triples[1][j]
        diff = u + vv
        t = mont_bound(diff, phi)
        hi_input = u + vv + t
        maximum = max(maximum, diff, hi_input)
        assert maximum <= 32767, ('level0', j, maximum)
        outputs.extend([mont_bound(hi_input, nscale),
                        mont_bound(t, 2 * nscale % Q)])
    return outputs, maximum


def main():
    closure, factor, tower = map(verified, (INPUT, FACTOR, TOWER))
    assert tower['materialized_leaf_gauge'] == 1
    owners = factor['physical_owners']
    cells = [owners[16 * vector] for vector in (0, 8, 16, 24, 32, 40)]
    alphas = [pow(row['leaf'], 32, Q) for row in cells]
    assert len(set(alphas)) == 6
    for vector, alpha in zip((0, 8, 16, 24, 32, 40), alphas):
        assert {pow(row['leaf'], 32, Q)
                for row in owners[16 * vector:16 * vector + 16]} == {alpha}
    crt = invert_matrix([[pow(alpha, j, Q) for j in range(6)]
                         for alpha in alphas])
    z = zetas_inv()
    alpha_table = [[1, z[794 + 8 * b] * RINV % Q,
                    z[798 + 8 * b] * RINV % Q] for b in range(2)]
    phi = z[810] * RINV % Q
    omega = (-886) * RINV % Q
    nscale = R * pow(48, -1, Q) % Q
    assert nscale == 213

    def factored(v):
        triples = []
        for b in range(2):
            x, y, zz = v[3 * b:3 * b + 3]
            t = omega * (y - zz) % Q
            triples.append([(x + y + zz) % Q,
                            alpha_table[b][1] * (x - y - t) % Q,
                            alpha_table[b][2] * (x - zz + t) % Q])
        upper, lower = [], []
        for j in range(3):
            u, v = triples[0][j], triples[1][j]
            t = phi * (u - v) % Q
            upper.append(nscale * (u + v - t) % Q)
            lower.append(2 * nscale * t % Q)
        return upper + lower

    direct = [[coefficient * R * pow(8, -1, Q) % Q
               for coefficient in row] for row in crt]
    basis = [[int(i == j) for i in range(6)] for j in range(6)]
    observed = [[factored(vector)[j] for vector in basis] for j in range(6)]
    assert observed == direct

    roots = sorted({row['leaf'] for row in owners})
    cohorts = [group for _, top in children(roots, 192)
               for _, group in children(top, 96)]
    assert len(cohorts) == 6
    cohort_by_alpha = {pow(min(group), 32, Q): group for group in cohorts}
    owner = {(row['leaf'], row['degree']): row['cell'] for row in owners}
    assert set(cohort_by_alpha) == set(alphas) and len(owner) == 768
    bounds = closure['BaseMulScale']['output_lane_bounds']
    physical_owners, _, physical_modes = ownership()
    physical_bounds = [[max(map(abs, bounds[16 * v + lane]))
                        for lane in range(16)] for v in range(48)]
    physical_stage_bounds = []
    for stage in (6, 5, 4, 3, 2):
        physical_bounds = stage_values(physical_bounds, stage,
                                       physical_modes, formal=True)
        physical_stage_bounds.append({'stage': stage,
                                      'max_abs': max(map(max, physical_bounds))})
    physical_untwist_bounds = [[mont_bound(value,
        pow(physical_owners[v][lane].xi, -physical_owners[v][lane].k, Q))
        for lane, value in enumerate(vector)]
        for v, vector in enumerate(physical_bounds)]
    physical_tail_pre = physical_final_bound = 0
    for i in range(8):
        for lane in range(16):
            six = [physical_untwist_bounds[i + 8 * group][lane]
                   for group in range(6)]
            outputs, pre = bound_tail(six, alpha_table, omega, phi, nscale)
            physical_tail_pre = max(physical_tail_pre, pre)
            physical_final_bound = max(physical_final_bound, *outputs)
    max_untwist_input = max_untwist_output = max_top_pre = max_top_output = 0
    formal_untwist = {}
    formal_final = {}
    for degree in range(4):
        block_bounds = {}
        for alpha in alphas:
            group = cohort_by_alpha[alpha]
            values = {leaf: max(map(abs, bounds[owner[leaf, degree]]))
                      for leaf in group}
            raw, scale = evaluate('H32', min(group), ZETA32, values,
                                  Counter(candidate_constants=set(),
                                          original_constants=set()), formal=True)
            assert scale == 2
            max_untwist_input = max(max_untwist_input, *raw)
            block_bounds[alpha] = [mont_bound(x, pow(min(group), -k, Q))
                                   for k, x in enumerate(raw)]
            formal_untwist[degree, alpha] = block_bounds[alpha]
            max_untwist_output = max(max_untwist_output,
                                     *block_bounds[alpha])
        for k in range(32):
            output_bounds, pre = bound_tail([block_bounds[a][k]
                                             for a in alphas],
                                            alpha_table, omega, phi, nscale)
            formal_final[degree, k] = [output_bounds[i]
                                        for i in (0, 2, 4, 1, 3, 5)]
            max_top_pre = max(max_top_pre, pre)
            max_top_output = max(max_top_output, *output_bounds)

    rng = random.Random(20260923)
    cases = [([WITNESS_C] * 768, [WITNESS_F] * 768)]
    for _ in range(100):
        cases.append(([rng.randrange(Q) for _ in range(768)],
                      [rng.randrange(Q) for _ in range(768)]))
    observed_max_pre = observed_max_out = 0
    consumer_cases = 0
    physical_consumer_cases = 0
    sources = [ROOT / 'upstream/supercop-avx2/invntt.s',
               ROOT / 'upstream/supercop-avx2/crepmod3.s',
               ROOT / 'upstream/supercop-avx2/consts.c']
    with tempfile.TemporaryDirectory(prefix='officialopt-mixed-tail-') as td:
        binary = Path(td) / 'official-inverse.so'
        subprocess.run(['cc', '-shared', '-fPIC', '-mavx2', '-o', str(binary),
                        *map(str, sources)], check=True, capture_output=True)
        lib = ctypes.CDLL(str(binary))
        inverse = lib.poly_invntt_scale
        crepmod3 = lib.poly_crepmod3
        inverse.argtypes = crepmod3.argtypes = [ctypes.c_void_p]
        backing, pointer, words = aligned_words()
        for output, _ in machine_base_mul_scale(cases):
            candidate = [0] * 768
            for degree in range(4):
                block_values = {}
                values_by_leaf = {leaf: output[owner[leaf, degree]]
                                  for leaf in roots}
                reference = reconstruct(values_by_leaf, roots, Counter())
                for alpha in alphas:
                    group = cohort_by_alpha[alpha]
                    raw, scale = evaluate('H32', min(group), ZETA32,
                                          values_by_leaf,
                                          Counter(candidate_constants=set(),
                                                  original_constants=set()))
                    assert scale == 2
                    block_values[alpha] = [mont_factor(x,
                        pow(min(group), -k, Q)) for k, x in enumerate(raw)]
                    assert all(abs(x) <= b for x, b in zip(
                        block_values[alpha], formal_untwist[degree, alpha])), (
                            degree, alpha,
                            [(k, raw[k], x, formal_untwist[degree, alpha][k])
                             for k, x in enumerate(block_values[alpha])
                             if abs(x) > formal_untwist[degree, alpha][k]][:4])
                for k in range(32):
                    out, pre = word_tail([block_values[a][k] for a in alphas],
                                         alpha_table, omega, phi, nscale)
                    assert all(abs(x) <= b for x, b in zip(
                        out, formal_final[degree, k])), (
                            degree, k, out, formal_final[degree, k])
                    observed_max_pre = max(observed_max_pre, pre)
                    observed_max_out = max(observed_max_out,
                                           *(abs(x) for x in out))
                    for p, x in enumerate(out):
                        assert x % Q == R * reference[32 * p + k] % Q
                        candidate[4 * (32 * p + k) + degree] = x
            words[:] = output
            inverse(pointer)
            control = list(words)
            assert all((a - b) % Q == 0 for a, b in zip(candidate, control))
            words[:] = control
            crepmod3(pointer)
            control_consumer = list(words)
            words[:] = candidate
            crepmod3(pointer)
            assert list(words) == control_consumer
            consumer_cases += 1
        for output, _ in machine_base_mul_scale(cases):
            cells = [output[16 * v:16 * v + 16] for v in range(48)]
            for stage in (6, 5, 4, 3, 2):
                cells = stage_values(cells, stage, physical_modes)
            candidate = [0] * 768
            for i in range(8):
                six_vectors = []
                for group in range(6):
                    v = i + 8 * group
                    six_vectors.append([mont_factor(value,
                        pow(physical_owners[v][lane].xi,
                            -physical_owners[v][lane].k, Q))
                        for lane, value in enumerate(cells[v])])
                for lane in range(16):
                    out, _ = word_tail([v[lane] for v in six_vectors],
                                       alpha_table, omega, phi, nscale)
                    for p, value in enumerate(out):
                        candidate[16 * (i + 8 * p) + lane] = value
            words[:] = output
            inverse(pointer)
            control = list(words)
            mismatch = [(j, a, b) for j, (a, b) in enumerate(zip(candidate, control))
                        if (a - b) % Q]
            assert not mismatch, (physical_consumer_cases, mismatch[:8])
            words[:] = control
            crepmod3(pointer)
            consumer = list(words)
            words[:] = candidate
            crepmod3(pointer)
            assert list(words) == consumer
            physical_consumer_cases += 1
    result = {
        'evidence_class': 'full_scalar_machine_word_tail_and_768_cell_interval_not_AVX2_schedule',
        'physical_y32_roots': alphas,
        'six_by_six_factored_vs_independent_CRT_basis': 6,
        'factored_matches_direct_CRT': True,
        'radix3_alpha': alpha_table,
        'omega': omega,
        'phi': phi,
        'final_scale_semantic': nscale,
        'final_scale_montgomery_word': nscale * R % Q,
        'mandatory_y32_untwist_montgomery_including_identity_lanes': True,
        'formal_bounds': {
            'max_radix2_output_before_y32_untwist': max_untwist_input,
            'max_after_y32_untwist': max_untwist_output,
            'max_top_preoperation': max_top_pre,
            'max_final_output': max_top_output,
        },
        'observed_bounds': {'max_top_preoperation': observed_max_pre,
                            'max_final_output': observed_max_out},
        'machine_BaseMulScale_and_linked_Official_inverse_crepmod3_cases': consumer_cases,
        'all_cases_modq_and_crepmod3_byte_exact': True,
        'physical_AVX2_route_stage_bounds': physical_stage_bounds,
        'physical_AVX2_route_max_after_y32_untwist': max(map(max, physical_untwist_bounds)),
        'physical_AVX2_route_max_top_preoperation': physical_tail_pre,
        'physical_AVX2_route_max_final_output': physical_final_bound,
        'physical_AVX2_route_consumer_cases': physical_consumer_cases,
        'physical_AVX2_route_modq_and_crepmod3_byte_exact': True,
        'source_sha256': {str(path.relative_to(ROOT)):
                          hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in [Path(__file__), INPUT, FACTOR, TOWER,
                                       ROOT / 'tools/research_twiddle_half_absorption.py',
                                       ROOT / 'tools/research_correlated_ct_butterfly.py',
                                       ROOT / 'tools/research_mixed_gauge_vector_schedule.py',
                                       ROOT / 'tools/research_physical_true_twist_replay.py',
                                       ROOT / 'tools/prove_inverse_ct_range.py']
                          + sources},
        'open': ['complete 16-YMM AVX2 def/use and output routing',
                 'linked constant traffic and dependency',
                 'cycle pricing against Official GS'],
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('source_sha256', 'radix3_alpha')}, indent=2))


if __name__ == '__main__':
    main()
