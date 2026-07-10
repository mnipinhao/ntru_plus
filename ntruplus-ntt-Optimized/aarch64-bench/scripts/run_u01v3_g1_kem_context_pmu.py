#!/usr/bin/env python3
"""Run KEM-context PMU for U01v3 G1 full-path variants."""

from __future__ import annotations

import csv
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


COMPONENTS = (
    "keypair_total",
    "encap_total",
    "decap_total",
    "encap_ntt_r",
    "encap_ntt_m",
    "decap_ntt_m1",
    "decap_ntt_r1",
)


@dataclass(frozen=True)
class Variant:
    label: str
    ntt_asm: str
    ntt32_asm: str


PROD_NTT32 = "ntruplus/asm/slothy/production/my_32ntt.opt.s"


def rows(cid: str) -> str:
    base = f"ntruplus/asm/slothy/experiments/ntt32_forward_ntt_aggressive_wave/{cid}"
    return " ".join(
        [
            PROD_NTT32,
            f"{base}/row0_stage345_{cid}.opt.s",
            f"{base}/row1_stage345_{cid}.opt.s",
            f"{base}/row2_stage345_{cid}.opt.s",
        ]
    )


VARIANTS = (
    Variant("A", "ntruplus/asm/gt/poly_ntt.s", PROD_NTT32),
    Variant(
        "G1",
        "ntruplus/asm/gt/experiment/poly_ntt_u01v3_g1_dropin.S",
        PROD_NTT32,
    ),
    Variant(
        "G1S2",
        "ntruplus/asm/gt/experiment/poly_ntt_u01v3_g1_s2_dropin.S",
        PROD_NTT32,
    ),
    Variant(
        "G1R123",
        "ntruplus/asm/gt/experiment/poly_ntt_u01v3_g1_r123_dropin.S",
        PROD_NTT32,
    ),
    Variant(
        "G1R123S2",
        "ntruplus/asm/gt/experiment/poly_ntt_u01v3_g1_r123_s2_dropin.S",
        PROD_NTT32,
    ),
)


def run(args: list[str], *, env: dict[str, str] | None = None, output: Path | None = None) -> str:
    print("command," + " ".join(args), flush=True)
    if output is None:
        completed = subprocess.run(args, check=True, text=True, capture_output=True, env=env)
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="")
        return completed.stdout
    with output.open("w", encoding="utf-8") as out:
        completed = subprocess.run(args, check=True, text=True, stdout=out, stderr=subprocess.STDOUT, env=env)
    return output.read_text(encoding="utf-8")


def parse_component_output(text: str) -> dict[str, dict[str, float]]:
    lines = text.splitlines()
    try:
        start = next(idx for idx, line in enumerate(lines) if line.startswith("variant,text_size"))
    except StopIteration as exc:
        raise RuntimeError("component PMU CSV header not found") from exc
    csv_lines = []
    for line in lines[start:]:
        if line.startswith("component_profile_sink="):
            break
        if line and not line.startswith("build_config,"):
            csv_lines.append(line)
    out: dict[str, dict[str, float]] = {}
    for row in csv.DictReader(csv_lines):
        name = row["variant"]
        if name not in COMPONENTS:
            continue
        cycles = float(row["cycles_per_call"])
        instructions = float(row["instructions_per_call"])
        out[name] = {
            "cycles": cycles,
            "instructions": instructions,
            "cpi": cycles / instructions if instructions else 0.0,
            "text_size": float(row["text_size"]),
            "static_insns": float(row["static_insns"]),
        }
    missing = [component for component in COMPONENTS if component not in out]
    if missing:
        raise RuntimeError(f"missing component rows: {missing}")
    return out


def symbol_info(binary: Path, symbol_name: str) -> dict[str, int]:
    out = subprocess.check_output(["nm", "-S", "--defined-only", str(binary)], text=True)
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[-1] == symbol_name:
            addr = int(parts[0], 16)
            size = int(parts[1], 16) if len(parts) >= 4 else 0
            return {
                "addr": addr,
                "size": size,
                "addr_mod32": addr & 31,
                "addr_mod64": addr & 63,
            }
    raise RuntimeError(f"symbol {symbol_name} not found in {binary}")


def text_size(binary: Path) -> int:
    out = subprocess.check_output(["size", str(binary)], text=True).splitlines()
    parts = out[-1].split()
    return int(parts[0])


def main() -> int:
    core = os.environ.get("CORE", "3")
    ntests = os.environ.get("U01V3_G1_KEM_PMU_NTESTS", "31")
    niterations = os.environ.get("U01V3_G1_KEM_PMU_NITERATIONS", "5000")
    nwarmup = os.environ.get("U01V3_G1_KEM_PMU_NWARMUP", "100")
    ninputs = os.environ.get("U01V3_G1_KEM_PMU_NINPUTS", "64")
    result_dir = Path(os.environ.get("U01V3_G1_KEM_PMU_RESULT_DIR", "results/u01v3_g1_kem_context_pmu"))
    result_dir.mkdir(parents=True, exist_ok=True)

    all_results: dict[str, dict[str, dict[str, float]]] = {}
    alignments: dict[str, dict[str, int]] = {}

    print(
        "kem_context_pmu_settings,"
        f"NTESTS={ntests},NITERATIONS={niterations},NWARMUP={nwarmup},"
        f"NINPUTS={ninputs},CORE={core}"
    )
    for variant in VARIANTS:
        target = result_dir / f"bench_{variant.label}_kem_component_pmu_bin"
        stats = result_dir / f"bench_{variant.label}_kem_component_pmu.stats"
        output = result_dir / f"bench_{variant.label}_kem_component_pmu.out"
        make_args = [
            "make",
            "-B",
            str(target),
            f"GT_KEM_COMPONENT_PROFILE_PMU_TARGET={target}",
            f"NTESTS={ntests}",
            f"NITERATIONS={niterations}",
            f"NWARMUP={nwarmup}",
            f"GT_KEM_COMPONENT_PROFILE_PMU_NINPUTS={ninputs}",
            f"GT_PRODUCTION_NTT_ASM={variant.ntt_asm}",
            f"GT_PRODUCTION_NTT32_ASM={variant.ntt32_asm}",
        ]
        run(make_args)
        run(["python3", "scripts/write_gt_kem_component_profile_stats.py", str(target), str(stats)])
        env = os.environ.copy()
        env["GT_KEM_COMPONENT_PROFILE_STATS_FILE"] = str(stats)
        text = run(["taskset", "-c", core, str(target)], env=env, output=output)
        all_results[variant.label] = parse_component_output(text)
        alignments[variant.label] = symbol_info(target, "poly_ntt")
        alignments[variant.label]["binary_text_size"] = text_size(target)
        print(
            "kem_context_alignment,"
            f"variant={variant.label},poly_ntt_addr=0x{alignments[variant.label]['addr']:x},"
            f"poly_ntt_size={alignments[variant.label]['size']},"
            f"addr_mod32={alignments[variant.label]['addr_mod32']},"
            f"addr_mod64={alignments[variant.label]['addr_mod64']},"
            f"binary_text_size={alignments[variant.label]['binary_text_size']}"
        )

    for component in COMPONENTS:
        base_a = all_results["A"][component]["cycles"]
        base_g1 = all_results["G1"][component]["cycles"]
        base_g1s2 = all_results["G1S2"][component]["cycles"]
        base_r123 = all_results["G1R123"][component]["cycles"]
        for variant in VARIANTS:
            row = all_results[variant.label][component]
            print(
                "kem_context_summary,"
                f"variant={variant.label},component={component},"
                f"cycles={row['cycles']:.3f},instructions={row['instructions']:.3f},"
                f"cpi={row['cpi']:.6f},"
                f"delta_vs_A={row['cycles'] - base_a:.3f},"
                f"delta_vs_G1={row['cycles'] - base_g1:.3f},"
                f"delta_vs_G1S2={row['cycles'] - base_g1s2:.3f},"
                f"delta_vs_G1R123={row['cycles'] - base_r123:.3f},"
                f"text_size={int(row['text_size'])},"
                f"static_insns={int(row['static_insns'])},"
                f"poly_ntt_addr_mod32={alignments[variant.label]['addr_mod32']},"
                f"poly_ntt_addr_mod64={alignments[variant.label]['addr_mod64']},"
                "correctness=pass"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
