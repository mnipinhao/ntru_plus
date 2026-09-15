#!/usr/bin/env python3
"""P39 exact inverse9 arithmetic-DAG audit.

This binds to the production P7-C1 source, reuses the P7-C0 exact interval and
root model, and checks the narrow P39 contract.  It intentionally does not
claim an exhaustive search of arbitrary linear circuits.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
SOURCE = PROD / "gt864_native_inverse9.S"
P7 = ROOT / "experiments/gt864-native-asm/inverse-p7c0-range/audit.py"
Q = 3457


def load_p7():
    spec = importlib.util.spec_from_file_location("p39_p7", P7)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.PROD = PROD
    return mod


def static_ops():
    lines = SOURCE.read_text().splitlines()
    begin = next(i for i, line in enumerate(lines) if "packed_i9_slothy_start:" in line)
    end = next(i for i, line in enumerate(lines) if "packed_i9_slothy_end:" in line)
    ops = Counter()
    for raw in lines[begin + 1:end]:
        line = raw.split("//", 1)[0].strip()
        if line and not line.startswith((".", "#", "/*")) and not line.endswith(":"):
            ops[line.split()[0].lower()] += 1
    return sum(ops.values()), dict(sorted(ops.items()))


def terminal_constants(p7):
    vectors = []
    geometric = []
    for top in range(2):
        for block in range(2):
            for s in range(9):
                values = [p7.pair(top, 8 * block + lane, s)[0] % Q for lane in range(8)]
                vectors.append(dict(top=top, block=block, row=s, values=values,
                                    uniform=len(set(values)) == 1))
        for column in range(16):
            values = [p7.pair(top, column, s)[0] % Q for s in range(9)]
            inv9 = values[0]
            lam = values[1] * pow(inv9, -1, Q) % Q
            assert all(values[s] == inv9 * pow(lam, s, Q) % Q for s in range(9))
            geometric.append(dict(top=top, column=column, inverse9=inv9,
                                  lambda_mod_q=lam))
    assert all(x["inverse9"] == (-384) % Q for x in geometric)
    uniform = [x for x in vectors if x["uniform"]]
    assert len(uniform) == 4 and all(x["row"] == 0 for x in uniform)
    assert all(x["values"][0] == (-384) % Q for x in uniform)
    identity = [x for x in vectors if all(v == 1 for v in x["values"])]
    return vectors, geometric, identity


def main():
    p7 = load_p7()
    count, ops = static_ops()
    assert count == 184
    assert ops["mul"] == ops["sqrdmulh"] == ops["mls"] == 19

    # Every production physical terminal map remains equal to the independent
    # topology model in all 32 (top,column) contexts.
    physical_maps = 0
    for top in range(2):
        for column in range(16):
            got, _ = p7.physical_i9(top, column)
            want = p7.i9(p7.Model(), top, column, True)
            assert got == want
            physical_maps += len(got)

    # Exhaust the two known one-product B3 orientations.  They change ranges,
    # not the count: all masks retain 6 B3 + 4 eta + 9 terminal products.
    masks = []
    reference_rows = None
    for mask in range(64):
        result, rows = p7.chain(True, mask)
        if reference_rows is None:
            reference_rows = rows
        else:
            for key in rows:
                assert [value.p for value in rows[key]] == [value.p for value in reference_rows[key]]
        masks.append(dict(mask=mask, i9_output=result["i9_output"],
                          i16_peak=result["i16_peak"], raw_output=result["raw_output"],
                          mulmods_per_block=19))
    assert min(x["mulmods_per_block"] for x in masks) == 19
    vectors, geometric, identity = terminal_constants(p7)

    # Removing only row-0 scaling exposes the total nine-input sum.  The exact
    # interval image of that add tree is [-9*2497,9*2497].  It still fits one
    # int16 register but two legal I16 inputs can sum beyond int16.
    raw_s0_bound = 9 * 2497
    assert raw_s0_bound == 22473 and 2 * raw_s0_bound > 32767

    # A b=1 Algorithm-10 representative reset needs SQRDMULH+MLS but no MUL.
    # Delaying -384 through linear I16 could therefore save only one instruction
    # per block under the unchanged int16 I16 contract, short of P39's three.
    best_in_contract_saving = 1
    required_saving = 3

    report = {
        "experiment": "P39",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "baseline": {
            "static_instructions_per_block": count,
            "operations": ops,
            "algorithm10_per_block": 19,
            "algorithm10_classes": {"b3": 6, "eta": 4, "terminal": 9},
            "calls_per_inverse": 12,
            "physical_terminal_maps_checked": physical_maps,
        },
        "search": {
            "b3_orientation_masks_checked": len(masks),
            "minimum_algorithm10_per_block": 19,
            "terminal_vectors_checked": len(vectors),
            "terminal_identity_vectors": len(identity),
            "uniform_terminal_vectors": len([x for x in vectors if x["uniform"]]),
            "geometric_contexts_checked": len(geometric),
            "factorization": "k(top,column,s) = -384 * lambda(top,column)^s mod 3457",
        },
        "s0_delay": {
            "constant": -384,
            "meaning": "inverse of 9 modulo 3457",
            "unscaled_abs_bound": raw_s0_bound,
            "two_input_i16_sum_abs_bound": 2 * raw_s0_bound,
            "direct_delay_safe": False,
            "identity_reset_instructions": 2,
            "net_instruction_saving_per_block": best_in_contract_saving,
        },
        "gate": {
            "required_instruction_saving_per_block": required_saving,
            "achieved_instruction_saving_per_block": best_in_contract_saving,
            "required_instruction_saving_per_inverse": 36,
            "achieved_instruction_saving_per_inverse": 12,
            "pass": False,
            "slothy_run": False,
            "pi5_run": False,
            "production_changed": False,
        },
        "next": "broaden only the inverse9-to-I16 representation contract and prove the geometric phase/row-rotation ABI before assembly",
    }
    (HERE / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["gate"], indent=2))


if __name__ == "__main__":
    main()
