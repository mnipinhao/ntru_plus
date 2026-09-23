/*
 * Freeze-only control: tests/test_codec_fused.c (unchanged) with tobytes bound
 * to ntruplus864_officialopt_tobytes_fused_min (exp001 + 2-op freeze,
 * asm/ntruplus864_officialopt_codec_fused_min.s); frombytes stays exp001's.
 */
#include <stdio.h>
#define ntruplus864_officialopt_tobytes_fused ntruplus864_officialopt_tobytes_fused_min
__attribute__((constructor)) static void banner(void) {
    puts("kernels under test: ntruplus864_officialopt_tobytes_fused_min + exp001 frombytes_fused");
}
#include "test_codec_fused.c"
