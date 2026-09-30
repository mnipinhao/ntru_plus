/*
 * SHAKE256 and the prefixed hashes against an independent reference.
 *
 * The package hashes with mlkem-native's x1 Keccak (fips202.c).  This test
 * compares it with a small textbook Keccak-f[1600]/SHAKE256 written here from
 * FIPS 202, on FIPS 202 known answers and on every input length 0..700 (all
 * rate-boundary cases) with several output lengths, and checks that
 * hash_f/g/h(buf, msg) = SHAKE256(0x00/0x01/0x02 || msg) with the KEM's input
 * and output lengths.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "fips202.h"
#include "params.h"
#include "symmetric.h"

static const uint64_t rc[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808aULL, 0x8000000080008000ULL,
    0x000000000000808bULL, 0x0000000080000001ULL, 0x8000000080008081ULL, 0x8000000000008009ULL,
    0x000000000000008aULL, 0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000aULL,
    0x000000008000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL, 0x8000000000008003ULL,
    0x8000000000008002ULL, 0x8000000000000080ULL, 0x000000000000800aULL, 0x800000008000000aULL,
    0x8000000080008081ULL, 0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL};
static const unsigned rot[25] = {0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43,
                                 25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14};

static uint64_t rol(uint64_t x, unsigned r) { return r ? (x << r) | (x >> (64 - r)) : x; }

/* State index x + 5y, FIPS 202 section 3.2. */
static void ref_keccakf(uint64_t a[25])
{
    for (int round = 0; round < 24; round++) {
        uint64_t c[5], b[25];
        for (int x = 0; x < 5; x++)
            c[x] = a[x] ^ a[x + 5] ^ a[x + 10] ^ a[x + 15] ^ a[x + 20];
        for (int x = 0; x < 5; x++)
            for (int y = 0; y < 5; y++)
                a[x + 5 * y] ^= c[(x + 4) % 5] ^ rol(c[(x + 1) % 5], 1);
        for (int x = 0; x < 5; x++)
            for (int y = 0; y < 5; y++)
                b[y + 5 * ((2 * x + 3 * y) % 5)] = rol(a[x + 5 * y], rot[x + 5 * y]);
        for (int x = 0; x < 5; x++)
            for (int y = 0; y < 5; y++)
                a[x + 5 * y] = b[x + 5 * y] ^ (~b[(x + 1) % 5 + 5 * y] & b[(x + 2) % 5 + 5 * y]);
        a[0] ^= rc[round];
    }
}

static void ref_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen)
{
    enum { RATE = 136 };
    uint64_t s[25] = {0};
    uint8_t block[RATE];

    while (inlen >= RATE) {
        for (int i = 0; i < RATE; i++)
            s[i / 8] ^= (uint64_t)in[i] << (8 * (i % 8));
        ref_keccakf(s);
        in += RATE;
        inlen -= RATE;
    }
    memset(block, 0, sizeof block);
    memcpy(block, in, inlen);
    block[inlen] ^= 0x1f;
    block[RATE - 1] ^= 0x80;
    for (int i = 0; i < RATE; i++)
        s[i / 8] ^= (uint64_t)block[i] << (8 * (i % 8));
    for (;;) {
        ref_keccakf(s);
        for (size_t i = 0; i < RATE && outlen; i++, outlen--)
            *out++ = (uint8_t)(s[i / 8] >> (8 * (i % 8)));
        if (!outlen)
            break;
    }
}

static uint64_t prng = 0x9e3779b97f4a7c15ULL;
static uint8_t next_byte(void)
{
    prng ^= prng << 13;
    prng ^= prng >> 7;
    prng ^= prng << 17;
    return (uint8_t)prng;
}

static int check_hash(const char *name, void (*h)(uint8_t *, const uint8_t *), uint8_t prefix,
                      size_t inlen, size_t outlen)
{
    uint8_t msg[1 + NTRUPLUS_POLYBYTES], got[512], want[512];

    for (int t = 0; t < 64; t++) {
        msg[0] = prefix;
        for (size_t i = 0; i < inlen; i++)
            msg[1 + i] = next_byte();
        h(got, msg + 1);
        ref_shake256(want, outlen, msg, inlen + 1);
        if (memcmp(got, want, outlen)) {
            printf("%s mismatch (trial %d)\n", name, t);
            return 1;
        }
    }
    return 0;
}

int main(void)
{
    static const uint8_t kat_empty[32] = {
        0x46, 0xb9, 0xdd, 0x2b, 0x0b, 0xa8, 0x8d, 0x13, 0x23, 0x3b, 0x3f, 0xeb, 0x74, 0x3e, 0xeb, 0x24,
        0x3f, 0xcd, 0x52, 0xea, 0x62, 0xb8, 0x1b, 0x82, 0xb5, 0x0c, 0x27, 0x64, 0x6e, 0xd5, 0x76, 0x2f};
    static const uint8_t kat_abc[32] = {
        0x48, 0x33, 0x66, 0x60, 0x13, 0x60, 0xa8, 0x77, 0x1c, 0x68, 0x63, 0x08, 0x0c, 0xc4, 0x11, 0x4d,
        0x8d, 0xb4, 0x45, 0x30, 0xf8, 0xf1, 0xe1, 0xee, 0x4f, 0x94, 0xea, 0x37, 0xe7, 0x8b, 0x57, 0x39};
    static const size_t outlens[] = {0, 1, 31, 32, 135, 136, 137, 192, 272, 300};
    uint8_t in[700], got[300], want[300];
    unsigned cases = 0;
    int bad = 0;

    mlk_shake256(got, 32, (const uint8_t *)"", 0);
    ref_shake256(want, 32, (const uint8_t *)"", 0);
    bad |= memcmp(got, kat_empty, 32) != 0 || memcmp(want, kat_empty, 32) != 0;
    mlk_shake256(got, 32, (const uint8_t *)"abc", 3);
    ref_shake256(want, 32, (const uint8_t *)"abc", 3);
    bad |= memcmp(got, kat_abc, 32) != 0 || memcmp(want, kat_abc, 32) != 0;
    if (bad) {
        printf("SHAKE256 known-answer test failed\n");
        return 1;
    }
    for (size_t inlen = 0; inlen <= sizeof in; inlen++) {
        for (size_t i = 0; i < inlen; i++)
            in[i] = next_byte();
        for (size_t k = 0; k < sizeof outlens / sizeof outlens[0]; k++) {
            mlk_shake256(got, outlens[k], in, inlen);
            ref_shake256(want, outlens[k], in, inlen);
            if (memcmp(got, want, outlens[k])) {
                printf("SHAKE256 mismatch inlen=%zu outlen=%zu\n", inlen, outlens[k]);
                return 1;
            }
            cases++;
        }
    }
    bad |= check_hash("hash_f", hash_f, 0x00, HASH_F_INBYTES, HASH_F_OUTBYTES);
    bad |= check_hash("hash_g", hash_g, 0x01, HASH_G_INBYTES, HASH_G_OUTBYTES);
    bad |= check_hash("hash_h", hash_h, 0x02, HASH_H_INBYTES, HASH_H_OUTBYTES);
    if (bad)
        return 1;
    printf("shake-prefixed: 2 FIPS 202 answers, %u SHAKE256 lengths, 3 x 64 hash_f/g/h "
           "prefixed inputs match the reference\n", cases);
    return 0;
}
