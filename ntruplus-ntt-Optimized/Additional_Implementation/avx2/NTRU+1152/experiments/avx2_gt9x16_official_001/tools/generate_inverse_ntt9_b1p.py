#!/usr/bin/env python3
"""Exhaust the ITAIL-B1P two-radix3 phase/orientation search."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

Q = 3457
PAPER_P = [0, 3, 6, 1, 4, 7, 8, 2, 5]
BASELINE_TWIST_EXPONENTS = [0, 0, 0, 0, -1, 1, 0, 1, -1]
DESTINATIONS = ((0, 3, 6), (1, 4, 7), (8, 2, 5))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scaled_radix3_matrix(omega: int) -> list[list[int]]:
    kappa = (omega - pow(omega, 2, Q)) % Q
    columns = []
    for active in range(3):
        a, b, c = [int(index == active) for index in range(3)]
        total = (b + c) % Q
        difference = (b - c) % Q
        product = kappa * difference % Q
        base = (2 * a - total) % Q
        columns.append([
            2 * (a + total) % Q,
            (base + product) % Q,
            (base - product) % Q,
        ])
    return [list(row) for row in zip(*columns)]


def dft_matrix(root: int) -> list[list[int]]:
    return [[pow(root, source * frequency, Q) for source in range(9)]
            for frequency in range(9)]


def r2_matrix(core: list[list[int]], rho: int) -> list[list[int]]:
    """Matrix of the already-proved Forward R2 implementation."""
    output = []
    first_groups = ((0, 3, 6), (1, 4, 7), (8, 2, 5))
    twist_exponents = ((0, 0, 0), (0, 1, -1), (0, -1, 1))
    for source in range(9):
        vector = [int(index == source) for index in range(9)]
        first = []
        for group in first_groups:
            first.append([
                sum(core[row][column] * vector[group[column]]
                    for column in range(3)) % Q
                for row in range(3)
            ])
        transformed = []
        for component, exponents in enumerate(twist_exponents):
            operands = [first[group][component] *
                        pow(rho, exponents[group], Q) % Q
                        for group in range(3)]
            transformed.extend([
                sum(core[row][column] * operands[column]
                    for column in range(3)) % Q
                for row in range(3)
            ])
        output.append(transformed)
    return [list(row) for row in zip(*output)]


def path_coefficient(core: list[list[int]], rho: int,
                     orientation: tuple[int, ...], output: int, source: int,
                     twists: list[int]) -> tuple[int, int]:
    """Return the unique two-R3 path coefficient and middle-wire index."""
    source_group = source // 3
    for second_group, destinations in enumerate(DESTINATIONS):
        if output in destinations:
            second_output = destinations.index(output)
            break
    else:  # pragma: no cover - DESTINATIONS is a partition
        raise AssertionError(output)
    middle = second_group + 3 * source_group
    first_input = (source % 3 - orientation[source_group]) % 3
    second_input = (source_group - orientation[3 + second_group]) % 3
    coefficient = (core[second_output][second_input] *
                   core[second_group][first_input] *
                   pow(rho, twists[middle], Q)) % Q
    return coefficient, middle


def target_matrix(core: list[list[int]], rho: int) -> list[list[int]]:
    zero = (0, 0, 0, 0, 0, 0)
    twists = [value % 9 for value in BASELINE_TWIST_EXPONENTS]
    return [[path_coefficient(core, rho, zero, output, source, twists)[0]
             for source in range(9)] for output in range(9)]


def relation_edges(core: list[list[int]], rho: int,
                   logarithm: dict[int, int], target: list[list[int]],
                   orientation: tuple[int, ...]) -> list[tuple[int, int, int]]:
    """Give (middle, output, L) constraints c_middle-d_output=L."""
    edges = []
    for output in range(9):
        for source in range(9):
            coefficient, middle = path_coefficient(
                core, rho, orientation, output, source, [0] * 9)
            ratio = target[output][source] * pow(coefficient, -1, Q) % Q
            if ratio not in logarithm:
                raise SystemExit("orientation ratio escaped the ninth-root gauge")
            edges.append((middle, output, logarithm[ratio]))
    return edges


def solve_inverse_and_output(edges: list[tuple[int, int, int]]) -> list[dict]:
    """Solve c_middle-d_output=L, retaining the three gauge freedoms."""
    adjacency: dict[tuple[str, int], list[tuple[tuple[str, int], int]]] = {}
    for middle, output, value in edges:
        cnode, dnode = ("c", middle), ("d", output)
        adjacency.setdefault(cnode, []).append((dnode, -value))
        adjacency.setdefault(dnode, []).append((cnode, value))

    values: dict[tuple[str, int], int] = {}
    components: list[list[tuple[str, int]]] = []
    for start in adjacency:
        if start in values:
            continue
        values[start] = 0
        stack = [start]
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor, delta in adjacency[node]:
                proposed = (values[node] + delta) % 9
                if neighbor in values and values[neighbor] != proposed:
                    raise SystemExit("inconsistent phase constraint graph")
                if neighbor not in values:
                    values[neighbor] = proposed
                    stack.append(neighbor)
        components.append(component)

    solutions = []
    for offsets in itertools.product(range(9), repeat=len(components)):
        middle = [values[("c", index)] for index in range(9)]
        output = [values[("d", index)] for index in range(9)]
        for component, offset in zip(components, offsets):
            for kind, index in component:
                destination = middle if kind == "c" else output
                destination[index] = (destination[index] + offset) % 9
        solutions.append({"interstage": middle, "output": output})
    return solutions


def solve_bmscale_from_expanded(
        expanded: list[tuple[int, int, int, int]]) -> list[dict]:
    solutions = []
    for seeds in itertools.product(range(9), repeat=3):
        middle: list[int | None] = [None] * 9
        source_gauge: list[int | None] = [None] * 9
        for index, value in zip((0, 3, 6), seeds):
            middle[index] = value
        changed = True
        valid = True
        while changed and valid:
            changed = False
            for middle_index, _output, source, value in expanded:
                if middle[middle_index] is not None and source_gauge[source] is None:
                    source_gauge[source] = (value - middle[middle_index]) % 9
                    changed = True
                elif source_gauge[source] is not None and middle[middle_index] is None:
                    middle[middle_index] = (value - source_gauge[source]) % 9
                    changed = True
                elif (source_gauge[source] is not None and
                      middle[middle_index] is not None and
                      (source_gauge[source] + middle[middle_index]) % 9 != value):
                    valid = False
                    break
        if valid and all(value is not None for value in middle + source_gauge):
            solutions.append({
                "interstage": [int(value) for value in middle],
                "bmscale_input": [int(value) for value in source_gauge],
            })
    return solutions


def score(solution: dict, residual_key: str | None = None) -> tuple:
    constants = solution["interstage"]
    nonzero = [value for value in constants if value]
    residual = solution.get(residual_key, []) if residual_key else []
    return (len(nonzero), len(set(nonzero)), sum(value != 0 for value in residual),
            constants, residual)


def summarize_solution(solution: dict, residual_key: str | None = None) -> dict:
    constants = solution["interstage"]
    nonzero = [value for value in constants if value]
    result = {
        "interstage_exponents": constants,
        "interstage_nontrivial_chains": len(nonzero),
        "distinct_interstage_nontrivial_constants": len(set(nonzero)),
        "montgomery_chains_including_six_kappa": 6 + len(nonzero),
        "estimated_peak_ymm_if_B0_schedule_is_retained": 15,
        "runtime_lane_or_register_permutations": 0,
        "exact_range_status": "deferred-to-ITAIL-B1R",
    }
    if residual_key:
        result[f"{residual_key}_exponents"] = solution[residual_key]
        result[f"{residual_key}_nonidentity"] = sum(
            value != 0 for value in solution[residual_key])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--tail-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    scaled = json.loads(args.scaled_oracle.read_text())
    tail_map = json.loads(args.tail_map.read_text())
    if scaled["variants"]["R2"]["physical_row_to_mathematical_p"] != PAPER_P:
        raise SystemExit("Forward R2 paper-P order changed")
    if tail_map["semantic_contract"]["physical_p_order"] != PAPER_P:
        raise SystemExit("inverse-tail physical-P contract changed")
    rho = scaled["rho_mod_q"]
    omega = scaled["omega3_mod_q"]
    core = scaled_radix3_matrix(omega)
    logarithm = {pow(rho, exponent, Q): exponent for exponent in range(9)}

    # Extract D_F rather than assuming the paper rotation leaves a phase.
    forward = r2_matrix(core, rho)
    canonical = dft_matrix(rho)
    forward_gauge = []
    basis_checks = 0
    for physical_row, p in enumerate(PAPER_P):
        ratios = {forward[physical_row][source] *
                  pow(4 * canonical[p][source] % Q, -1, Q) % Q
                  for source in range(9)}
        if len(ratios) != 1 or next(iter(ratios)) not in logarithm:
            raise SystemExit("Forward R2 is not a component scalar gauge")
        exponent = logarithm[next(iter(ratios))]
        forward_gauge.append({"physical_row": physical_row,
                              "mathematical_p": p, "rho_exponent": exponent})
        basis_checks += 9
    if any(entry["rho_exponent"] for entry in forward_gauge):
        raise SystemExit("Forward R2 unexpectedly retained a nonidentity gauge")

    target = target_matrix(core, rho)
    cases = []
    selected = []
    p1_feasible = 0
    p2_feasible = 0
    all_p3_four = True
    for orientation in itertools.product(range(3), repeat=6):
        edges = relation_edges(core, rho, logarithm, target, orientation)
        expanded = []
        for edge_index, (middle, output, value) in enumerate(edges):
            expanded.append((middle, output, edge_index % 9, value))

        inverse_output = solve_inverse_and_output(edges)
        exact = [solution for solution in inverse_output
                 if not any(solution["output"])]
        p1 = min(exact, key=score) if exact else None
        p3 = min(inverse_output, key=lambda item: score(item, "output"))
        p2_solutions = solve_bmscale_from_expanded(expanded)
        p2 = min(p2_solutions,
                 key=lambda item: score(item, "bmscale_input")) \
            if p2_solutions else None
        if p1:
            p1_feasible += 1
        if p2:
            p2_feasible += 1
        for solution in inverse_output:
            for middle, output, value in edges:
                if ((solution["interstage"][middle] -
                     solution["output"][output]) % 9 != value):
                    raise SystemExit("P1/P3 phase solution failed exact replay")
        for solution in p2_solutions:
            for middle, _output, source, value in expanded:
                if ((solution["interstage"][middle] +
                     solution["bmscale_input"][source]) % 9 != value):
                    raise SystemExit("P2 phase solution failed exact replay")
        all_p3_four &= score(p3)[0] >= 4
        record = {
            "orientation": list(orientation),
            "P1_inverse_constants_exact_output":
                summarize_solution(p1) if p1 else None,
            "P2_bmscale_plus_inverse_exact_output":
                summarize_solution(p2, "bmscale_input") if p2 else None,
            "P3_inverse_plus_top_split_residual":
                summarize_solution(p3, "output"),
            "zero_runtime_permutation": True,
        }
        cases.append(record)
        if p1 and score(p1)[:2] == (4, 2):
            selected.append(record)

    if (len(cases) != 729 or p1_feasible != 27 or p2_feasible != 27 or
            not all_p3_four):
        raise SystemExit("B1P exhaustive-search regression")
    selected.sort(key=lambda item: item["orientation"])
    shortlist_orientations = ([0, 0, 0, 0, 0, 0],
                              [0, 1, 2, 0, 0, 0],
                              [0, 2, 1, 0, 0, 0])
    shortlist = [next(item for item in selected
                      if item["orientation"] == orientation)
                 for orientation in shortlist_orientations]

    document = {
        "schema": "ntruplus1152-itail-b1p/v1",
        "checkpoint": "G1C-ITAIL-B1P-phase-orientation-superoptimizer",
        "fixed_contract": {
            "physical_input_p": PAPER_P,
            "algorithm_family": "two scaled radix-3 layers",
            "runtime_lane_or_register_permutations": 0,
            "inverse_target": "natural-s output at B0 scale",
        },
        "forward_gauge": {
            "definition": "R2[p,a] / (4 * canonical_DFT9[p,a])",
            "by_component": forward_gauge,
            "depends_only_on_p": True,
            "independent_of_q_and_terminal_j": True,
            "identity": True,
            "base_mul_squared_exponents": [0] * 9,
            "conclusion": "paper P rotation is fully compensated inside Forward R2; there is no D_F^2 phase debt to absorb",
        },
        "search": {
            "orientation_tuple": "(first_r0,first_r1,first_r2,second_s0,second_s1,second_s2)",
            "cyclic_choices_per_node": 3,
            "candidate_count": len(cases),
            "exact_natural_output_candidates": p1_feasible,
            "bmscale_exact_output_candidates": p2_feasible,
            "cases": cases,
        },
        "lower_bound": {
            "six_intrinsic_kappa_chains": 6,
            "minimum_nontrivial_interstage_chains": 4,
            "minimum_total_montgomery_chains": 10,
            "minimum_distinct_interstage_constants": 2,
            "proved_over_all_729_with_output_gauge_allowed": all_p3_four,
        },
        "absorption_decision": {
            "P0_current_B0": "Pareto-optimal: 10 chains, two nontrivial interstage constants, zero permutation",
            "P1_inverse_interstage": "27 exact-output orientations; none beats P0",
            "P2_BMScale": "27 exact-output orientations; rekeying BMScale does not reduce the four-chain lower bound",
            "P3_inverse_top_split": "all 729 admit a residual output gauge, but none reduces the four-chain lower bound; top-split ASM absorption remains unpriced",
            "P4_split": "not entered: P2 and P3 independently meet the same structural lower bound and no Forward D_F^2 debt exists",
        },
        "shortlist_for_B1R": shortlist,
        "decision": {
            "selected_control": [0, 0, 0, 0, 0, 0],
            "range_discriminators": [[0, 1, 2, 0, 0, 0],
                                     [0, 2, 1, 0, 0, 0]],
            "assembly_authorized": False,
            "next": "ITAIL-B1R exact range/normalization comparison of the three tied orientations before any ASM change",
        },
        "proof": {
            "forward_basis_checks": basis_checks,
            "orientation_cases": len(cases),
            "source_sha256": {
                "scaled_oracle": sha256(args.scaled_oracle),
                "inverse_tail_map": sha256(args.tail_map),
            },
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated ITAIL-B1P search is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
