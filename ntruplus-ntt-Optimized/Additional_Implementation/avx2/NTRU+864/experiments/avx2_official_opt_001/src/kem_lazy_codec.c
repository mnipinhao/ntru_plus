/*
 * NTRU+864 AVX2 candidate avx2-officialopt-lazy-codec-864-exp001: the
 * qualified caller-lazy KEM (generated src/kem_lazy.c, 6 poly_ntt call sites
 * -> ntruplus864_officialopt_ntt_caller_lazy) with its poly_tobytes /
 * poly_frombytes calls bound to the layout-fused codec
 * (asm/ntruplus864_officialopt_codec_fused.s).  Hand-written preprocessor
 * overlay; kem_lazy.c itself is unchanged, so the lazy-only candidate stays
 * intact and both can be linked into one ELF.
 */
#define poly_tobytes ntruplus864_officialopt_tobytes_fused
#define poly_frombytes ntruplus864_officialopt_frombytes_fused
#include "kem_lazy.c"
