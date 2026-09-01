#!/usr/bin/env python3
"""Generate Algorithm-10 fixed-Barrett tables from the frozen M5D roots."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
RINV = pow(R, -1, Q)


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def reciprocal(value: int) -> int:
    """Nearest integer to value*2^15/Q; Q is odd, so there are no ties."""
    numerator = abs(value) * (1 << 15)
    rounded = (numerator + Q // 2) // Q
    return -rounded if value < 0 else rounded


def pair_from_mont(value: int) -> tuple[int, int]:
    normal = centered(value * RINV)
    return normal, reciprocal(normal)


def load_m5d() -> object:
    path = Path(__file__).resolve().parent.parent / "gt_fr0_inverse_consumer/generate_tables.py"
    spec = importlib.util.spec_from_file_location("gt864_m5d_tables", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def emit_vector_pair_table(lines: list[str], name: str,
                           values: list[list[int]]) -> None:
    lines.append(f"static const int16_t {name}[{len(values)}][2][8] = {{")
    for row in values:
        low = [pair_from_mont(value)[0] for value in row]
        high = [pair_from_mont(value)[1] for value in row]
        lines.append("    {{" + ",".join(map(str, low)) + "},")
        lines.append("     {" + ",".join(map(str, high)) + "}},")
    lines.extend(["};", ""])


def emit_header(path: Path, tables: dict[str, object]) -> None:
    lines = [
        "#ifndef GT864_FR0_INVERSE_BARRETT_TABLES_H",
        "#define GT864_FR0_INVERSE_BARRETT_TABLES_H",
        "",
        "#include <stdint.h>",
        "",
        "/* Each fixed constant is (b, round(b*2^15/3457)). */",
        "static const int16_t gt864_inverse9_twist_barrett[2][2][9][2][8] = {",
    ]
    for top in tables["inverse9"]:
        lines.append("  {")
        for block in top:
            lines.append("    {")
            for row in block:
                low = [pair_from_mont(value)[0] for value in row]
                high = [pair_from_mont(value)[1] for value in row]
                lines.append("      {{" + ",".join(map(str, low)) + "},")
                lines.append("       {" + ",".join(map(str, high)) + "}},")
            lines.append("    },")
        lines.append("  },")
    lines.extend(["};", ""])

    # Stage rows are stored as four-wide groups of adjacent (b,b') pairs.
    lines.append("static const int16_t gt864_inverse16_stage_barrett[4][16] = {")
    for stage, row in enumerate(tables["inverse16_stage"]):
        length = 1 << (stage + 1)
        sequence = [row[j % (length // 2)] for j in range(8)]
        flat = [item for value in sequence for item in pair_from_mont(value)]
        lines.append("    {" + ",".join(map(str, flat)) + "},")
    lines.extend(["};", ""])

    emit_vector_pair_table(lines, "gt864_inverse16_main_scale_barrett",
                           tables["inverse16_main_scale"])
    emit_vector_pair_table(lines, "gt864_inverse16_tail_scale_barrett",
                           tables["inverse16_tail_scale"])
    lines.extend(["#endif", ""])
    path.write_text("\n".join(lines))


def all_mont_constants(tables: dict[str, object]) -> set[int]:
    values = {
        -886, 1033, 1510, 708,
        int(tables["delta_inv_mont"]), int(tables["alpha_mont"]),
    }
    for top in tables["inverse9"]:
        for block in top:
            for row in block:
                values.update(row)
    for key in ("inverse16_stage", "inverse16_main_scale", "inverse16_tail_scale"):
        for row in tables[key]:
            values.update(row)
    return values


def prove(tables: dict[str, object]) -> dict[str, object]:
    max_abs = 0
    checked = 0
    constants = sorted(pair_from_mont(value) for value in all_mont_constants(tables))
    # Exhaust all signed halfwords for every distinct public constant.
    for value, high in constants:
        for source in range(-32768, 32768):
            quotient = (2 * source * high + (1 << 15)) >> 16
            result = ((source * value - quotient * Q + (1 << 15)) & 0xffff) - (1 << 15)
            assert (result - source * value) % Q == 0
            max_abs = max(max_abs, abs(result))
            checked += 1
    return {
        "gate": "gt864_fixed_barrett_algorithm10",
        "status": "pass",
        "distinct_constants": len(constants),
        "exhaustive_signed_halfword_products": checked,
        "maximum_output_abs": max_abs,
        "theorem_bound_strict": "3*q/2",
        "production_linked": False,
    }


def main() -> None:
    module = load_m5d()
    reference = Path(__file__).resolve().parents[8] / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c"
    tables = module.make_tables(reference)
    if len(sys.argv) == 3 and sys.argv[1] == "--header":
        emit_header(Path(sys.argv[2]), tables)
        return
    print(json.dumps(prove(tables), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
