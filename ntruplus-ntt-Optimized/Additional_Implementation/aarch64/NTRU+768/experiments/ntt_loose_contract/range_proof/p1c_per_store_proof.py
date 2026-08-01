#!/usr/bin/env python3
"""P1-C hard gate for removing Forward-NTT final reductions.

The proof is deliberately conservative:

* it is bound to the exact active production NTT and its modular source;
* it checks both mutually-exclusive output suffixes in the flattened source;
* it proves a signed-int16 envelope through all five lazy CT stages;
* it records one result for every logical 8-lane output store and caller; and
* it authorizes assembly generation only when every producer, machine, and
  downstream semantic obligation succeeds.

This script does not generate assembly.  ``--require-safe`` is the hard gate a
future generator must run first.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

Q = 3457
INT16_MIN = -32768
INT16_MAX = 32767
RAW_GT_DFT_ABSMAX = 3 * (Q - 1)
STAGE_COUNT = 5
LOGICAL_STORES_PER_ENDPOINT = 96
VECTOR_LANES = 8

ACTIVE_NTT_SHA256 = (
    "6f874aa58557ba12ed20f36bc3e3bb8c8e642c2f1d70c17bed13453510ecacbc"
)
MODULAR_NTT32_SHA256 = (
    "3ff85cc9c56b82d14f6b7bd5dca1173e5fcc22faa8dd8bba68c0c65e5164a355"
)


@dataclass(frozen=True)
class Interval:
    lo: int
    hi: int

    @property
    def absmax(self) -> int:
        return max(abs(self.lo), abs(self.hi))

    def within(self, other: "Interval") -> bool:
        return self.lo >= other.lo and self.hi <= other.hi


@dataclass(frozen=True)
class Caller:
    name: str
    endpoint: str
    input_bound: Interval
    input_evidence: str
    machine_bound: Interval
    machine_obligation: str
    semantic_bound: Interval
    semantic_obligation: str


def repository_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (
            (parent / "ntruplus-GT-Production").is_dir()
            and (parent / "ntruplus-ntt-Optimized").is_dir()
        ):
            return parent
    raise RuntimeError("could not locate repository root")


ROOT = repository_root()
ACTIVE_NTT = (
    ROOT
    / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768/asm/ntt.S"
)
MODULAR_NTT32 = (
    ROOT
    / "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/"
    "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S"
)
KEM_C = (
    ROOT
    / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768/kem.c"
)
CBD_S = (
    ROOT
    / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768/asm/cbd.S"
)
SUPPORT_S = (
    ROOT
    / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768/asm/support.S"
)
DEFAULT_JSON = Path(__file__).resolve().with_name("p1c_per_store_bounds.json")


CALLERS = (
    Caller(
        name="keygen_g",
        endpoint="gt_keygen_poly_ntt_to_cq",
        input_bound=Interval(-3, 3),
        input_evidence="poly_cbd1 gives {-1,0,1}; poly_triple multiplies by 3",
        machine_bound=Interval(-16383, 16383),
        machine_obligation=(
            "baseinv prepare uses signed-16 vneg followed by vshl #1"
        ),
        semantic_bound=Interval(-(Q // 2), Q // 2),
        semantic_obligation=(
            "baseinv reduce_mul2/reduce_mul3/fqmul proof covers production "
            "centered representatives only"
        ),
    ),
    Caller(
        name="encap_m",
        endpoint="poly_ntt",
        input_bound=Interval(-1, 1),
        input_evidence="poly_sotp_encode emits centered ternary coefficients",
        machine_bound=Interval(-32767, 32767),
        machine_obligation="Q31 addend is loaded as int16 and widened to int32",
        semantic_bound=Interval(-(Q // 2), Q // 2),
        semantic_obligation=(
            "the checked Q31 byte-contract proof covers the production "
            "centered NTT addend only"
        ),
    ),
    Caller(
        name="decap_m1",
        endpoint="poly_ntt",
        input_bound=Interval(-1, 1),
        input_evidence="poly_crepmod3 emits centered ternary coefficients",
        machine_bound=Interval(
            -(INT16_MAX - (Q // 2)), INT16_MAX - (Q // 2)
        ),
        machine_obligation=(
            "poly_sub computes centered ciphertext minus m2 in signed-16 lanes"
        ),
        semantic_bound=Interval(-(Q // 2), Q // 2),
        semantic_obligation=(
            "verify basemul equivalence after poly_sub is proven only from "
            "the production centered NTT representative contract"
        ),
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def s16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def sqrdmulh_s16(a: int, b: int) -> int:
    """Scalar semantics of AArch64 SQrdMulh for one signed 16-bit lane."""

    require(INT16_MIN <= a <= INT16_MAX, "sqrdmulh lhs outside int16")
    require(INT16_MIN <= b <= INT16_MAX, "sqrdmulh rhs outside int16")
    if a == INT16_MIN and b == INT16_MIN:
        return INT16_MAX
    return s16((a * b + (1 << 14)) >> 15)


def fqmul_lane(x: int, twiddle: int, reciprocal: int) -> int:
    """Exact signed-16 MUL/SQrdMulh/MLS sequence used by the NTT."""

    quotient = sqrdmulh_s16(x, reciprocal)
    product = s16(x * twiddle)
    return s16(product - quotient * Q)


def active_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if not line.lstrip().startswith("//")]


def suffix(text: str, start: str, end: str) -> tuple[int, list[str]]:
    lines = text.splitlines()
    start_index = next(i for i, line in enumerate(lines) if line.strip() == start)
    end_index = next(i for i, line in enumerate(lines) if line.strip() == end)
    require(start_index < end_index, f"bad source marker order: {start} .. {end}")
    return start_index + 1, lines[start_index:end_index]


def reduction_lines(lines: list[str], base_line: int) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    pattern = re.compile(r"^\s*sqdmulh\s+[^,]+,\s*[^,]+,\s*v0\.H\[1\]")
    for offset, line in enumerate(lines):
        if pattern.search(line) and not line.lstrip().startswith("//"):
            result.append(
                {
                    "line": base_line + offset,
                    "instruction": line.strip(),
                }
            )
    return result


def parse_twiddle_pairs(text: str) -> list[tuple[int, int]]:
    marker = "u01_block_first_gt_ntt32_batch8_twiddle_vecs:"
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == marker) + 1
    vectors: list[list[int]] = []
    hword = re.compile(r"^\s*\.hword\s+(.+)$")
    for line in lines[start:]:
        match = hword.match(line)
        if not match:
            break
        values = [int(value.strip()) for value in match.group(1).split(",")]
        require(len(values) == 8, "twiddle vector does not have eight lanes")
        vectors.append(values)
    require(len(vectors) == 10, f"expected 10 twiddle vectors, found {len(vectors)}")

    pairs: list[tuple[int, int]] = []
    for index in range(0, len(vectors), 2):
        pairs.extend(zip(vectors[index], vectors[index + 1]))
    return pairs


def prove_fqmul_bound(pairs: list[tuple[int, int]]) -> tuple[Interval, dict[str, int]]:
    minimum = INT16_MAX
    maximum = INT16_MIN
    min_x = min_twiddle = min_reciprocal = 0
    max_x = max_twiddle = max_reciprocal = 0
    for twiddle, reciprocal in pairs:
        for x in range(INT16_MIN, INT16_MAX + 1):
            value = fqmul_lane(x, twiddle, reciprocal)
            if value < minimum:
                minimum = value
                min_x, min_twiddle, min_reciprocal = x, twiddle, reciprocal
            if value > maximum:
                maximum = value
                max_x, max_twiddle, max_reciprocal = x, twiddle, reciprocal
    require(
        minimum >= -(Q - 1) and maximum <= Q - 1,
        f"fqmul exhaustive bound [{minimum}, {maximum}] exceeds q-1",
    )
    return (
        Interval(minimum, maximum),
        {
            "min_x": min_x,
            "min_twiddle": min_twiddle,
            "min_reciprocal": min_reciprocal,
            "max_x": max_x,
            "max_twiddle": max_twiddle,
            "max_reciprocal": max_reciprocal,
        },
    )


def stage_bounds(fqmul: Interval) -> list[dict[str, object]]:
    current = Interval(-RAW_GT_DFT_ABSMAX, RAW_GT_DFT_ABSMAX)
    rows: list[dict[str, object]] = [
        {
            "stage": 0,
            "name": "GT raw 3-point DFT input",
            "bound": asdict(current),
            "signed_int16_safe": current.lo >= INT16_MIN
            and current.hi <= INT16_MAX,
        }
    ]
    for stage in range(1, STAGE_COUNT + 1):
        current = Interval(current.lo + fqmul.lo, current.hi + fqmul.hi)
        safe = current.lo >= INT16_MIN and current.hi <= INT16_MAX
        require(safe, f"stage {stage} interval {current} can wrap signed int16")
        rows.append(
            {
                "stage": stage,
                "name": f"after lazy CT stage {stage}",
                "bound": asdict(current),
                "signed_int16_safe": safe,
            }
        )
    return rows


def source_checks() -> tuple[dict[str, object], dict[str, list[dict[str, object]]]]:
    active_text = ACTIVE_NTT.read_text()
    modular_text = MODULAR_NTT32.read_text()
    kem_text = KEM_C.read_text()
    cbd_text = CBD_S.read_text()
    support_text = SUPPORT_S.read_text()

    active_hash = sha256(ACTIVE_NTT)
    modular_hash = sha256(MODULAR_NTT32)
    require(active_hash == ACTIVE_NTT_SHA256, "active production ntt.S hash changed")
    require(
        modular_hash == MODULAR_NTT32_SHA256,
        "modular NTT32 source hash changed",
    )
    for needle in (
        "poly_ntt:",
        "gt_keygen_poly_ntt_to_cq:",
        ".Lgt_shared_core_generic_suffix:",
        ".Lgt_shared_core_cq_suffix:",
        ".Lgt_shared_core_epilogue:",
    ):
        require(needle in active_text, f"active NTT missing marker {needle}")
    for needle in (
        "GT frontend feeds raw 3-point DFT outputs bounded by 3*(q-1)",
        "The five lazy",
        "stage345_block0",
        "stage345_block1",
        "stage345_block2",
        "stage345_block3",
    ):
        require(needle in modular_text, f"modular source missing evidence {needle}")
    for needle in (
        "gt_keygen_poly_ntt_to_cq(out",
        "poly_sotp_encode(&m",
        "poly_ntt(&m, &m)",
        "poly_crepmod3(&m1",
        "poly_ntt(&m2, &m1)",
    ):
        require(needle in kem_text, f"kem.c caller evidence missing {needle}")
    require("poly_cbd1:" in cbd_text, "CBD source missing poly_cbd1")
    require("poly_sotp_encode:" in cbd_text, "CBD source missing SOTP encode")
    require("poly_triple:" in support_text, "support source missing poly_triple")
    require("poly_crepmod3:" in support_text, "support source missing crepmod3")

    generic_base, generic = suffix(
        active_text,
        ".Lgt_shared_core_generic_suffix:",
        ".Lgt_shared_core_cq_suffix:",
    )
    cq_base, cq = suffix(
        active_text,
        ".Lgt_shared_core_cq_suffix:",
        ".Lgt_shared_core_epilogue:",
    )
    endpoint_reductions = {
        "poly_ntt": reduction_lines(generic, generic_base),
        "gt_keygen_poly_ntt_to_cq": reduction_lines(cq, cq_base),
    }
    for endpoint, rows in endpoint_reductions.items():
        require(
            len(rows) == LOGICAL_STORES_PER_ENDPOINT,
            f"{endpoint}: expected 96 final reductions, found {len(rows)}",
        )
    require(
        sum(
            "srshr" in line and "#11" in line
            for line in active_lines("\n".join(generic))
        )
        == LOGICAL_STORES_PER_ENDPOINT,
        "generic suffix does not contain 96 SRSHR #11 operations",
    )
    require(
        sum(
            "srshr" in line and "#11" in line
            for line in active_lines("\n".join(cq))
        )
        == LOGICAL_STORES_PER_ENDPOINT,
        "CQ suffix does not contain 96 SRSHR #11 operations",
    )
    cq_store_comments = re.findall(r"direct CQ group(\d+) c([0-3])", "\n".join(cq))
    require(
        len(cq_store_comments) == LOGICAL_STORES_PER_ENDPOINT,
        f"CQ suffix has {len(cq_store_comments)} annotated stores, expected 96",
    )
    require(
        len(set(cq_store_comments)) == LOGICAL_STORES_PER_ENDPOINT,
        "CQ annotated store coordinates are not unique",
    )

    return (
        {
            "active_ntt": {
                "path": str(ACTIVE_NTT.relative_to(ROOT)),
                "sha256": active_hash,
                "generic_suffix_final_reduction_chains": len(
                    endpoint_reductions["poly_ntt"]
                ),
                "cq_suffix_final_reduction_chains": len(
                    endpoint_reductions["gt_keygen_poly_ntt_to_cq"]
                ),
                "important_count_note": (
                    "The file contains 192 chains total, but its two 96-chain "
                    "suffixes are mutually exclusive; one NTT call executes 96."
                ),
            },
            "modular_ntt32": {
                "path": str(MODULAR_NTT32.relative_to(ROOT)),
                "sha256": modular_hash,
                "active_final_reduction_chains_per_row": sum(
                    "sqdmulh" in line
                    and "v0.H[1]" in line
                    and not line.lstrip().startswith("//")
                    for line in modular_text.splitlines()
                ),
            },
        },
        endpoint_reductions,
    )


def store_rows(
    endpoint_reductions: dict[str, list[dict[str, object]]],
    final_bound: Interval,
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    rows: list[dict[str, object]] = []
    caller_summary: dict[str, dict[str, object]] = {}
    for caller in CALLERS:
        machine_safe = final_bound.within(caller.machine_bound)
        semantic_safe = final_bound.within(caller.semantic_bound)
        implementation_safe = machine_safe and semantic_safe
        reductions = endpoint_reductions[caller.endpoint]
        for index, reduction in enumerate(reductions):
            rows.append(
                {
                    "caller": caller.name,
                    "endpoint": caller.endpoint,
                    "logical_store": index,
                    "row": index // 32,
                    "block": (index % 32) // 8,
                    "vector_in_block": index % 8,
                    "lanes": VECTOR_LANES,
                    "pre_final_reduction_bound": asdict(final_bound),
                    "final_reduction_line": reduction["line"],
                    "final_reduction_instruction": reduction["instruction"],
                    "machine_safe_without_final_reduction": machine_safe,
                    "semantic_safe_without_final_reduction": semantic_safe,
                    "implementation_safe_without_final_reduction": implementation_safe,
                }
            )
        caller_summary[caller.name] = {
            "endpoint": caller.endpoint,
            "input_bound": asdict(caller.input_bound),
            "input_evidence": caller.input_evidence,
            "machine_bound": asdict(caller.machine_bound),
            "machine_obligation": caller.machine_obligation,
            "semantic_bound": asdict(caller.semantic_bound),
            "semantic_obligation": caller.semantic_obligation,
            "producer_bound": asdict(final_bound),
            "logical_stores_checked": len(reductions),
            "machine_safe_without_final_reduction": machine_safe,
            "semantic_safe_without_final_reduction": semantic_safe,
            "implementation_safe_without_final_reduction": implementation_safe,
        }
    return rows, caller_summary


def build_result() -> dict[str, object]:
    sources, endpoint_reductions = source_checks()
    pairs = parse_twiddle_pairs(ACTIVE_NTT.read_text())
    fqmul, fqmul_witnesses = prove_fqmul_bound(pairs)
    stages = stage_bounds(fqmul)
    final_bound = Interval(**stages[-1]["bound"])
    stores, callers = store_rows(endpoint_reductions, final_bound)

    expected_rows = len(CALLERS) * LOGICAL_STORES_PER_ENDPOINT
    require(len(stores) == expected_rows, "per-store result is incomplete")
    authorization = all(
        row["implementation_safe_without_final_reduction"] for row in stores
    )
    return {
        "schema": "ntruplus-p1c-per-store-proof-v1",
        "q": Q,
        "sources": sources,
        "arithmetic": {
            "sqrdmulh_model": (
                "signed saturating rounding doubling high multiply, 16-bit lanes"
            ),
            "fqmul_model": "s16(s16(x*twiddle) - sqrdmulh(x,reciprocal)*q)",
            "twiddle_pairs_checked": len(pairs),
            "fqmul_inputs_exhaustively_checked": (
                len(pairs) * (INT16_MAX - INT16_MIN + 1)
            ),
            "fqmul_output_bound": asdict(fqmul),
            "fqmul_extreme_witnesses": fqmul_witnesses,
            "stage_bounds": stages,
        },
        "callers": callers,
        "stores": stores,
        "summary": {
            "callers_checked": len(CALLERS),
            "logical_stores_per_caller": LOGICAL_STORES_PER_ENDPOINT,
            "logical_stores_checked": len(stores),
            "lanes_covered": len(stores) * VECTOR_LANES,
            "removed_instructions_if_one_endpoint_were_fully_safe": (
                LOGICAL_STORES_PER_ENDPOINT * 3
            ),
            "assembly_generation_allowed": authorization,
            "decision": (
                "proof_succeeded_generate_candidate"
                if authorization
                else "proof_failed_do_not_generate_assembly"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--emit",
        type=Path,
        nargs="?",
        const=DEFAULT_JSON,
        help="write the deterministic JSON proof artifact",
    )
    parser.add_argument(
        "--require-safe",
        action="store_true",
        help="return failure unless assembly generation is authorized",
    )
    args = parser.parse_args()

    try:
        result = build_result()
    except (AssertionError, RuntimeError, StopIteration) as error:
        print(f"P1-C proof infrastructure failure: {error}", file=sys.stderr)
        return 2

    if args.emit is not None:
        args.emit.parent.mkdir(parents=True, exist_ok=True)
        args.emit.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    summary = result["summary"]
    print(f"callers_checked={summary['callers_checked']}")
    print(f"logical_stores_checked={summary['logical_stores_checked']}")
    print(f"lanes_covered={summary['lanes_covered']}")
    print(
        "ASM_GENERATION_ALLOWED="
        + str(summary["assembly_generation_allowed"]).lower()
    )
    print(f"decision={summary['decision']}")

    if args.require_safe and not summary["assembly_generation_allowed"]:
        print(
            "P1-C hard gate rejected ASM generation: at least one downstream "
            "machine/semantic contract is unproven.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
