#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"

static size_t clear_calls;
static size_t clear_bytes;
static size_t nonzero_after_clear;
static size_t saw_keygen_large;
static size_t saw_fips_state;
static size_t saw_domain_image;

void gt_secure_clear_audit_hook(const void *address, size_t length)
{
    const volatile uint8_t *bytes = address;
    size_t i;

    clear_calls++;
    clear_bytes += length;
    if (length == 1536 || length == 384)
        saw_keygen_large++;
    if (length == 200 || length == 208)
        saw_fips_state++;
    if (length == 1153 || length == 129)
        saw_domain_image++;
    for (i = 0; i < length; i++)
        nonzero_after_clear += (bytes[i] != 0);
}

int main(void)
{
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss_enc[CRYPTO_BYTES];
    uint8_t ss_dec[CRYPTO_BYTES];

    if (crypto_kem_keypair(pk, sk) != 0 ||
        crypto_kem_enc(ct, ss_enc, pk) != 0 ||
        crypto_kem_dec(ss_dec, ct, sk) != 0 ||
        memcmp(ss_enc, ss_dec, sizeof ss_enc) != 0) {
        fputs("P0 zeroization harness: KEM failure\n", stderr);
        return 1;
    }
    printf("clear_calls=%zu,clear_bytes=%zu,nonzero_after_clear=%zu,"
           "keygen_large=%zu,fips_state=%zu,domain_image=%zu\n",
           clear_calls, clear_bytes, nonzero_after_clear,
           saw_keygen_large, saw_fips_state, saw_domain_image);
    if (nonzero_after_clear != 0 || saw_keygen_large < 2 ||
        saw_fips_state == 0 || saw_domain_image == 0) {
        fputs("P0 zeroization harness: incomplete clear coverage\n", stderr);
        return 1;
    }
    puts("Official-aligned explicit C zeroization: ok");
    return 0;
}
