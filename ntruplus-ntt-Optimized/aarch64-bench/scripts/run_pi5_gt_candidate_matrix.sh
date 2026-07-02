#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bench_dir="$(cd "${script_dir}/.." && pwd)"
runner="${script_dir}/run_pi5_matrix.py"
python_bin="${PYTHON:-python3}"
runs="${RUNS:-5}"
stamp="$(date +%Y%m%d-%H%M%S)"
suite_dir="${SUITE_DIR:-${bench_dir}/logs/pi5-gt-current-${stamp}}"
extra_args=("$@")

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

run_case gt_opt_default \
  --variants gt_opt \
  --modes invntt,basemul,basemul_add,ntt_mul_pipeline,ntt_basemul_add_pipeline,kem_dec \
  "${stage_args[@]}"

run_case gt_base_n1 \
  --variants gt_opt \
  --modes basemul,basemul_add,ntt_mul_pipeline,ntt_basemul_add_pipeline,kem_dec \
  --make-var GT_BASE_OPT_ASM=ntruplus/asm/baseline/base_gt_opt_wrapper.S

run_case gt_invntt_stage123_stripescratch \
  --variants gt_opt \
  --modes invntt,ntt_mul_pipeline,ntt_basemul_add_pipeline,kem_dec \
  "${stage_args[@]}" \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch.s \
  --make-var GT_INVNTT_STAGE_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch_benchstages.s

run_case gt_base_n1_invntt_stage123_stripescratch \
  --variants gt_opt \
  --modes invntt,basemul,basemul_add,ntt_mul_pipeline,ntt_basemul_add_pipeline,kem_dec \
  "${stage_args[@]}" \
  --make-var GT_BASE_OPT_ASM=ntruplus/asm/baseline/base_gt_opt_wrapper.S \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch.s \
  --make-var GT_INVNTT_STAGE_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch_benchstages.s

echo "wrote ${suite_dir}"
