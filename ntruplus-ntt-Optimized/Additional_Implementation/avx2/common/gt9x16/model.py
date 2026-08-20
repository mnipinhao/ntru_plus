#!/usr/bin/env python3
"""Structural model shared by NTRU+864 and NTRU+1152 GT9x16 experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass

GT_SIZE = 144
GT_ROWS = 9
GT_LANES = 16
SHEAR_STAGES = (
    (1, 0xAA, (0, 1, 2, 3, 4, 5, 6, 7, 8)),
    (2, 0xCC, (0, 2, 4, 6, 8, 1, 3, 5, 7)),
    (4, 0xF0, (0, 4, 8, 3, 7, 2, 6, 1, 5)),
)


def gt_input_index(u: int, v: int) -> int:
    """AVX2-oriented CRT input map n = 16u + 81v (mod 144)."""
    return (16 * u + 81 * v) % GT_SIZE


def gt_output_index(p: int, q: int) -> int:
    """CRT output map k = 64p + 9q (mod 144)."""
    return (64 * p + 9 * q) % GT_SIZE


def relabel_h_to_r(h_rows: list[list[int]]) -> list[list[int]]:
    """Free logical relabel R[a] = H[5a mod 9]."""
    _validate_rows(h_rows)
    return [h_rows[(5 * a) % GT_ROWS][:] for a in range(GT_ROWS)]


def scalar_y(r_rows: list[list[int]]) -> list[list[int]]:
    """Materialized logical rows Y[a][v] = R[a+v mod 9][v]."""
    _validate_rows(r_rows)
    return [[r_rows[(a + v) % GT_ROWS][v] for v in range(GT_LANES)]
            for a in range(GT_ROWS)]


def scalar_shear_z(r_rows: list[list[int]]) -> list[list[int]]:
    """Three blend stages expressed as scalar lane selections."""
    _validate_rows(r_rows)
    rows = [row[:] for row in r_rows]
    for shift, mask, cycle in SHEAR_STAGES:
        before = [row[:] for row in rows]
        for row in range(GT_ROWS):
            for lane in range(GT_LANES):
                if mask & (1 << (lane % 8)):
                    rows[row][lane] = before[(row + shift) % GT_ROWS][lane]
        if {(cycle[i] + shift) % GT_ROWS for i in range(GT_ROWS)} != set(cycle):
            raise AssertionError("invalid in-place shear cycle")
    return rows


def materialize_y_from_z(z_rows: list[list[int]]) -> list[list[int]]:
    _validate_rows(z_rows)
    return [z_rows[a][:8] + z_rows[(a - 1) % GT_ROWS][8:]
            for a in range(GT_ROWS)]


def _validate_rows(rows: list[list[int]]) -> None:
    if len(rows) != GT_ROWS or any(len(row) != GT_LANES for row in rows):
        raise ValueError("expected a 9x16 row matrix")


@dataclass(frozen=True)
class GT9x16Model:
    parameter: int
    components: int
    component_degree: int
    radix_9: int = 9
    lanes: int = 16

    def validate(self) -> None:
        if self.parameter != self.components * self.component_degree:
            raise ValueError("parameter is not components * component_degree")
        if self.components % self.radix_9:
            raise ValueError("component count is not divisible by radix 9")
        if (self.components // self.radix_9) % self.lanes:
            raise ValueError("radix-9 groups do not fill AVX2 lane blocks")
        coordinates = {self.coordinates(index) for index in range(self.parameter)}
        if len(coordinates) != self.parameter:
            raise ValueError("index mapping is not bijective")
        input_indices = {gt_input_index(u, v) for u in range(GT_ROWS) for v in range(GT_LANES)}
        output_indices = {gt_output_index(p, q) for p in range(GT_ROWS) for q in range(GT_LANES)}
        if len(input_indices) != GT_SIZE or len(output_indices) != GT_SIZE:
            raise ValueError("Good-Thomas CRT mapping is not bijective")
        for u in range(GT_ROWS):
            for v in range(GT_LANES):
                for p in range(GT_ROWS):
                    for q in range(GT_LANES):
                        left = gt_input_index(u, v) * gt_output_index(p, q)
                        right = 16 * u * p + 9 * v * q
                        if (left - right) % GT_SIZE:
                            raise ValueError("Good-Thomas mixed-term identity failed")
        sample = [[row * GT_LANES + lane for lane in range(GT_LANES)]
                  for row in range(GT_ROWS)]
        y_rows = scalar_y(sample)
        z_rows = scalar_shear_z(sample)
        if materialize_y_from_z(z_rows) != y_rows:
            raise ValueError("three-stage shear invariant failed")

    def coordinates(self, index: int) -> tuple[int, int, int, int]:
        if not 0 <= index < self.parameter:
            raise IndexError(index)
        component, coefficient = divmod(index, self.component_degree)
        radix9_digit, block_offset = divmod(component, self.components // self.radix_9)
        lane_block, lane = divmod(block_offset, self.lanes)
        return coefficient, radix9_digit, lane_block, lane

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


MODELS = {
    864: GT9x16Model(parameter=864, components=288, component_degree=3),
    1152: GT9x16Model(parameter=1152, components=288, component_degree=4),
}
