#!/usr/bin/env python3
"""Machine-check the exact M4/M5A FR-0 int16 and Montgomery range contract."""

from __future__ import annotations

import json
from dataclasses import dataclass

Q = 3457
QINV = 12929
THETA = 9
R = (1 << 16) % Q
RHO_MONT = -886
RHO2_MONT = 1033
ETA_MONT = 708
ETA_INV_MONT = 1510
INT16_MIN = -(1 << 15)
INT16_MAX = (1 << 15) - 1
INT32_MAX = (1 << 31) - 1

Interval = tuple[int, int]


def wrap16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def montgomery(value: int, constant_mont: int) -> tuple[int, int, int, int]:
    product = value * constant_mont
    quotient = wrap16(wrap16(product) * QINV)
    numerator = product - quotient * Q
    assert numerator % (1 << 16) == 0
    output = numerator // (1 << 16)
    assert output * R % Q == value * constant_mont % Q
    return output, product, quotient, numerator


def centered_mont(value: int) -> int:
    value = value * R % Q
    return value - Q if value > Q // 2 else value


def twist_sets() -> tuple[tuple[int, ...], ...]:
    result = []
    for power in range(1, 9):
        constants = set()
        for residue in (1, 5):
            for column in range(16):
                lam = pow(THETA, residue + 6 * column, Q)
                constants.add(centered_mont(pow(lam, power, Q)))
        result.append(tuple(sorted(constants)))
    return tuple(result)


TWISTS = twist_sets()
RHO = (RHO_MONT,)
RHO2 = (RHO2_MONT,)
ETA = (ETA_MONT,)
ETA_INV = (ETA_INV_MONT,)


@dataclass
class Step:
    name: str
    operation: str
    inputs: list[Interval]
    output: Interval


class Analyzer:
    def __init__(self) -> None:
        self.steps: list[Step] = []
        self._mul_cache: dict[tuple[Interval, tuple[int, ...]], Interval] = {}

    def note(self, name: str, operation: str, inputs: list[Interval],
             output: Interval) -> Interval:
        self.steps.append(Step(name, operation, inputs, output))
        return output

    def add(self, name: str, left: Interval, right: Interval) -> Interval:
        output = (left[0] + right[0], left[1] + right[1])
        return self.note(name, "int16_vector_add", [left, right], output)

    def mul(self, name: str, value: Interval,
            constants: tuple[int, ...]) -> Interval:
        key = (value, constants)
        if key not in self._mul_cache:
            minimum = None
            maximum = None
            for constant in constants:
                for operand in range(value[0], value[1] + 1):
                    output = montgomery(operand, constant)[0]
                    minimum = output if minimum is None else min(minimum, output)
                    maximum = output if maximum is None else max(maximum, output)
            assert minimum is not None and maximum is not None
            self._mul_cache[key] = (minimum, maximum)
        return self.note(name, "R0_times_public_cR_to_R0", [value],
                         self._mul_cache[key])

    def b3(self, name: str, x0: Interval, x1: Interval,
           x2: Interval) -> tuple[Interval, Interval, Interval]:
        sum01 = self.add(f"{name}.sum01", x0, x1)
        out0 = self.add(f"{name}.out0", sum01, x2)
        mix1 = self.add(
            f"{name}.mix1",
            self.mul(f"{name}.rho_x1", x1, RHO),
            self.mul(f"{name}.rho2_x2", x2, RHO2),
        )
        out1 = self.add(f"{name}.out1", x0, mix1)
        mix2 = self.add(
            f"{name}.mix2",
            self.mul(f"{name}.rho2_x1", x1, RHO2),
            self.mul(f"{name}.rho_x2", x2, RHO),
        )
        out2 = self.add(f"{name}.out2", x0, mix2)
        return out0, out1, out2


def analyze(input_interval: Interval) -> tuple[Analyzer, list[Interval]]:
    analyzer = Analyzer()
    f = [input_interval]
    for power, constants in enumerate(TWISTS, 1):
        f.append(analyzer.mul(f"twist.f{power}", input_interval, constants))

    a = analyzer.b3("level1.a", f[0], f[3], f[6])
    b = analyzer.b3("level1.b", f[1], f[4], f[7])
    c = analyzer.b3("level1.c", f[8], f[2], f[5])

    group0 = analyzer.b3("level2.group0", a[0], b[0], c[0])
    group1 = analyzer.b3(
        "level2.group1",
        a[1],
        analyzer.mul("inter.eta_b1", b[1], ETA),
        analyzer.mul("inter.eta_inv_c1", c[1], ETA_INV),
    )
    group2 = analyzer.b3(
        "level2.group2",
        a[2],
        analyzer.mul("inter.eta_inv_b2", b[2], ETA_INV),
        analyzer.mul("inter.eta_c2", c[2], ETA),
    )
    outputs = [group0[0], group1[0], group2[1], group0[1], group1[1],
               group2[2], group0[2], group1[2], group2[0]]
    return analyzer, outputs


def maximum_abs(analyzer: Analyzer) -> int:
    return max(abs(endpoint)
               for step in analyzer.steps
               for endpoint in step.output)


def summarize_stages(analyzer: Analyzer) -> dict[str, Interval]:
    groups: dict[str, list[Interval]] = {}
    for step in analyzer.steps:
        prefix = step.name.split(".", 1)[0]
        groups.setdefault(prefix, []).append(step.output)
    return {
        prefix: (
            min(interval[0] for interval in intervals),
            max(interval[1] for interval in intervals),
        )
        for prefix, intervals in groups.items()
    }


def main() -> None:
    constants = set(value for group in TWISTS for value in group)
    constants.update((RHO_MONT, RHO2_MONT, ETA_MONT, ETA_INV_MONT))
    congruence_checks = 0
    largest_product = 0
    largest_numerator = 0
    for constant in constants:
        for value in range(INT16_MIN, INT16_MAX + 1):
            _, product, _, numerator = montgomery(value, constant)
            largest_product = max(largest_product, abs(product))
            largest_numerator = max(largest_numerator, abs(numerator))
            congruence_checks += 1
    assert largest_product <= INT32_MAX
    assert largest_numerator <= INT32_MAX

    contracts = {
        "centered": (-1728, 1728),
        "mixed_current_test": (-1728, 3456),
        "symmetric_q": (-3456, 3456),
        "maximum_proved_symmetric": (-15752, 15752),
        "first_failing_symmetric": (-15753, 15753),
    }
    reports = {}
    for name, input_interval in contracts.items():
        analyzer, outputs = analyze(input_interval)
        reports[name] = {
            "input": input_interval,
            "maximum_abs_any_int16_step": maximum_abs(analyzer),
            "all_int16_steps_safe": maximum_abs(analyzer) <= INT16_MAX,
            "output_union": (
                min(interval[0] for interval in outputs),
                max(interval[1] for interval in outputs),
            ),
            "stage_unions": summarize_stages(analyzer),
            "critical_steps": [
                {"name": step.name, "output": step.output}
                for step in sorted(
                    analyzer.steps,
                    key=lambda item: max(abs(item.output[0]), abs(item.output[1])),
                    reverse=True,
                )[:8]
            ],
        }
    assert reports["maximum_proved_symmetric"]["all_int16_steps_safe"]
    assert not reports["first_failing_symmetric"]["all_int16_steps_safe"]
    assert reports["maximum_proved_symmetric"]["maximum_abs_any_int16_step"] == 32767
    assert reports["first_failing_symmetric"]["maximum_abs_any_int16_step"] == 32768

    payload = {
        "gate": "gt864_fr0_formal_range_proof",
        "status": "pass",
        "arithmetic": "exact_integer_interval_overapproximation_of_vector_schedule",
        "int16_add_semantics": "proof_requires_no_wrap",
        "montgomery": {
            "q": Q,
            "qinv": QINV,
            "unique_public_constants": len(constants),
            "exhaustive_congruence_checks": congruence_checks,
            "largest_abs_32bit_product": largest_product,
            "largest_abs_32bit_reduction_numerator": largest_numerator,
            "all_widened_intermediates_fit_int32": True,
        },
        "producer_requirement": {
            "symmetric_input_bound_max": 15752,
            "meaning": "NTT16 must prove every P8+tail logical value lies in [-15752,15752]",
        },
        "contracts": reports,
        "production_linked": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
