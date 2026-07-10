#!/usr/bin/env python3
"""Freeze reproducibility hashes for the four independent G1 variants."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


EXP = Path(__file__).resolve().parent
NTRU = EXP.parents[2]
REPO = NTRU.parents[2]
BENCH = REPO / "aarch64-bench"
OUTPUT = EXP / "u01v3_g1_r123_s2_frozen_manifest.json"


FILES: tuple[tuple[str, Path], ...] = (
    ("manifest_generator", Path(__file__).resolve()),
    ("generator_input", NTRU / "experiments/forward_ntt_phase123_u01/phase123_shared_prefix_v2_allrows.sym.s"),
    ("generator_input", NTRU / "asm/gt/experiment/u01_block_first_tables.inc"),
    ("generator", NTRU / "experiments/forward_ntt_phase123_u01/generate_phase123_shared_prefix_v2.py"),
    ("generator", NTRU / "experiments/forward_ntt_phase123_u01/generate_u01v3_f0123_track_g.py"),
    ("generator", NTRU / "experiments/forward_ntt_phase123_u01/generate_u01v3_g1_fullpath.py"),
    ("generator_utility", NTRU / "experiments/forward_ntt_phase123_u01/audit_umov_str_candidate.py"),
    ("generator", EXP / "generate_g1_stage345_reduction_slothy.py"),
    ("generator", EXP / "optimize_g1_stage345_reduction.py"),
    ("generator", EXP / "integrate_g1_stage345_reduction_slothy.py"),
    ("slothy_input", NTRU / "asm/slothy/experiments/u01v3_g1_stage345_reduction/block0_stage345_reduction.input.s"),
    ("slothy_input", NTRU / "asm/slothy/experiments/u01v3_g1_stage345_reduction/block1_stage345_reduction.input.s"),
    ("slothy_input", NTRU / "asm/slothy/experiments/u01v3_g1_stage345_reduction/block2_stage345_reduction.input.s"),
    ("slothy_input", NTRU / "asm/slothy/experiments/u01v3_g1_stage345_reduction/block3_stage345_reduction.input.s"),
    ("slothy_output", NTRU / "asm/slothy/experiments/u01v3_g1_stage345_reduction/block1_stage345_reduction.opt.s"),
    ("slothy_output", NTRU / "asm/slothy/experiments/u01v3_g1_stage345_reduction/block2_stage345_reduction.opt.s"),
    ("slothy_output", NTRU / "asm/slothy/experiments/u01v3_g1_stage345_reduction/block3_stage345_reduction.opt.s"),
    ("slothy_log", EXP / "slothy_logs/block0_n1.log"),
    ("slothy_log", EXP / "slothy_logs/block1_n1.log"),
    ("slothy_log", EXP / "slothy_logs/block2_n1.log"),
    ("slothy_log", EXP / "slothy_logs/block3_n1.log"),
    ("contract", EXP / "baseline-contract.yml"),
    ("contract", EXP / "kernel-contract.yml"),
    ("contract", EXP / "candidate-contract.yml"),
    ("audit", NTRU / "experiments/forward_ntt_phase123_u01/u01v3_g1_s2_transform_audit.json"),
    ("audit", EXP / "g1_r123_s2_transform_audit.json"),
    ("variant_g1", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1.S"),
    ("variant_g1", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_dropin.S"),
    ("variant_g1", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_abi_sentinel.S"),
    ("variant_g1_s2", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_s2.S"),
    ("variant_g1_s2", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_s2_dropin.S"),
    ("variant_g1_s2", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_s2_abi_sentinel.S"),
    ("variant_g1_r123", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_r123.S"),
    ("variant_g1_r123", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_r123_dropin.S"),
    ("variant_g1_r123", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_r123_abi_sentinel.S"),
    ("variant_g1_r123_s2", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_r123_s2.S"),
    ("variant_g1_r123_s2", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_r123_s2_dropin.S"),
    ("variant_g1_r123_s2", NTRU / "asm/gt/experiment/poly_ntt_u01v3_g1_r123_s2_abi_sentinel.S"),
    ("production", NTRU / "asm/gt/poly_ntt_g1_r123_s2.S"),
    ("production", NTRU / "asm/gt/poly_ntt_g1_r123_s2_tables.inc"),
    ("production_build", NTRU / "Makefile"),
    ("production_build", BENCH / "Makefile"),
    ("correctness_test", NTRU / "gt_test/test_u01v3_g1_fullpath.c"),
    ("correctness_test", NTRU / "gt_test/test_u01v3_g1_reduction_slothy.c"),
    ("paired_benchmark", BENCH / "bench_u01v3_g1_r123_paired_kem_pmu.c"),
    ("paired_benchmark", BENCH / "bench_kem_u01v3_g1_r123_prod_wrapper.c"),
    ("paired_benchmark", BENCH / "bench_kem_u01v3_g1_r123_candidate_wrapper.c"),
    ("paired_benchmark", BENCH / "bench_kem_u01v3_g1_r123_capture_wrapper.c"),
    ("paired_benchmark_audit", BENCH / "scripts/audit_u01v3_g1_r123_paired_binary.py"),
    ("paired_benchmark_summary", BENCH / "scripts/summarize_u01v3_g1_r123_paired_kem.py"),
    ("paired_result", BENCH / "results/u01v3_g1_r123_paired_kem/pmu.out"),
    ("paired_result", BENCH / "results/u01v3_g1_r123_paired_kem/layout.json"),
    ("paired_result", BENCH / "results/u01v3_g1_r123_paired_kem/linkage_audit.log"),
    ("paired_result", BENCH / "results/u01v3_g1_r123_paired_kem/summary.json"),
    ("paired_result", BENCH / "results/u01v3_g1_r123_paired_kem/summary.md"),
    ("threeway_benchmark", BENCH / "scripts/run_gt_production_threeway.py"),
    ("threeway_benchmark", BENCH / "bench.c"),
    ("threeway_benchmark", BENCH / "hal/hal.c"),
    ("threeway_result", BENCH / "results/gt_production_g1r123s2_threeway/summary.json"),
    ("threeway_result", BENCH / "results/gt_production_g1r123s2_threeway/summary.md"),
)


def digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(REPO)),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main() -> int:
    artifacts = []
    for role, path in FILES:
        if not path.is_file():
            raise FileNotFoundError(path)
        entry = digest(path)
        entry["role"] = role
        artifacts.append(entry)

    manifest = {
        "candidate_family": "u01v3_g1",
        "production_default_changed": True,
        "variants": {
            "G1": "poly_ntt_u01v3_g1",
            "G1_S2": "poly_ntt_u01v3_g1_s2",
            "G1_R123": "poly_ntt_u01v3_g1_r123",
            "G1_R123_S2": "poly_ntt_u01v3_g1_r123_s2",
        },
        "generator_commands": [
            "python3 experiments/forward_ntt_phase123_u01/generate_u01v3_g1_fullpath.py",
            "python3 experiments/forward_ntt_phase123_u01/g1_stage345_reduction_slothy/generate_g1_stage345_reduction_slothy.py",
            "SLOTHY_PATH=$HOME/slothy python3 experiments/forward_ntt_phase123_u01/g1_stage345_reduction_slothy/optimize_g1_stage345_reduction.py",
            "python3 experiments/forward_ntt_phase123_u01/g1_stage345_reduction_slothy/integrate_g1_stage345_reduction_slothy.py",
        ],
        "slothy": {
            "version": "0.2.1",
            "target": "slothy.targets.aarch64.neoverse_n1_experimental",
            "allow_renaming": False,
            "new_spills": False,
            "scheduled_blocks": [1, 2, 3],
            "unchanged_blocks": [0],
        },
        "s2_transform": {
            "g1_safe_sites_per_row": 27,
            "g1_kept_ext_str_per_row": 5,
            "g1_r123_safe_sites_per_row": 28,
            "g1_r123_kept_ext_str_per_row": 4,
        },
        "promotion": {
            "status": "production",
            "production_asm": "asm/gt/poly_ntt_g1_r123_s2.S",
            "legacy_switch": "GT_PRODUCTION_USE_LEGACY_NTT=1",
            "production_default_changed": True,
            "same_binary_full_kem_gate": "pass",
            "threeway_full_kem_gate": "pass",
        },
        "artifacts": sorted(artifacts, key=lambda entry: str(entry["path"])),
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")
    print(OUTPUT)
    print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
