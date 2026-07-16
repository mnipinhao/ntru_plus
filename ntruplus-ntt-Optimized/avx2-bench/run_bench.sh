#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
CC=${CC:-gcc}
CORE=${CORE:-2}
PERF_PREFIX=${PERF_PREFIX:-}
PERF_REPETITIONS=${PERF_REPETITIONS:-5}
PERF_CORE_EVENTS=${PERF_CORE_EVENTS:-cycles}
PERF_CACHE_EVENTS=${PERF_CACHE_EVENTS:-}
RUN_TSC=${RUN_TSC:-0}
STRICT_ENV=${STRICT_ENV:-0}
OPERATIONS=${OPERATIONS:-"ntt gt-ntt gt-ntt-asm-soa basemul gt-basemul-soa invntt gt-invntt32 gt-invntt32-asm gt-invdft3 gt-invdft3-asm gt-invpost gt-invpost-asm gt-invntt-soa gt-invntt-soa-hybrid gt-invntt-soa-dft3-hybrid gt-invntt-soa-postprocess-hybrid polymul gt-polymul-soa gt-polymul-soa-hybrid gt-polymul-soa-dft3-hybrid gt-polymul-soa-postprocess-hybrid"}
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
RESULT_DIR=${RESULT_DIR:-"$ROOT/results/$STAMP"}
TARGET="$ROOT/build/avx2_bench"

mkdir -p "$RESULT_DIR"

if ! command -v taskset >/dev/null 2>&1; then
  echo "taskset is required" >&2
  exit 1
fi
if ! command -v perf >/dev/null 2>&1; then
  echo "perf is required" >&2
  exit 1
fi

{
  echo "timestamp_utc=$STAMP"
  echo "core=$CORE"
  echo "operations=$OPERATIONS"
  echo "perf_core_events=$PERF_CORE_EVENTS"
  echo "perf_cache_events=$PERF_CACHE_EVENTS"
  echo "run_tsc=$RUN_TSC"
  uname -a
  lscpu
  "$CC" --version 2>/dev/null | head -n 1 || true
  perf --version
  echo -n "perf_event_paranoid="
  cat /proc/sys/kernel/perf_event_paranoid 2>/dev/null || echo unknown
  echo -n "governor="
  cat "/sys/devices/system/cpu/cpu${CORE}/cpufreq/scaling_governor" 2>/dev/null || echo unknown
  echo -n "thread_siblings="
  cat "/sys/devices/system/cpu/cpu${CORE}/topology/thread_siblings_list" 2>/dev/null || echo unknown
  if [[ -r /sys/devices/system/cpu/cpufreq/boost ]]; then
    echo -n "boost="
    cat /sys/devices/system/cpu/cpufreq/boost
  elif [[ -r /sys/devices/system/cpu/intel_pstate/no_turbo ]]; then
    echo -n "intel_no_turbo="
    cat /sys/devices/system/cpu/intel_pstate/no_turbo
  else
    echo "boost=unknown"
  fi
} >"$RESULT_DIR/metadata.txt"

if [[ "$STRICT_ENV" == 1 ]] && grep -q '^boost=1$' "$RESULT_DIR/metadata.txt"; then
  echo "boost is enabled and STRICT_ENV=1" >&2
  exit 1
fi

"$TARGET" --validate | tee "$RESULT_DIR/validation.txt"

for operation in $OPERATIONS; do
  if [[ "$RUN_TSC" == 1 ]]; then
    taskset -c "$CORE" "$TARGET" "$operation" \
      | tee "$RESULT_DIR/${operation}.tsc.txt"
  fi

  # Keep the core and cache events in separate passes.  Requesting all six at
  # once can multiplex the general-purpose counters on the target host.
  # shellcheck disable=SC2086
  $PERF_PREFIX perf stat -x, -r "$PERF_REPETITIONS" \
    -e "$PERF_CORE_EVENTS" \
    -o "$RESULT_DIR/${operation}.core.perf.csv" \
    taskset -c "$CORE" "$TARGET" "$operation" --perf-loop \
    >"$RESULT_DIR/${operation}.core.perf.stdout.txt"

  if [[ -n "$PERF_CACHE_EVENTS" ]]; then
    # shellcheck disable=SC2086
    $PERF_PREFIX perf stat -x, -r "$PERF_REPETITIONS" \
      -e "$PERF_CACHE_EVENTS" \
      -o "$RESULT_DIR/${operation}.cache.perf.csv" \
      taskset -c "$CORE" "$TARGET" "$operation" --perf-loop \
      >"$RESULT_DIR/${operation}.cache.perf.stdout.txt"
  fi
done

echo "results=$RESULT_DIR"
