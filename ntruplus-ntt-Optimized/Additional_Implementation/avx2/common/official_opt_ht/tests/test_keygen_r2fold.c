/*
 * Keygen R^2-fold differential (NTRU+768 / 864 / 1152 AVX2; parameter from params.h).
 *
 * Component part (real linked code, Official vs fold):
 *   finv' = ntruplusN_officialopt_baseinv_r2fold(f_hat)  vs  finv = poly_baseinv(f_hat)
 *     same status; on success finv' == R * finv (mod q) in every lane, R = 2^16,
 *     |finv'| <= 18112 (any fqmul output of int16 operands);
 *   h' = ntruplusN_officialopt_basemul_nor2(g_hat, finv')  vs  h = poly_basemul(g_hat, finv)
 *     h' == h (mod q) in every lane, h' inside the proven interval (range_proof_ht:
 *     768 [-10446, 10448], 864 [-8936, 8936], 1152 [-11250, 11250]),
 *     poly_tobytes(h') == poly_tobytes(h) byte for byte.
 *   Inputs: KEYGEN_SEEDS keygen f/g pairs (Official SHAKE256 -> cbd1 -> triple (+1)
 *   -> caller-lazy Forward), RANDOM_INV uniform int16 polynomials and
 *   ZERO_BASE polynomials with one all-zero base (degree 4 for 768/1152, 3 for 864;
 *   forced failure).
 * KEM part: KEYPAIR_SEEDS KAT-DRBG seeds, Official kem.c (v0) vs the R^2-fold
 *   KEMs v1 = kem_lazy_r2fold.c, v2 = r2fold_only control, v3 = candidate
 *   (768: + HT Forward + HT inverse; 864/1152: + HT Forward):
 *   pk/sk byte-exact and equal randombytes consumption; every 97th seed forces
 *   g = 0 (second keygen SHAKE256 output zeroed: genuine BaseInv failure and
 *   retry), every 89th seed forces a one-shot f BaseInv failure (poisoned output).
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"
#include "fips202.h"
#include "kat/rng.h"

#ifndef FWD_NTT
#error "define FWD_NTT"
#endif
void FWD_NTT(poly *);
/* Per-parameter names, proven nor2 output interval and BaseInv base layout
 * (poly_baseinv_2: chunk i of BASE_WORDS words, rows c = 0..BASE_ROWS-1, lane j). */
#if NTRUPLUS_N == 768
#define R2INV_FN ntruplus768_officialopt_baseinv_r2fold
#define REAL_R2INV_FN __real_ntruplus768_officialopt_baseinv_r2fold
#define WRAP_R2INV_FN __wrap_ntruplus768_officialopt_baseinv_r2fold
#define NOR2_FN ntruplus768_officialopt_basemul_nor2
#define NOR2_LO -10446
#define NOR2_HI 10448
#define BASE_WORDS 64U
#define BASE_ROWS 4
#elif NTRUPLUS_N == 864
#define R2INV_FN ntruplus864_officialopt_baseinv_r2fold
#define REAL_R2INV_FN __real_ntruplus864_officialopt_baseinv_r2fold
#define WRAP_R2INV_FN __wrap_ntruplus864_officialopt_baseinv_r2fold
#define NOR2_FN ntruplus864_officialopt_basemul_nor2
#define NOR2_LO -8936
#define NOR2_HI 8936
#define BASE_WORDS 48U
#define BASE_ROWS 3
#elif NTRUPLUS_N == 1152
#define R2INV_FN ntruplus1152_officialopt_baseinv_r2fold
#define REAL_R2INV_FN __real_ntruplus1152_officialopt_baseinv_r2fold
#define WRAP_R2INV_FN __wrap_ntruplus1152_officialopt_baseinv_r2fold
#define NOR2_FN ntruplus1152_officialopt_basemul_nor2
#define NOR2_LO -11250
#define NOR2_HI 11250
#define BASE_WORDS 64U
#define BASE_ROWS 4
#else
#error "unsupported NTRUPLUS_N"
#endif
int R2INV_FN(poly *, const poly *);
void NOR2_FN(poly *, const poly *, const poly *);

#define DECL(v)                                                          \
    int v##_keypair(unsigned char *, unsigned char *);
DECL(v0)
DECL(v1)
DECL(v2)
DECL(v3)
static int (*const keypair[4])(unsigned char *, unsigned char *) = {v0_keypair, v1_keypair,
                                                                    v2_keypair, v3_keypair};
static const char *const vname[4] = {"official", "lazy_r2fold", "r2fold_only", "candidate"};

enum { KEYGEN_SEEDS = 12000, RANDOM_INV = 4000, ZERO_BASE = 2000, KEYPAIR_SEEDS = 10000 };
#define RMOD ((1 << 16) % NTRUPLUS_Q)

/* ---------------------------------------------------------------- injection wraps */
static int force_g, force_f;
static unsigned shake_calls, injected_g, injected_f;
static unsigned long long random_calls;
static unsigned baseinv_fail[4], cur_variant;

static int zero_g(uint8_t *out, size_t outlen, size_t inlen) {
    if (force_g && outlen == NTRUPLUS_N / 4 && inlen == 32 && ++shake_calls == 2) {
        memset(out, 0, outlen);
        injected_g++;
        return 1;
    }
    return 0;
}
void __real_fips202avx_shake256(uint8_t *, size_t, const uint8_t *, size_t);
void __wrap_fips202avx_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen) {
    if (!zero_g(out, outlen, inlen)) __real_fips202avx_shake256(out, outlen, in, inlen);
}
void __real_ntruplus_mlkfips202_shake256(uint8_t *, size_t, const uint8_t *, size_t);
void __wrap_ntruplus_mlkfips202_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen) {
    if (!zero_g(out, outlen, inlen)) __real_ntruplus_mlkfips202_shake256(out, outlen, in, inlen);
}
static int inject_f(poly *out) {
    if (force_f) {
        force_f = 0;
        injected_f++;
        memset(out, 0xa5, sizeof *out);
        return 1;
    }
    return 0;
}
int __real_poly_baseinv(poly *, const poly *);
int __wrap_poly_baseinv(poly *out, const poly *in) {
    if (inject_f(out)) return 1;
    int s = __real_poly_baseinv(out, in);
    baseinv_fail[cur_variant] += (unsigned)s;
    return s;
}
int REAL_R2INV_FN(poly *, const poly *);
int WRAP_R2INV_FN(poly *out, const poly *in) {
    if (inject_f(out)) return 1;
    int s = REAL_R2INV_FN(out, in);
    baseinv_fail[cur_variant] += (unsigned)s;
    return s;
}
void __real_randombytes(unsigned char *, unsigned long long);
void __wrap_randombytes(unsigned char *out, unsigned long long len) {
    random_calls++;
    __real_randombytes(out, len);
}

/* ---------------------------------------------------------------- helpers */
static uint64_t state = UINT64_C(0x2f0ab5c3e1d49768);
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}
static int mod_eq(int a, int b) { return (a - b) % NTRUPLUS_Q == 0; }

static unsigned long inv_ok, inv_fail, mul_checked;
static int inv_lo, inv_hi, h_lo, h_hi;

/* Official vs fold BaseInv on a; on success returns 1 and leaves both inverses. */
static int check_inv(const poly *a, poly *finv, poly *finv2, const char *what, unsigned t) {
    int so = __real_poly_baseinv(finv, a);
    int sf = REAL_R2INV_FN(finv2, a);
    if (so != sf) {
        fprintf(stderr, "BaseInv status mismatch %s t=%u (%d vs %d)\n", what, t, so, sf);
        return -1;
    }
    if (so) {
        inv_fail++;
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (finv->coeffs[i] || finv2->coeffs[i]) {
                fprintf(stderr, "failure output not zero %s t=%u\n", what, t);
                return -1;
            }
        return 0;
    }
    inv_ok++;
    for (unsigned i = 0; i < NTRUPLUS_N; i++) {
        int x = finv2->coeffs[i];
        if (!mod_eq(x, RMOD * finv->coeffs[i]) || x < -18112 || x > 18112) {
            fprintf(stderr, "finv' != R*finv %s t=%u lane=%u\n", what, t, i);
            return -1;
        }
        if (x < inv_lo) inv_lo = x;
        if (x > inv_hi) inv_hi = x;
    }
    return 1;
}

static int check_mul(const poly *a, const poly *inv, const poly *inv2, const char *what, unsigned t) {
    poly h, h2;
    uint8_t b[NTRUPLUS_POLYBYTES], b2[NTRUPLUS_POLYBYTES];
    poly_basemul(&h, a, inv);
    NOR2_FN(&h2, a, inv2);
    for (unsigned i = 0; i < NTRUPLUS_N; i++) {
        int x = h2.coeffs[i];
        if (!mod_eq(x, h.coeffs[i]) || x < NOR2_LO || x > NOR2_HI) {
            fprintf(stderr, "nor2 product mismatch %s t=%u lane=%u (%d vs %d)\n", what, t, i, x, h.coeffs[i]);
            return 1;
        }
        if (x < h_lo) h_lo = x;
        if (x > h_hi) h_hi = x;
    }
    poly_tobytes(b, &h);
    poly_tobytes(b2, &h2);
    if (memcmp(b, b2, sizeof b)) {
        fprintf(stderr, "tobytes mismatch %s t=%u\n", what, t);
        return 1;
    }
    mul_checked++;
    return 0;
}

static void sample(poly *p, int is_f) {
    uint8_t coins[32], buf[NTRUPLUS_N / 4];
    for (unsigned i = 0; i < 32; i++) coins[i] = (uint8_t)random_word();
    shake256(buf, sizeof buf, coins, sizeof coins);
    poly_cbd1(p, buf);
    poly_triple(p);
    if (is_f) p->coeffs[0] += 1;
    FWD_NTT(p);
}

static void seed_rng(unsigned s) {
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; i++) entropy[i] = (unsigned char)(i * 29U + 0x5aU);
    for (size_t i = 0; i < 4; i++) entropy[i] = (unsigned char)(s >> (8 * i)); /* distinct per seed */
    randombytes_init(entropy, NULL, 256);
}

int main(void) {
    poly f, g, finv, finv2, ginv, ginv2, a;
    inv_lo = inv_hi = h_lo = h_hi = 0;
    unsigned keygen_pairs = 0;
    for (unsigned t = 0; t < KEYGEN_SEEDS; t++) {
        sample(&f, 1);
        sample(&g, 0);
        int rf = check_inv(&f, &finv, &finv2, "keygen f", t);
        int rg = check_inv(&g, &ginv, &ginv2, "keygen g", t);
        if (rf < 0 || rg < 0) return 1;
        if (rf == 1 && check_mul(&g, &finv, &finv2, "h=g*finv", t)) return 1;
        if (rg == 1 && check_mul(&f, &ginv, &ginv2, "f*ginv", t)) return 1;
        keygen_pairs += (rf == 1 && rg == 1);
    }
    printf("  keygen components: %u seeds, %u pairs invertible, finv'==R*finv, nor2==BaseMul (mod q), "
           "tobytes equal (%lu products)\n", KEYGEN_SEEDS, keygen_pairs, mul_checked);
    for (unsigned t = 0; t < RANDOM_INV; t++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) a.coeffs[i] = (int16_t)random_word();
        if (check_inv(&a, &finv, &finv2, "random int16", t) < 0) return 1;
    }
    unsigned zero_fail_before = (unsigned)inv_fail;
    for (unsigned t = 0; t < ZERO_BASE; t++) {
        /* NTT-domain operand with one all-zero base: chunk k (BASE_WORDS words),
         * lane j -> coefficients BASE_WORDS k + 16c + j, c = 0..BASE_ROWS-1 (basemul/baseinv
         * layout; 768/1152: 64 words, degree 4; 864: 48 words, degree 3). */
        for (unsigned i = 0; i < NTRUPLUS_N; i++) a.coeffs[i] = (int16_t)((int)(random_word() % 32001U) - 16000);
        unsigned k = random_word() % (NTRUPLUS_N / BASE_WORDS), j = random_word() % 16U;
        for (unsigned c = 0; c < BASE_ROWS; c++) a.coeffs[BASE_WORDS * k + 16U * c + j] = 0;
        if (check_inv(&a, &finv, &finv2, "zero base", t) < 0) return 1;
    }
    printf("  BaseInv: %lu successes, %lu failures (both implementations identical; %u of the "
           "%u zero-base inputs failed); finv' range [%d,%d]; nor2 range [%d,%d]\n",
           inv_ok, inv_fail, (unsigned)inv_fail - zero_fail_before, ZERO_BASE, inv_lo, inv_hi, h_lo, h_hi);
    if ((unsigned)inv_fail - zero_fail_before != ZERO_BASE) {
        fputs("zero-base failure path not exercised\n", stderr);
        return 1;
    }

    /* KEM keypairs */
    unsigned char pk[4][NTRUPLUS_PUBLICKEYBYTES], sk[4][NTRUPLUS_SECRETKEYBYTES];
    unsigned forced_g = 0, forced_f = 0;
    unsigned long long retries = 0;
    for (unsigned s = 0; s < KEYPAIR_SEEDS; s++) {
        int mode = (s % 97U == 5U) ? 1 : (s % 89U == 7U) ? 2 : 0;
        unsigned long long calls[4];
        for (unsigned v = 0; v < 4; v++) {
            seed_rng(s);
            random_calls = 0;
            shake_calls = 0;
            cur_variant = v;
            force_g = (mode == 1);
            force_f = (mode == 2);
            unsigned ig = injected_g, jf = injected_f;
            if (keypair[v](pk[v], sk[v])) return 1;
            calls[v] = random_calls;
            if ((mode == 1 && injected_g != ig + 1) || (mode == 2 && injected_f != jf + 1) || force_f) {
                fprintf(stderr, "injection not consumed seed=%u variant=%s\n", s, vname[v]);
                return 1;
            }
            force_g = 0;
            if (v && (memcmp(pk[v], pk[0], sizeof pk[0]) || memcmp(sk[v], sk[0], sizeof sk[0]) ||
                      calls[v] != calls[0])) {
                fprintf(stderr, "keypair mismatch seed=%u variant=%s mode=%d\n", s, vname[v], mode);
                return 1;
            }
        }
        forced_g += (mode == 1);
        forced_f += (mode == 2);
        retries += calls[0] - 2;
    }
    for (unsigned v = 1; v < 4; v++)
        if (baseinv_fail[v] != baseinv_fail[0]) {
            fputs("natural+forced BaseInv failure counts differ\n", stderr);
            return 1;
        }
    printf("  keypair: %u seeds x %u R^2-fold KEMs byte-exact vs Official (pk/sk, randombytes calls); "
           "forced g=0 retries %u, forced f failures %u, total extra draws %llu, genuine BaseInv "
           "failures per KEM %u\n", KEYPAIR_SEEDS, 3, forced_g, forced_f, retries, baseinv_fail[0]);
    printf("NTRU+%d keygen R^2 fold differential: pass\n", NTRUPLUS_N);
    return 0;
}
