#!/usr/bin/env python3
"""Structural model shared by NTRU+864 and NTRU+1152 GT9x16 experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass


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
