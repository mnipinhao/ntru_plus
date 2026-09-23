#!/usr/bin/env python3
"""Real-overflow witness and modular-average CT butterfly feasibility screen.

The q-half uses AVX2 vpavgw semantics on sign-bit-biased inputs, then adds a
shared odd-parity correction. It is an executable word model, not linked ASM.
"""

import ctypes
import hashlib
import json
import random
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from close_yang_contract import scaled_body
from probe_inverse_ct_gauge import Q, R, ROOT
from prove_forward_lanes import mont_word, signed16
from prove_inverse_ct_range import mont_worst_bound
from research_full_twisted_pairings import children
from research_yang_true_twist import ZETA32, cyclic_inverse
from research_true_twist_repair_v2 import INPUT, FACTORS, TOWER, verified

RESULT = ROOT / 'results/yang-true-y-twist-correlated-butterfly-20260923.json'
WITNESS_C = 3449
WITNESS_F = 3349


def mont_factor(x, factor):
    word = signed16(factor * R % Q)
    output = mont_word(x, word)
    assert -32768 <= output <= 32767
    assert output % Q == x * factor % Q
    return output


def qhalf(a, b):
    """Exact signed AVX2 vpavgw-bias identity plus mod-q parity correction."""
    assert -32768 <= a <= 32767 and -32768 <= b <= 32767
    ua, ub = (a + 32768) & 65535, (b + 32768) & 65535
    avg = signed16(((ua + ub + 1) // 2) ^ 32768)
    parity = (a ^ b) & 1
    result = avg + 1728 * parity  # -1/2 mod 3457
    assert result == (a + b + 1) // 2 + 1728 * parity
    assert -32768 <= result <= 32767, ('qhalf output overflow', a, b, result)
    assert (2 * result - a - b) % Q == 0
    return result


def inverse_block(values, xi, n, zeta, trace):
    if n == 1:
        return [values[xi]]
    half = n // 2
    upper = inverse_block(values, xi, half, zeta * zeta % Q, trace)
    lower = inverse_block(values, xi * zeta % Q, half,
                          zeta * zeta % Q, trace)
    first, second = [], []
    for k, (a, b) in enumerate(zip(upper, lower)):
        factor = pow(zeta, -k, Q)
        t = b if factor == 1 else mont_factor(b, factor)
        assert -32768 <= -t <= 32767
        hi, lo = qhalf(a, t), qhalf(a, -t)
        trace.append({'node_size': n, 'root': xi, 'position': k,
                      'a': a, 'b': b, 'twiddle': factor, 'twiddled_b': t,
                      'upper': hi, 'lower': lo})
        first.append(hi)
        second.append(lo)
    return first + second


def support_tree(xi, n, zeta):
    """Prove each butterfly combines disjoint sets of decoded quartic leaves."""
    if n == 1:
        return [frozenset((xi,))], 0
    half = n // 2
    upper, checks_a = support_tree(xi, half, zeta * zeta % Q)
    lower, checks_b = support_tree(xi * zeta % Q, half,
                                   zeta * zeta % Q)
    unions = []
    for a, b in zip(upper, lower):
        assert a.isdisjoint(b)
        unions.append(a | b)
    return unions + unions, checks_a + checks_b + half


def machine_base_mul_scale(cases):
    with tempfile.TemporaryDirectory(prefix='officialopt-corr-ct-') as tmp:
        temp = Path(tmp)
        source = ROOT / 'upstream/supercop-avx2'
        objects = []
        for name in ('basemul.s', 'consts.c'):
            obj = temp / (Path(name).stem + '.o')
            subprocess.run(['cc', '-c', '-fPIC', '-mavx2', '-o', str(obj),
                            str(source / name)], check=True, capture_output=True)
            objects.append(str(obj))
        binary = temp / 'basemul.so'
        subprocess.run(['cc', '-shared', '-o', str(binary), *objects],
                       check=True, capture_output=True)
        library = ctypes.CDLL(str(binary))
        fn = library.poly_basemul_scale
        fn.argtypes = [ctypes.c_void_p] * 3
        aligned = []
        for _ in range(3):
            backing = ctypes.create_string_buffer(1536 + 31)
            ptr = (ctypes.addressof(backing) + 31) & ~31
            aligned.append((backing, ptr, (ctypes.c_int16 * 768).from_address(ptr)))
        for c, f in cases:
            aligned[0][2][:] = c
            aligned[1][2][:] = f
            fn(aligned[2][1], aligned[0][1], aligned[1][1])
            actual = list(aligned[2][2])
            source_replay, _ = scaled_body(None, c, f)
            assert actual == source_replay
            yield actual, hashlib.sha256(binary.read_bytes()).hexdigest()


def main():
    closure, factors, tower = map(verified, (INPUT, FACTORS, TOWER))
    assert tower['materialized_leaf_gauge'] == 1
    owners = factors['physical_owners']
    mapping = {(owner['leaf'], owner['degree']): owner['cell']
               for owner in owners}
    assert len(mapping) == 768
    roots = sorted({leaf for leaf, _ in mapping})
    cohorts = [group for _, top in children(roots, 192)
               for _, group in children(top, 96)]
    assert len(cohorts) == 6
    for group in cohorts:
        supports, checks = support_tree(min(group), 32, ZETA32)
        assert checks == 80 and all(s == set(group) for s in supports)
    rng = random.Random(20260923)
    cases = [([WITNESS_C] * 768, [WITNESS_F] * 768)]
    for _ in range(100):
        cases.append(([rng.randrange(Q) for _ in range(768)],
                      [rng.randrange(Q) for _ in range(768)]))
    max_raw = 0
    max_qhalf = 0
    max_by_stage = {str(n): 0 for n in (2, 4, 8, 16, 32)}
    witness = None
    for case, (output, elf_sha) in enumerate(machine_base_mul_scale(cases)):
        bounds = closure['BaseMulScale']['output_lane_bounds']
        assert all(lo <= x <= hi for x, (lo, hi) in zip(output, bounds))
        max_raw = max(max_raw, max(map(abs, output)))
        if case == 0:
            degree3 = [output[mapping[leaf, 3]] for leaf in roots]
            assert set(degree3) == {7596}
            assert 2 * 7596 == 15192 and 4 * 7596 == 30384
            assert 8 * 7596 == 60768 > 32767
            assert signed16(60768) == -4768
            assert (60768 - signed16(60768)) % Q != 0
            witness = {
                'canonical_c_coefficient': WITNESS_C,
                'canonical_f_coefficient': WITNESS_F,
                'all_192_degree3_BaseMulScale_words': 7596,
                'no_repair_CT_identity_size2': 15192,
                'no_repair_CT_identity_size4': 30384,
                'no_repair_CT_identity_size8_mathematical': 60768,
                'vpaddw_wrapped': signed16(60768),
                'residue_corrupted_by_wrap': True,
                'machine_BaseMulScale_ELF_sha256': elf_sha,
            }
        for group in cohorts:
            xi = min(group)
            for degree in range(4):
                values = {leaf: output[mapping[leaf, degree]] for leaf in group}
                trace = []
                actual = inverse_block(values, xi, 32, ZETA32, trace)
                reference = cyclic_inverse(values, xi, 32, ZETA32, Counter())
                assert [x % Q for x in actual] == [x % Q for x in reference]
                for item in trace:
                    n = str(item['node_size'])
                    for name in ('a', 'b', 'twiddled_b', 'upper', 'lower'):
                        max_by_stage[n] = max(max_by_stage[n], abs(item[name]))
                    max_qhalf = max(max_qhalf, abs(item['upper']), abs(item['lower']))
                # The final y32 untwist is still required by the exact tower.
                for k, x in enumerate(actual):
                    untwisted = mont_factor(x, pow(xi, -k, Q))
                    assert untwisted % Q == reference[k] * pow(xi, -k, Q) % Q
    assert witness is not None
    # For |a|,|b| <= B, the signed ceil average is within B. An odd sum
    # adds exactly 1728, so the next uniform bound is max(B,Mont(B))+1728.
    # vpavgw operates on biased unsigned words and cannot overflow here.
    bound = closure['BaseMulScale']['maximum_abs']
    assert bound == 7644
    formal_bounds = []
    for n in (2, 4, 8, 16, 32):
        twiddled = mont_worst_bound(bound)
        bound = max(bound, twiddled) + 1728
        assert bound <= 32767
        formal_bounds.append({'node_size': n, 'input_abs_bound': bound-1728,
                              'nonidentity_twiddle_abs_bound': twiddled,
                              'output_abs_bound': bound})
    final_untwist_bound = mont_worst_bound(bound)
    assert final_untwist_bound <= 32767
    for a in (-16284, -16283, -1, 0, 1, 16283, 16284):
        for b in (-16284, -16283, -1, 0, 1, 16283, 16284):
            qhalf(a, b)
    result = {
        'evidence_class': 'linked_BaseMulScale_witness_and_executable_word_butterfly_not_AVX2_kernel',
        'canonical_actual_overflow_witness': witness,
        'positive_Q_half_identity': 'vpavgw(signbias(a),signbias(b)) unbias = ceil((a+b)/2); add 1728 iff parity(a xor b)=1',
        'input_cases': len(cases),
        'cohort_degree_blocks_per_case': 24,
        'butterfly_operands_have_disjoint_leaf_supports': True,
        'disjoint_support_checks': 6 * 80,
        'correlation_scope': 'accepted canonical CT/SK coefficients may vary independently across quartic leaves; valid KEM-derived inputs can be narrower, but canonical invalid inputs still reach BaseMulScale',
        'max_BaseMulScale_raw_abs_observed': max_raw,
        'max_modular_half_output_abs_observed': max_qhalf,
        'max_abs_by_stage_observed': max_by_stage,
        'formal_uniform_radix2_bounds': formal_bounds,
        'formal_final_y32_untwist_abs_bound': final_untwist_bound,
        'formal_bound_argument': 'signed ceil average of two values in [-B,B] stays in [-B,B]; odd correction adds 1728; lower twiddle uses conservative Montgomery bound; no 16-bit add of unhalved values',
        'all_blocks_modq_match_independent_scalar_CT': True,
        'all_signed_word_assertions_pass': True,
        'scale': 'per-level modular division by two; no deferred 1/32 in this radix2 block; full tail constants must be regenerated',
        'machine_ledger': 'not_lowered; two qhalf outputs share one parity correction, but sign bias, negation, routing, constant loads, 16-YMM allocation and complete tail remain to price',
        'source_sha256': {str(path.relative_to(ROOT)):
                          hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__), INPUT, FACTORS, TOWER,
                                       ROOT / 'upstream/supercop-avx2/basemul.s',
                                       ROOT / 'upstream/supercop-avx2/consts.c')},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key != 'source_sha256'}, indent=2))


if __name__ == '__main__':
    main()
