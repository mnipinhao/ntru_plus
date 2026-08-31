#!/usr/bin/env python3
"""Machine-check the stock Neon forward/BaseMul physical leaf ABI."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


Q = 3457
N = 864
POINTS = N // 3
R = (1 << 16) % Q
ALPHA = (-722) % Q
BETA = (1 - (-722)) % Q


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1
    if value > 1:
        factors.append(value)
    return factors


def alpha_oriented_primitive_864_root() -> int:
    for candidate in range(2, Q):
        if (pow(candidate, N, Q) == 1
                and all(pow(candidate, N // factor, Q) != 1
                        for factor in prime_factors(N))
                and pow(candidate, 144, Q) == ALPHA):
            return candidate
    raise AssertionError("alpha-oriented primitive-864 root not found")


def parse_reference_zetas(source: Path) -> list[int]:
    text = source.read_text(encoding="utf-8")
    match = re.search(
        r"const\s+int16_t\s+zetas\s*\[\s*288\s*\]\s*=\s*\{(.*?)\};",
        text,
        re.DOTALL,
    )
    assert match is not None, "reference zetas[288] not found"
    values = [int(token) for token in re.findall(r"-?\d+", match.group(1))]
    assert len(values) == POINTS
    return values


def parse_basemul_table(source: Path) -> list[int]:
    text = source.read_text(encoding="utf-8")
    table = text.split("zetas_mul:", 1)
    assert len(table) == 2, "zetas_mul label not found"
    tokens = re.findall(r"0x[0-9a-fA-F]+|-?\d+", "\n".join(
        line for line in table[1].splitlines() if ".hword" in line
    ))
    return [signed16(int(token, 0)) for token in tokens]


def require_source_contract(ntt_source: Path, base_source: Path) -> None:
    ntt = ntt_source.read_text(encoding="utf-8")
    base = base_source.read_text(encoding="utf-8")

    for pattern in (
        r"st1\s+\{v4\.8h\s*-\s*v6\.8h\},\s*\[dst\],\s*#48",
        r"st1\s+\{v7\.8h\s*-\s*v9\.8h\},\s*\[dst\],\s*#48",
    ):
        assert re.search(pattern, ntt), f"missing forward store pattern: {pattern}"

    for pattern in (
        r"ld1\s+\{v4\.8h\s*-\s*v6\.8h\},\s*\[src1\],\s*#48",
        r"ld1\s+\{v7\.8h\s*-\s*v9\.8h\},\s*\[src2\],\s*#48",
        r"st1\s+\{v7\.8h\s*-\s*v9\.8h\},\s*\[dst\],\s*#48",
    ):
        assert re.search(pattern, base), f"missing basemul ABI pattern: {pattern}"

    add_body = base.split("_looptop_add:", 1)[1].split(".unreq", 1)[0]
    assert re.search(
        r"ld1\s+\{v10\.8h\s*-\s*v12\.8h\},\s*\[src3\],\s*#48",
        add_body,
    ), "BaseMulAdd addend does not use the same three-vector tile"


def build_grid_lookup() -> dict[int, tuple[str, int, int, int]]:
    theta = alpha_oriented_primitive_864_root()
    assert pow(theta, 144, Q) == ALPHA
    eta = pow(theta, 96, Q)

    lookup: dict[int, tuple[str, int, int, int]] = {}
    for top, residue in (("alpha", 1), ("beta", 5)):
        exponents = [exponent for exponent in range(96)
                     if exponent % 6 == residue]
        assert len(exponents) == 16
        for column, exponent in enumerate(exponents):
            lam = pow(theta, exponent, Q)
            for row in range(9):
                root = lam * pow(eta, row, Q) % Q
                assert root not in lookup
                assert pow(root, 144, Q) == (ALPHA if top == "alpha" else BETA)
                lookup[root] = (top, row, column, exponent)
    assert len(lookup) == POINTS
    return lookup


def main() -> None:
    repo = Path(__file__).resolve().parents[8]
    reference = repo / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c"
    neon = repo / "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864"
    ntt_source = neon / "asm/ntt.s"
    base_source = neon / "asm/base.s"

    require_source_contract(ntt_source, base_source)
    zetas = parse_reference_zetas(reference)
    table = parse_basemul_table(base_source)
    assert len(table) == 8 + POINTS
    leaf_table = table[8:]

    expected: list[int] = []
    for pair in range(18):
        roots = zetas[144 + 8 * pair:152 + 8 * pair]
        expected.extend(roots)
        expected.extend(signed16(-root) for root in roots)
    assert leaf_table == expected, "BaseMul zeta lanes differ from stock leaf order"

    r_inverse = pow(R, -1, Q)
    lookup = build_grid_lookup()
    rows: list[str] = []
    top_counts = {"alpha": 0, "beta": 0}
    for leaf, root_mont in enumerate(leaf_table):
        root = root_mont * r_inverse % Q
        top, row, column, exponent = lookup[root]
        top_counts[top] += 1
        group, lane = divmod(leaf, 8)
        offsets = tuple(24 * group + component * 8 + lane
                        for component in range(3))
        rows.append(
            f"{leaf},{group},{lane},{top},{row},{column},{exponent},"
            f"{offsets[0]},{offsets[1]},{offsets[2]},{root_mont},{root}"
        )

    assert top_counts == {"alpha": 144, "beta": 144}
    assert len(set(rows)) == POINTS
    mapping_hash = hashlib.sha256("\n".join(rows).encode("ascii")).hexdigest()

    print("gt864_layout_consumer_abi_gate=pass")
    print("forward_final_store=two_soa_tiles_of_8_leaves_per_96_bytes")
    print("basemul_input=soa_tile8,j0_then_j1_then_j2")
    print("basemuladd_addend=same_soa_tile8")
    print("physical_leaf_count=288")
    print("top_alpha_leaves=144")
    print("top_beta_leaves=144")
    print(f"mapping_sha256={mapping_hash}")
    print("columns=leaf,group,lane,top,row,column,lambda_exponent,"
          "j0_offset,j1_offset,j2_offset,zeta_mont,zeta_normal")
    for row in rows[:16]:
        print("map," + row)
    print("scope=stock_abi_reconstruction,no_gt_ntt16_ntt9_implementation")


if __name__ == "__main__":
    main()
