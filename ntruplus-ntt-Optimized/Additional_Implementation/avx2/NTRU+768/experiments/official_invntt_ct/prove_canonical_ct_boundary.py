#!/usr/bin/env python3
"""Prove whether a pure five-layer CT network can hit the Official boundary."""

import argparse
from pathlib import Path

from derive_lane_native_ct import (
    Q, derive, effective_twiddle, inv, parse_array, roots_vector, shuffle_level,
)


def symbolic_input() -> list[list[dict[int, tuple[int, tuple[str, ...]]]]]:
    return [
        [{16 * register + lane: (1, ())} for lane in range(16)]
        for register in range(8)
    ]


def multiply_symbolic(value, variable: str):
    return {
        source: (sign, factors + (variable,))
        for source, (sign, factors) in value.items()
    }


def combine_symbolic(left, right, subtract: bool):
    result = dict(left)
    for source, (sign, factors) in right.items():
        if source in result:
            raise AssertionError("radix-2 paths unexpectedly recombined")
        result[source] = (-sign if subtract else sign, factors)
    return result


def ct_symbolic_level(regs, level: int):
    outputs = []
    for register in range(4):
        top, bottom = regs[register], regs[register + 4]
        multiplied = [
            multiply_symbolic(bottom[lane], f"L{level}R{register}I{lane}")
            for lane in range(16)
        ]
        outputs.append([
            combine_symbolic(top[lane], multiplied[lane], False)
            for lane in range(16)
        ])
        outputs.append([
            combine_symbolic(top[lane], multiplied[lane], True)
            for lane in range(16)
        ])
    return outputs[0::2] + outputs[1::2]


def symbolic_network():
    regs = symbolic_input()
    for level in (6, 5, 4, 3):
        regs = shuffle_level(ct_symbolic_level(regs, level), level)
    return ct_symbolic_level(regs, 2)


def numeric_input(source: int) -> list[list[int]]:
    return [
        [1 if 16 * register + lane == source else 0 for lane in range(16)]
        for register in range(8)
    ]


def gs_level(regs: list[list[int]], roots: list[list[int]]) -> list[list[int]]:
    tops = []
    bottoms = []
    for top, bottom, twiddles in zip(regs[:4], regs[4:], roots):
        tops.append([(top[lane] + bottom[lane]) % Q for lane in range(16)])
        bottoms.append([
            (top[lane] - bottom[lane]) * twiddles[lane] % Q
            for lane in range(16)
        ])
    return tops + bottoms


def official_column(table: list[int], block: int, source: int) -> list[int]:
    regs = numeric_input(source)
    base = 32 * block
    for level in (6, 5, 4, 3):
        regs = shuffle_level(gs_level(regs, roots_vector(table, base, level)), level)
    root = effective_twiddle(table[192 + 4 * block + 578])
    return sum(gs_level(regs, [[root] * 16 for _ in range(4)]), [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consts", type=Path, required=True)
    args = parser.parse_args()
    table = parse_array(args.consts, "zetas_inv")
    _, boundary_scales = derive(table)
    symbolic = symbolic_network()
    flat = sum(symbolic, [])
    anchors = []
    for source in range(128):
        terms = [cell[source] for cell in flat if source in cell]
        if terms and all(not factors for _, factors in terms):
            anchors.append(source)
    print(f"fixed-ct-topology anchor-columns={anchors}")
    for block in range(6):
        flattened = sum(boundary_scales[8 * block:8 * block + 8], [])
        ratios = set()
        for strand in range(4):
            values = flattened[strand::4]
            ratios.update(
                values[index + 1] * inv(values[index]) % Q
                for index in range(31)
            )
        if len(ratios) != 1:
            raise AssertionError(f"block {block} is not one geometric untwist")
        ratio = ratios.pop()
        print(
            f"block={block} boundary-scale=rho^-i ratio={ratio} "
            f"ratio^32={pow(ratio, 32, Q)}"
        )
    impossible = False
    for block in range(6):
        for source in anchors:
            column = official_column(table, block, source)
            nonzero = [value for value in column if value != 0]
            target_unique = sorted(set(nonzero))
            ct_terms = [cell[source][0] for cell in flat if source in cell]
            ct_unique = sorted(set(value % Q for value in ct_terms))
            compatible = column == [
                cell.get(source, (0, ()))[0] % Q for cell in flat
            ]
            print(
                f"block={block} anchor={source} outputs={len(nonzero)} "
                f"ct-values={ct_unique} official-unique={len(target_unique)} "
                f"official-first={target_unique[:8]} compatible={compatible}"
            )
            impossible |= not compatible
    if impossible:
        print("result=no-pure-five-layer-ct-solution")
        print("required=boundary-diagonal-or-parent-fusion")
        return 0
    print("result=pure-five-layer-ct-not-disproved")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
