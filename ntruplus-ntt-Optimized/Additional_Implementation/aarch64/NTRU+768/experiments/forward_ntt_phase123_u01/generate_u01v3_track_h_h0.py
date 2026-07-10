#!/usr/bin/env python3
"""Generate the Track H H0 block3-load-elision upper-bound diagnostic.

H0 is deliberately not a correctness candidate.  It keeps the complete G1
instruction stream except for the 24 Stage345 block3 q loads (eight per row).
The stale register values stand in for inputs that a hypothetical upstream
producer would hand off for free.  This makes H0 an optimistic whole-path PMU
upper bound for Track H, not an implementation that may be promoted.
"""

from __future__ import annotations

import re
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123
from generate_phase123_shared_prefix_v3_block1_block01_fuse import load_stage345_block
from generate_u01v3_f0123_track_g import (
    G1_BENCH,
    G1_SYMBOL,
    P_SYMBOL,
    V_SYMBOL,
    build_e3_stage345,
    emit_body_g1,
    emit_wrapper,
)


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
ASM_ROOT = NTRU_ROOT / "asm/gt/experiment"
BENCH_ROOT = NTRU_ROOT.parents[2] / "aarch64-bench"

H0_SYMBOL = "u01v3_f0123_h0_block3_load_elision"
H0_ASM = ASM_ROOT / f"{H0_SYMBOL}.S"
H0_BENCH = BENCH_ROOT / "bench_u01v3_f0123_h0_block3_load_upperbound_pmu.c"
H0_RESULT = ROOT / "u01v3_f0123_h0_upperbound_result.md"

LOAD_RE = re.compile(r"^\s*ldr\s+(q\d+),\s*\[x4,\s*#(\d+)\]")


def remove_block3_q_loads(lines: list[str]) -> tuple[list[str], list[dict[str, object]]]:
    out: list[str] = []
    removed: list[dict[str, object]] = []
    for source_index, line in enumerate(lines):
        code = line.split("//", 1)[0].rstrip()
        match = LOAD_RE.match(code)
        if match and int(match.group(2)) % 16 == 0:
            q_index = int(match.group(2)) // 16
            if 24 <= q_index <= 31:
                removed.append(
                    {
                        "source_index": source_index,
                        "q_index": q_index,
                        "destination": match.group(1),
                        "scratch_offset": int(match.group(2)),
                        "original": code.strip(),
                    }
                )
                out.append(
                    f"        // H0 diagnostic: elided block3 Q{q_index} load; "
                    f"stale {match.group(1)} models a free register handoff."
                )
                continue
        out.append(line)
    if len(removed) != 8 or {entry["q_index"] for entry in removed} != set(range(24, 32)):
        raise ValueError(f"expected eight unique block3 q loads, found {removed}")
    return out, removed


def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"expected one replacement site, found {count}: {old[:80]!r}")
    return source.replace(old, new, 1)


def emit_h0_bench() -> str:
    source = G1_BENCH.read_text()
    source = replace_once(
        source,
        '#error "bench_u01v3_f0123_track_g_pmu requires Linux perf_event_open"',
        '#error "bench_u01v3_f0123_h0_block3_load_upperbound_pmu requires Linux perf_event_open"',
    )
    source = replace_once(source, "#define VARIANT_COUNT 3", "#define VARIANT_COUNT 4")
    source = replace_once(
        source,
        "\tint is_oracle;\n};",
        "\tint is_oracle;\n\tint is_diagnostic;\n};",
    )
    source = replace_once(
        source,
        f"void {G1_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);",
        f"void {G1_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);\n"
        f"void {H0_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);",
    )
    source = replace_once(
        source,
        f"extern const char {G1_SYMBOL}_end[];",
        f"extern const char {G1_SYMBOL}_end[];\nextern const char {H0_SYMBOL}_end[];",
    )
    old_variants = f'''static const struct variant variants[VARIANT_COUNT] = {{
\t{{"P", "production_source_order_f0123", {P_SYMBOL}, {P_SYMBOL}_end, 1}},
\t{{"V", "u01v2_shared_prefix_scratch_f0123", {V_SYMBOL}, {V_SYMBOL}_end, 0}},
\t{{"G1", "u01v3_g1_delayed_block3", {G1_SYMBOL}, {G1_SYMBOL}_end, 0}},
}};'''
    new_variants = f'''static const struct variant variants[VARIANT_COUNT] = {{
\t{{"P", "production_source_order_f0123", {P_SYMBOL}, {P_SYMBOL}_end, 1, 0}},
\t{{"V", "u01v2_shared_prefix_scratch_f0123", {V_SYMBOL}, {V_SYMBOL}_end, 0, 0}},
\t{{"G1", "u01v3_g1_delayed_block3", {G1_SYMBOL}, {G1_SYMBOL}_end, 0, 0}},
\t{{"H0", "block3_load_elision_upper_bound", {H0_SYMBOL}, {H0_SYMBOL}_end, 0, 1}},
}};'''
    source = replace_once(source, old_variants, new_variants)
    source = replace_once(
        source,
        "\t\tmismatches[v] = 0;\n\t\tif (variants[v].is_oracle) {",
        "\t\tmismatches[v] = 0;\n"
        "\t\tif (variants[v].is_diagnostic) {\n"
        "\t\t\tstatus[v] = 2;\n"
        "\t\t\tmismatches[v] = -1;\n"
        "\t\t\tcontinue;\n"
        "\t\t}\n"
        "\t\tif (variants[v].is_oracle) {",
    )
    source = replace_once(
        source,
        'printf("u01v3_f0123_track_g_pmu NTESTS=%d NITERATIONS=%d sink=%" PRIu64 "\\n", NTESTS, NITERATIONS, sink);',
        'printf("u01v3_f0123_track_h_h0_pmu NTESTS=%d NITERATIONS=%d sink=%" PRIu64 "\\n", NTESTS, NITERATIONS, sink);',
    )
    source = replace_once(
        source,
        'printf("id,name,status,cycles,instructions,cpi,delta_vs_P,delta_vs_V,text_size,addr_mod32,addr_mod64,mismatches\\n");',
        'printf("id,name,status,cycles,instructions,cpi,delta_vs_P,delta_vs_V,delta_vs_G1,text_size,addr_mod32,addr_mod64,mismatches\\n");',
    )
    source = replace_once(
        source,
        "\tconst uint64_t v_cycles = median_cycles(1);",
        "\tconst uint64_t v_cycles = median_cycles(1);\n\tconst uint64_t g1_cycles = median_cycles(2);",
    )
    source = replace_once(
        source,
        '''\t\tprintf("%s,%s,%s,%" PRIu64 ",%" PRIu64 ",%.4f,%+" PRId64 ",%+" PRId64 ",%zu,%lu,%lu,%d\\n",
\t\t       variants[v].id, variants[v].name, status[v] ? "pass" : "fail",
\t\t       cyc, ins, cpi, (int64_t)cyc - (int64_t)p_cycles,
\t\t       (int64_t)cyc - (int64_t)v_cycles, text_size(&variants[v]),
\t\t       (unsigned long)(addr % 32), (unsigned long)(addr % 64),
\t\t       mismatches[v]);''',
        '''\t\tconst char *status_name = status[v] == 2 ? "diagnostic" : (status[v] ? "pass" : "fail");
\t\tprintf("%s,%s,%s,%" PRIu64 ",%" PRIu64 ",%.4f,%+" PRId64 ",%+" PRId64 ",%+" PRId64 ",%zu,%lu,%lu,%d\\n",
\t\t       variants[v].id, variants[v].name, status_name,
\t\t       cyc, ins, cpi, (int64_t)cyc - (int64_t)p_cycles,
\t\t       (int64_t)cyc - (int64_t)v_cycles,
\t\t       (int64_t)cyc - (int64_t)g1_cycles, text_size(&variants[v]),
\t\t       (unsigned long)(addr % 32), (unsigned long)(addr % 64),
\t\t       mismatches[v]);''',
    )
    return source


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage345 = {block: load_stage345_block(block) for block in range(4)}
    h0_stage3453, removed = remove_block3_q_loads(stage345[3])
    e3_stage3450, e3_stage3451, e3_stage3452, _metadata = build_e3_stage345()
    h0_body, _stage12_reports = emit_body_g1(
        phase_lines,
        e3_stage3450,
        e3_stage3451,
        e3_stage3452,
        h0_stage3453,
    )
    H0_ASM.write_text(emit_wrapper(H0_SYMBOL, h0_body))
    H0_BENCH.write_text(emit_h0_bench())
    if not H0_RESULT.exists():
        H0_RESULT.write_text(
            "# U01v3 Track H H0 Block3 Load Upper Bound\n\n"
            "Status: generated, PMU pending. Production default unchanged.\n\n"
            "H0 mechanically removes the eight Stage345 block3 q loads in each "
            "of three rows, for 24 removed loads total. It is intentionally not "
            "a correctness candidate: stale register values model a hypothetical "
            "free producer-to-consumer register handoff while keeping the rest of "
            "the G1 whole-path instruction order unchanged.\n\n"
            "```text\n"
            f"symbol: {H0_SYMBOL}\n"
            f"removed block3 q loads: {len(removed) * 3}\n"
            "arithmetic/scatter changed: no\n"
            "correctness status: skipped diagnostic\n"
            "Pi5 PMU: pending\n"
            "```\n"
        )
    print(H0_ASM)
    print(H0_BENCH)
    print(H0_RESULT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
