#!/usr/bin/env bash
set -eu

bench=${1:?usage: run_round3_pmu.sh BENCH_BINARY}
backend_candidates="ntt basemul basemul_scale baseinv invntt tobytes frombytes"
common_candidates="add sub cbd1 triple crepmod3 sotp_encode sotp_decode hash_f hash_g hash_h shake256 randombytes32 randombytes96"

run_groups() {
    candidate=$1
    backend=$2
    prefix="results/round3-pmu-${candidate}-${backend}"
    for group in 1 2 3 4; do
        case $group in
            1) events='cpu_core/cycles/,cpu_core/instructions/' ;;
            2) events='cpu_core/uops_retired.slots/,cpu_core/mem_inst_retired.all_loads/,cpu_core/mem_inst_retired.all_stores/' ;;
            3) events='cpu_core/mem_load_retired.l1_miss/,cpu_core/branches/,cpu_core/branch-misses/' ;;
            4) events='cpu_core/slots/,cpu_core/topdown-fe-bound/,cpu_core/topdown-be-bound/' ;;
        esac
        perf stat -x, --no-big-num -o "${prefix}-g${group}.csv" \
            -e "$events" -- "$bench" --candidate "$candidate" \
            --backend "$backend" --iterations 1000000 --samples 20 \
            > "${prefix}-g${group}-run.json"
        echo "round3 PMU complete: ${candidate}:${backend}:group${group}"
    done
}

for candidate in $backend_candidates; do
    run_groups "$candidate" official
    run_groups "$candidate" gt
done
for candidate in $common_candidates; do
    run_groups "$candidate" official
done
