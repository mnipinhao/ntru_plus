#!/bin/bash
# Validate the portable baseline-vs-optimized workflow end-to-end.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BENCH_DIR="${ROOT_DIR}/bench"
PARAM_SET="${PARAM_SET:-NTRU+768}"
CYCLE_ITERATIONS="${CYCLE_ITERATIONS:-200}"
CYCLE_WARMUP="${CYCLE_WARMUP:-50}"

case "${PARAM_SET}" in
  NTRU+768|NTRU+864|NTRU+1152) ;;
  *)
    echo "[validate] ERROR: unsupported PARAM_SET=${PARAM_SET}"
    exit 1
    ;;
esac

IMPL_A="${IMPL_A:-${ROOT_DIR}/ntruplus-ntt-Optimized/Reference_Implementation/${PARAM_SET}}"
IMPL_B="${IMPL_B:-${ROOT_DIR}/ntruplus-ntt-Optimized/Optimized_Implementation/${PARAM_SET}}"

echo "[validate] root: ${ROOT_DIR}"

if [ ! -d "${BENCH_DIR}" ]; then
  echo "[validate] ERROR: bench directory not found at ${BENCH_DIR}"
  exit 1
fi
for impl in "${IMPL_A}" "${IMPL_B}"; do
  if [ ! -d "${impl}" ]; then
    echo "[validate] ERROR: implementation directory missing: ${impl}"
    exit 1
  fi
done

RUN_TAG="validation_$(date +%Y%m%d_%H%M%S)"

echo "[validate] parameter set: ${PARAM_SET}"
echo "[validate] implementation A: ${IMPL_A}"
echo "[validate] implementation B: ${IMPL_B}"
echo "[validate] running KAT-gated cycle comparison"
make -C "${BENCH_DIR}" \
  PARAM_SET="${PARAM_SET}" \
  IMPL_A="${IMPL_A}" \
  IMPL_B="${IMPL_B}" \
  RUN_TAG="${RUN_TAG}" \
  CYCLE_ITERATIONS="${CYCLE_ITERATIONS}" \
  CYCLE_WARMUP="${CYCLE_WARMUP}" \
  compare

echo "[validate] SUCCESS"
echo "[validate] artifacts:"
echo "  - ${BENCH_DIR}/results/kat/${RUN_TAG}/"
echo "  - ${BENCH_DIR}/results/cycles/${RUN_TAG}/"
