#!/usr/bin/env python3
"""Conservative signed-i16 interval replay of the CT radix-2 prototype.

The caller's actual BaseMulScale output envelope must be supplied separately;
this script reports the largest *uniform* input bound accepted by the CT
prefix, rather than assuming random differential tests constitute a proof.
"""

import argparse
import json
from functools import lru_cache
from math import ceil
from pathlib import Path

from probe_inverse_ct_gauge import Q, R, ROOT, compute, route


def mont_bound(input_bound, factor):
    word = (factor * R) % Q
    centered = min(word, Q - word)
    return ceil(input_bound * centered / 65536) + 1729


def mont_worst_bound(input_bound):
    return ceil(input_bound * 1728 / 65536) + 1729


@lru_cache(maxsize=None)
def barrett_bound(input_bound):
    if input_bound > 32767:
        raise ValueError("Barrett input already exceeds signed-i16")
    return max(abs(x - Q * ((x * 9 + 16384) >> 15))
               for x in range(-input_bound, input_bound + 1))


def repaired_replay(initial_bound, data):
    """One public, pair-wise repair pattern shared by all six packets."""
    mem = [[initial_bound] * 16 for _ in range(48)]
    stages, plan = [], {}
    for stage_data in data["stages"]:
        stage = stage_data["stage"]
        new = [[0] * 16 for _ in range(48)]
        repair_pairs = []
        for pair in range(4):
            a_vectors = [mem[packet * 8 + pair] for packet in range(6)]
            b_vectors = [mem[packet * 8 + pair + 4] for packet in range(6)]
            tw_vectors = [stage_data["twiddles"][packet * 4 + pair]
                          for packet in range(6)]
            reduce_a = reduce_b = False
            while True:
                aa = [[barrett_bound(x) for x in vec] if reduce_a else vec
                      for vec in a_vectors]
                bb = [[barrett_bound(x) for x in vec] if reduce_b else vec
                      for vec in b_vectors]
                if any(x > 32767 for vec in bb for x in vec):
                    reduce_b = True
                    continue
                sums = []
                for av, bv, tw in zip(aa, bb, tw_vectors):
                    identity = tw == [1] * 16
                    product = bv if identity else [mont_bound(x, t) for x, t in zip(bv, tw)]
                    sums.extend(x + y for x, y in zip(av, product))
                if max(sums) <= 32767:
                    break
                if not reduce_a and (reduce_b or
                                     max(map(max, a_vectors)) >= max(map(max, b_vectors))):
                    reduce_a = True
                elif not reduce_b:
                    reduce_b = True
                else:
                    raise ValueError(f"cannot repair stage={stage} pair={pair}")
            repair_pairs.append({"a": reduce_a, "b": reduce_b})
            for packet, (av, bv, tw) in enumerate(zip(aa, bb, tw_vectors)):
                base = packet * 8
                identity = tw == [1] * 16
                product = bv if identity else [mont_bound(x, t) for x, t in zip(bv, tw)]
                output = [x + y for x, y in zip(av, product)]
                new[base + pair] = output
                new[base + pair + 4] = output[:]
        if stage != 2:
            routed = [[0] * 16 for _ in range(48)]
            for packet in range(6):
                base = packet * 8
                for pair in range(4):
                    lo, hi = route(stage, new[base + 2 * pair],
                                   new[base + 2 * pair + 1])
                    routed[base + pair] = lo
                    routed[base + pair + 4] = hi
            new = routed
        mem = new
        plan[stage] = repair_pairs
        stages.append({"stage": stage, "max_abs_bound": max(map(max, mem)),
                       "repaired_vectors": 6 * sum(x["a"] + x["b"] for x in repair_pairs),
                       "per_vector_max_abs_bound": list(map(max, mem))})
    gauges = data["stages"][-1]["output_gauges"]
    normalized = [[mont_bound(bound, gauge) for bound, gauge in zip(vec, words)]
                  for vec, words in zip(mem, gauges)]
    norm_max = max(x for vec in normalized for x in vec)
    # The unchanged radix-3 tail forms Y-Z, X-Y-w(Y-Z), X-Z+w(Y-Z),
    # and X+Y+Z before its fixed Montgomery/Barrett operations.  This is
    # deliberately a uniform over-approximation; no exact output claim.
    radix3_y_minus_z = 2 * norm_max
    radix3_w_term = mont_worst_bound(radix3_y_minus_z)
    radix3_alpha_input = 2 * norm_max + radix3_w_term
    radix3_sum = 3 * norm_max
    radix3_reduced_sum = barrett_bound(radix3_sum)
    level0_input = max(radix3_reduced_sum,
                       mont_worst_bound(radix3_alpha_input))
    level0_pair = 2 * level0_input
    tail = {"post_gauge_normalization_max_abs": norm_max,
            "radix3_y_minus_z_max_abs": radix3_y_minus_z,
            "radix3_alpha_mont_input_max_abs": radix3_alpha_input,
            "radix3_sum_before_barrett_max_abs": radix3_sum,
            "level0_pair_add_sub_max_abs": level0_pair,
            "all_signed_i16_preoperations_safe":
                max(radix3_alpha_input, radix3_sum, level0_pair) <= 32767}
    if not tail["all_signed_i16_preoperations_safe"]:
        raise ValueError("unchanged radix-3/level-0 tail exceeds signed i16")
    return {"input_abs_bound": initial_bound, "stages": stages, "plan": plan,
            "total_repaired_vectors": sum(s["repaired_vectors"] for s in stages),
            "unchanged_tail_uniform_bound": tail}


def replay(initial_bound, data):
    mem = [[initial_bound] * 16 for _ in range(48)]
    stages = []
    failures = []
    for stage_data in data["stages"]:
        stage = stage_data["stage"]
        new = [[0] * 16 for _ in range(48)]
        for packet in range(6):
            base = packet * 8
            upper, lower = [], []
            for pair in range(4):
                a = mem[base + pair]
                b = mem[base + pair + 4]
                tw = stage_data["twiddles"][packet * 4 + pair]
                identity_vector = tw == [1] * 16
                if identity_vector:
                    product = b
                else:
                    product = [mont_bound(x, w) for x, w in zip(b, tw)]
                for lane, (bound_a, bound_b, t) in enumerate(zip(a, b, tw)):
                    if bound_b > 32767:
                        failures.append([stage, packet, pair, lane, "Mont_input", bound_b])
                    if identity_vector and bound_a + bound_b > 32767:
                        failures.append([stage, packet, pair, lane, "add_or_sub", bound_a + bound_b])
                out = [x + y for x, y in zip(a, product)]
                for lane, bound in enumerate(out):
                    if bound > 32767:
                        failures.append([stage, packet, pair, lane, "CT_output", bound])
                upper.append(out)
                lower.append(out[:])
            if stage == 2:
                new[base:base + 8] = upper + lower
            else:
                inputs = upper + lower
                for pair in range(4):
                    lo, hi = route(stage, inputs[2 * pair], inputs[2 * pair + 1])
                    new[base + pair] = lo
                    new[base + pair + 4] = hi
        mem = new
        stages.append({"stage": stage, "max_abs_bound": max(map(max, mem)),
                       "per_vector_max_abs_bound": list(map(max, mem)),
                       "failures_so_far": len(failures)})
    gauges = data["stages"][-1]["output_gauges"]
    for vector, (bounds, words) in enumerate(zip(mem, gauges)):
        for lane, (bound, gauge) in enumerate(zip(bounds, words)):
            if bound > 32767:
                failures.append(["final", vector, lane, "Mont_input", bound])
            mont_bound(bound, gauge)
    return {"input_abs_bound": initial_bound, "stages": stages,
            "failure_count": len(failures), "first_failures": failures[:16]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-bound", type=int, default=7644)
    args = parser.parse_args()
    # The pinned Decap path decodes both BaseMulScale operands canonically.
    # Signed high-word product <= floor((q-1)^2 / 2^16); the Montgomery
    # low-word correction contributes at most 1729 in absolute value.
    runtime_product = ((Q - 1) * (Q - 1)) // 65536 + 1729
    zeta_of_two_products = mont_worst_bound(2 * runtime_product)
    caller_plane_bounds = {
        "c0": runtime_product + zeta_of_two_products,
        "c1": 2 * runtime_product + zeta_of_two_products,
        "c2": 3 * runtime_product + zeta_of_two_products,
        "c3": 4 * runtime_product,
    }
    if args.input_bound < max(caller_plane_bounds.values()):
        raise ValueError("requested input bound does not cover BaseMulScale ledger")
    data = compute()
    given = replay(args.input_bound, data)
    repaired = repaired_replay(args.input_bound, data)
    low, high = 0, 32767
    while low < high:
        mid = (low + high + 1) // 2
        if replay(mid, data)["failure_count"]:
            high = mid - 1
        else:
            low = mid
    result = {"kind": "conservative_symmetric_uniform_bound_with_source_level_caller_ledger",
              "caller_bound_derivation": {
                  "canonical_input_interval": [0, Q - 1],
                  "runtime_montgomery_product_max_abs": runtime_product,
                  "zeta_of_two_products_max_abs": zeta_of_two_products,
                  "plane_bounds": caller_plane_bounds,
                  "note": "source-level formula census; not machine-exhaustive bit-vector proof"},
              "given": given, "repaired": repaired,
              "max_uniform_input_abs_bound": low}
    output = ROOT / "results/officialopt-inverse-ct-range-20260921.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
