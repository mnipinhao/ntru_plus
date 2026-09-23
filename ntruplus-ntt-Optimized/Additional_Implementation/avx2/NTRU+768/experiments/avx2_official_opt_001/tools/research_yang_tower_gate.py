#!/usr/bin/env python3
"""Exact first gate for gauge-aware radix-3 and a shared Forward/inverse ABI.

This is a modular ownership/cost screen, not a linked schedule or a range
proof. In particular, the inverse CT prefix gauges are *intermediate* gauges:
they must not be silently treated as Forward's materialized NTT output ABI.
"""

import hashlib
import itertools
import json
import random
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import Q, RINV, ROOT, compute, zetas_inv


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) % Q for row in matrix]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def semantic_tail(inputs, gauges, alpha, omega, phi, final_scale):
    halves = []
    for half in range(2):
        x, y, z = [inputs[3 * half + j] * gauges[3 * half + j] % Q
                   for j in range(3)]
        t = omega * (y - z)
        halves.append([x + y + z,
                       alpha[half][1] * (x - y - t),
                       alpha[half][2] * (x - z + t)])
    outputs = []
    for degree in range(3):
        u, v = halves[0][degree], halves[1][degree]
        t = phi * (u - v)
        outputs.extend((final_scale * (u + v - t) % Q,
                        2 * final_scale * t % Q))
    return outputs


def matrix_from_oracle(gauges, alpha, omega, phi, final_scale):
    columns = [semantic_tail(col, gauges, alpha, omega, phi, final_scale)
               for col in identity(6)]
    return [[columns[col][row] for col in range(6)] for row in range(6)]


def dft3_matrix(omega):
    # The existing three-output radix-3 equations have this exact DFT form.
    return [[1, 1, 1],
            [1, pow(omega, 2, Q), omega],
            [1, omega, pow(omega, 2, Q)]]


def main():
    source = [Path(__file__), ROOT / 'tools/probe_inverse_ct_gauge.py',
              ROOT / 'tools/close_yang_contract.py',
              ROOT / 'upstream/supercop-avx2/consts.c',
              ROOT / 'upstream/supercop-avx2/ntt.s',
              ROOT / 'upstream/supercop-avx2/invntt.s',
              ROOT / 'upstream/supercop-avx2/basemul.s',
              ROOT / 'upstream/supercop-avx2/baseinv.s',
              ROOT / 'upstream/supercop-avx2/pack.s']
    gauges = compute()['stages'][-1]['output_gauges']
    zetas = zetas_inv()
    alpha = [[1, zetas[794 + 8 * b] * RINV % Q,
              zetas[798 + 8 * b] * RINV % Q] for b in range(2)]
    omega = (-886) * RINV % Q
    phi = zetas[810] * RINV % Q
    final_scale = 1679 * RINV % Q
    assert (omega * omega + omega + 1) % Q == 0
    dft = dft3_matrix(omega)
    assert dft[1] == [1, (-1 - omega) % Q, omega]
    assert dft[2] == [1, omega, (-1 - omega) % Q]

    rng = random.Random(20260923)
    rows = []
    dense_full_vector_chains = 0
    dense_radix3_vector_chains = 0
    s0_distinct = Counter()
    geometric_triples = 0
    cube_root_twists = 0
    for cohort in range(8):
        indices = [cohort + 8 * j for j in range(3)] + [
            cohort + 24 + 8 * j for j in range(3)]
        lane_matrices = []
        for lane in range(16):
            gs = [gauges[k][lane] for k in indices]
            matrix = matrix_from_oracle(gs, alpha, omega, phi, final_scale)
            # Independent construction: apply both DFT3s, alpha and exact
            # trinomial level-0 matrix directly, without calling the oracle.
            dft_values = []
            for half in range(2):
                dft_values.append([[sum(dft[j][k] * gs[3*half+k] *
                     int(k == col-3*half) for k in range(3)) % Q
                     for col in range(3*half,3*half+3)] for j in range(3)])
            for col in identity(6):
                direct = []
                for j in range(3):
                    u = alpha[0][j] * sum(dft_values[0][j][k] * col[k]
                                              for k in range(3)) % Q
                    v = alpha[1][j] * sum(dft_values[1][j][k] * col[k+3]
                                              for k in range(3)) % Q
                    t = phi * (u-v)
                    direct += [final_scale * (u+v-t) % Q,
                               2 * final_scale * t % Q]
                assert direct == matvec(matrix, col)
            for _ in range(16):
                v = [rng.randrange(Q) for _ in range(6)]
                assert matvec(matrix, v) == semantic_tail(
                    v, gs, alpha, omega, phi, final_scale)
            lane_matrices.append(matrix)
            for half in (0, 1):
                triple=gs[3*half:3*half+3]
                s0_distinct[len(set(triple))] += 1
                geometric_triples += triple[1]*triple[1]%Q == triple[0]*triple[2]%Q
                twist=triple[1]*pow(triple[0],-1,Q)%Q
                cube_root_twists += pow(twist,3,Q)==1
                twisted=[[dft[row][col]*pow(twist,col,Q)%Q for col in range(3)]
                         for row in range(3)]
                output_scale_permutation=any(
                    all(twisted[row]==[scale*dft[perm[row]][col]%Q
                                       for col in range(3)]
                        for row,scale in enumerate(scales))
                    for perm in itertools.permutations(range(3))
                    for scales in ((1,1,1),))
                assert output_scale_permutation == (pow(twist,3,Q)==1)
        # One multiply per nontrivial coefficient vector in a naive dense
        # realization; identity/zero vectors need no multiply. This is an
        # upper-cost construction, never a lower bound on all algorithms.
        full = []
        for row in range(6):
            for col in range(6):
                vector = [lane_matrices[lane][row][col] for lane in range(16)]
                if any(vector) and vector != [1] * 16:
                    full.append([row, col])
        dense_full_vector_chains += len(full)
        radix3 = []
        for half in range(2):
            for row in range(3):
                for col in range(3):
                    vector = [dft[row][col] * gauges[indices[3*half+col]][lane] % Q
                              for lane in range(16)]
                    if vector != [1] * 16:
                        radix3.append([half, row, col])
        dense_radix3_vector_chains += len(radix3)
        rows.append({'cohort': cohort, 'physical_vectors': indices,
                     'full_six_by_six_nontrivial_vector_coefficients': len(full),
                     'dense_radix3_nontrivial_vector_coefficients': len(radix3),
                     'full_matrix_coefficient_positions': full})

    # The CT-prefix outputs are coefficient-side intermediate vectors. This
    # screen only tests whether they could be passed through the *current*
    # quartic ABI with scalar per-leaf correction; it does not posit such an
    # ABI or claim a global obstruction to a new Forward tower.
    uniform = 0
    for tile in range(12):
        for lane in range(16):
            uniform += len({gauges[4*tile+j][lane] for j in range(4)}) == 1
    caller_edges = {
        'keygen': ['forward_f_g', 'baseinv', 'basemul', 'pk_sk_encode'],
        'encap': ['pk_decode', 'forward_r_m', 'r_hash_bytes', 'basemul_add', 'ct_encode'],
        'decap': ['ct_sk_decode', 'basemul_scale', 'inverse', 'crepmod3',
                  'forward_m', 'recovery_basemul', 'recovered_r_hash',
                  'reencryption_equality']}
    result = {
        'evidence_class': 'exact_modular_mapping_and_structural_screen_only',
        'modulus': Q, 'intermediate_gauge_semantics':
            'semantic CT-prefix value = gauge * stored value (mod q)',
        'radix3': {'omega': omega, 'dft_matrix': dft,
                   's0_distinct_input_gauge_counts': dict(s0_distinct),
                   'geometric_gauge_triples': geometric_triples,
                   'triples_with_cube_root_twist': cube_root_twists,
                   'triples_total':256,
                   'ct_gs_output_rescale_witness':
                       'For F3*diag(1,c,c^2)=D*P*F3 with only output scale D and output permutation P, c must be a cubic root of unity. Here 248/256 c values are not.',
                   'dense_three_by_three_vector_chains': dense_radix3_vector_chains,
                   'existing_pre_radix3_relative_chains': 40,
                   'existing_radix3_omega_chains': 16,
                   'screen_conclusion': 'fixed-prefix GS output rescale/permutation is invalid for 248/256 lane triples; dense direct composition removes explicit normalization but costs more products; new factored map or changed prefix required'},
        'full_tail': {'cohorts': rows,
                      'dense_six_by_six_vector_chains': dense_full_vector_chains,
                      'existing_stage5reuse_tail_chains': 144,
                      'existing_stage5reuse_full_inverse_chains': 222,
                      'screen_conclusion': 'dense direct composition is a valid oracle, not an ASM candidate'},
        'joint_tower': {'inverse_prefix_nonidentity_lanes': sum(x != 1 for v in gauges for x in v),
                        'inverse_prefix_quartic_scalar_gauge_leaves': uniform,
                        'quartic_leaves': 192,
                        'warning': 'these inverse-prefix gauges are not the materialized Forward NTT ABI; no caller-gauge candidate is established by this screen',
                        'consumer_edges': caller_edges},
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in source}}
    target = ROOT / 'results/yang-joint-tower-gate-20260923.json'
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'radix3': result['radix3'],
                      'dense_six_by_six_vector_chains': dense_full_vector_chains,
                      'joint_tower': result['joint_tower']}, indent=2))


if __name__ == '__main__':
    main()
