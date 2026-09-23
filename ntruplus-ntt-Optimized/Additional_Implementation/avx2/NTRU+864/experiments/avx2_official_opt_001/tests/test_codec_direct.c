/*
 * exp002 codec differential: tests/test_codec_fused.c (unchanged) with the
 * kernel under test bound to the direct 12-bit codec
 * (asm/ntruplus864_officialopt_codec_direct.s).  Same cases, same checks:
 * vs Official poly_tobytes / poly_frombytes in the same ELF and the
 * independent scalar wire model, canaries, immutability, misalignments.
 */
#include <stdio.h>
#define ntruplus864_officialopt_tobytes_fused ntruplus864_officialopt_tobytes_direct
#define ntruplus864_officialopt_frombytes_fused ntruplus864_officialopt_frombytes_direct
__attribute__((constructor)) static void banner(void) {
    puts("kernels under test: ntruplus864_officialopt_{tobytes,frombytes}_direct (exp002)");
}
#include "test_codec_fused.c"
