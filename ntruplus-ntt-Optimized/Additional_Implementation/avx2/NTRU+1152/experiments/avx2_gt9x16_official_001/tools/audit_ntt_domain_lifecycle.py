#!/usr/bin/env python3
"""Audit the pinned Official forward/BaseMul/BaseInv/inverse physical lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_function(path: Path, name: str) -> dict:
    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(path)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    symbols = subprocess.run(
        ["nm", "-n", str(path)], check=True, text=True,
        stdout=subprocess.PIPE).stdout
    globals_text = [(int(address, 16), symbol) for address, symbol in
                    re.findall(r"^([0-9a-f]+)\s+T\s+(\S+)$", symbols, re.MULTILINE)]
    starts = {symbol: address for address, symbol in globals_text}
    if name not in starts:
        raise SystemExit(f"missing Official function {name}")
    text_size_output = subprocess.run(
        ["size", "-A", str(path)], check=True, text=True,
        stdout=subprocess.PIPE).stdout
    text_size_match = re.search(r"^\.text\s+(\d+)\s+", text_size_output, re.MULTILINE)
    if not text_size_match:
        raise SystemExit(f"missing .text size for {path}")
    start = starts[name]
    end = min((address for address, _ in globals_text if address > start),
              default=int(text_size_match.group(1)))
    all_lines = re.findall(r"^\s*([0-9a-f]+):\s+.*$", disassembly, re.MULTILINE)
    selected_addresses = {address for address in map(lambda value: int(value, 16), all_lines)
                          if start <= address < end}
    lines = [line for line in disassembly.splitlines()
             if (match := re.match(r"^\s*([0-9a-f]+):\s+", line)) and
             int(match.group(1), 16) in selected_addresses]
    body = "\n".join(lines)
    ymm = sorted({int(value) for value in re.findall(r"\bymm(\d+)\b", body)})
    vector_loads = sum(bool(re.search(
        r"\bvmov\w*\s+[xy]mm\d+\s*,\s*(?:[XY]MMWORD|DWORD|QWORD) PTR \[", line))
        for line in lines)
    vector_stores = sum(bool(re.search(
        r"\bvmov\w*\s+(?:[XY]MMWORD|DWORD|QWORD) PTR \[[^]]+\]\s*,\s*[xy]mm\d+", line))
        for line in lines)
    return {
        "object": path.name,
        "object_sha256": sha256(path),
        "static_instruction_count": len(lines),
        "vector_load_instruction_count": vector_loads,
        "vector_store_instruction_count": vector_stores,
        "distinct_ymm_registers": ymm,
        "distinct_ymm_count": len(ymm),
        "conservative_peak_live_ymm": 16 if len(ymm) == 16 else len(ymm),
        "calls": len(re.findall(r"\bcall\b", body)),
        "vzeroupper": len(re.findall(r"\bvzeroupper\b", body)),
        "stack_references": len(re.findall(r"\[(?:r|e)?(?:sp|bp)[^]]*\]", body)),
        "frame_instructions": sum(bool(re.search(
            r"\b(?:push|pop|enter|leave)\b|\b(?:sub|add)\s+rsp", line)) for line in lines),
    }


def require(text: str, patterns: list[str], label: str) -> None:
    for pattern in patterns:
        if pattern not in text:
            raise SystemExit(f"{label}: pinned source no longer contains {pattern!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ntt-object", type=Path, required=True)
    parser.add_argument("--basemul-object", type=Path, required=True)
    parser.add_argument("--baseinv-object", type=Path, required=True)
    parser.add_argument("--invntt-object", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    ntt_source = (args.upstream / "ntt.s").read_text()
    basemul_source = (args.upstream / "basemul.s").read_text()
    baseinv_source = (args.upstream / "baseinv.s").read_text()
    invntt_source = (args.upstream / "invntt.s").read_text()
    consts_source = (args.upstream / "consts.c").read_text()
    poly_source = (args.upstream / "poly.c").read_text()
    kem_source = (args.upstream / "kem.c").read_text()
    require(ntt_source, ["_looptop_start_3456:", "vmovdqa %ymm10, 224(%rdi)"], "forward")
    require(basemul_source, ["_reduce_R2_loop:", ".global poly_basemul_scale"], "BaseMul")
    require(baseinv_source, ["vmovdqu %ymm8, (%rsi)", "vmovdqu %ymm8, 32(%rsi)"], "BaseInv phase 1")
    require(poly_source, ["__m256i den[18]", "poly_baseinv_2(r, den)"], "BaseInv wrapper")
    require(invntt_source, ["_looptop_start_6543:", "_16xNinv_scale"], "inverse")
    require(consts_source, ["#define NINV_SCALE -33"], "inverse scale")
    require(kem_source, ["poly_basemul_scale(&m, &c, &f);", "poly_invntt_scale(&m);"], "KEM caller")
    if pow(288, -1, 3457) * pow(2, 32, 3457) % 3457 != (-33) % 3457:
        raise SystemExit("inverse R^-1 scale proof failed")

    functions = {
        "poly_ntt": object_function(args.ntt_object, "poly_ntt"),
        "poly_basemul": object_function(args.basemul_object, "poly_basemul"),
        "poly_basemul_scale": object_function(args.basemul_object, "poly_basemul_scale"),
        "poly_baseinv_1": object_function(args.baseinv_object, "poly_baseinv_1"),
        "poly_invntt_scale": object_function(args.invntt_object, "poly_invntt_scale"),
    }
    for name, audit in functions.items():
        if audit["calls"] or audit["vzeroupper"] or audit["stack_references"] or audit["frame_instructions"]:
            raise SystemExit(f"{name}: Official leaf invariant changed")

    document = {
        "parameter": 1152,
        "source": "pinned SUPERCOP NTRU+1152 AVX2",
        "source_hashes": {
            name: sha256(args.upstream / name)
            for name in ("ntt.s", "basemul.s", "baseinv.s", "invntt.s", "consts.c", "poly.c", "kem.c")
        },
        "functions": functions,
        "boundaries": {
            "forward_terminal_store": {
                "bytes": 2304,
                "outer_blocks": 9,
                "bytes_per_outer_block": 256,
                "terminal_blocks_per_outer_block": 2,
                "vectors_per_terminal_block": 4,
                "vector_offsets_bytes": [0, 32, 64, 96],
                "terminal_coefficient_order": [0, 1, 2, 3],
                "standalone_permutation_after_store": False,
                "scale_r_exponent": 0,
            },
            "regular_basemul": {
                "input_terminal_blocks": 18,
                "input_vectors_per_operand_per_block": 4,
                "input_vector_offsets_bytes": [0, 32, 64, 96],
                "factor_constants": "lane-wise zeta*qinv and zeta; one 64-byte pair per two terminal blocks",
                "output_layout": "same four-vector terminal-major block shape",
                "output_scale_r_exponent": 0,
                "post_arithmetic_pass": "in-kernel full-array R^2 Montgomery pass",
                "standalone_layout_conversion": False,
            },
            "scaled_basemul_inverse_feed": {
                "input_layout": "same as regular BaseMul",
                "output_layout": "same four-vector terminal-major block shape",
                "output_scale_r_exponent": -1,
                "post_arithmetic_pass": "none; deliberately omits regular BaseMul R^2 pass",
                "observed_caller_edge": "poly_basemul_scale -> poly_invntt_scale",
                "standalone_layout_conversion": False,
            },
            "baseinv": {
                "phase1_input_vectors_per_terminal_block": 4,
                "phase1_input_vector_offsets_bytes": [0, 32, 64, 96],
                "phase1_output_layout": "same four-vector terminal-major block shape",
                "phase1_side_output": "18 denominator YMM vectors",
                "wrapper_stack_object": "den[18], 576 bytes before compiler alignment/other state",
                "phase2": "batch-invert denominators then multiply four output vectors per terminal block",
                "final_output_scale_r_exponent": 0,
                "standalone_layout_conversion": False,
            },
            "inverse_load": {
                "bytes": 2304,
                "outer_blocks": 9,
                "bytes_per_outer_block": 256,
                "vectors_loaded_per_outer_block": 8,
                "vector_offsets_bytes": [0, 32, 64, 96, 128, 160, 192, 224],
                "expected_input_scale_r_exponent": -1,
                "normalization": "inverse constants include the scale expected from poly_basemul_scale",
                "standalone_permutation_before_load": False,
                "scale_proof": {
                    "ninv_scale_signed": -33,
                    "ninv_scale_mod_q": (-33) % 3457,
                    "equals_inverse_288_times_r_squared_mod_q":
                        pow(288, -1, 3457) * pow(2, 32, 3457) % 3457,
                    "interpretation": "one extra R versus an R^0 inverse normalization compensates the R^-1 input",
                },
            },
        },
        "lifecycle_edges": [
            {"producer": "poly_ntt", "consumer": "poly_basemul/poly_baseinv", "scale": "R^0", "conversion": "none"},
            {"producer": "poly_basemul", "consumer": "later NTT-domain arithmetic/storage", "scale": "R^0", "conversion": "none"},
            {"producer": "poly_baseinv", "consumer": "poly_basemul", "scale": "R^0", "conversion": "none"},
            {"producer": "poly_basemul_scale", "consumer": "poly_invntt_scale", "scale": "R^-1", "conversion": "none"},
        ],
        "audit_conclusion": {
            "official_resident_layout": "18 contiguous terminal-major blocks; four YMM coefficients x 16 factors",
            "inverse_feed_is_distinct_scale_contract": True,
            "baseinv_has_denominator_side_channel": True,
            "all_hot_assembly_leaves_use_all_16_ymm": all(
                entry["distinct_ymm_count"] == 16 for entry in functions.values()),
            "standalone_full_layout_passes": 0,
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated NTT-domain lifecycle audit is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
