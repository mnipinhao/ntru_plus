#!/bin/sh
# Build four shared objects on the Pi: each NTRU+1152 implementation plain and
# instrumented. The instrumented builds redirect poly_*/hash_* through timing
# wrappers with -D, exactly as the NTRU+864 profiler does.
set -eu
GT=${GT:-/home/pi/ntruplus-experiments/gt1152-p10-kem-20260917}
OFF=${OFF:-/home/pi/supercop-20260831/crypto_kem/ntruplus1152/aarch64}
CF="-O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -fPIC -ffunction-sections -fdata-sections"
# The package selects its assembly kernels with these; without them inverse.c
# compiles its C fallbacks and the profile is of a different implementation.
CF="$CF -DNTRUPLUS1152_ASM_BASEMUL_RINV -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH"

REDIR_COMMON="-Dpoly_tobytes=prof_poly_tobytes -Dpoly_frombytes=prof_poly_frombytes \
 -Dpoly_cbd1=prof_poly_cbd1 -Dpoly_sotp_encode=prof_poly_sotp_encode \
 -Dpoly_sotp_decode=prof_poly_sotp_decode -Dpoly_ntt=prof_poly_ntt \
 -Dpoly_baseinv=prof_poly_baseinv -Dpoly_basemul=prof_poly_basemul \
 -Dpoly_basemul_add=prof_poly_basemul_add -Dpoly_sub=prof_poly_sub \
 -Dpoly_triple=prof_poly_triple -Dhash_f=prof_hash_f -Dhash_g=prof_hash_g \
 -Dhash_h=prof_hash_h"
REDIR_GT="$REDIR_COMMON -Dpoly_tobytes_small=prof_poly_tobytes_small \
 -Dpoly_tobytes_compare=prof_poly_tobytes_compare \
 -Dpoly_invntt_ternary=prof_poly_invntt_ternary \
 -Dpoly_basemul_rinv=prof_poly_basemul_rinv -Dhash_g_fr0=prof_hash_g_fr0"
REDIR_OFF="$REDIR_COMMON -Dpoly_invntt_scale=prof_poly_invntt_scale -Dpoly_crepmod3=prof_poly_crepmod3 -Dpoly_basemul_scale=prof_poly_basemul_scale"

# ---- GT ----
GT_C="kem.c symmetric.c fips202.c hash_fixed.c base.c inverse.c pack.c support.c api_glue.c"
GT_S="keccakf1600.S basemul_rinv.S baseinv_num.S baseinv_finish.S ntt.S inverse16_tail.S \
      ntt_top.S ntt_tail.S ntt9.S inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S"
rm -rf build && mkdir -p build/gt build/off
cd build/gt
for f in $GT_C $GT_S; do cp "$GT/$f" .; done
for f in "$GT"/*.h; do cp "$f" .; done
gcc $CF -I. -shared $GT_C $GT_S -o ../../gt.so
cp ../../wrap_gt.c ../../wrap_common.h .
gcc $CF -I. -c $REDIR_GT kem.c -o kem-prof.o
gcc $CF -I. -c wrap_gt.c -o wrap.o
REST=$(echo $GT_C | sed 's/kem\.c//')
gcc $CF -I. -shared -Wl,-Bsymbolic kem-prof.o wrap.o $REST $GT_S -o ../../gt-prof.so
cd ../..

# ---- official ----
cd build/off
for f in "$OFF"/*.c "$OFF"/*.h "$OFF"/*.s; do cp "$f" .; done
cp /home/pi/supercop-20260831/bench/pinhao/include/aarch64/crypto_*.h . 2>/dev/null || true
# The harness supplies randombytes; SUPERCOP normally provides this header.
printf '#ifndef RANDOMBYTES_H\n#define RANDOMBYTES_H\n#include <stddef.h>\n#include <stdint.h>\nvoid randombytes(uint8_t *out, size_t outlen);\n#endif\n' > randombytes.h
sed -i '/#include "crypto_kem.h"/d' kem.c
OFF_C="kem.c symmetric.c fips202.c poly.c"
OFF_S="add.s base.s cbd.s crepmod3.s ntt.s pack.s"
gcc $CF -I. -shared $OFF_C $OFF_S -o ../../off.so
cp ../../wrap_off.c ../../wrap_common.h .
gcc $CF -I. -c $REDIR_OFF kem.c -o kem-prof.o
gcc $CF -I. -c wrap_off.c -o wrap.o
REST=$(echo $OFF_C | sed 's/kem\.c//')
gcc $CF -I. -shared -Wl,-Bsymbolic kem-prof.o wrap.o $REST $OFF_S -o ../../off-prof.so
cd ../..

gcc -O3 -rdynamic -D_DEFAULT_SOURCE harness.c -ldl -o profile_harness
echo "built: gt.so gt-prof.so off.so off-prof.so profile_harness"
