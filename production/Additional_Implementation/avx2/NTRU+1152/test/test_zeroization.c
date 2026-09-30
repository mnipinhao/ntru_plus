/*
 * Runtime audit of the C clears (Official policy, docs/IMPLEMENTATION.md
 * section 8): every secure_clear() call reports its buffer through the audit
 * hook, which counts calls and bytes per operation and checks that the buffer
 * really is zero afterwards.  Covered: keypair, enc and dec, and the failure
 * paths enc with a non-canonical pk, dec with a non-canonical ct, and dec of a
 * tampered (canonical) ct.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "params.h"

void ntruplus1152_avx2opt_secure_clear_audit_hook(const void *p, size_t n);

static size_t calls, bytes, nonzero;

void ntruplus1152_avx2opt_secure_clear_audit_hook(const void *p, size_t n)
{
    const volatile uint8_t *x = p;

    calls++;
    bytes += n;
    while (n--)
        nonzero += *x++ != 0;
}

/* Coefficient i of a 12-bit packed polynomial (the encoding of pk, ct and sk). */
static uint16_t get_coeff(const uint8_t *x, size_t i)
{
    size_t o = 3 * (i / 2);

    return (i & 1) ? (uint16_t)((x[o + 1] >> 4) | (x[o + 2] << 4))
                   : (uint16_t)(x[o] | ((x[o + 1] & 0x0f) << 8));
}

static void set_coeff(uint8_t *x, size_t i, uint16_t v)
{
    size_t o = 3 * (i / 2);

    if (!(i & 1)) {
        x[o] = (uint8_t)v;
        x[o + 1] = (uint8_t)((x[o + 1] & 0xf0) | (v >> 8));
    } else {
        x[o + 1] = (uint8_t)((x[o + 1] & 0x0f) | ((v & 15) << 4));
        x[o + 2] = (uint8_t)(v >> 4);
    }
}

static int zero(const uint8_t *x, size_t n)
{
    uint8_t a = 0;

    while (n--)
        a |= *x++;
    return a == 0;
}

static int report(const char *op, size_t min_calls, size_t min_bytes)
{
    int bad = nonzero != 0 || calls < min_calls || bytes < min_bytes;

    printf("%-8s clear_calls=%zu clear_bytes=%zu nonzero_after=%zu%s\n", op, calls, bytes,
           nonzero, bad ? "  FAIL" : "");
    calls = bytes = nonzero = 0;
    return bad;
}

int main(void)
{
    uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES], ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t xpk[CRYPTO_PUBLICKEYBYTES], xct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t a[CRYPTO_BYTES], b[CRYPTO_BYTES];
    const size_t poly = 2 * NTRUPLUS_N;
    int bad = 0;

    /* keypair: h, coins, buf, f, finv, g, ginv + den of each inversion */
    if (crypto_kem_keypair(pk, sk))
        return 1;
    bad |= report("keypair", 9, 5 * poly + 32 + NTRUPLUS_N / 4);
    /* enc: msg, buf, r, m, coins + hash_g and hash_h inputs */
    if (crypto_kem_enc(ct, a, pk))
        return 1;
    bad |= report("enc", 7, 2 * poly);
    /* dec: msg, buf1..3, c, f, hinv, m + hash_g and hash_h inputs */
    if (crypto_kem_dec(b, ct, sk) || memcmp(a, b, sizeof a))
        return 1;
    bad |= report("dec", 10, 4 * poly);

    /* enc, non-canonical pk: ss and coins are cleared, ct and ss are all zero */
    memcpy(xpk, pk, sizeof xpk);
    set_coeff(xpk, 0, NTRUPLUS_Q);
    memset(xct, 0xa5, sizeof xct);
    memset(b, 0xa5, sizeof b);
    bad |= crypto_kem_enc(xct, b, xpk) != 1 || !zero(xct, sizeof xct) || !zero(b, sizeof b);
    bad |= report("enc-pk", 2, CRYPTO_BYTES + NTRUPLUS_N / 8);
    /* dec, non-canonical ct: ss and every dec buffer are cleared, ss is zero */
    memcpy(xct, ct, sizeof xct);
    set_coeff(xct, 0, NTRUPLUS_Q);
    memset(b, 0xa5, sizeof b);
    bad |= crypto_kem_dec(b, xct, sk) != 1 || !zero(b, sizeof b);
    bad |= report("dec-ct", 9, CRYPTO_BYTES + 4 * poly);
    /* dec, tampered canonical ct (explicit rejection): the dec clears, ss is zero */
    memcpy(xct, ct, sizeof xct);
    set_coeff(xct, 0, (uint16_t)((get_coeff(xct, 0) + 1) % NTRUPLUS_Q));
    memset(b, 0xa5, sizeof b);
    bad |= crypto_kem_dec(b, xct, sk) != 1 || !zero(b, sizeof b);
    bad |= report("dec-rej", 10, 4 * poly);
    return bad;
}
