#!/bin/bash
# Validate baseline-vs-optimized workflow end-to-end.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BENCH_DIR="${ROOT_DIR}/bench"

echo "[validate] root: ${ROOT_DIR}"

if [ ! -d "${BENCH_DIR}" ]; then
  echo "[validate] ERROR: bench directory not found at ${BENCH_DIR}"
  exit 1
fi
if [ ! -d "${ROOT_DIR}/ntruplus-KpqC-Final" ]; then
  echo "[validate] ERROR: baseline tree missing"
  exit 1
fi
if [ ! -d "${ROOT_DIR}/ntruplus-Optimized" ]; then
  echo "[validate] ERROR: optimized tree missing; run ./scripts/setup_workspace.sh first"
  exit 1
fi

cd "${BENCH_DIR}"
RUN_TAG="validation_$(date +%Y%m%d_%H%M%S)"

echo "[validate] step 1/2: KAT comparison"
make RUN_TAG="${RUN_TAG}" compare-kat

echo "[validate] step 2/2: cycle comparison (KAT-gated)"
make RUN_TAG="${RUN_TAG}" CYCLE_ITERATIONS=200 CYCLE_WARMUP=50 cycles-compare

echo "[validate] SUCCESS"
echo "[validate] artifacts:"
echo "  - bench/results/kat/${RUN_TAG}/"
echo "  - bench/results/cycles/${RUN_TAG}/"