#!/usr/bin/env python3
"""Compare complete materialized AVX2 macro schedules for two true-y CT inverses.

The packet schedule is intentionally conservative: every radix-2 stage and
each tail phase uses the existing 1536-byte backing. Its explicit register
budget and constant-profile counts are not a linked instruction allocation.
"""

import hashlib
import json
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import Q, ROOT, route
from research_mixed_gauge_vector_schedule import ownership
from research_physical_true_twist_replay import build as physical_build
from research_true_twist_repair_v2 import FACTORS, INPUT, TOWER, verified
from research_twiddle_half_absorption import RECIPE

RESULT = ROOT / 'results/yang-true-y-twist-two-schedules-20260923.json'
SELECTIVE = ROOT / 'results/yang-true-y-twist-selective-repair-20260923.json'
MIXED = ROOT / 'results/yang-true-y-twist-mixed-gauge-full-tail-20260923.json'


def stage_cost(rows, plan=None, mixed=False):
    stages = []
    prefix = Counter()
    all_profiles = set()
    for stage in (6, 5, 4, 3, 2):
        details = rows[str(stage)]
        stage_rows = []
        for packet in range(6):
            pair_rows = details[4 * packet:4 * packet + 4]
            active = []
            repairs = 0
            half_mixed = half_full = 0
            for pair, row in enumerate(pair_rows):
                factors = (row['candidate_factors'] if mixed
                           else row['original_factors'])
                if any(w != 1 for w in factors):
                    active.append(tuple(factors))
                if mixed:
                    masks = [RECIPE[kind][2] == 'half'
                             for kind in row['lane_kinds']]
                    if any(masks):
                        half_full += all(masks)
                        half_mixed += not all(masks)
                else:
                    repair = plan[str(stage)][4 * packet + pair]
                    repairs += int(repair['reduce_a']) + int(repair['reduce_b'])
            profiles = set(active)
            all_profiles.update(profiles)
            item = {
                'packet': packet,
                'Montgomery_vector_pairs': len(active),
                'Barrett_repair_vectors': repairs,
                'qhalf_full_vector_pairs': half_full,
                'qhalf_mixed_vector_pairs': half_mixed,
                'distinct_nonidentity_twiddle_profiles': len(profiles),
                'twiddle_pair_loads_lower_bound_if_cached_within_packet': 2 * len(profiles),
                'twiddle_pair_loads_if_reloaded_every_multiply': 2 * len(active),
                'data_loads_stage_materialized': 8,
                'data_stores_stage_materialized': 8,
                'route_groups': 0 if stage == 2 else 2,
                'route_vector_pairs': 0 if stage == 2 else 4,
            }
            stage_rows.append(item)
            for key in ('Montgomery_vector_pairs', 'Barrett_repair_vectors',
                        'qhalf_full_vector_pairs', 'qhalf_mixed_vector_pairs',
                        'twiddle_pair_loads_lower_bound_if_cached_within_packet',
                        'twiddle_pair_loads_if_reloaded_every_multiply',
                        'data_loads_stage_materialized',
                        'data_stores_stage_materialized', 'route_groups',
                        'route_vector_pairs'):
                prefix[key] += item[key]
        stages.append({'stage': stage, 'packets': stage_rows,
                       'totals': {key: sum(row[key] for row in stage_rows)
                                  for key in stage_rows[0] if key != 'packet'}})
    return stages, dict(prefix), all_profiles


def path_layers(rows, plan=None, mixed=False):
    # A structural path, not a cycles/latency model. The field `layers`
    # counts data-dependent macro boundaries; individual AVX2 op latency is
    # deliberately not assigned.
    empty = (0, 0, 0, 0, 0, 0)  # layers, M, B, half, add, route
    mem = [[empty] * 16 for _ in range(48)]
    report = []
    for stage in (6, 5, 4, 3, 2):
        new = [None] * 48
        for packet in range(6):
            upper, lower = [], []
            for pair in range(4):
                a, b = mem[8 * packet + pair], mem[8 * packet + pair + 4]
                row = rows[str(stage)][4 * packet + pair]
                factors = (row['candidate_factors'] if mixed
                           else row['original_factors'])
                repair = None if mixed else plan[str(stage)][4 * packet + pair]
                out = []
                for aa, bb, factor, kind in zip(a, b, factors, row['lane_kinds']):
                    ra = int(bool(repair and repair['reduce_a']))
                    rb = int(bool(repair and repair['reduce_b']))
                    aa = (aa[0] + ra, aa[1], aa[2] + ra,
                          aa[3], aa[4], aa[5])
                    bb = (bb[0] + rb + int(factor != 1),
                          bb[1] + int(factor != 1), bb[2] + rb,
                          bb[3], bb[4], bb[5])
                    chosen = max((aa, bb), key=lambda value: value[0])
                    half = int(mixed and RECIPE[kind][2] == 'half')
                    out.append((chosen[0] + 1 + half, chosen[1], chosen[2],
                                chosen[3] + half, chosen[4] + 1,
                                chosen[5]))
                upper.append(out)
                lower.append(out)
            outputs = upper + lower
            if stage == 2:
                new[8 * packet:8 * packet + 8] = outputs
            else:
                for pair in range(4):
                    lo, hi = route(stage, outputs[2 * pair], outputs[2 * pair + 1])
                    new[8 * packet + pair] = [(v[0] + 1, *v[1:5], v[5] + 1)
                                              for v in lo]
                    new[8 * packet + pair + 4] = [(v[0] + 1, *v[1:5], v[5] + 1)
                                                  for v in hi]
        mem = new
        report.append({'stage': stage,
                       'maximum_macro_layers': max(v[0] for row in mem for v in row),
                       'max_M_on_selected_path': max(v[1] for row in mem for v in row),
                       'max_B_on_selected_path': max(v[2] for row in mem for v in row),
                       'max_qhalf_on_selected_path': max(v[3] for row in mem for v in row)})
    return report


def main():
    verified(INPUT)
    verified(FACTORS)
    verified(TOWER)
    selective = json.loads(SELECTIVE.read_text())
    mixed = json.loads(MIXED.read_text())
    nodes, physical_rows, _ = physical_build()
    _, routes, mixed_rows = ownership()
    plain_rows = {str(stage): [{
        'original_factors': [lane['twiddle'] for lane in row],
        'lane_kinds': mixed_rows[str(stage)][index]['lane_kinds'],
    } for index, row in enumerate(rows)]
        for stage, rows in zip((6, 5, 4, 3, 2), physical_rows)}
    s_stages, s_prefix, s_profiles = stage_cost(plain_rows,
                                               selective['plans'])
    m_stages, m_prefix, m_profiles = stage_cost(mixed_rows, mixed=True)
    assert s_prefix['Montgomery_vector_pairs'] == 78
    assert m_prefix['Montgomery_vector_pairs'] == 96
    assert s_prefix['Barrett_repair_vectors'] == 24
    assert m_prefix['Barrett_repair_vectors'] == 0
    assert m_prefix['qhalf_mixed_vector_pairs'] == 24
    assert m_prefix['qhalf_full_vector_pairs'] == 24
    assert routes == {6: 24, 5: 24, 4: 24, 3: 24, 2: 0}
    untwist_profiles = {tuple(pow(node.xi, -node.k, Q) for node in vec)
                        for vec in nodes}
    assert len(untwist_profiles) == 48
    common_tail = {
        'y32_untwist_Montgomery_vectors': 48,
        'radix3_Montgomery_vectors': 48,
        'level0_and_final_Montgomery_vectors': 72,
        'top_Barrett_vectors': 16,
        'distinct_y32_untwist_profiles': len(untwist_profiles),
        'top_data_loads_materialized': 144,
        'top_data_stores_materialized': 144,
        'top_dependency': 'untwist -> radix3 omega/alpha -> level0 phi/final',
    }
    def summarize(prefix, profiles):
        return {
            'prefix': prefix,
            'full_Montgomery_vectors': prefix['Montgomery_vector_pairs'] + 168,
            'full_Barrett_vectors': prefix['Barrett_repair_vectors'] + 16,
            'full_data_loads_materialized': prefix['data_loads_stage_materialized'] + 144,
            'full_data_stores_materialized': prefix['data_stores_stage_materialized'] + 144,
            'distinct_prefix_nonidentity_twiddle_profiles': len(profiles),
            'minimum_prefix_twiddle_table_bytes_paired_words': 64 * len(profiles),
            'minimum_untwist_table_bytes_paired_words': 64 * len(untwist_profiles),
        }
    result = {
        'evidence_class': 'complete_same_boundary_materialized_macro_schedule_not_linked_AVX2_or_cycles',
        'semantic_controls': {
            'selective_repair_101_compiled_BaseMulScale_cases':
            selective['physical_semantic_replay']['modq_inverse_and_crepmod3_byte_exact'],
            'mixed_gauge_101_compiled_BaseMulScale_cases':
            mixed['physical_AVX2_route_modq_and_crepmod3_byte_exact'],
        },
        'physical_root_choice': 'xi is first physical upper-child leaf; zeta is lower-child xi / upper-child xi at every AVX2 butterfly',
        'stage_routes': routes,
        'schedule_policy': 'for each stage and 8-vector packet: load one route group of two butterfly pairs (four vectors), compute pair 0 then pair 1, route their four outputs, store to the same backing; stage 2 needs no route; untwist, radix3 and level0 each materialize to that backing',
        'register_budget': {
            'stage_route_group_live_data_vectors': 4,
            'first_pair_outputs_held_during_second_pair': 2,
            'isolated_mixed_pair_linked_register_names': 9,
            'assumed_pair_macro_register_cap_including_constant_temporaries': 10,
            'conservative_pair_plus_pending_cap': 12,
            'route_four_outputs_plus_two_temporaries_cap': 6,
            'tail_triplet_macro_cap': 12,
            'peak_claim': 'at most 12 macro-allocated YMM under stage materialization; exact instruction-level def/use and linked spill not proved',
        },
        'common_tail': common_tail,
        'selective_repair': {'stages': s_stages,
                             'macro_dependency_layers': path_layers(plain_rows,
                                 selective['plans']),
                             'summary': summarize(s_prefix, s_profiles)},
        'mixed_gauge': {'stages': m_stages,
                        'macro_dependency_layers': path_layers(mixed_rows,
                            mixed=True),
                        'summary': summarize(m_prefix, m_profiles)},
        'limits': ['all constant load counts are paired-profile traffic bounds, not linked load uops',
                   'the conservative schedule incurs large symmetric stage traffic and does not establish a compact-loop win',
                   'macro register caps are explicit scheduling constraints, not complete AVX2 def/use allocation',
                   'dependency layers are unweighted graph depth, not cycles'],
        'source_sha256': {str(path.relative_to(ROOT)):
                          hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__), SELECTIVE, MIXED, FACTORS,
                                       ROOT / 'tools/research_physical_true_twist_replay.py',
                                       ROOT / 'tools/research_mixed_gauge_vector_schedule.py')},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('source_sha256', 'selective_repair', 'mixed_gauge')},
                     indent=2))
    print(json.dumps({'selective': result['selective_repair']['summary'],
                      'mixed': result['mixed_gauge']['summary'],
                      'selective_depth': result['selective_repair']['macro_dependency_layers'],
                      'mixed_depth': result['mixed_gauge']['macro_dependency_layers']},
                     indent=2))


if __name__ == '__main__':
    main()
