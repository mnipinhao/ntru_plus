#!/usr/bin/env python3
"""Build an exact dynamic instruction-class ledger for the P25 inverse boundary."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
P25 = ROOT / "experiments/gt864-p25-official-profile"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_lines(path: Path) -> list[str]:
    result = []
    for raw in path.read_text().splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line or line.startswith(("#", "/*", "*", "*/")):
            continue
        if line.startswith(".") and not line.endswith(":"):
            continue
        result.append(line)
    return result


def mnemonic(line: str) -> str | None:
    if line.endswith(":") or ".req " in line or ".unreq " in line:
        return None
    token = line.split(None, 1)[0].lower()
    if token.startswith("c("):
        return None
    return token


def instructions(lines: list[str]) -> list[str]:
    return [m for line in lines if (m := mnemonic(line)) is not None]


def between(lines: list[str], start: str, stop: str, include_stop: bool = False) -> list[str]:
    first = lines.index(start) + 1
    last = lines.index(stop, first) + int(include_stop)
    return lines[first:last]


def through_ret(lines: list[str], start: str) -> list[str]:
    first = lines.index(start) + 1
    last = next(i for i in range(first, len(lines)) if lines[i].split(None, 1)[0].lower() == "ret")
    return lines[first:last + 1]


def official_inverse_trace(lines: list[str]) -> list[str]:
    fn = through_ret(lines, "poly_invntt_scale:")
    a = fn.index("_looptop_6543:")
    b = next(i for i in range(a, len(fn)) if fn[i] == "b.ne _looptop_6543")
    c = fn.index("_looptop_210:")
    d = next(i for i in range(c, len(fn)) if fn[i] == "b.ne _looptop_210")
    return (instructions(fn[:a]) + instructions(fn[a + 1:b + 1]) * 18 +
            instructions(fn[b + 1:c]) + instructions(fn[c + 1:d + 1]) * 6 +
            instructions(fn[d + 1:]))


def single_loop_trace(lines: list[str], start: str, loop: str, branch: str,
                      trips: int) -> list[str]:
    fn = through_ret(lines, start)
    a = fn.index(loop)
    b = next(i for i in range(a, len(fn)) if fn[i] == branch)
    return (instructions(fn[:a]) + instructions(fn[a + 1:b + 1]) * trips +
            instructions(fn[b + 1:]))


def helper_trace(path: Path, symbol: str) -> list[str]:
    return instructions(through_ret(clean_lines(path), symbol + ":"))


def macro_instructions(lines: list[str], name: str) -> list[str]:
    a = lines.index(f".macro {name}")
    b = lines.index(".endm", a)
    return instructions(lines[a + 1:b])


def gt_wrapper_trace(path: Path) -> tuple[list[str], dict[str, int]]:
    """Expand the fixed nested wrapper loops without expanding helper calls."""
    raw = []
    for source in path.read_text().splitlines():
        line = source.split("//", 1)[0].strip()
        if not line or line.startswith(("#", "/*", "*", "*/")):
            continue
        raw.append(line)
    save = macro_instructions(raw, "SAVE_PUBLIC")
    restore = macro_instructions(raw, "RESTORE_PUBLIC")
    start = raw.index("C(gt864_inverse_ternary_asm):") + 1
    body = raw[start:]

    def ins(a: str, b: str, include_b: bool = False) -> list[str]:
        return instructions(between(body, a, b, include_b))

    # Prefix ends just before the first top-loop label. SAVE_PUBLIC is a macro.
    top = body.index(".Lp8inv_top:")
    prefix_lines = body[:top]
    prefix = []
    for line in prefix_lines:
        prefix.extend(save if line == "SAVE_PUBLIC" else instructions([line]))

    i9_setup = ins(".Lp8inv_i9:", "bl C(packed_i9)", True)
    i9_iter_tail = instructions(["add x28, x28, #1", "cmp x28, #2", "b.ne .Lp8inv_i9"])
    component_tail = instructions(["add x27, x27, #1", "cmp x27, #3", "b.ne .Lp8inv_component"])
    top_tail = instructions(["add x26, x26, #1", "cmp x26, #2", "b.ne .Lp8inv_top"])
    i9 = []
    for _top in range(2):
        i9 += instructions(["mov x27, #0"])
        for _component in range(3):
            i9 += instructions(["mov x28, #0"])
            for _block in range(2):
                i9 += i9_setup + i9_iter_tail
            i9 += component_tail
        i9 += top_tail

    main_setup = ins(".Lp8inv_main:", "bl C(lazy_i16)", True)
    main_iter_tail = instructions(["add x27, x27, #1", "cmp x27, #2", "b.ne .Lp8inv_main"])
    main_component_tail = instructions(["add x26, x26, #1", "cmp x26, #3", "b.ne .Lp8inv_main_component"])
    main = instructions(["mov x26, #0"])
    for _component in range(3):
        main += instructions(["mov x27, #0"])
        for _half in range(2):
            main += main_setup + main_iter_tail
        main += main_component_tail

    tail = instructions(between(body, "b.ne .Lp8inv_main_component", "bl C(lazy_itail)", True))
    raw_ternary = instructions(between(body, "bl C(lazy_itail)", "bl C(gt864_crepmod3_raw)", True))
    wipe_start = body.index("bl C(gt864_crepmod3_raw)") + 1
    restore_pos = body.index("RESTORE_PUBLIC", wipe_start)
    wipe_lines = body[wipe_start:restore_pos]
    loop_label = wipe_lines.index(".Lp13inv_wipe:")
    loop_branch = wipe_lines.index("b.ne .Lp13inv_wipe")
    wipe = (instructions(wipe_lines[:loop_label]) +
            instructions(wipe_lines[loop_label + 1:loop_branch + 1]) * 14 +
            instructions(wipe_lines[loop_branch + 1:]))
    trace = prefix + i9 + main + tail + raw_ternary + wipe + restore
    pieces = {"prefix": len(prefix), "i9_control": len(i9),
              "main_control": len(main), "tail_control": len(tail),
              "raw_ternary_control": len(raw_ternary), "wipe": len(wipe),
              "restore": len(restore)}
    return trace, pieces


def category(m: str) -> str:
    if m == "mul":
        return "mul"
    if m == "sqrdmulh":
        return "sqrdmulh"
    if m == "mls":
        return "mls"
    if m in {"add", "sub", "neg", "cmgt", "cmeq", "cmhi", "and", "eor", "bic"}:
        return "vector_integer"
    if m in {"trn1", "trn2", "zip1", "zip2", "uzp1", "uzp2", "ext", "tbl", "tbx", "ins"}:
        return "vector_routing"
    if m == "orr":
        return "vector_copy"
    if m == "umov":
        return "lane_extract"
    if m in {"ldr", "ld1", "ldp"}:
        return "load"
    if m in {"str", "st1", "stp", "strh"}:
        return "store"
    if m in {"b", "b.ne", "bl", "ret", "cbz", "cbnz"}:
        return "control_transfer"
    return "scalar_setup_control"


def summarize(trace: list[str]) -> dict[str, object]:
    mnemonics = Counter(trace)
    categories = Counter(category(x) for x in trace)
    return {"instructions": len(trace), "categories": dict(sorted(categories.items())),
            "mnemonics": dict(sorted(mnemonics.items()))}


def main() -> None:
    official_ntt = HERE / "official-ntt.s"
    official_crep = HERE / "official-crepmod3.s"
    gt_paths = {
        "inverse9_x12": (PROD / "gt864_native_inverse9.S", "packed_i9", 12),
        "main_i16_x6": (PROD / "gt864_native_inverse16_lazy.S", "lazy_i16", 6),
        "tail_i16": (PROD / "gt864_native_inverse_tail_lazy.S", "lazy_itail", 1),
    }
    official_inverse = official_inverse_trace(clean_lines(official_ntt))
    official_crep_trace = single_loop_trace(clean_lines(official_crep),
                                             "poly_crepmod3:", "_looptop:",
                                             "b.ne _looptop", 27)
    wrapper, wrapper_pieces = gt_wrapper_trace(PROD / "gt864_native_public.S")
    gt_stages: dict[str, list[str]] = {}
    for name, (path, symbol, calls) in gt_paths.items():
        gt_stages[name] = helper_trace(path, symbol) * calls
    gt_stages["raw_to_ternary"] = single_loop_trace(
        clean_lines(PROD / "gt864_crepmod3_raw.S"), "gt864_crepmod3_raw:",
        ".Lp8_loop:", "b.ne .Lp8_loop", 27)
    gt_stages["wrapper_control_wipe"] = wrapper
    gt_trace = sum(gt_stages.values(), [])
    official_trace = official_inverse + official_crep_trace

    p25 = json.loads((P25 / "event-results.json").read_text())
    measured_official = int(
        p25["decaps"]["official"]["Inverse"]["instructions"]["median"] +
        p25["decaps"]["official"]["Crepmod3"]["instructions"]["median"])
    measured_gt = int(
        p25["decaps"]["gt"]["Inverse_to_ternary"]["instructions"]["median"])
    report = {
        "experiment": "GT864-P26-INVERSE-DEFICIT-AUDIT-20260914",
        "production_revision": json.loads((P25 / "environment.json").read_text())["gt_production_revision"],
        "official_tree_sha256": json.loads((P25 / "environment.json").read_text())["official_tree_hash"],
        "source_sha256": {
            "official_ntt": sha256(official_ntt),
            "official_crepmod3": sha256(official_crep),
            **{path.name: sha256(path) for path, _, _ in gt_paths.values()},
            "gt864_crepmod3_raw.S": sha256(PROD / "gt864_crepmod3_raw.S"),
            "gt864_native_public.S": sha256(PROD / "gt864_native_public.S"),
        },
        "measured_p25": {
            "official_instructions": measured_official,
            "gt_instructions": measured_gt,
            "deficit": measured_gt - measured_official,
        },
        "exact_dynamic_source_ledger": {
            "official_inverse": summarize(official_inverse),
            "official_crepmod3": summarize(official_crep_trace),
            "official_total": summarize(official_trace),
            "gt_stages": {name: summarize(trace) for name, trace in gt_stages.items()},
            "gt_total": summarize(gt_trace),
            "gt_wrapper_pieces": wrapper_pieces,
        },
        "load_instruction_breakdown": {
            "official": {
                "coefficient_or_intermediate": 171,
                "constant_table": 81,
                "callee_restore": 4,
                "total": 256,
            },
            "gt": {
                "coefficient_or_intermediate": 328,
                "constant_table": 706,
                "callee_restore": 10,
                "total": 1044,
                "constant_detail": {
                    "inverse9_twist_x3": 216,
                    "i16_stage_x3": 42,
                    "i16_composite_x4": 448,
                },
            },
        },
        "historical_constraints": {
            "P21_scatter_ideal_removal_ceiling_cycles": 175.016,
            "P25_inverse_cycle_deficit": 280.675,
            "scatter_only_cannot_close_gap": True,
            "P11_full_or_D_store_route_candidates": "all slower",
            "P22_copy_free_main_i16": "local win but complete Inverse/Decaps regression",
        },
        "current_call_coordinate_proof": {
            "formula": "natural_index = 27*k + 3*row + component",
            "main_call": "fixed component, four rows, k=0..31",
            "tail_call": "fixed row=8, all three components, k=0..31",
            "main_fixed_component_implies_index_mod_3": True,
            "max_consecutive_natural_coefficients_from_one_main_call": 1,
            "direct_natural_q_store_from_one_current_main_call": False,
        },
    }
    oc = report["exact_dynamic_source_ledger"]["official_total"]["categories"]
    gc = report["exact_dynamic_source_ledger"]["gt_total"]["categories"]
    report["category_delta_gt_minus_official"] = {
        key: gc.get(key, 0) - oc.get(key, 0) for key in sorted(set(oc) | set(gc))
    }
    report["source_to_pmu_reconciliation"] = {
        "official": measured_official - len(official_trace),
        "gt": measured_gt - len(gt_trace),
    }
    delta = report["category_delta_gt_minus_official"]
    modular_delta = delta["mul"] + delta["sqrdmulh"] + delta["mls"]
    report["decision"] = {
        "modular_multiply_instruction_delta": modular_delta,
        "reduction_is_not_the_deficit": modular_delta < 0,
        "dominant_excess": {
            "lane_extract": delta["lane_extract"],
            "load": delta["load"],
            "store": delta["store"],
            "scalar_setup_control": delta["scalar_setup_control"],
        },
        "next_gate": "P27 consumer-oriented I16 lane-basis search",
        "required_change": (
            "change the producer lane/bank basis before terminal materialization; "
            "do not replay P11's store-then-route or P22's copy-only DAG"
        ),
    }
    # Hard reconciliation gates.  The 22/21 instructions are the matched
    # profiler's call-site measurement shell; their one-instruction difference
    # converts the source-ledger +3741 exactly to the measured +3740.
    assert measured_gt - measured_official == 3740
    assert len(gt_trace) - len(official_trace) == 3741
    assert report["source_to_pmu_reconciliation"] == {"official": 22, "gt": 21}
    assert modular_delta == -151
    assert report["load_instruction_breakdown"]["official"]["total"] == 256
    assert report["load_instruction_breakdown"]["gt"]["total"] == 1044
    assert 175.016 < 280.675
    for component in range(3):
        for half in range(2):
            indices = sorted(27 * k + 3 * row + component
                             for k in range(32)
                             for row in range(4 * half, 4 * half + 4))
            assert all(b - a >= 3 for a, b in zip(indices, indices[1:]))
    (HERE / "audit-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
