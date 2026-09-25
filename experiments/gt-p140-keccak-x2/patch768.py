#!/usr/bin/env python3
"""P140 prototype on an NTRU+768 tree: the f and g CBD seeds through one two-state SHAKE256.
  fips202.c/.h  shake256_x2(out0, out1, outlen, in0, in1, inlen) for inlen < 136: FEAT_SHA3 runs
                both states through keccakf1600_x2_v84a.S (mlkem-native's x2), else two x1 calls.
  kem.c         the key pair draws the next 32 coins before trying f, and expands both seeds at
                once; coins are consumed in stream order whichever of f or g takes them, and a draw
                happens only when it is certain to be used, so randombytes sees the same calls in
                the same order (KAT unchanged).
  Makefile      keccakf1600_x2_v84a.S
usage: patch768.py TREE"""
import sys, re
T = sys.argv[1]
def sub(path, old, new, count=1):
    t = open(f'{T}/{path}').read(); assert t.count(old) >= 1, (path, old[:60]); open(f'{T}/{path}', 'w').write(t.replace(old, new, count))
# Makefile
sub('Makefile', '\tkeccakf1600_v84a.S \\\n', '\tkeccakf1600_v84a.S \\\n\tkeccakf1600_x2_v84a.S \\\n')
# fips202.h
sub('fips202.h', 'void shake256_absorb(shake256ctx *state, const uint8_t *input, size_t inlen);',
'''/* Two independent one-shot SHAKE256 calls with the same lengths, inlen < 136
 * (one rate block).  FEAT_SHA3 builds permute both states in one two-state
 * call; other builds make two single-state calls. */
void shake256_x2(uint8_t *out0, uint8_t *out1, size_t outlen,
                 const uint8_t *in0, const uint8_t *in1, size_t inlen);

void shake256_absorb(shake256ctx *state, const uint8_t *input, size_t inlen);''')
# fips202.c: after the permutation selection block
sub('fips202.c', '''static void KeccakF1600_StatePermute(uint64_t *state) {
    ntruplus_keccak_f1600_x1_v84a_aarch64(state,''', '''extern void ntruplus_keccak_f1600_x2_v84a_aarch64(
    uint64_t *state, const uint64_t *rc);

static void KeccakF1600_StatePermute_x2(uint64_t *state) {
    ntruplus_keccak_f1600_x2_v84a_aarch64(state, KeccakF_RoundConstants);
}

static void KeccakF1600_StatePermute(uint64_t *state) {
    ntruplus_keccak_f1600_x1_v84a_aarch64(state,''')
sub('fips202.c', '''static void KeccakF1600_StatePermute(uint64_t *state) {
    ntruplus_keccak_f1600_x1_aarch64(state, KeccakF_RoundConstants);
}''', '''static void KeccakF1600_StatePermute(uint64_t *state) {
    ntruplus_keccak_f1600_x1_aarch64(state, KeccakF_RoundConstants);
}

static void KeccakF1600_StatePermute_x2(uint64_t *state) {
    KeccakF1600_StatePermute(state);
    KeccakF1600_StatePermute(state + 25);
}''')
t = open(f'{T}/fips202.c').read()
i = t.index('void shake256_prefixed(uint8_t *output, size_t outlen, uint8_t domain,')
i = t.rindex('/*************************************************', 0, i)
x2 = '''/*************************************************
 * Name:        shake256_x2
 *
 * Description: Two independent SHAKE256(in_i[inlen]) -> out_i[outlen], for
 *              inlen < SHAKE256_RATE, permuted together (two states laid out
 *              one after the other, as the two-state permutation takes them).
 **************************************************/
void shake256_x2(uint8_t *out0, uint8_t *out1, size_t outlen,
                 const uint8_t *in0, const uint8_t *in1, size_t inlen) {
    uint64_t s[50];
    uint8_t t[SHAKE256_RATE];
    size_t i, k;

    for (i = 0; i < 50; ++i) {
        s[i] = 0;
    }
    for (k = 0; k < 2; ++k) {
        for (i = 0; i < SHAKE256_RATE; ++i) {
            t[i] = 0;
        }
        memcpy(t, k ? in1 : in0, inlen);
        t[inlen] ^= 0x1F;
        t[SHAKE256_RATE - 1] ^= 0x80;
        for (i = 0; i < SHAKE256_RATE / 8; ++i) {
            s[25 * k + i] ^= load64(t + 8 * i);
        }
    }
    while (outlen > 0) {
        size_t n = outlen < SHAKE256_RATE ? outlen : SHAKE256_RATE;

        KeccakF1600_StatePermute_x2(s);
        for (k = 0; k < 2; ++k) {
            uint8_t *o = k ? out1 : out0;
            for (i = 0; i + 8 <= n; i += 8) {
                store64(o + i, s[25 * k + i / 8]);
            }
            for (; i < n; ++i) {
                o[i] = (uint8_t)(s[25 * k + i / 8] >> (8 * (i % 8)));
            }
        }
        out0 += n;
        out1 += n;
        outlen -= n;
    }
    secure_clear(s, sizeof s);
    secure_clear(t, sizeof t);
}

'''
open(f'{T}/fips202.c', 'w').write(t[:i] + x2 + t[i:])
# kem.c: seeds expanded by the caller
for fg in ('f', 'g'):
    sub('kem.c', f'''static inline int gen{fg}_derand(keygen_poly *{fg},
                              keygen_poly *{fg}inv,
                              const uint8_t *coins, uint8_t buf[NTRUPLUS_N / 4])
{{
    int result;

    shake256(buf, NTRUPLUS_N / 4, coins, 32);

''', f'''static inline int gen{fg}_from_seed(keygen_poly *{fg},
                                 keygen_poly *{fg}inv,
                                 const uint8_t buf[NTRUPLUS_N / 4])
{{
    int result;

''')
old = t2 = open(f'{T}/kem.c').read()
a = t2.index('int crypto_kem_keypair_internal(uint8_t *pk, uint8_t *sk)\n{')
b = t2.index('    crypto_kem_keypair_derand(pk, sk, &f, &finv, &g, &ginv);', a)
new = '''int crypto_kem_keypair_internal(uint8_t *pk, uint8_t *sk)
{
    /*
     * Coins are drawn and consumed in stream order, as a loop drawing 32
     * bytes per f attempt and then per g attempt would: while f is being
     * tried, the next draw is certain to be used (by an f retry or by g), so
     * it is drawn up front and both seeds are expanded in one two-state
     * SHAKE256.  randombytes sees the same calls in the same order.
     */
    uint8_t coins[2][NTRUPLUS_SYMBYTES];
    uint8_t buf[2][NTRUPLUS_N / 4];
    unsigned cur = 0;

    keygen_poly f, g;
    keygen_poly finv, ginv;

    randombytes(coins[0], sizeof coins[0]);
    randombytes(coins[1], sizeof coins[1]);
    shake256_x2(buf[0], buf[1], NTRUPLUS_N / 4, coins[0], coins[1], 32);

    while (genf_from_seed(&f, &finv, buf[cur])) {
        /* the drawn-ahead seed is the next f attempt; the draw after it is
         * again certain to be used */
        cur ^= 1;
        randombytes(coins[cur ^ 1], sizeof coins[0]);
        shake256(buf[cur ^ 1], NTRUPLUS_N / 4, coins[cur ^ 1], 32);
    }
    cur ^= 1;
    while (geng_from_seed(&g, &ginv, buf[cur])) {
        randombytes(coins[cur], sizeof coins[0]);
        shake256(buf[cur], NTRUPLUS_N / 4, coins[cur], 32);
    }

'''
t2 = t2[:a] + new + t2[b:]
open(f'{T}/kem.c', 'w').write(t2)
