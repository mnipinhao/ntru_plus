#!/usr/bin/env bash
set -eu

bench=${1:?usage: run_round3_direct.sh BENCH_BINARY}
candidates="ntt basemul basemul_scale baseinv invntt tobytes frombytes add sub cbd1 triple crepmod3 sotp_encode sotp_decode hash_f hash_g hash_h shake256 randombytes32 randombytes96"

for candidate in $candidates; do
    "$bench" --candidate "$candidate" --iterations 1000000 --samples 20 \
        > "results/round3-direct-${candidate}.json"
    echo "round3 direct complete: ${candidate}"
done

