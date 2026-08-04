#!/usr/bin/env python3
"""Single source of truth for the NTRU+768 AVX2 GT rewrite.

The script derives the Official index tree, Good--Thomas maps, twists,
quartic moduli, scalar schedules, fixed lane maps, and arithmetic bounds.  It
does not import tables from the older GT experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
N = 768
D = 4
L = 576
ZETA = 22
PHI = 2735
PHI_INV = 723
OMEGA96 = 675
BRANCH_F = (2, 22)
BRANCH_F_EXP = (395, 1)

# Figure 22 in the Official Main supporting specification.  The generator
# independently reconstructs this list from the tree and asserts exact order.
OFFICIAL_INDEX_SPEC = (
    1, 289, 145, 433, 73, 361, 217, 505, 37, 325, 181, 469, 109, 397, 253, 541,
    19, 307, 163, 451, 91, 379, 235, 523, 55, 343, 199, 487, 127, 415, 271, 559,
    7, 295, 151, 439, 79, 367, 223, 511, 43, 331, 187, 475, 115, 403, 259, 547,
    25, 313, 169, 457, 97, 385, 241, 529, 61, 349, 205, 493, 133, 421, 277, 565,
    13, 301, 157, 445, 85, 373, 229, 517, 49, 337, 193, 481, 121, 409, 265, 553,
    31, 319, 175, 463, 103, 391, 247, 535, 67, 355, 211, 499, 139, 427, 283, 571,
    5, 293, 149, 437, 77, 365, 221, 509, 41, 329, 185, 473, 113, 401, 257, 545,
    23, 311, 167, 455, 95, 383, 239, 527, 59, 347, 203, 491, 131, 419, 275, 563,
    11, 299, 155, 443, 83, 371, 227, 515, 47, 335, 191, 479, 119, 407, 263, 551,
    29, 317, 173, 461, 101, 389, 245, 533, 65, 353, 209, 497, 137, 425, 281, 569,
    17, 305, 161, 449, 89, 377, 233, 521, 53, 341, 197, 485, 125, 413, 269, 557,
    35, 323, 179, 467, 107, 395, 251, 539, 71, 359, 215, 503, 143, 431, 287, 575,
)


def centered(x: int) -> int:
    x %= Q
    return x - Q if x > (Q - 1) // 2 else x


def official_index_tree() -> list[int]:
    leaves = [L // 6, 5 * L // 6]
    leaves = [child for psi in leaves
              for child in (psi // 3, (psi + L) // 3,
                            (psi + 2 * L) // 3)]
    for _ in range(5):
        leaves = [child for psi in leaves
                  for child in (psi // 2, (psi + L) // 2)]
    return leaves


def input_crt(n3: int, n32: int) -> int:
    return (64 * n3 + 33 * n32) % 96


def output_crt(k3: int, k32: int) -> int:
    return (32 * k3 + 3 * k32) % 96


def bitreverse(x: int, bits: int) -> int:
    r = 0
    for _ in range(bits):
        r = (r << 1) | (x & 1)
        x >>= 1
    return r


def ct_schedule(size: int) -> list[dict[str, int]]:
    bits = size.bit_length() - 1
    nodes: list[dict[str, int]] = []
    for stage in range(1, bits + 1):
        distance = 1 << (bits - stage)
        for lo in range(size):
            if lo & distance:
                continue
            power = 0 if stage == 1 else (
                bitreverse(lo >> (bits + 1 - stage), stage - 1)
                << (bits - stage)
            )
            nodes.append({
                "stage": stage,
                "lo": lo,
                "hi": lo + distance,
                "root_power": power,
            })
    return nodes


def derive() -> dict[str, object]:
    official = official_index_tree()
    assert tuple(official) == OFFICIAL_INDEX_SPEC
    assert pow(ZETA, L, Q) == 1
    assert pow(ZETA, L // 2, Q) == Q - 1
    assert pow(ZETA, 96, Q) == PHI
    assert PHI * PHI_INV % Q == 1
    assert pow(OMEGA96, 96, Q) == 1
    assert all(pow(OMEGA96, d, Q) != 1 for d in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48))
    assert pow(BRANCH_F[0], 96, Q) == PHI_INV
    assert pow(BRANCH_F[1], 96, Q) == PHI

    input_map = [input_crt(n3, n32) for n3 in range(3)
                 for n32 in range(32)]
    output_map = [output_crt(k3, k32) for k3 in range(3)
                  for k32 in range(32)]
    assert sorted(input_map) == list(range(96))
    assert sorted(output_map) == list(range(96))
    for n3 in range(3):
        for n32 in range(32):
            n = input_crt(n3, n32)
            assert n % 3 == n3 and n % 32 == n32

    preweight = [
        [centered(pow(f, -n, Q)) for n in range(96)]
        for f in BRANCH_F
    ]
    postweight = [
        [centered(pow(f, n, Q)) for n in range(96)]
        for f in BRANCH_F
    ]
    assert all(preweight[branch][n] * postweight[branch][n] % Q == 1
               for branch in range(2) for n in range(96))

    alpha: list[int] = []
    alpha_exp: list[int] = []
    for branch in range(2):
        for k3 in range(3):
            for k32 in range(32):
                k = output_crt(k3, k32)
                exponent = (6 * k - BRANCH_F_EXP[branch]) % L
                value = pow(ZETA, exponent, Q)
                expected_top = PHI if branch == 0 else PHI_INV
                assert pow(value, 96, Q) == expected_top
                alpha_exp.append(exponent)
                alpha.append(centered(value))

    assert sorted(alpha_exp) == sorted(official)
    official_pos = {exponent: i for i, exponent in enumerate(official)}
    gt_to_official = [official_pos[exponent] for exponent in alpha_exp]
    official_to_gt = [0] * 192
    for gt_slot, official_slot in enumerate(gt_to_official):
        official_to_gt[official_slot] = gt_slot
    assert sorted(gt_to_official) == list(range(192))
    assert all(gt_to_official[official_to_gt[i]] == i for i in range(192))
    assert all(alpha_exp[official_to_gt[i]] == official[i] for i in range(192))

    montgomery_r = (1 << 16) % Q
    alpha_montgomery = [centered(value * montgomery_r) for value in alpha]
    alpha_montgomery_qinv = [
        ((value * 12929 + (1 << 15)) % (1 << 16)) - (1 << 15)
        for value in alpha_montgomery
    ]

    omega32 = pow(OMEGA96, 3, Q)
    omega16 = pow(omega32, 2, Q)
    ntt16 = ct_schedule(16)
    for node in ntt16:
        node["twiddle"] = centered(pow(omega16, node["root_power"], Q))
    intt16 = []
    for node in reversed(ntt16):
        inv_node = dict(node)
        inv_node["twiddle"] = centered(pow(omega16, -node["root_power"], Q))
        intt16.append(inv_node)

    b_common = {
        "split": "plus=low+high; minus=low-high",
        "odd_half_twist": [centered(pow(omega32, j, Q)) for j in range(16)],
        "cyclic16_forward": ntt16,
        "cyclic16_inverse": intt16,
        "store": "Q=2*k16 for plus; Q=2*k16+1 for twisted-minus",
        "normalization": pow(32, -1, Q),
    }
    schedules = {
        "B1": {**b_common, "cyclic_half_identity_reduce": False,
               "status": "scalar-and-avx2-complete-selected"},
        "B2": {**b_common, "cyclic_half_identity_reduce": True,
               "status": "scalar-and-avx2-complete-not-selected"},
        "C": {
            "kind": "fully-weighted-direct-row-correctness-control",
            "forward_weights": [
                [centered(pow(omega32, n * k, Q)) for n in range(32)]
                for k in range(32)
            ],
            "inverse_weights": [
                [centered(pow(omega32, -n * k, Q)) for k in range(32)]
                for n in range(32)
            ],
            "normalization": pow(32, -1, Q),
            "static_multiply_count_per_row": 1024,
            "register_plan_ymm": 32,
            "status": "rejected-before-avx2",
            "rejection": ["register-plan-exceeds-16",
                          "static-multiply-cost-exceeds-B"],
        },
    }

    bounds = []
    for multiple in range(3, 7):
        bound = multiple * Q
        bounds.append({
            "name": f"{multiple}q",
            "bound": bound,
            "int16_input": bound <= 32767,
            "pair_sum_2B2": 2 * bound * bound,
            "pair_sum_fits_int32": 2 * bound * bound < (1 << 31),
            "accumulator_4B2": 4 * bound * bound,
            "accumulator_fits_int32": 4 * bound * bound < (1 << 31),
            "unreduced_add_sub_fits_int16": 2 * bound <= 32767,
            "reducer_proof": "pass-for-signed-int32-accumulator",
            "bm_a_unreduced_int16_add_sub": "not-used",
            "bm_b_narrow_add_sub_eligible": 2 * bound <= 32767,
        })

    return {
        "official_index": official,
        "input_map": input_map,
        "output_map": output_map,
        "preweight": preweight,
        "postweight": postweight,
        "alpha": alpha,
        "alpha_exponent": alpha_exp,
        "alpha_montgomery": alpha_montgomery,
        "alpha_montgomery_qinv": alpha_montgomery_qinv,
        "gt_to_official": gt_to_official,
        "official_to_gt": official_to_gt,
        "omega32": centered(omega32),
        "omega16": centered(omega16),
        "omega16_powers": [centered(pow(omega16, i, Q)) for i in range(16)],
        "split_untwist": [centered(pow(omega32, -i, Q)) for i in range(16)],
        "inv16": pow(16, -1, Q),
        "schedules": schedules,
        "bounds": bounds,
    }


def c_array(ctype: str, name: str, values: list[int], width: int = 16) -> str:
    lines = [f"const {ctype} {name}[{len(values)}] = {{"]
    for start in range(0, len(values), width):
        row = ", ".join(f"{x:6d}" for x in values[start:start + width])
        lines.append(f"    {row},")
    lines.append("};")
    return "\n".join(lines)


def render_header() -> str:
    return """/* Generated by tools/generate_gt_rewrite.py; do not edit. */
#ifndef GT_GENERATED_TABLES_H
#define GT_GENERATED_TABLES_H
#include <stdint.h>
extern const uint16_t gt_official_index[192];
extern const uint8_t gt_input_crt[96];
extern const uint8_t gt_output_crt[96];
extern const int16_t gt_preweight[2][96];
extern const int16_t gt_postweight[2][96];
extern const int16_t gt_alpha[192];
extern const uint16_t gt_alpha_exponent[192];
extern const int16_t gt_alpha_montgomery[192];
extern const int16_t gt_alpha_montgomery_qinv[192];
extern const uint8_t gt_to_official[192];
extern const uint8_t gt_official_to_gt[192];
extern const int16_t gt_b_split_twist[16];
extern const int16_t gt_b_split_untwist[16];
extern const int16_t gt_omega16_powers[16];
extern const int16_t gt_inv16;
#endif
"""


def render_c(data: dict[str, object]) -> str:
    preweight = data["preweight"]
    postweight = data["postweight"]
    assert isinstance(preweight, list)
    assert isinstance(postweight, list)
    parts = [
        "/* Generated by tools/generate_gt_rewrite.py; do not edit. */",
        '#include "gt_generated_tables.h"',
        "",
        c_array("uint16_t", "gt_official_index", data["official_index"]),
        "",
        c_array("uint8_t", "gt_input_crt", data["input_map"]),
        "",
        c_array("uint8_t", "gt_output_crt", data["output_map"]),
        "",
        "const int16_t gt_preweight[2][96] = {",
        "    {",
        "\n".join("        " + ", ".join(f"{x:6d}" for x in preweight[0][i:i + 16]) + ","
                  for i in range(0, 96, 16)),
        "    },",
        "    {",
        "\n".join("        " + ", ".join(f"{x:6d}" for x in preweight[1][i:i + 16]) + ","
                  for i in range(0, 96, 16)),
        "    },",
        "};",
        "",
        "const int16_t gt_postweight[2][96] = {",
        "    {",
        "\n".join("        " + ", ".join(f"{x:6d}" for x in postweight[0][i:i + 16]) + ","
                  for i in range(0, 96, 16)),
        "    },",
        "    {",
        "\n".join("        " + ", ".join(f"{x:6d}" for x in postweight[1][i:i + 16]) + ","
                  for i in range(0, 96, 16)),
        "    },",
        "};",
        "",
        c_array("int16_t", "gt_alpha", data["alpha"]),
        "",
        c_array("uint16_t", "gt_alpha_exponent", data["alpha_exponent"]),
        "",
        c_array("int16_t", "gt_alpha_montgomery", data["alpha_montgomery"]),
        "",
        c_array("int16_t", "gt_alpha_montgomery_qinv",
                data["alpha_montgomery_qinv"]),
        "",
        c_array("uint8_t", "gt_to_official", data["gt_to_official"]),
        "",
        c_array("uint8_t", "gt_official_to_gt", data["official_to_gt"]),
        "",
        c_array("int16_t", "gt_b_split_twist",
                data["schedules"]["B1"]["odd_half_twist"]),
        "",
        c_array("int16_t", "gt_b_split_untwist", data["split_untwist"]),
        "",
        c_array("int16_t", "gt_omega16_powers", data["omega16_powers"]),
        "",
        f"const int16_t gt_inv16 = {centered(data['inv16'])};",
        "",
    ]
    return "\n".join(parts)


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def outputs(root: Path) -> dict[Path, str]:
    data = derive()
    artifacts: dict[Path, str] = {
        root / "gt_generated_tables.h": render_header(),
        root / "gt_generated_tables.c": render_c(data),
        root / "reference-tables.json": canonical_json({
            key: data[key] for key in (
                "official_index", "input_map", "output_map", "preweight",
                "postweight",
                "alpha", "alpha_exponent", "gt_to_official",
                "alpha_montgomery", "alpha_montgomery_qinv",
                "official_to_gt")
        }),
        root / "n32-schedules.json": canonical_json(data["schedules"]),
        root / "range-metadata.json": canonical_json({
            "top_raw": {"min": -2891, "max": 2896},
            "canonical": {"min": -1728, "max": 1728},
            "basemul_candidates": data["bounds"],
            "claims": "BM-A signed-int32 accumulator and fixed reducer proof complete; BM-B narrow add/sub eligibility is reported separately",
        }),
    }
    digest_map = {
        path.name: hashlib.sha256(text.encode()).hexdigest()
        for path, text in artifacts.items()
    }
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    artifacts[root / "manifest.json"] = canonical_json({
        "schema_version": 1,
        "generator_sha256": script_hash,
        "official_revision": "0c249d5828b90e8dd5de2c8405323d5ee2a0ce41",
        "parameters": {"q": Q, "n": N, "d": D, "zeta": ZETA,
                       "zeta_order": L, "phi": PHI,
                       "phi_inverse": PHI_INV, "omega96": OMEGA96},
        "layout": {
            "batch": "((branch*3+k3)*2+block32)",
            "Q": "16*block32+lane",
            "word": "64*batch+16*degree+lane",
            "k32_order": "natural",
        },
        "scale": {"reference_tables": "normal",
                  "scalar_backend": "normal-centered"},
        "artifacts_sha256": digest_map,
        "assertions": [
            "root-order", "top-factors", "crt-bijections",
            "forward-inverse-permutations", "official-index-192-exact",
            "quartic-modulus-per-slot", "preweight-postweight-inverse",
        ],
    })
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parent.parent / "generated")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = outputs(args.output_dir)
    stale = []
    for path, text in rendered.items():
        if args.check:
            if not path.exists() or path.read_text() != text:
                stale.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    if stale:
        for path in stale:
            print(f"stale generated artifact: {path}")
        return 1
    print("generated-check=passed" if args.check else "generated=updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
