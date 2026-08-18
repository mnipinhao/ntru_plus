#!/bin/sh
order=/home/nuc/src/ntru-plus-avx2-gt-rewrite-official-001/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001/tools/hot_function_order_h1.ld
echo "gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -ffunction-sections -fdata-sections -Wl,--gc-sections -Wl,--section-ordering-file=$order -gdwarf-4 -Wall"
