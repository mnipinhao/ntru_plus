#include "api.h"
#include <stdio.h>
#include <string.h>
int main(void) {
    unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES], got[CRYPTO_BYTES];
    for (unsigned i = 0; i < 64; ++i) {
        if (crypto_kem_keypair(pk, sk) || crypto_kem_enc(ct, ss, pk) ||
            crypto_kem_dec(got, ct, sk) || memcmp(ss, got, sizeof ss)) return 1;
        ct[i % sizeof ct] ^= 1;
        crypto_kem_dec(got, ct, sk);
        if (!memcmp(ss, got, sizeof ss)) return 2;
    }
    puts("PASS: 64 KEM round trips and tampered ciphertext rejection");
    return 0;
}
