/*
 * NTRU+864 AVX2 direct-codec-only KEM variant (diagnostic control): the pinned
 * Official kem.c, unmodified, with its poly_tobytes / poly_frombytes calls
 * bound to the direct 12-bit codec (asm/ntruplus864_officialopt_codec_direct.s).
 * Hand-written preprocessor overlay; Official Forward (poly_ntt) is kept.
 */
#define poly_tobytes ntruplus864_officialopt_tobytes_direct
#define poly_frombytes ntruplus864_officialopt_frombytes_direct
#include "../upstream/supercop-avx2/kem.c"
