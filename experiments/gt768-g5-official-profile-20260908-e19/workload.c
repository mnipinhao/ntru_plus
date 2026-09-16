#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "api.h"
void bench_randombytes_reset(uint32_t seed);
static unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
static unsigned char ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES], ds[CRYPTO_BYTES];
int main(int argc, char **argv) {
    if (argc != 3) return 1;
    const int mode = atoi(argv[1]);
    const unsigned long count = strtoul(argv[2], 0, 10);
    uint64_t sink = 0;
    if (mode < 0 || mode > 2 || !count) return 2;
    bench_randombytes_reset(123);
    if (crypto_kem_keypair(pk, sk) || crypto_kem_enc(ct, ss, pk) ||
        crypto_kem_dec(ds, ct, sk) || memcmp(ss, ds, sizeof ss)) return 3;
    for (unsigned long i = 0; i < count; i++) {
        int rc = mode == 0 ? crypto_kem_keypair(pk, sk) :
                 mode == 1 ? crypto_kem_enc(ct, ss, pk) : crypto_kem_dec(ds, ct, sk);
        if (rc) return 4;
        sink += mode == 0 ? pk[i % sizeof pk] :
                mode == 1 ? ct[i % sizeof ct] : ds[i % sizeof ds];
    }
    printf("mode=%d operations=%lu sink=%llu\n",mode,count,(unsigned long long)sink);
    return 0;
}
