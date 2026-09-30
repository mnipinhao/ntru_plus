#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "api.h"
static size_t calls, bytes, nonzero;
void gt_secure_clear_audit_hook(const void *p, size_t n) {
    const volatile uint8_t *x=p; calls++; bytes+=n; while(n--) nonzero += *x++ != 0;
}
int main(void) {
    uint8_t pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES],ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t a[CRYPTO_BYTES],b[CRYPTO_BYTES];
    if (crypto_kem_keypair(pk,sk)||crypto_kem_enc(ct,a,pk)||crypto_kem_dec(b,ct,sk)||memcmp(a,b,sizeof a)) return 1;
    printf("clear_calls=%zu clear_bytes=%zu nonzero_after=%zu\n",calls,bytes,nonzero);
    return nonzero != 0 || calls < 20 || bytes < 10000;
}
