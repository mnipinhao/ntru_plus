#!/usr/bin/env python3
"""Derive and self-check the d=4 branch-paired AoS algebra.

This tool intentionally derives tables from field identities.  It does not read
or transpose Official or GT assembly tables.  Its stdout is deterministic JSON
and is the reproducible Stage-2 metadata artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import tempfile
from pathlib import Path

Q = 3457
N = 768
QUARTIC = 4
ROWS = 96
BRANCHES = 2
R = pow(2, 16, Q)
RINV = pow(R, -1, Q)

# The first value is the field representative of Official's Montgomery-encoded
# -1033.  The other is its conjugate in Y^2 - Y + 1.
ALPHA = (-1033 * RINV) % Q
BRANCH_ROOTS = (ALPHA, (1 - ALPHA) % Q)
# beta_b^96 = BRANCH_ROOTS[b].  They are selected by algebraic identity, not
# by an existing SIMD table order.
BRANCH_SCALES = (22, 2)
OMEGA96 = 641


def gt_input_index(n3: int, n32: int) -> int:
    return (64 * n3 + 33 * n32) % ROWS


def gt_output_index(k3: int, k32: int) -> int:
    return (32 * k3 + 3 * k32) % ROWS


def physical_index(branch: int, k3: int, k32: int, coeff: int) -> int:
    """AoS lane(b,u,c)=8*b+4*u+c, grouped by (k3,floor(k32/2))."""
    assert 0 <= branch < BRANCHES
    assert 0 <= k3 < 3
    assert 0 <= k32 < 32
    assert 0 <= coeff < QUARTIC
    vector = 16 * k3 + k32 // 2
    lane = 8 * branch + 4 * (k32 & 1) + coeff
    return 16 * vector + lane


def logical_from_physical(index: int) -> tuple[int, int, int, int]:
    assert 0 <= index < N
    vector, lane = divmod(index, 16)
    k3, pair = divmod(vector, 16)
    branch, lane = divmod(lane, 8)
    u, coeff = divmod(lane, 4)
    return branch, k3, 2 * pair + u, coeff


def mod_poly_add(a: list[int], b: list[int]) -> list[int]:
    return [(x + y) % Q for x, y in zip(a, b)]


def d4_forward(coeffs: list[int]) -> list[int]:
    """COEFF -> d4AoS NTT, using Y=X^4 and CRT at Y^96 roots."""
    assert len(coeffs) == N
    out = [0] * N
    omega_powers = [pow(OMEGA96, k, Q) for k in range(ROWS)]
    for branch, beta in enumerate(BRANCH_SCALES):
        root = BRANCH_ROOTS[branch]
        for k3 in range(3):
            for k32 in range(32):
                k = gt_output_index(k3, k32)
                gamma = beta * omega_powers[k] % Q
                for c in range(QUARTIC):
                    value = 0
                    gamma_i = 1
                    for i in range(ROWS):
                        low = coeffs[4 * i + c] % Q
                        high = coeffs[384 + 4 * i + c] % Q
                        value = (value + (low + root * high) * gamma_i) % Q
                        gamma_i = gamma_i * gamma % Q
                    out[physical_index(branch, k3, k32, c)] = value
    return out


def d4_inverse(values: list[int]) -> list[int]:
    """d4AoS NTT -> canonical natural coefficients via inverse DFT and CRT."""
    assert len(values) == N
    branch_poly = [[[0] * ROWS for _ in range(QUARTIC)]
                   for _ in range(BRANCHES)]
    inv_rows = pow(ROWS, -1, Q)
    for branch, beta in enumerate(BRANCH_SCALES):
        for c in range(QUARTIC):
            for i in range(ROWS):
                total = 0
                for k3 in range(3):
                    for k32 in range(32):
                        k = gt_output_index(k3, k32)
                        gamma = beta * pow(OMEGA96, k, Q) % Q
                        total += values[physical_index(branch, k3, k32, c)] \
                            * pow(gamma, -i, Q)
                branch_poly[branch][c][i] = total * inv_rows % Q

    out = [0] * N
    alpha0, alpha1 = BRANCH_ROOTS
    inv_delta = pow((alpha0 - alpha1) % Q, -1, Q)
    for c in range(QUARTIC):
        for i in range(ROWS):
            u0 = branch_poly[0][c][i]
            u1 = branch_poly[1][c][i]
            high = (u0 - u1) * inv_delta % Q
            low = (u0 - alpha0 * high) % Q
            out[4 * i + c] = low
            out[384 + 4 * i + c] = high
    return out


def quartic_mul(a: list[int], b: list[int], zeta: int) -> list[int]:
    """Multiply in F_q[T]/(T^4-zeta)."""
    full = [0] * 7
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            full[i + j] = (full[i + j] + x * y) % Q
    return [(full[c] + zeta * full[c + 4]) % Q for c in range(3)] + [full[3]]


def d4_basemul(a: list[int], b: list[int]) -> list[int]:
    out = [0] * N
    for branch, beta in enumerate(BRANCH_SCALES):
        for k3 in range(3):
            for k32 in range(32):
                k = gt_output_index(k3, k32)
                zeta = beta * pow(OMEGA96, k, Q) % Q
                left = [a[physical_index(branch, k3, k32, c)]
                        for c in range(QUARTIC)]
                right = [b[physical_index(branch, k3, k32, c)]
                         for c in range(QUARTIC)]
                product = quartic_mul(left, right, zeta)
                for c, value in enumerate(product):
                    out[physical_index(branch, k3, k32, c)] = value
    return out


def schoolbook(a: list[int], b: list[int]) -> list[int]:
    wide = [0] * (2 * N - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            wide[i + j] = (wide[i + j] + x * y) % Q
    for degree in range(2 * N - 2, N - 1, -1):
        value = wide[degree]
        wide[degree - 384] = (wide[degree - 384] + value) % Q
        wide[degree - 768] = (wide[degree - 768] - value) % Q
    return wide[:N]


def check_algebra() -> dict[str, object]:
    assert all(Q % divisor for divisor in range(2, 59))
    assert (ALPHA * ALPHA - ALPHA + 1) % Q == 0
    assert BRANCH_ROOTS[0] * BRANCH_ROOTS[1] % Q == 1
    assert sum(BRANCH_ROOTS) % Q == 1
    assert tuple(pow(beta, ROWS, Q) for beta in BRANCH_SCALES) == BRANCH_ROOTS
    assert pow(OMEGA96, ROWS, Q) == 1
    assert pow(OMEGA96, ROWS // 2, Q) != 1
    assert pow(OMEGA96, ROWS // 3, Q) != 1

    assert sorted(gt_input_index(n3, n32) for n3 in range(3)
                  for n32 in range(32)) == list(range(ROWS))
    assert sorted(gt_output_index(k3, k32) for k3 in range(3)
                  for k32 in range(32)) == list(range(ROWS))
    assert all(logical_from_physical(physical_index(b, k3, k32, c))
               == (b, k3, k32, c)
               for b in range(BRANCHES) for k3 in range(3)
               for k32 in range(32) for c in range(QUARTIC))

    rng = random.Random(0xD4A05)
    vectors = [[0] * N]
    for index in (0, 1, 383, 384, 767):
        vector = [0] * N
        vector[index] = 1
        vectors.append(vector)
    vectors.extend([[rng.randrange(-3, 5) % Q for _ in range(N)]
                    for _ in range(12)])
    for vector in vectors:
        assert d4_inverse(d4_forward(vector)) == vector

    for _ in range(8):
        left = [rng.randrange(-3, 5) % Q for _ in range(N)]
        right = [rng.randrange(-3, 5) % Q for _ in range(N)]
        assert d4_inverse(d4_basemul(d4_forward(left), d4_forward(right))) \
            == schoolbook(left, right)

    mapping = [physical_index(b, k3, k32, c)
               for b in range(BRANCHES) for k3 in range(3)
               for k32 in range(32) for c in range(QUARTIC)]
    return {
        "q": Q,
        "ring": "Z_3457[X]/(X^768-X^384+1)",
        "alpha": ALPHA,
        "branch_roots": BRANCH_ROOTS,
        "branch_scales": BRANCH_SCALES,
        "omega96": OMEGA96,
        "normalization": pow(ROWS, -1, Q),
        "aos_lane_formula": "8*b + 4*u + c",
        "vectors": 48,
        "mapping_sha256": hashlib.sha256(
            ",".join(map(str, mapping)).encode()).hexdigest(),
        "self_check": "passed",
    }


def artifact_map() -> dict[str, bytes]:
    """Return every checked-in artifact as stable UTF-8 bytes."""
    logical_to_physical = {
        "logical_order": ["branch", "k3", "k32", "coefficient"],
        "physical_words": [
            physical_index(b, k3, k32, c)
            for b in range(BRANCHES) for k3 in range(3)
            for k32 in range(32) for c in range(QUARTIC)
        ],
    }
    physical_to_logical = {
        "logical_order": ["branch", "k3", "k32", "coefficient"],
        "physical_words_in_order": [
            list(logical_from_physical(word)) for word in range(N)
        ],
    }
    roots = [
        [b, k3, k32, gt_output_index(k3, k32),
         BRANCH_SCALES[b] * pow(OMEGA96, gt_output_index(k3, k32), Q) % Q]
        for b in range(BRANCHES) for k3 in range(3) for k32 in range(32)
    ]
    inverse_roots = [item + [pow(item[4], -1, Q)] for item in roots]
    dft3_root = pow(OMEGA96, 32, Q)
    artifacts = {
        "logical_to_physical.json": logical_to_physical,
        "physical_to_logical.json": physical_to_logical,
        "forward_roots.json": roots,
        "inverse_roots.json": inverse_roots,
        "dft3_constants.json": {
            "omega3": dft3_root,
            "omega3_squared": dft3_root * dft3_root % Q,
            "omega3_cubed": pow(dft3_root, 3, Q),
        },
        "basemul_zetas.json": roots,
        "normalization.json": {
            "forward_scale": 1,
            "inverse_dft96": pow(ROWS, -1, Q),
            "crt_delta_inverse": pow((BRANCH_ROOTS[0] - BRANCH_ROOTS[1]) % Q,
                                     -1, Q),
            "montgomery_R": R,
            "montgomery_R_inverse": RINV,
        },
        "natural_output_map.json": {
            "entry_order": ["branch_polynomial_index", "coefficient",
                            "natural_low_word", "natural_high_word"],
            "entries": [
                [i, c, 4 * i + c, 384 + 4 * i + c]
                for i in range(ROWS) for c in range(QUARTIC)
            ],
        },
        "metadata.json": check_algebra(),
    }
    return {
        name: (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
        for name, value in artifacts.items()
    }


def manifest_bytes(artifacts: dict[str, bytes]) -> bytes:
    lines = [f"{hashlib.sha256(artifacts[name]).hexdigest()}  {name}"
             for name in sorted(artifacts)]
    return ("\n".join(lines) + "\n").encode()


def check_directory(directory: Path) -> None:
    artifacts = artifact_map()
    expected = dict(artifacts)
    expected["MANIFEST.sha256"] = manifest_bytes(artifacts)
    actual_names = {path.name for path in directory.iterdir() if path.is_file()}
    if actual_names != set(expected):
        raise SystemExit(
            f"generated artifact names differ: actual={sorted(actual_names)} "
            f"expected={sorted(expected)}")
    for name, content in expected.items():
        if (directory / name).read_bytes() != content:
            raise SystemExit(f"stale generated artifact: {name}")
    with tempfile.TemporaryDirectory(prefix="d4aos-generated-") as temp:
        temp_dir = Path(temp)
        for name, content in expected.items():
            (temp_dir / name).write_bytes(content)
        for name, content in expected.items():
            if (temp_dir / name).read_bytes() != content:
                raise SystemExit(f"temporary regeneration mismatch: {name}")
    expected_digest = check_algebra()["mapping_sha256"]
    if expected_digest != "8c1aecfa7391fe8b75c9c4dac4ee6538ea95787d0291ab1a5a89d5697587f8b3":
        raise SystemExit("unexpected logical-to-physical mapping digest")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", choices=sorted(artifact_map()),
                        help="print one generated artifact to stdout")
    parser.add_argument("--manifest", action="store_true",
                        help="print MANIFEST.sha256 to stdout")
    parser.add_argument("--check-dir", type=Path,
                        help="regenerate in a temporary directory and byte-check DIR")
    args = parser.parse_args()
    artifacts = artifact_map()
    if args.check_dir:
        check_directory(args.check_dir)
        print("d4aos-generated-check=passed")
    elif args.artifact:
        print(artifacts[args.artifact].decode(), end="")
    elif args.manifest:
        print(manifest_bytes(artifacts).decode(), end="")
    else:
        print(json.dumps(check_algebra(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
