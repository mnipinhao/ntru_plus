#!/usr/bin/env python3
"""Source-anchored caller census for existing-multiply range repairs.

This is a prototype selection gate, not a linked def/use or cycle proof.
"""

import hashlib
import json
from pathlib import Path

from probe_inverse_ct_gauge import ROOT

RESULT = ROOT / 'results/officialopt-defuse-repair-gate-20260923.json'
SCREEN = ROOT / 'results/yang-true-y-twist-repair-v2-20260923.json'
FORWARD = ROOT / 'results/officialopt-forward-lane-proof-20260921.json'
CONSUMER = ROOT / 'results/officialopt-forward-consumer-proof-20260921.json'
UPSTREAM = ROOT / 'upstream/supercop-avx2'
QUAL = ROOT / 'qualification/avx2-officialopt-caller-lazy-qual001'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    screen = json.loads(SCREEN.read_text())
    for name, digest in screen['source_sha256'].items():
        assert sha(ROOT / name) == digest, ('stale true-twist screen', name)
    for name, digest in screen['proof_inputs_sha256'].items():
        assert sha(ROOT / name) == digest, ('stale proof input', name)
    forward = json.loads(FORWARD.read_text())
    consumer = json.loads(CONSUMER.read_text())
    assert sha(UPSTREAM / 'ntt.s') == forward['ntt_source_sha256']
    assert set(forward['domains']) == {
        'keygen_f', 'keygen_g', 'encap_r', 'encap_m',
        'decap_message', 'decap_reenc_r'}
    assert all(name in consumer for name in ('keygen', 'encap', 'decap'))

    ntt = (QUAL / 'ntt_caller_lazy.s').read_text()
    kem = (QUAL / 'kem.c').read_text()
    poly = (UPSTREAM / 'poly.c').read_text()
    basemul = (UPSTREAM / 'basemul.s').read_text()
    inverse = (UPSTREAM / 'invntt.s').read_text()
    assert 'ntruplus768_officialopt_ntt_caller_lazy' in ntt
    assert ntt.count('vpmulhrsw') == 0, 'unexpected standalone Barrett in caller-lazy Forward'
    assert 'fqinv_batch' in poly and '_mm256_cmpeq_epi16' in poly
    assert '_mm256_mulhrs_epi16' not in poly
    assert 'vpmulhrsw' not in basemul
    assert 'poly_basemul_scale(&m, &c, &f)' in kem
    assert 'poly_invntt_scale(&m)' in kem
    assert 'ntruplus768_officialopt_ntt_caller_lazy(&r)' in kem
    assert 'ntruplus768_officialopt_ntt_caller_lazy(&m)' in kem
    level3 = inverse.split('#level3\n', 1)[1].split('#level2\n', 1)[0]
    for row in ('vpaddw %ymm7,  %ymm3, %ymm11',
                'vpsubw %ymm7,  %ymm3, %ymm7',
                'vpmullw %ymm15, %ymm7,  %ymm3',
                'vpmulhrsw %ymm1, %ymm11, %ymm3'):
        assert row in level3, ('GS def/use changed', row)
    assert level3.index('vpaddw %ymm7,  %ymm3, %ymm11') < \
           level3.index('vpmulhrsw %ymm1, %ymm11, %ymm3')
    assert level3.index('vpsubw %ymm7,  %ymm3, %ymm7') < \
           level3.index('vpmullw %ymm15, %ymm7,  %ymm3')
    first = screen['first_unproved_per_cohort_degree']
    assert len(first) == 24
    assert all(not row['existing_multiply_before_add'] for row in first)

    result = {
        'evidence_class': 'source_anchored_candidate_selection_not_linked_schedule_or_performance',
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in
                          (UPSTREAM / 'ntt.s', UPSTREAM / 'invntt.s',
                           UPSTREAM / 'basemul.s', UPSTREAM / 'poly.c',
                           QUAL / 'ntt_caller_lazy.s', QUAL / 'kem.c')},
        'proof_sha256': {str(p.relative_to(ROOT)): sha(p)
                         for p in (SCREEN, FORWARD, CONSUMER)},
        'caller': {
            'keygen': {
                'input_domains': ['keygen_f', 'keygen_g'],
                'existing_repair': 'caller-lazy removes 48 terminal Barrett vectors per Forward; remaining BaseInv fqmul/fqsqr reductions are intrinsic to runtime multiplication',
                'nearest_existing_fixed_multiply': 'BaseInv R3 correction and application of inverted denominator occur after product/zero dependencies',
                'candidate_status': 'no independent hazardous add with a proven earlier existing constant multiply; no new ASM authorized',
                'blocking_contract': 'literal zero test and retry/clear sequence'},
            'encap': {
                'input_domains': ['encap_r', 'encap_m'],
                'existing_repair': 'caller-lazy removes 48 terminal Barrett vectors per Forward; BaseMul has Montgomery-internal reductions and no standalone Barrett',
                'nearest_existing_fixed_multiply': 'quartic zeta correction consumes accumulated products; R2 finalizer precedes add-m',
                'candidate_status': 'no removable independent repair proven; no new ASM authorized',
                'blocking_contract': 'r hash bytes, h validation, add-m scale and ciphertext bytes'},
            'decap': {
                'input_domains': ['canonical_decoded_c_f_hinv', 'decap_message', 'decap_reenc_r'],
                'true_twist_first_failed_cohort_degree_nodes': 24,
                'true_twist_first_failed_identity_twiddle_nodes': 24,
                'first_node_sizes': screen['first_failure_node_sizes'],
                'existing_GS_dependency': 'difference branch twiddle consumes subtraction output; untwiddled sum branch has standalone Barrett after addition',
                'verified_level3_register_flow': {
                    'sum': 'vpaddw ymm7,ymm3 -> ymm11; Barrett reads ymm11 later',
                    'difference': 'vpsubw ymm7,ymm3 -> ymm7; Montgomery reads ymm7 later'},
                'candidate_status': 'no chain-free existing-multiply repair at first true-twist hazards; no full range/scale/allocation schedule, so no ASM authorized',
                'blocking_contract': 'BaseMulScale lane bounds, deferred 1/32, final y32 untwist, radix3/trinomial, crepmod3'},
        },
        'new_namespaced_ASM_candidates': 0,
        'short_cycle_campaign': 'not_applicable_no_qualified_candidate',
        'scope_limit': 'does not rule out correlated bounds or a new arithmetic decomposition; source-order census is not an instruction-level linked def/use proof',
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'callers': list(result['caller']),
                      'first_identity_hazards': len(first),
                      'selected_ASM_candidates': 0}, indent=2))


if __name__ == '__main__':
    main()
