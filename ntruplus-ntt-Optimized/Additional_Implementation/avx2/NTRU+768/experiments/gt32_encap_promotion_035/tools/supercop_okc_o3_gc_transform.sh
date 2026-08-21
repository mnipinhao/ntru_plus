#!/bin/sh
echo 'gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -ffunction-sections -fdata-sections -Wl,--gc-sections -Wl,-T,/home/nuc/supercop-20260627/crypto_kem/ntruplus768/avx2-gt32-clean-033b-transform/hot-order.ld -gdwarf-4 -Wall'
