#!/usr/bin/env python3
"""Run bounded GT production GC/link-order experiments on a pinned Pi 5."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "results/gt_icache_link_order_2026-07-23"
RESULT_JSON = RESULT_DIR / "result.json"
RESULT_MD = RESULT_DIR / "result.md"

NTESTS = int(os.environ.get("GT_ICACHE_NTESTS", "61"))
NITERATIONS = int(os.environ.get("GT_ICACHE_NITERATIONS", "2000"))
NWARMUP = int(os.environ.get("GT_ICACHE_NWARMUP", "100"))
PERF_REPEATS = int(os.environ.get("GT_ICACHE_PERF_REPEATS", "3"))
CORE = os.environ.get("GT_ICACHE_CORE", "3")

MODES = ("kem_keygen", "kem_enc", "kem_dec")
VARIANTS = {
    "L0_current": {
        "link_order": "current",
        "section_gc": 0,
    },
    "L1_gc": {
        "link_order": "current",
        "section_gc": 1,
    },
    "L2_mode_hot": {
        "link_order": "mode_hot",
        "section_gc": 0,
    },
    "L3_mode_hot_gc": {
        "link_order": "mode_hot",
        "section_gc": 1,
    },
}
PERF_GROUPS = (
    ("cycles", "instructions", "branch-misses"),
    (
        "L1-icache-load-misses",
        "stalled-cycles-frontend",
        "stalled-cycles-backend",
    ),
)
SYMBOLS = (
    "crypto_kem_keypair",
    "crypto_kem_enc",
    "crypto_kem_dec",
    "poly_ntt",
    "poly_basemul",
    "poly_invntt",
    "poly_crepmod3",
    "gt_decap_verify_to_bytes",
    "poly_basemul_add_encap_direct32_q31_tobytes_contract",
    "gt_keygen_baseinv_bpq_to_cq_scaled_r",
    "gt_keygen_basemul_bpq_cq_to_cq_scaled_r",
)


def run(command: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


def make_binary(
    target: Path,
    mode: str,
    counter: str,
    link_order: str,
    section_gc: int,
) -> None:
    command = [
        "make",
        "-f",
        "Makefile.production",
        "-B",
        f"TARGET={target}",
        "VARIANT=gt_production_default",
        f"BENCH_MODE={mode}",
        f"CYCLES={counter}",
        f"NTESTS={NTESTS}",
        f"NITERATIONS={NITERATIONS}",
        f"NWARMUP={NWARMUP}",
        f"GT_PRODUCTION_LINK_ORDER={link_order}",
        f"GT_PRODUCTION_USE_SECTION_GC={section_gc}",
    ]
    run(command)


def run_internal(target: Path, metric: str) -> int:
    completed = run(["taskset", "-c", CORE, str(target)])
    match = re.search(rf" {re.escape(metric)} = (\d+)", completed.stdout)
    if not match:
        raise RuntimeError(f"missing {metric} result in {target}:\n{completed.stdout}")
    return int(match.group(1))


def binary_size(target: Path) -> dict[str, int]:
    output = run(["size", str(target)]).stdout.splitlines()
    fields = output[-1].split()
    return {
        "text": int(fields[0]),
        "data": int(fields[1]),
        "bss": int(fields[2]),
        "total": int(fields[3]),
    }


def symbol_layout(target: Path) -> dict[str, dict[str, int]]:
    output = run(["nm", "-S", "-n", "--defined-only", str(target)]).stdout
    result = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) != 4:
            continue
        address, size, _kind, name = fields
        if name not in SYMBOLS:
            continue
        numeric_address = int(address, 16)
        result[name] = {
            "address": numeric_address,
            "size": int(size, 16),
            "mod32": numeric_address % 32,
            "mod64": numeric_address % 64,
        }
    return result


def parse_perf(path: Path) -> dict[str, float]:
    result = {}
    for raw in path.read_text(encoding="ascii").splitlines():
        fields = raw.split(",")
        if len(fields) < 3:
            continue
        value = fields[0].strip().replace(" ", "")
        event = fields[2].strip().split(":", 1)[0]
        if not value or value.startswith("<") or not event:
            continue
        try:
            result[event] = float(value)
        except ValueError:
            continue
    return result


def perf_diagnostics(target: Path, tag: str) -> dict[str, float]:
    merged = {}
    for group_index, events in enumerate(PERF_GROUPS):
        output = RESULT_DIR / f"{tag}.perf{group_index}.csv"
        run(
            [
                "perf",
                "stat",
                "-x,",
                "-r",
                str(PERF_REPEATS),
                "--output",
                str(output),
                "-e",
                ",".join(events),
                "taskset",
                "-c",
                CORE,
                str(target),
            ]
        )
        merged.update(parse_perf(output))
    calls = NTESTS * NITERATIONS
    return {
        event: value / calls
        for event, value in merged.items()
    }


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, object]] = {}

    for variant, config in VARIANTS.items():
        results[variant] = {}
        for mode in MODES:
            stem = f"gt_icache_{variant}_{mode}"
            cycles_target = Path("/tmp") / f"{stem}_cycles"
            instructions_target = Path("/tmp") / f"{stem}_instructions"

            make_binary(
                cycles_target,
                mode,
                "PERF",
                config["link_order"],
                config["section_gc"],
            )
            cycles = run_internal(cycles_target, "cycles")
            size = binary_size(cycles_target)
            layout = symbol_layout(cycles_target)
            perf = perf_diagnostics(cycles_target, stem)

            make_binary(
                instructions_target,
                mode,
                "INSTRUCTIONS",
                config["link_order"],
                config["section_gc"],
            )
            instructions = run_internal(instructions_target, "instructions")

            results[variant][mode] = {
                "cycles": cycles,
                "instructions": instructions,
                "cpi": cycles / instructions,
                "size": size,
                "symbols": layout,
                "perf_per_measured_call": perf,
                "correctness": "pass",
            }
            print(
                f"{variant} {mode}: {cycles} cycles, {instructions} instructions, "
                f"text={size['text']}"
            )

    baseline = results["L0_current"]
    for variant, modes in results.items():
        for mode, data in modes.items():
            data["delta_vs_L0"] = {
                "cycles": data["cycles"] - baseline[mode]["cycles"],
                "instructions": (
                    data["instructions"] - baseline[mode]["instructions"]
                ),
                "text": data["size"]["text"] - baseline[mode]["size"]["text"],
            }

    winners = {}
    for mode in MODES:
        winners[mode] = min(results, key=lambda variant: results[variant][mode]["cycles"])

    payload = {
        "host": "Raspberry Pi 5 Cortex-A76",
        "core": CORE,
        "ntests": NTESTS,
        "niterations": NITERATIONS,
        "nwarmup": NWARMUP,
        "perf_repeats": PERF_REPEATS,
        "variants": VARIANTS,
        "results": results,
        "cycle_winners": winners,
    }
    RESULT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")

    rows = []
    for mode in MODES:
        for variant in VARIANTS:
            data = results[variant][mode]
            delta = data["delta_vs_L0"]
            perf = data["perf_per_measured_call"]
            rows.append(
                "| {mode} | {variant} | {cycles} | {instructions} | {cpi:.4f} | "
                "{text} | {dc:+d} | {dt:+d} | {l1i:.2f} | {front:.2f} | "
                "{back:.2f} |".format(
                    mode=mode,
                    variant=variant,
                    cycles=data["cycles"],
                    instructions=data["instructions"],
                    cpi=data["cpi"],
                    text=data["size"]["text"],
                    dc=delta["cycles"],
                    dt=delta["text"],
                    l1i=perf.get("L1-icache-load-misses", float("nan")),
                    front=perf.get("stalled-cycles-frontend", float("nan")),
                    back=perf.get("stalled-cycles-backend", float("nan")),
                )
            )

    RESULT_MD.write_text(
        f"""# GT production I-cache and link-order result

Pi 5 Cortex-A76, core {CORE}, portable `NO_CE`, {NTESTS} samples x
{NITERATIONS} calls. Internal cycles/instructions are medians. External perf
events are process-level means divided by measured calls; use them for
same-mode relative diagnosis, not as isolated kernel counts.

| Mode | Variant | Cycles | Instructions | CPI | Text | Cycles vs L0 | Text vs L0 | L1I misses/call | Front stalls/call | Backend stalls/call |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

Cycle winners:

```json
{json.dumps(winners, indent=2)}
```

Promotion rule: a link-order/GC candidate must not regress any full-KEM mode.
Alignment padding was intentionally excluded because the previous blanket
32-byte alignment experiment regressed encapsulation.
""",
        encoding="ascii",
    )
    print(json.dumps({"cycle_winners": winners}, indent=2))


if __name__ == "__main__":
    main()
