#!/bin/bash
# NTRU+ workspace setup for baseline-vs-optimized workflow.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASELINE_DIR="${ROOT_DIR}/ntruplus-KpqC-Final"
OPTIMIZED_DIR="${ROOT_DIR}/ntruplus-Optimized"

echo "[setup] root: ${ROOT_DIR}"

if [ ! -d "${BASELINE_DIR}" ]; then
  echo "[setup] ERROR: baseline source tree not found at ${BASELINE_DIR}"
  exit 1
fi

mkdir -p "${ROOT_DIR}/bench/kat" "${ROOT_DIR}/bench/cycles" "${ROOT_DIR}/bench/results"

if [ ! -d "${OPTIMIZED_DIR}" ]; then
  echo "[setup] creating optimized copy..."
  cp -R "${BASELINE_DIR}" "${OPTIMIZED_DIR}"
  echo "[setup] created ${OPTIMIZED_DIR}"
else
  echo "[setup] optimized tree already exists, skip copy"
fi

if [ ! -f "${ROOT_DIR}/bench/Makefile" ]; then
  echo "[setup] ERROR: bench/Makefile is missing"
  exit 1
fi

echo "[setup] done"
echo "[setup] next:"
echo "  1) ./scripts/validate_optimization.sh"
echo "  2) cd ntruplus-Optimized/Reference_Implementation/NTRU+768"
echo "  3) edit target function"
echo "  4) cd ../../../bench && make compare"