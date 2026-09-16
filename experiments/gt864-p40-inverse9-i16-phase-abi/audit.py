#!/usr/bin/env python3
"""P40 exact phase ABI, range, table, and instruction-ledger audit."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GENERATOR = HERE / "generate.py"
Q = 3457
BASELINE = {"inverse9": 184, "main": 657, "tail": 589}
CALLS = {"inverse9": 12, "main": 6, "tail": 1}


def load_generator():
    spec = importlib.util.spec_from_file_location("p40_generate", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(module)
    return module


def modular_i16(values, stage):
    """The production bit-reversed-input radix-2 CT topology modulo q."""
    values = [values[i] % Q for i in range(16)]
    n = 0
    for level in range(4):
        step = 1 << level
        for start in range(0, 16, 2 * step):
            for j in range(step):
                left, right = start + j, start + j + step
                b = stage[(1 << level) - 1 + j] % Q
                a = values[left]
                product = values[right] * b % Q
                values[left] = (a + product) % Q
                values[right] = (a - product) % Q
                n += 1
    assert n == 32
    return values


def phase_proof(g):
    contexts = 0
    basis_checks = 0
    factor_checks = 0
    for top, column, row in itertools.product(range(2), range(16), range(9)):
        k = g.p7.pair(top, column, row)[0] % Q
        base = g.p7.pair(top, 0, row)[0] % Q
        assert k == base * pow(g.DELTA, column * row, Q) % Q
        factor_checks += 1

    standard = []
    for level in range(4):
        for j in range(1 << level):
            standard.append(g.p7.STAGE[16 * level + 2 * j] % Q)

    for kind in ("main0", "main1", "tail"):
        rows = g.row_lanes(kind)
        pairs = g.stage_pairs(kind)
        for lane, row in enumerate(rows):
            if row is None:
                continue
            twisted = [b[lane] % Q for b, _ in pairs]
            for basis in range(16):
                raw = [int(i == basis) for i in range(16)]
                phased = [raw[c] * pow(g.DELTA, row * c, Q) % Q for c in range(16)]
                phased = [phased[i] for i in g.BR]
                candidate = [raw[i] for i in g.BR]
                assert modular_i16(phased, standard) == modular_i16(candidate, twisted)
                basis_checks += 1
            contexts += 1
    return {
        "terminal_factor_contexts": factor_checks,
        "active_i16_lane_contexts": contexts,
        "linear_basis_vectors": basis_checks,
        "factorization": "k(top,c,s)=k(top,0,s)*delta^(c*s)",
    }


def table_proof(g):
    checks = 0
    for kind, table, old in (
        ("main0", g.MAIN0, g.p13.MAIN_NEW),
        ("main1", g.MAIN1, g.p13.MAIN_NEW),
        ("tail", g.TAIL, g.p13.TAIL_NEW),
    ):
        factors = g.scale_vector(kind)
        for column in range(16):
            for half in (0, 16):
                for lane in range(8):
                    got = table[32 * column + half + lane]
                    want = g.center(old[32 * column + half + lane] * factors[lane])
                    assert got == want
                    assert table[32 * column + half + 8 + lane] == g.magic(want)
                    checks += 1
    for kind in ("main0", "main1", "tail"):
        for b, h in g.stage_pairs(kind):
            assert all(y == g.magic(x) for x, y in zip(b, h))
            checks += 8
    return checks


def instruction_ledger(g):
    model = json.loads((HERE / "model.json").read_text())
    candidate = model["instructions"]
    helper_delta = {
        name: CALLS[name] * (candidate[name] - BASELINE[name]) for name in BASELINE
    }
    # The raw inverse9 no longer consumes x3.  Four public pointer-formation
    # instructions disappear in each of twelve calls.  Main/tail pointer
    # selection replaces existing MOVs one-for-one.
    wrapper_delta = -4 * CALLS["inverse9"]
    total_delta = sum(helper_delta.values()) + wrapper_delta
    assert total_delta == -136
    assert -total_delta >= 36
    return {
        "baseline_per_call": BASELINE,
        "candidate_per_call": candidate,
        "calls": CALLS,
        "helper_dynamic_delta": helper_delta,
        "wrapper_dynamic_delta": wrapper_delta,
        "net_dynamic_delta_per_inverse": total_delta,
        "net_dynamic_saving_per_inverse": -total_delta,
    }


def main():
    g = load_generator()
    model = json.loads((HERE / "model.json").read_text())
    pi_path = HERE / "pi-results.json"
    pi_result = json.loads(pi_path.read_text()) if pi_path.exists() else None
    assert g.DELTA == 2863
    assert model["delta_order"] == 144
    assert pow(g.DELTA, 81, Q) == 550
    assert pow(g.DELTA, 64, Q) == 1520
    assert 550 * 1520 % Q == g.DELTA
    assert max(model["i16_peak"].values()) < 32768
    assert model["terminal_resets"] == {
        "main_low": [], "main_high": [], "tail_low": [6], "tail_high": []
    }
    for family in model["terminal_pre_reset"].values():
        for column, sides in family.items():
            for side, bound in sides.items():
                if bound > 5185:
                    assert (column == "6" and side == "low" and family is model["terminal_pre_reset"]["tail"])

    phase = phase_proof(g)
    table_checks = table_proof(g)
    ledger = instruction_ledger(g)
    report = {
        "experiment": "P40",
        "status": "final-reject" if pi_result and pi_result["status"] == "reject" else "static-gate-pass",
        "generator_sha256": hashlib.sha256(GENERATOR.read_bytes()).hexdigest(),
        "phase_proof": phase,
        "table_entries_checked": table_checks,
        "range": {
            "raw_inverse9_bounds": model["raw_bounds"],
            "i16_peak": model["i16_peak"],
            "terminal_pre_reset": model["terminal_pre_reset"],
            "terminal_resets": model["terminal_resets"],
            "accepted_output_radius": 5185,
        },
        "instruction_ledger": ledger,
        "memory": {
            "new_coefficient_loads": 0,
            "new_coefficient_stores": 0,
            "new_scratch_bytes": 0,
            "new_memory_passes": 0,
        },
        "gate": {
            "minimum_net_instruction_saving": 36,
            "achieved_net_instruction_saving": ledger["net_dynamic_saving_per_inverse"],
            "exact_phase_identity": True,
            "signed_int16_closed": True,
            "p8_radius_closed": True,
            "pass": True,
            "next": ("candidate rejected by paired Pi5 cycles; retain P35 production"
                     if pi_result and pi_result["status"] == "reject"
                     else "Slothy no-spill allocation and bounded Cortex-A76 timing"),
        },
    }
    if pi_result:
        report["pi5"] = pi_result
    (HERE / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["gate"], indent=2))


if __name__ == "__main__":
    main()
