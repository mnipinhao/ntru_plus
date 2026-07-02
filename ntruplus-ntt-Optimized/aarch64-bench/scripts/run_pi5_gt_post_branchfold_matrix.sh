#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bench_dir="$(cd "${script_dir}/.." && pwd)"
runner="${script_dir}/run_pi5_matrix.py"
python_bin="${PYTHON:-python3}"
runs="${RUNS:-5}"
stamp="$(date +%Y%m%d-%H%M%S)"
suite_dir="${SUITE_DIR:-${bench_dir}/logs/pi5-gt-post-branchfold-${stamp}}"
extra_args=("$@")

post_modes="invntt,ntt_mul_pipeline,ntt_basemul_add_pipeline,kem_dec"

stage_args=()
if [[ "${INCLUDE_INVNTT_STAGES:-0}" == "1" ]]; then
  stage_args=(--include-invntt-stages)
fi

run_case() {
  local name="$1"
  shift
  echo "== ${name} =="
  "${python_bin}" "${runner}" \
    --runs "${runs}" \
    --log-dir "${suite_dir}/${name}" \
    "$@" \
    "${extra_args[@]}"
}

mkdir -p "${suite_dir}"

# P0: promoted default and preserved pre-promotion inverse baseline.
run_case gt_promoted_default \
  --variants gt_opt \
  --modes "${post_modes}" \
  "${stage_args[@]}"

run_case gt_legacy_directstage123_branchfold \
  --variants gt_opt \
  --modes "${post_modes}" \
  "${stage_args[@]}" \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_directstage123_branchfold.s \
  --make-var GT_INVNTT_STAGE_ASM=ntruplus/asm/inv_my_ntt_directstage123_branchfold_benchstages.s

# P1: post-row branchfold loop scope.
run_case gt_post_branchfold_a72_1stripe \
  --variants gt_opt \
  --modes "${post_modes}" \
  "${stage_args[@]}" \
  --make-var GT_INVNTT_ASM=ntruplus/asm/variants/inv_my_ntt_post_branchfold_a72.s

run_case gt_post_branchfold_3stripe \
  --variants gt_opt \
  --modes "${post_modes}" \
  "${stage_args[@]}" \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_post_branchfold_3stripe_slothy.s

run_case gt_post_branchfold_6stripe \
  --variants gt_opt \
  --modes "${post_modes}" \
  "${stage_args[@]}" \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_post_branchfold_6stripe_slothy.s

# P2: same loop scopes, but with adjacent normal/precompute q-pair loads.
run_case gt_post_branchfold_constgrp3 \
  --variants gt_opt \
  --modes "${post_modes}" \
  "${stage_args[@]}" \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_post_branchfold_constgrp3.s

run_case gt_post_branchfold_6stripe_constgrp3 \
  --variants gt_opt \
  --modes "${post_modes}" \
  "${stage_args[@]}" \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_post_branchfold_6stripe_constgrp3.s

# P3: first compression probe for the repeated branchfold constants.
run_case gt_post_branchfold_consthalf \
  --variants gt_opt \
  --modes "${post_modes}" \
  "${stage_args[@]}" \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_post_branchfold_consthalf.s

echo "wrote ${suite_dir}"
