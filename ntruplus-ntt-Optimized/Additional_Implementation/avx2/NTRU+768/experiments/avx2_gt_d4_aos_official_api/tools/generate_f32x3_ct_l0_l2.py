#!/usr/bin/env python3
"""Generate deterministic CT L0-L2 AoS consumption-order artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

Q = 3457
R = pow(2, 16, Q)
QINV = pow(Q, -1, 1 << 16)
OMEGA32_INV = pow(pow(641, 3, Q), -1, Q)


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def factor_pair(exponent: int) -> tuple[int, int, int]:
    mathematical = pow(OMEGA32_INV, exponent, Q)
    montgomery = mathematical * R % Q
    qinv = signed16(montgomery * QINV)
    return mathematical, montgomery, qinv


def signed_mulhi(left: int, right: int) -> int:
    return (signed16(left) * signed16(right)) >> 16


def generator_self_test(exponents: set[int]) -> None:
    inverse_r = pow(R, -1, Q)

    for exponent in exponents:
        mathematical, factor, factor_qinv = factor_pair(exponent)
        assert factor * inverse_r % Q == mathematical
        assert signed16(factor * QINV) == factor_qinv

        for value in (0, 1, Q - 1, 17, 1729):
            low = signed16(value * factor_qinv)
            reduced = signed_mulhi(value, factor) - signed_mulhi(low, Q)
            assert reduced % Q == value * mathematical % Q


def vector(name: str, exponents: tuple[int, int]) -> dict[str, object]:
    pairs = [factor_pair(exponent) for exponent in exponents]
    factors = [pairs[u][1] for branch in range(2) for u in range(2)
               for _ in range(4)]
    qinvs = [pairs[u][2] for branch in range(2) for u in range(2)
             for _ in range(4)]
    return {
        "name": name,
        "exponents": list(exponents),
        "mathematical": [pairs[0][0], pairs[1][0]],
        "factor_lanes": factors,
        "qinv_lanes": qinvs,
        "lane_order": "8*b+4*u+c",
        "scale_in": "R^0",
        "scale_out": "R^0",
        "input_bound": "[0,3456]",
        "output_bound": "[0,3456]",
    }


def metadata() -> dict[str, object]:
    factors = [
        vector("l1", (0, 8)),
        vector("l2_j1_0", (0, 4)),
        vector("l2_j1_1", (8, 12)),
    ]
    tiles = []
    for row in range(3):
        for tile in range(4):
            base_t = 4 * tile
            source_u = 1 if base_t >= 8 else 0
            sources = []
            for local_t in range(4):
                stage_t = base_t + local_t
                stage_sources = []
                for packed_u in range(2):
                    source_j = int(f"{2 * stage_t + packed_u:05b}"[::-1], 2)
                    stage_sources.append({
                        "block": source_j // 2,
                        "u": source_j & 1,
                    })
                sources.append(stage_sources)
            tiles.append({
                "row": row,
                "tile": tile,
                "base_t": base_t,
                "source_u": source_u,
                "stage_blocks": [base_t + i for i in range(4)],
                "bitrev_sources": sources,
            })
    factor_by_name = {str(item["name"]): item for item in factors}
    consumption_order = []
    layer_positions = (
        ("L0", ((0, "identity"), (1, "identity"),
                 (2, "identity"), (3, "identity"))),
        ("L1", ((0, "l1"), (1, "l1"))),
        ("L2", ((0, "l2_j1_0"), (1, "l2_j1_1"))),
    )

    for tile_record in tiles:
        for layer, positions in layer_positions:
            for butterfly_position, factor_name in positions:
                if factor_name == "identity":
                    mathematical = [1, 1]
                    montgomery = [R, R]
                    qinv = [signed16(R * QINV), signed16(R * QINV)]
                    operation = "direct_add_sub_identity"
                else:
                    factor = factor_by_name[factor_name]
                    mathematical = list(factor["mathematical"])
                    montgomery = [factor["factor_lanes"][0],
                                  factor["factor_lanes"][4]]
                    qinv = [factor["qinv_lanes"][0], factor["qinv_lanes"][4]]
                    operation = "montgomery_ct_butterfly"

                consumption_order.append({
                    "layer": layer,
                    "row": tile_record["row"],
                    "merged_tile": tile_record["tile"],
                    "base_t": tile_record["base_t"],
                    "butterfly_position": butterfly_position,
                    "branches": [0, 1],
                    "packed_u": [0, 1],
                    "quartic_coefficients": [0, 1, 2, 3],
                    "mathematical_inverse_root": mathematical,
                    "montgomery_factor": montgomery,
                    "qinv": qinv,
                    "physical_lane_sequence": "8*b+4*u+c",
                    "operation": operation,
                    "scale": "R^0 -> R^0",
                    "input_bound": "[0,3456]",
                    "output_bound": "[0,3456]",
                })

    return {
        "experiment": "AVX2-GT-D4-AOS-F32X3-CT-MERGED-L0-L2-001",
        "q": Q,
        "omega32_inverse": OMEGA32_INV,
        "qinv_signed16": signed16(QINV),
        "factors": factors,
        "tiles": tiles,
        "consumption_order": consumption_order,
        "logical_groups": {"l0": 48, "l1": 24, "l2": 24},
    }


def asm_vector(label: str, lanes: list[int]) -> str:
    values = ", ".join(str(value) for value in lanes)
    return f".p2align 5\n{label}:\n\t.short {values}\n"


def artifacts() -> dict[str, bytes]:
    meta = metadata()
    factors = meta["factors"]
    asm = "/* Generated by generate_f32x3_ct_l0_l2.py; do not edit. */\n"
    header = "/* Generated by generate_f32x3_ct_l0_l2.py; do not edit. */\n"
    header += "#ifndef D4AOS_F32X3_CT_L0_L2_TABLES_H\n"
    header += "#define D4AOS_F32X3_CT_L0_L2_TABLES_H\n#include <stdint.h>\n"
    for item in factors:
        name = str(item["name"])
        asm += asm_vector(f".Lct_{name}_factor", item["factor_lanes"])
        asm += asm_vector(f".Lct_{name}_qinv", item["qinv_lanes"])
        for suffix, lanes in (("factor", item["factor_lanes"]),
                              ("qinv", item["qinv_lanes"])):
            values = ", ".join(str(value) for value in lanes)
            header += f"static const int16_t d4aos_ct_{name}_{suffix}[16] = {{{values}}};\n"
    header += "#endif\n"
    result = {
        "d4_aos_f32x3_ct_l0_l2_tables.inc": asm.encode(),
        "d4_aos_f32x3_ct_l0_l2_tables.h": header.encode(),
        "d4_aos_f32x3_ct_l0_l2_tables.json":
            (json.dumps(meta, indent=2, sort_keys=True) + "\n").encode(),
    }
    manifest = "".join(
        f"{hashlib.sha256(result[name]).hexdigest()}  {name}\n"
        for name in sorted(result)
    ).encode()
    result["MANIFEST.sha256"] = manifest
    return result


def metadata_l3_l4() -> dict[str, object]:
    tables = []
    consumption = []
    exponents = set()

    for tile in range(4):
        specifications = (
            ("l3", "pair_0_4", 0, 4, (4 * tile, 4 * tile + 2)),
            ("l3", "pair_8_12", 8, 12, (4 * tile, 4 * tile + 2)),
            ("l4", "pair_0_8", 0, 8, (2 * tile, 2 * tile + 1)),
            ("l4", "pair_4_12", 4, 12, (8 + 2 * tile, 9 + 2 * tile)),
        )

        for layer, position, source_delta, partner_delta, factor_exponents in specifications:
            table_name = f"{layer}_t{tile}_{position}"
            item = vector(table_name, factor_exponents)
            tables.append(item)
            exponents.update(factor_exponents)

            for row in range(3):
                consumption.append({
                    "layer": layer.upper(),
                    "row": row,
                    "tile": tile,
                    "butterfly_position": position,
                    "source_block": tile + source_delta,
                    "partner_block": tile + partner_delta,
                    "branch": [0, 1],
                    "u": [0, 1],
                    "mathematical_inverse_root": item["mathematical"],
                    "signed_montgomery_factor": [item["factor_lanes"][0],
                                                     item["factor_lanes"][4]],
                    "qinv": [item["qinv_lanes"][0], item["qinv_lanes"][4]],
                    "physical_lane_sequence": "8*b+4*u+c",
                    "input_scale": "R^0",
                    "output_scale": "R^0",
                    "input_bound": "[0,3456]",
                    "output_bound": "[0,3456]",
                })

    generator_self_test(exponents | {0})
    return {
        "experiment": "AVX2-GT-D4-AOS-F32X3-CT-MERGED-L3-L4-001",
        "q": Q,
        "omega32_inverse": OMEGA32_INV,
        "qinv_signed16": signed16(QINV),
        "tile_block_map": [
            {"tile": tile, "blocks": [tile, tile + 4, tile + 8, tile + 12]}
            for tile in range(4)
        ],
        "tables": tables,
        "consumption_order": consumption,
        "logical_groups": {"l3": 24, "l4": 24},
        "self_test": "basis/factor-reconstruction/Montgomery-comparison",
    }


def artifacts_l3_l4() -> dict[str, bytes]:
    meta = metadata_l3_l4()
    asm = "/* Generated by generate_f32x3_ct_l0_l2.py; do not edit. */\n"
    header = "/* Generated by generate_f32x3_ct_l0_l2.py; do not edit. */\n"
    header += "#ifndef D4AOS_F32X3_CT_L3_L4_TABLES_H\n"
    header += "#define D4AOS_F32X3_CT_L3_L4_TABLES_H\n#include <stdint.h>\n"

    for item in meta["tables"]:
        name = str(item["name"])
        asm += asm_vector(f".Lct_{name}_factor", item["factor_lanes"])
        asm += asm_vector(f".Lct_{name}_qinv", item["qinv_lanes"])
        for suffix, lanes in (("factor", item["factor_lanes"]),
                              ("qinv", item["qinv_lanes"])):
            values = ", ".join(str(value) for value in lanes)
            header += f"static const int16_t d4aos_ct_{name}_{suffix}[16] = {{{values}}};\n"

    header += "#endif\n"
    result = {
        "d4_aos_f32x3_ct_l3_l4_tables.inc": asm.encode(),
        "d4_aos_f32x3_ct_l3_l4_tables.h": header.encode(),
        "d4_aos_f32x3_ct_l3_l4_tables.json":
            (json.dumps(meta, indent=2, sort_keys=True) + "\n").encode(),
    }
    manifest = "".join(
        f"{hashlib.sha256(result[name]).hexdigest()}  {name}\n"
        for name in sorted(result)
    ).encode()
    result["MANIFEST.sha256"] = manifest
    return result


def metadata_dft3() -> dict[str, object]:
    omega3 = pow(pow(641, 32, Q), -1, Q)
    mathematical = omega3
    montgomery_positive = omega3 * R % Q
    montgomery_signed = (montgomery_positive - Q
                         if montgomery_positive > Q // 2
                         else montgomery_positive)
    omega_qinv = signed16(montgomery_signed * QINV)
    barrett_v = (1 << 26) // Q
    generator_self_test({32})

    entries = []
    for block in range(16):
        entries.append({
            "t": block,
            "branch": [0, 1],
            "u": [0, 1],
            "quartic_coefficient_group": [0, 1, 2, 3],
            "mathematical_omega": mathematical,
            "signed_montgomery_representation": montgomery_signed,
            "qinv": omega_qinv,
            "physical_lane_order": "8*b+4*u+c",
            "consumer_instruction_region": "COMPACT_IDFT3_BARRETT omega chain",
        })

    return {
        "experiment": "AVX2-GT-D4-AOS-F32X3-COMPACT-DFT3-001",
        "q": Q,
        "omega3": omega3,
        "omega3_montgomery_signed": montgomery_signed,
        "omega3_qinv": omega_qinv,
        "barrett_v": barrett_v,
        "input_scale": "R^0",
        "output_scale": "R^0",
        "input_bound": "[0,3456]",
        "raw_bounds": {"D0": "[0,10368]", "D1_D2": "[-5368,5368]"},
        "reduced_bound": "[0,3457]",
        "row_block_entries": entries,
    }


def artifacts_dft3() -> dict[str, bytes]:
    meta = metadata_dft3()
    repeated = lambda value: ", ".join([str(value)] * 16)
    asm = "/* Generated by generate_f32x3_ct_l0_l2.py; do not edit. */\n"
    asm += f".p2align 5\n.Ld4_dft3_q:\n\t.short {repeated(Q)}\n"
    asm += f".p2align 5\n.Ld4_dft3_barrett_v:\n\t.short {repeated(meta['barrett_v'])}\n"
    asm += f".p2align 5\n.Ld4_dft3_omega_qinv:\n\t.short {repeated(meta['omega3_qinv'])}\n"
    asm += f".p2align 5\n.Ld4_dft3_omega:\n\t.short {repeated(meta['omega3_montgomery_signed'])}\n"
    header = "/* Generated by generate_f32x3_ct_l0_l2.py; do not edit. */\n"
    header += "#ifndef D4AOS_F32X3_DFT3_TABLES_H\n#define D4AOS_F32X3_DFT3_TABLES_H\n"
    header += f"#define D4AOS_DFT3_OMEGA {meta['omega3']}\n"
    header += f"#define D4AOS_DFT3_OMEGA_MONT {meta['omega3_montgomery_signed']}\n"
    header += f"#define D4AOS_DFT3_OMEGA_QINV {meta['omega3_qinv']}\n"
    header += f"#define D4AOS_DFT3_BARRETT_V {meta['barrett_v']}\n#endif\n"
    result = {
        "d4_aos_f32x3_dft3_tables.inc": asm.encode(),
        "d4_aos_f32x3_dft3_tables.h": header.encode(),
        "d4_aos_f32x3_dft3_tables.json":
            (json.dumps(meta, indent=2, sort_keys=True) + "\n").encode(),
    }
    manifest = "".join(
        f"{hashlib.sha256(result[name]).hexdigest()}  {name}\n"
        for name in sorted(result)
    ).encode()
    result["MANIFEST.sha256"] = manifest
    return result


def metadata_terminal() -> dict[str, object]:
    inverse32 = pow(32, Q - 2, Q)
    inverse3 = pow(3, Q - 2, Q)
    inverse96 = inverse32 * inverse3 % Q
    twist_base = (22, 2)
    crt_alpha = (2735, 723)
    delta_inverse = pow((crt_alpha[0] - crt_alpha[1]) % Q, Q - 2, Q)
    records = []

    dft_slot_to_row = (0, 2, 1)
    for block in range(16):
        for dft_slot, row in enumerate(dft_slot_to_row):
            factor_lanes = []
            qinv_lanes = []
            constituents = []
            offsets = []
            for branch in range(2):
                for packed_u in range(2):
                    natural_index = (64 * row + 33 * (2 * block + packed_u)) % 96
                    untwist = pow(twist_base[branch], Q - 1 - natural_index, Q)
                    combined = inverse96 * untwist % Q
                    montgomery = combined * R % Q
                    factor_qinv = signed16(montgomery * QINV)
                    factor_lanes.extend([montgomery] * 4)
                    qinv_lanes.extend([factor_qinv] * 4)
                    constituents.append({
                        "branch": branch,
                        "u": packed_u,
                        "natural_index": natural_index,
                        "untwist_factor": untwist,
                        "inverse_length_factor": inverse32,
                        "inverse_dft3_factor": inverse3,
                        "rminus1_compensation": 1,
                        "branch_correction": 1,
                        "combined_mathematical": combined,
                        "montgomery": montgomery,
                        "qinv": factor_qinv,
                    })
            for packed_u in range(2):
                natural_index = (64 * row + 33 * (2 * block + packed_u)) % 96
                offsets.append(8 * natural_index)
            for packed_u in range(2):
                natural_index = (64 * row + 33 * (2 * block + packed_u)) % 96
                offsets.append(768 + 8 * natural_index)
            for item in constituents:
                reconstructed = (item["untwist_factor"] * item["inverse_length_factor"] *
                                 item["inverse_dft3_factor"] *
                                 item["rminus1_compensation"] *
                                 item["branch_correction"]) % Q
                assert reconstructed == item["combined_mathematical"]
            # Rebuild in physical half order: both u values for low, then high.
            def direct_vector(low_values: list[int], high_values: list[int]) -> tuple[list[int], list[int]]:
                values = []
                qinvs = []
                for mathematical in low_values + high_values:
                    montgomery = mathematical * R % Q
                    values.extend([montgomery] * 4)
                    qinvs.extend([signed16(montgomery * QINV)] * 4)
                return values, qinvs
            p_values, p_qinvs = direct_vector(
                [constituents[u]["combined_mathematical"] *
                 (1 - crt_alpha[0] * delta_inverse) % Q for u in range(2)],
                [-constituents[2 + u]["combined_mathematical"] * delta_inverse % Q
                 for u in range(2)])
            q_values, q_qinvs = direct_vector(
                [constituents[2 + u]["combined_mathematical"] *
                 crt_alpha[0] * delta_inverse % Q for u in range(2)],
                [constituents[u]["combined_mathematical"] * delta_inverse % Q
                 for u in range(2)])
            records.append({
                "r": row, "dft_slot": dft_slot, "t": block,
                "quartic_coefficient_group": [0, 1, 2, 3],
                "constituents": constituents,
                "factor_lanes": factor_lanes,
                "qinv_lanes": qinv_lanes,
                "direct_p_lanes": p_values,
                "direct_p_qinv_lanes": p_qinvs,
                "direct_q_lanes": q_values,
                "direct_q_qinv_lanes": q_qinvs,
                "output_offsets": offsets,
                "input_scale": "R^0", "output_scale": "R^0",
                "input_range": "[0,3457]", "output_range": "[0,3456]",
                "physical_lane_order": "8*b+4*u+c",
                "consumer": "FUSED_D4_TERMINAL",
            })
    return {
        "experiment": "AVX2-GT-D4-AOS-F32X3-TERMINAL-001",
        "inverse32": inverse32, "inverse3": inverse3, "inverse96": inverse96,
        "twist_base": list(twist_base), "crt_alpha": list(crt_alpha),
        "delta_inverse": delta_inverse,
        "alpha0": crt_alpha[0], "records": records,
        "consumption_order": "t-major, DFT slots D0,D1,D2 map to r=0,2,1",
    }


def artifacts_terminal() -> dict[str, bytes]:
    meta = metadata_terminal()
    asm = "/* Generated by generate_f32x3_ct_l0_l2.py; do not edit. */\n"
    asm += ".p2align 5\n.Lterminal_offsets:\n"
    for record in meta["records"]:
        asm += "\t.long " + ", ".join(str(x) for x in record["output_offsets"]) + "\n"
    asm += ".p2align 5\n.Lterminal_direct_tables:\n"
    for record in meta["records"]:
        for key in ("direct_p_lanes", "direct_p_qinv_lanes",
                    "direct_q_lanes", "direct_q_qinv_lanes"):
            asm += "\t.short " + ", ".join(str(x) for x in record[key]) + "\n"
    header = "/* Generated by generate_f32x3_ct_l0_l2.py; do not edit. */\n"
    header += "#ifndef D4AOS_F32X3_TERMINAL_TABLES_H\n#define D4AOS_F32X3_TERMINAL_TABLES_H\n"
    header += f"#define D4AOS_TERMINAL_INV96 {meta['inverse96']}\n"
    header += f"#define D4AOS_TERMINAL_DELTA_INV {meta['delta_inverse']}\n#endif\n"
    result = {
        "d4_aos_f32x3_terminal_tables.inc": asm.encode(),
        "d4_aos_f32x3_terminal_tables.h": header.encode(),
        "d4_aos_f32x3_terminal_tables.json":
            (json.dumps(meta, indent=2, sort_keys=True) + "\n").encode(),
    }
    manifest = "".join(f"{hashlib.sha256(result[n]).hexdigest()}  {n}\n"
                       for n in sorted(result)).encode()
    result["MANIFEST.sha256"] = manifest
    return result


def check(directory: Path, expected: dict[str, bytes], label: str) -> None:
    names = {path.name for path in directory.iterdir() if path.is_file()}
    if names != set(expected):
        raise SystemExit(f"artifact names differ: {sorted(names)}")
    with tempfile.TemporaryDirectory(prefix="d4aos-ct-l0-l2-") as temp:
        regenerated = Path(temp)
        for name, content in expected.items():
            (regenerated / name).write_bytes(content)
        for name, content in expected.items():
            if (directory / name).read_bytes() != content:
                raise SystemExit(f"stale artifact: {name}")
            if (regenerated / name).read_bytes() != content:
                raise SystemExit(f"regeneration mismatch: {name}")
    digest = hashlib.sha256(b"".join(expected[name] for name in sorted(expected))).hexdigest()
    print(f"{label}=passed digest={digest}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", choices=sorted(artifacts()))
    parser.add_argument("--check-dir", type=Path)
    parser.add_argument("--l3-l4-artifact", choices=sorted(artifacts_l3_l4()))
    parser.add_argument("--l3-l4-check-dir", type=Path)
    parser.add_argument("--dft3-artifact", choices=sorted(artifacts_dft3()))
    parser.add_argument("--dft3-check-dir", type=Path)
    parser.add_argument("--terminal-artifact", choices=sorted(artifacts_terminal()))
    parser.add_argument("--terminal-check-dir", type=Path)
    args = parser.parse_args()
    if args.check_dir:
        check(args.check_dir, artifacts(), "f32x3-ct-l0-l2-generated-check")
    elif args.l3_l4_check_dir:
        check(args.l3_l4_check_dir, artifacts_l3_l4(),
              "f32x3-ct-l3-l4-generated-check")
    elif args.dft3_check_dir:
        check(args.dft3_check_dir, artifacts_dft3(),
              "f32x3-compact-dft3-generated-check")
    elif args.terminal_check_dir:
        check(args.terminal_check_dir, artifacts_terminal(),
              "f32x3-terminal-generated-check")
    elif args.artifact:
        print(artifacts()[args.artifact].decode(), end="")
    elif args.l3_l4_artifact:
        print(artifacts_l3_l4()[args.l3_l4_artifact].decode(), end="")
    elif args.dft3_artifact:
        print(artifacts_dft3()[args.dft3_artifact].decode(), end="")
    elif args.terminal_artifact:
        print(artifacts_terminal()[args.terminal_artifact].decode(), end="")
    else:
        print(json.dumps(metadata(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
