/*
 * NTRU+864 AVX2 candidate avx2-officialopt-lazy-codec-864-exp002: the
 * qualified caller-lazy KEM (generated src/kem_lazy.c, 6 poly_ntt call sites
 * -> ntruplus864_officialopt_ntt_caller_lazy) with its poly_tobytes /
 * poly_frombytes calls bound to the direct 12-bit codec
 * (asm/ntruplus864_officialopt_codec_direct.s).  Hand-written preprocessor
 * overlay; kem_lazy.c itself is unchanged, so the lazy-only and exp001
 * candidates stay intact and all can be linked into one ELF.
 */
#define poly_tobytes ntruplus864_officialopt_tobytes_direct
#define poly_frombytes ntruplus864_officialopt_frombytes_direct
#include "kem_lazy.c"
