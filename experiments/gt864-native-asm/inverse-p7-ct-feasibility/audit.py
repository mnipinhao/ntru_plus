#!/usr/bin/env python3
"""P7: reproducible CT/GS, ordering, range, instruction and memory audit."""

from __future__ import annotations

import collections
import hashlib
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
REF = ROOT / ("ntruplus-ntt-Optimized/Additional_Implementation/aarch64/Experiment/"
              "NTRU+864/good_thomas_campaign/experiments/gt_fr0_inverse_consumer/"
              "gt864_fr0_inverse.c")
OFFICIAL = ROOT / ("experiments/gt864-native-asm/baseinv-tobytes-next-model/"
                   "official-results/official-source/ntt.s")
PROFILE = ROOT / "experiments/gt864-native-asm/official-profile-20260911/results.json"
Q = 3457
N = 16
BITREV4 = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primitive_root_16() -> int:
    for g in range(2, Q):
        w = pow(g, (Q - 1) // N, Q)
        if pow(w, N, Q) == 1 and pow(w, N // 2, Q) != 1:
            return w
    raise AssertionError("no order-16 root")


def ct_dit_bitrev_input(values: list[int], root: int) -> list[int]:
    a = [values[BITREV4[i]] % Q for i in range(N)]
    length = 2
    while length <= N:
        step_root = pow(root, N // length, Q)
        for start in range(0, N, length):
            w = 1
            for j in range(length // 2):
                u = a[start + j]
                v = a[start + j + length // 2] * w % Q
                a[start + j] = (u + v) % Q
                a[start + j + length // 2] = (u - v) % Q
                w = w * step_root % Q
        length *= 2
    return a


def gs_dif_natural_input(values: list[int], root: int) -> list[int]:
    a = [x % Q for x in values]
    length = N
    while length >= 2:
        step_root = pow(root, N // length, Q)
        for start in range(0, N, length):
            w = 1
            for j in range(length // 2):
                u = a[start + j]
                v = a[start + j + length // 2]
                a[start + j] = (u + v) % Q
                a[start + j + length // 2] = (u - v) * w % Q
                w = w * step_root % Q
        length //= 2
    return a


def dft(values: list[int], root: int) -> list[int]:
    return [sum(values[j] * pow(root, j * k, Q) for j in range(N)) % Q
            for k in range(N)]


def ordering_trials(count: int = 10_000) -> dict[str, object]:
    root = primitive_root_16()
    rng = random.Random(0x5037C7)
    for case in range(count):
        x = [rng.randrange(Q) for _ in range(N)]
        want = dft(x, root)
        ct = ct_dit_bitrev_input(x, root)
        gs_raw = gs_dif_natural_input(x, root)
        gs_natural = [gs_raw[BITREV4[i]] for i in range(N)]
        assert ct == want, case
        assert gs_natural == want, case
    return {
        "trials": count,
        "root_order_16": root,
        "bit_reverse4": BITREV4,
        "ct_contract": "bit-reversed input -> natural output",
        "gs_contract": "natural input -> bit-reversed output",
        "mismatches": 0,
    }


def source_instruction_counts(path: Path) -> dict[str, object]:
    counts: collections.Counter[str] = collections.Counter()
    for raw in path.read_text().splitlines():
        line = raw.split("//", 1)[0].strip()
        if (not line or line.endswith(":") or line.startswith((".", "#", "/*", "*"))
                or ".req" in line or ".unreq" in line):
            continue
        counts[line.split()[0].lower()] += 1
    return {"instructions_including_ret": sum(counts.values()), "operations": dict(counts)}


def official_dynamic_count() -> dict[str, int]:
    lines = OFFICIAL.read_text().splitlines()

    def is_instruction(raw: str) -> bool:
        line = raw.split("//", 1)[0].strip()
        return bool(line and not line.endswith(":") and
                    not line.startswith((".", "#", "/*", "*")) and
                    ".req" not in line and ".unreq" not in line)

    def operations(part: list[str]) -> collections.Counter[str]:
        out: collections.Counter[str] = collections.Counter()
        for raw in part:
            if is_instruction(raw):
                out[raw.split("//", 1)[0].strip().split()[0].lower()] += 1
        return out

    def locate(text: str, after: int = -1) -> int:
        return next(i for i, line in enumerate(lines) if i > after and line.strip() == text)

    start = locate("poly_invntt_scale:")
    end = locate("ret", start)
    l1 = locate("_looptop_6543:", start)
    l1_end = locate("sub dst, dst, #1728", l1)
    l2 = locate("_looptop_210:", l1_end)
    l2_end = locate("b.ne _looptop_210", l2)
    loop1 = sum(map(is_instruction, lines[l1 + 1:l1_end]))
    loop2 = sum(map(is_instruction, lines[l2 + 1:l2_end + 1]))
    static = sum(map(is_instruction, lines[start + 1:end + 1]))
    outside = static - loop1 - loop2
    whole_ops = operations(lines[start + 1:end + 1])
    loop1_ops = operations(lines[l1 + 1:l1_end])
    loop2_ops = operations(lines[l2 + 1:l2_end + 1])
    outside_ops = whole_ops - loop1_ops - loop2_ops
    dynamic_ops = outside_ops + collections.Counter({
        key: value * 18 for key, value in loop1_ops.items()
    }) + collections.Counter({
        key: value * 6 for key, value in loop2_ops.items()
    })
    return {
        "loop_6543_instructions": loop1,
        "loop_6543_iterations": 18,
        "loop_210_instructions": loop2,
        "loop_210_iterations": 6,
        "outside_loop_instructions": outside,
        "estimated_dynamic_instructions": loop1 * 18 + loop2 * 6 + outside,
        "estimated_dynamic_operations": dict(dynamic_ops),
    }


def range_model() -> dict[str, object]:
    # A fixed Algorithm-10 product returns magnitude < q. CT therefore grows
    # only the unmultiplied u path by q per layer. GS doubles its sum path.
    b = 3456
    ct = [b]
    for _ in range(4):
        b += Q - 1
        ct.append(b)
    b = 3456
    gs = [b]
    for _ in range(4):
        b *= 2
        gs.append(b)
    assert ct[-1] < 32768
    assert gs[-2] < 32768 <= gs[-1]
    return {
        "input_abs": 3456,
        "ct_conservative_layer_abs": ct,
        "current_correlation_aware_ct_peak_abs": 30939,
        "gs_unreduced_sum_path_abs": gs,
        "int16_max": 32767,
        "conclusion": "GS needs at least one sum-path range cut; CT does not",
    }


def coordinate_checks() -> dict[str, object]:
    fr_seen = set()
    for top in range(2):
        for row in range(9):
            for column in range(16):
                block, lane = divmod(column, 8)
                group = top * 18 + row * 2 + block
                for component in range(3):
                    idx = 24 * group + 8 * component + lane
                    assert 0 <= idx < 864 and idx not in fr_seen
                    fr_seen.add(idx)
    assert len(fr_seen) == 864

    natural_seen = set()
    for top_half in range(2):
        for t in range(16):
            for s in range(9):
                for component in range(3):
                    idx = 3 * (s + 9 * (t + 16 * top_half)) + component
                    assert idx not in natural_seen
                    natural_seen.add(idx)
    assert natural_seen == set(range(864))
    return {
        "fr0_index": "24*(top*18 + row*2 + column//8) + 8*component + column%8",
        "fr0_bijection_coefficients": len(fr_seen),
        "natural_index": "3*(s + 9*(t + 16*top_half)) + component",
        "natural_bijection_coefficients": len(natural_seen),
        "degree_3_components": 3,
    }


def main() -> None:
    ref_text = REF.read_text()
    official_text = OFFICIAL.read_text()
    assert "int16x8_t v = fqmul_public" in ref_text
    assert "value[left] = vaddq_s16(u, v);" in ref_text
    assert "value[right] = vsubq_s16(u, v);" in ref_text
    assert re.search(r"sub v10\.8h, v7\.8h, v4\.8h.*?add v4\.8h, v4\.8h, v7\.8h.*?mul v7\.8h, v10\.8h",
                     official_text, re.S)

    kernels = {}
    calls = {"packed_i9": 12, "lazy_i16": 6, "lazy_itail": 1}
    files = {
        "packed_i9": PROD / "gt864_native_inverse9.S",
        "lazy_i16": PROD / "gt864_native_inverse16_lazy.S",
        "lazy_itail": PROD / "gt864_native_inverse_tail_lazy.S",
        "center864": PROD / "gt864_native_center864.S",
    }
    for name, path in files.items():
        kernels[name] = source_instruction_counts(path)
        kernels[name]["sha256"] = sha256(path)
    leaf_dynamic = sum((kernels[name]["instructions_including_ret"] * count)
                       for name, count in calls.items())
    # center864: seven setup instructions, 43 loop instructions x27, ret.
    center_dynamic = 7 + 43 * 27 + 1
    assert center_dynamic == 1169
    gt_dynamic_ops: collections.Counter[str] = collections.Counter()
    for name, count in calls.items():
        gt_dynamic_ops.update({
            op: amount * count for op, amount in kernels[name]["operations"].items()
        })
    center_ops = kernels["center864"]["operations"]
    # Seven setup instructions and ret execute once; the 43-instruction body
    # (from the first LDR through B.NE) executes 27 times.
    for op, amount in center_ops.items():
        if op in {"mov", "dup"}:
            gt_dynamic_ops[op] += amount
        elif op == "ret":
            gt_dynamic_ops[op] += 1
        else:
            gt_dynamic_ops[op] += amount * 27

    profile = json.loads(PROFILE.read_text())["call_site_profile"]["decaps"]
    official_cycles = profile["official"]["Inverse"]["net_cycles"]["median"]
    gt_cycles = profile["gt"]["Inverse"]["net_cycles"]["median"]
    result = {
        "status": "pass-local-ct-benefit-only",
        "classification": {
            "gt_inverse16": "Cooley-Tukey DIT",
            "gt_inverse9": "oriented radix-3 direct inverse DFT; twiddle-on-input/CT-side",
            "selected_official_inverse": "Gentleman-Sande DIF",
            "mixed_binary_ct_gs_layers_in_gt_inverse16": False,
        },
        "source_identity": {
            "gt_reference_c_sha256": sha256(REF),
            "selected_official_ntt_s_sha256": sha256(OFFICIAL),
        },
        "coordinates": coordinate_checks(),
        "ordering_proof": ordering_trials(),
        "range": range_model(),
        "gt_static_kernels": kernels,
        "gt_dynamic_leaf_instruction_estimate": {
            "inverse9_12_calls": kernels["packed_i9"]["instructions_including_ret"] * 12,
            "inverse16_main_6_calls": kernels["lazy_i16"]["instructions_including_ret"] * 6,
            "inverse16_tail_1_call": kernels["lazy_itail"]["instructions_including_ret"],
            "center864_1_call": center_dynamic,
            "total_before_public_wrapper": leaf_dynamic + center_dynamic,
            "operations": dict(gt_dynamic_ops),
        },
        "selected_official_dynamic_instruction_estimate": official_dynamic_count(),
        "memory_ledger_bytes": {
            "gt_transform_input_read": 1728,
            "gt_p8_write": 1728,
            "gt_p8_read_including_64_padding": 1792,
            "gt_natural_scatter_write": 1728,
            "gt_center_read": 1728,
            "gt_center_write": 1728,
            "gt_tail_initialization_write": 256,
            "gt_scratch_wipe_write": 1792,
            "gt_scratch_bytes": 1792,
            "explicit_full_polynomial_bitrev_pass": 0,
        },
        "terminal_scatter": {
            "main_umov": 128 * 6,
            "main_strh": 128 * 6,
            "tail_umov": 96,
            "tail_strh": 96,
            "total_umov": 864,
            "total_scalar_stores": 864,
            "st1_lane_control": "rejected: +484.157 cycles at complete inverse",
        },
        "pi5_profile_cycles": {
            "selected_official_inverse": official_cycles,
            "gt_inverse": gt_cycles,
            "gt_minus_official": gt_cycles - official_cycles,
            "gt_percent_slower": (gt_cycles / official_cycles - 1.0) * 100.0,
        },
        "decision": {
            "ct_local_benefit_realized": True,
            "ct_end_to_end_win_established": False,
            "production_changed": False,
            "reason": "CT is the right fixed-ABI radix-16 choice, but CT/GS is not the dominant whole-inverse cost",
        },
    }
    (HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
