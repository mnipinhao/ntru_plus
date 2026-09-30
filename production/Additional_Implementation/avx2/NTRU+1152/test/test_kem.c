/* KEM round trips and tampered-ciphertext rejection (test_canonical.c covers
 * the non-canonical key and ciphertext encodings). */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"

#define TEST_ROUNDS 100

static int all_zero(const unsigned char *x, size_t n)
{
    unsigned char acc = 0;

    while (n--)
        acc |= *x++;
    return acc == 0;
}

int main(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES], ss_enc[CRYPTO_BYTES], ss_dec[CRYPTO_BYTES];
    int round;

    for (round = 0; round < TEST_ROUNDS; round++) {
        if (crypto_kem_keypair(pk, sk) != 0) {
            fprintf(stderr, "keypair failed at round %d\n", round);
            return 1;
        }
        if (crypto_kem_enc(ct, ss_enc, pk) != 0) {
            fprintf(stderr, "encapsulation failed at round %d\n", round);
            return 1;
        }
        if (crypto_kem_dec(ss_dec, ct, sk) != 0 ||
            memcmp(ss_enc, ss_dec, CRYPTO_BYTES) != 0) {
            fprintf(stderr, "decapsulation mismatch at round %d\n", round);
            return 1;
        }
        /* Flip one bit: decapsulation must reject (return 1, all-zero key). */
        ct[(size_t)round * 7 % CRYPTO_CIPHERTEXTBYTES] ^= (unsigned char)(1u << (round % 8));
        memset(ss_dec, 0xa5, sizeof ss_dec);
        if (crypto_kem_dec(ss_dec, ct, sk) != 1 || !all_zero(ss_dec, sizeof ss_dec)) {
            fprintf(stderr, "tampered ciphertext accepted at round %d\n", round);
            return 1;
        }
    }

    printf("%s avx2-opt: %d KEM round trips and tampered-ciphertext rejections passed\n",
           CRYPTO_ALGNAME, TEST_ROUNDS);
    return 0;
}
