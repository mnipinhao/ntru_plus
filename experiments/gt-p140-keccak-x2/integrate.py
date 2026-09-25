#!/usr/bin/env python3
"""P140 integration: key generation's f and g seeds through one two-state SHAKE256, in the NTRU+768,
NTRU+864 and NTRU+1152 production trees.  usage: integrate.py AARCH64_DIR X2_ASM"""
import sys, shutil, re
A, X2 = sys.argv[1], sys.argv[2]
def edit(path, old, new, count=1):
    t = open(path).read()
    assert t.count(old) >= 1, (path, old[:70])
    open(path, 'w').write(t.replace(old, new, count))

PERMUTE_X2 = '''/*
 * Two states at once, laid out one after the other.  keccakf1600_x2_v84a.S
 * (mlkem-native's x2 FEAT_SHA3 routine) permutes both for about the price of
 * one on cores that implement FEAT_SHA3; elsewhere two single-state calls.
 */
#if defined(__aarch64__) && defined(__ARM_FEATURE_SHA3)
extern void ntruplus_keccak_f1600_x2_v84a_aarch64(uint64_t *state,
                                                  const uint64_t *rc);

static void KeccakF1600_StatePermute_x2(uint64_t *state) {
    ntruplus_keccak_f1600_x2_v84a_aarch64(state, KeccakF_RoundConstants);
}
#else
static void KeccakF1600_StatePermute_x2(uint64_t *state) {
    KeccakF1600_StatePermute(state);
    KeccakF1600_StatePermute(state + 25);
}
#endif

/*************************************************
 * Name:        shake256_x2
 *
 * Description: Two independent SHAKE256(in_k[inlen]) -> out_k[outlen],
 *              inlen < SHAKE256_RATE, permuted together.  The same bytes as
 *              two shake256 calls.
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
DECL = '''/* Two independent one-shot SHAKE256 calls with the same lengths, inlen < 136
 * (one rate block): key generation's f and g seeds.  FEAT_SHA3 builds permute
 * both states in one two-state call. */
void shake256_x2(uint8_t *out0, uint8_t *out1, size_t outlen,
                 const uint8_t *in0, const uint8_t *in1, size_t inlen);

'''
KEYGEN_COMMENT = '''    /*
     * Coins are drawn and consumed in stream order, exactly as one draw per f
     * attempt and then one per g attempt: while f is being tried, the next
     * draw is certain to be used (by an f retry or by g), so it is drawn up
     * front and both seeds are expanded in one two-state SHAKE256.
     * randombytes sees the same calls in the same order.
     */
'''
for s in ('768', '864', '1152'):
    D = f'{A}/NTRU+{s}'
    shutil.copy(X2, f'{D}/keccakf1600_x2_v84a.S')
    # fips202.c / .h
    t = open(f'{D}/fips202.c').read()
    anchor = '/*************************************************\n * Name:        shake256_prefixed'
    assert t.count(anchor) == 1
    open(f'{D}/fips202.c', 'w').write(t.replace(anchor, PERMUTE_X2 + anchor))
    h = open(f'{D}/fips202.h').read()
    m = re.search(r'\nvoid shake256_prefixed\(', h); assert m
    i = h.rindex('\n\n', 0, m.start()) + 2 if '\n\n' in h[:m.start()] else m.start() + 1
    open(f'{D}/fips202.h', 'w').write(h[:i] + DECL + h[i:])
    # kem.c
    k = open(f'{D}/kem.c').read()
    if s == '768':
        for fg in ('f', 'g'):
            old = f'''static inline int gen{fg}_derand(keygen_poly *{fg},
                              keygen_poly *{fg}inv,
                              const uint8_t *coins, uint8_t buf[NTRUPLUS_N / 4])
{{
    int result;

    shake256(buf, NTRUPLUS_N / 4, coins, 32);

'''
            assert old in k, fg
            k = k.replace(old, f'''static inline int gen{fg}_from_seed(keygen_poly *{fg},
                                 keygen_poly *{fg}inv,
                                 const uint8_t buf[NTRUPLUS_N / 4])
{{
    int result;

''')
        a = k.index('int crypto_kem_keypair_internal(uint8_t *pk, uint8_t *sk)\n{')
        b = k.index('    crypto_kem_keypair_derand(pk, sk, &f, &finv, &g, &ginv);', a)
        k = k[:a] + '''int crypto_kem_keypair_internal(uint8_t *pk, uint8_t *sk)
{
''' + KEYGEN_COMMENT + '''    uint8_t coins[2][NTRUPLUS_SYMBYTES];
    uint8_t buf[2][NTRUPLUS_N / 4];
    unsigned cur = 0;

    keygen_poly f, g;
    keygen_poly finv, ginv;

    randombytes(coins[0], sizeof coins[0]);
    randombytes(coins[1], sizeof coins[1]);
    shake256_x2(buf[0], buf[1], NTRUPLUS_N / 4, coins[0], coins[1], 32);

    while (genf_from_seed(&f, &finv, buf[cur])) {
        cur ^= 1;
        randombytes(coins[cur ^ 1], sizeof coins[0]);
        shake256(buf[cur ^ 1], NTRUPLUS_N / 4, coins[cur ^ 1], 32);
    }
    cur ^= 1;
    while (geng_from_seed(&g, &ginv, buf[cur])) {
        randombytes(coins[cur], sizeof coins[0]);
        shake256(buf[cur], NTRUPLUS_N / 4, coins[cur], 32);
    }

''' + k[b:]
    else:
        for fg in ('f', 'g'):
            old = f'static inline int gen{fg}_derand(poly *{fg}, poly *{fg}inv, uint8_t buf[NTRUPLUS_N / 4], const uint8_t *coins)\n{{\n    shake256(buf, NTRUPLUS_N / 4, coins, 32);\n\n'
            assert old in k, (s, fg)
            k = k.replace(old, f'static inline int gen{fg}_from_seed(poly *{fg}, poly *{fg}inv, const uint8_t buf[NTRUPLUS_N / 4])\n{{\n')
        old = k[k.index('int crypto_kem_keypair(uint8_t *pk, uint8_t *sk)\n{'):k.index('    crypto_kem_keypair_derand(pk, sk, &f, &finv, &g, &ginv);')]
        k = k.replace(old, '''int crypto_kem_keypair(uint8_t *pk, uint8_t *sk)
{
''' + KEYGEN_COMMENT + '''    uint8_t coins[2][NTRUPLUS_SYMBYTES];
    /* Fully overwritten by SHAKE, erased on exit. */
    uint8_t buf[2][NTRUPLUS_N / 4];
    unsigned cur = 0;
    int r;

    poly f, finv;
    poly g, ginv;

    randombytes(coins[0], sizeof coins[0]);
    randombytes(coins[1], sizeof coins[1]);
    shake256_x2(buf[0], buf[1], NTRUPLUS_N / 4, coins[0], coins[1], 32);

    for (;;) {
        r = genf_from_seed(&f, &finv, buf[cur]);
        ntruplus_declassify(&r, sizeof r);
        if (!r)
            break;
        cur ^= 1;
        randombytes(coins[cur ^ 1], sizeof coins[0]);
        shake256(buf[cur ^ 1], NTRUPLUS_N / 4, coins[cur ^ 1], 32);
    }
    cur ^= 1;
    for (;;) {
        r = geng_from_seed(&g, &ginv, buf[cur]);
        ntruplus_declassify(&r, sizeof r);
        if (!r)
            break;
        randombytes(coins[cur], sizeof coins[0]);
        shake256(buf[cur], NTRUPLUS_N / 4, coins[cur], 32);
    }

''')
    open(f'{D}/kem.c', 'w').write(k)
    # Makefile
    mk = f'{D}/Makefile'
    if s == '768':
        edit(mk, '\tkeccakf1600_v84a.S \\\n\tkem_api.S', '\tkeccakf1600_v84a.S \\\n\tkeccakf1600_x2_v84a.S \\\n\tkem_api.S')
    elif s == '864':
        edit(mk, '\t$(BUILD_DIR)/keccakf1600_v84a.o', '\t$(BUILD_DIR)/keccakf1600_v84a.o \\\n\t$(BUILD_DIR)/keccakf1600_x2_v84a.o')
    else:
        edit(mk, 'ASM_SRC := keccakf1600.S keccakf1600_v84a.S ', 'ASM_SRC := keccakf1600.S keccakf1600_v84a.S keccakf1600_x2_v84a.S ')
    t = open(mk).read()
    t = re.sub(r'(\$\(TEST_SHAKE_PREFIXED\):[^\n]*\n(?:[^\n]*\\\n)*[^\n]*?)keccakf1600_v84a\.S', r'\1keccakf1600_v84a.S keccakf1600_x2_v84a.S', t) if s != '1152' else \
        t.replace('test/test_shake_prefixed.c fips202.c keccakf1600.S keccakf1600_v84a.S', 'test/test_shake_prefixed.c fips202.c keccakf1600.S keccakf1600_v84a.S keccakf1600_x2_v84a.S')
    open(mk, 'w').write(t)
print('ok')
