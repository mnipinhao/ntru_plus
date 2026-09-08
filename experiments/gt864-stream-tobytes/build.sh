#!/bin/sh
set -eu
prod=/home/pi/ntruplus-experiments/gt864-production-k1-validation/NTRU+864
flags='-O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -fPIC -ffunction-sections -fdata-sections'
gcc $flags -I"$prod" -c tobytes.c -o tobytes.o
gcc $flags -I"$prod" -Dpoly_ntt=gt_d1_poly_ntt -Dpoly_invntt=gt_d1_poly_invntt -Dpoly_baseinv=gt_d1_poly_baseinv -Dpoly_basemul=gt_d1_poly_basemul -Dpoly_basemul_add=gt_d1_poly_basemul_add -Dpoly_tobytes=stream_tobytes -Dpoly_frombytes=p3b12_candidate_frombytes -c "$prod/kem.c" -o kem.o
objs='symmetric poly fips202 gt864_poly_api gt864_fr0_basemul gt864_fr0_basemul_d1 gt864_fr0_inverse_asm_wrapper add ntt base crepmod3 pack cbd gt864_forward_poly_ntt gt864_forward_six_bank gt864_top_split gt864_fr0_inverse9_block gt864_inverse16_blocks cluster_transpose_frombytes byte_api input_once_frombytes byte_boundary route9 raw_pack stock_wrapper tail_variants'
set --
for obj in $objs; do set -- "$@" "$prod/$obj.o"; done
gcc -shared -Wl,-Bsymbolic -Wl,--gc-sections "$@" tobytes.o kem.o -o libnative.so
gcc $flags -rdynamic -I"$prod" test.c tobytes.o "$prod/libgt864.so" -Wl,-rpath,"$prod" -o test_native
./test_native
gcc -O3 -rdynamic paired.c -ldl -o paired
ln -sf "$prod/libgt864.so" sc.so
for n in 0 1 2 3 4 5; do BASE=sc CAND=libnative taskset -c 3 ./paired $((n % 2)) > paired$n.log; done
