#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"

#define TEST_ROUNDS 100

int main(void)
{
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss_enc[CRYPTO_BYTES];
    uint8_t ss_dec[CRYPTO_BYTES];
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
        if (crypto_kem_dec(ss_dec, ct, sk) != 0) {
            fprintf(stderr, "decapsulation failed at round %d\n", round);
            return 1;
        }
        if (memcmp(ss_enc, ss_dec, CRYPTO_BYTES) != 0) {
            fprintf(stderr, "shared-secret mismatch at round %d\n", round);
            return 1;
        }
    }

    printf("NTRU+768 GT-Optimized: %d KEM round trips passed\n",
           TEST_ROUNDS);
    return 0;
}
