/*
 * NTRU+864 AVX2 codec-only KEM variant (diagnostic control): the pinned
 * Official kem.c, unmodified, with its poly_tobytes / poly_frombytes calls
 * bound to the layout-fused codec (asm/ntruplus864_officialopt_codec_fused.s).
 * Hand-written preprocessor overlay; no line of kem.c is copied or edited.
 * Official Forward (poly_ntt) is kept, so this isolates the codec effect.
 */
#define poly_tobytes ntruplus864_officialopt_tobytes_fused
#define poly_frombytes ntruplus864_officialopt_frombytes_fused
#include "../upstream/supercop-avx2/kem.c"
