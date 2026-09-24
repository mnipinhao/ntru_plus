/*
 * Official vs caller-lazy KEM byte differential for NTRU+864/1152 AVX2.
 * Copied from NTRU+768 avx2_official_opt_001/tests/test_kem_lazy.c (Round 6:
 * 100 deterministic vectors, invalid PK/CT/SK, forced g-retry via a
 * linker-wrapped CBD1 expansion, optional TEST_F_RETRY f-inversion failure
 * injection via --wrap=poly_baseinv) and parameterised only through params.h.
 * Adds a noncanonical-coefficient CT check. Test-only wrappers never reach an
 * exported KEM.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "kat/rng.h"
#include "poly.h"

#ifdef TEST_F_RETRY
static int force_f_failure;
static unsigned injected_f_failures;
/* Natural BaseInv failure classification: within one keypair, every BaseInv
 * call before the first success is on f, every later one is on g. */
static int keygen_impl = -1, keygen_on_g;
static unsigned natural_f_failures[2], natural_g_failures[2];
int __real_poly_baseinv(poly *, const poly *);
int __wrap_poly_baseinv(poly *out, const poly *in) {
    if (force_f_failure) {
        force_f_failure = 0;
        injected_f_failures++;
        memset(out, 0xa5, sizeof *out); /* failure output must not be consumed */
        return 1;
    }
    int status = __real_poly_baseinv(out, in);
    if (keygen_impl >= 0) {
        if (status && !keygen_on_g) natural_f_failures[keygen_impl]++;
        else if (status) natural_g_failures[keygen_impl]++;
        else keygen_on_g = 1;
    }
    return status;
}
#define KEYGEN_CLASSIFY(impl) (keygen_impl = (impl), keygen_on_g = 0)
#ifdef CANDIDATE_BASEINV
/* A candidate whose keygen reaches BaseInv through another symbol (the keygen
 * R^2-fold candidates: -DCANDIDATE_BASEINV=<symbol> plus -Wl,--wrap=<symbol>)
 * gets the same one-shot f-failure injection and failure classification. */
#define KEM_TEST_BCAT_(a, b) a##b
#define KEM_TEST_BCAT(a, b) KEM_TEST_BCAT_(a, b)
int KEM_TEST_BCAT(__real_, CANDIDATE_BASEINV)(poly *, const poly *);
int KEM_TEST_BCAT(__wrap_, CANDIDATE_BASEINV)(poly *out, const poly *in) {
    if (force_f_failure) {
        force_f_failure = 0;
        injected_f_failures++;
        memset(out, 0xa5, sizeof *out);
        return 1;
    }
    int status = KEM_TEST_BCAT(__real_, CANDIDATE_BASEINV)(out, in);
    if (keygen_impl >= 0) {
        if (status && !keygen_on_g) natural_f_failures[keygen_impl]++;
        else if (status) natural_g_failures[keygen_impl]++;
        else keygen_on_g = 1;
    }
    return status;
}
#endif
#else
#define KEYGEN_CLASSIFY(impl) ((void)0)
#endif

int official_ref_keypair(unsigned char *, unsigned char *);
int official_ref_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_ref_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_lazy_keypair(unsigned char *, unsigned char *);
int official_lazy_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_lazy_dec(unsigned char *, const unsigned char *, const unsigned char *);

static unsigned long long random_calls;
static unsigned keygen_shake_calls;
static int force_zero_g_once;
void __real_fips202avx_shake256(uint8_t *, size_t, const uint8_t *, size_t);
void __wrap_fips202avx_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen) {
    if (force_zero_g_once && outlen == NTRUPLUS_N / 4 && inlen == 32 &&
        ++keygen_shake_calls == 2) {
        memset(out, 0, outlen); /* CBD1(g)=0; BaseInv must reject and retry. */
        return;
    }
    __real_fips202avx_shake256(out, outlen, in, inlen);
}
#ifdef CANDIDATE_SHAKE256
/* A candidate whose KEM reaches SHAKE256 through another symbol (the
 * mlkem-native Keccak candidates: -DCANDIDATE_SHAKE256=<symbol> plus
 * -Wl,--wrap=<symbol>) gets the same test-only forced-g injection. */
#define KEM_TEST_CAT_(a, b) a##b
#define KEM_TEST_CAT(a, b) KEM_TEST_CAT_(a, b)
void KEM_TEST_CAT(__real_, CANDIDATE_SHAKE256)(uint8_t *, size_t, const uint8_t *, size_t);
void KEM_TEST_CAT(__wrap_, CANDIDATE_SHAKE256)(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen) {
    if (force_zero_g_once && outlen == NTRUPLUS_N / 4 && inlen == 32 &&
        ++keygen_shake_calls == 2) {
        memset(out, 0, outlen);
        return;
    }
    KEM_TEST_CAT(__real_, CANDIDATE_SHAKE256)(out, outlen, in, inlen);
}
#endif
void __real_randombytes(unsigned char *, unsigned long long);
void __wrap_randombytes(unsigned char *out, unsigned long long length) {
    random_calls++;
    __real_randombytes(out, length);
}

static void seed_rng(unsigned trial) {
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; i++)
        entropy[i] = (unsigned char)(i * 31U + trial * 13U);
    randombytes_init(entropy, NULL, 256);
}

int main(void) {
    unsigned char pk_o[NTRUPLUS_PUBLICKEYBYTES], pk_l[NTRUPLUS_PUBLICKEYBYTES];
    unsigned char sk_o[NTRUPLUS_SECRETKEYBYTES], sk_l[NTRUPLUS_SECRETKEYBYTES];
    unsigned char ct_o[NTRUPLUS_CIPHERTEXTBYTES], ct_l[NTRUPLUS_CIPHERTEXTBYTES];
    unsigned char ss_o[NTRUPLUS_SSBYTES], ss_l[NTRUPLUS_SSBYTES];
    unsigned char dec_o[NTRUPLUS_SSBYTES], dec_l[NTRUPLUS_SSBYTES];
    unsigned long long retries = 0;

    for (unsigned trial = 0; trial < 100; trial++) {
        seed_rng(trial);
        random_calls = 0;
        KEYGEN_CLASSIFY(0);
        int status_o = official_ref_keypair(pk_o, sk_o);
        unsigned long long calls_o = random_calls;
        seed_rng(trial);
        random_calls = 0;
        KEYGEN_CLASSIFY(1);
        int status_l = official_lazy_keypair(pk_l, sk_l);
        KEYGEN_CLASSIFY(-1);
        unsigned long long calls_l = random_calls;
        if (status_o || status_l || calls_o != calls_l || calls_o < 2 ||
            memcmp(pk_o, pk_l, sizeof pk_o) || memcmp(sk_o, sk_l, sizeof sk_o)) {
            fprintf(stderr, "lazy Keygen mismatch trial=%u\n", trial);
            return 1;
        }
        retries += calls_o - 2;

        seed_rng(trial + 1000U);
        status_o = official_ref_enc(ct_o, ss_o, pk_o);
        seed_rng(trial + 1000U);
        status_l = official_lazy_enc(ct_l, ss_l, pk_l);
        if (status_o || status_l || memcmp(ct_o, ct_l, sizeof ct_o) ||
            memcmp(ss_o, ss_l, sizeof ss_o)) {
            fprintf(stderr, "lazy Encap mismatch trial=%u\n", trial);
            return 1;
        }

        status_o = official_ref_dec(dec_o, ct_o, sk_o);
        status_l = official_lazy_dec(dec_l, ct_l, sk_l);
        if (status_o || status_l || memcmp(dec_o, dec_l, sizeof dec_o) ||
            memcmp(dec_o, ss_o, sizeof dec_o)) {
            fprintf(stderr, "lazy Decap mismatch trial=%u\n", trial);
            return 1;
        }

        ct_o[(trial * 17U) % sizeof ct_o] ^= (unsigned char)(1U << (trial & 7U));
        ct_l[(trial * 17U) % sizeof ct_l] ^= (unsigned char)(1U << (trial & 7U));
        status_o = official_ref_dec(dec_o, ct_o, sk_o);
        status_l = official_lazy_dec(dec_l, ct_l, sk_l);
        if (status_o != status_l || memcmp(dec_o, dec_l, sizeof dec_o)) {
            fprintf(stderr, "lazy invalid-CT mismatch trial=%u\n", trial);
            return 1;
        }
        /* Noncanonical first CT coefficient (poly_frombytes rejection). */
        {
            unsigned char nc_o[NTRUPLUS_CIPHERTEXTBYTES], nc_l[NTRUPLUS_CIPHERTEXTBYTES];
            memcpy(nc_o, ct_o, sizeof nc_o);
            memcpy(nc_l, ct_l, sizeof nc_l);
            nc_o[0] = nc_l[0] = 0xff;
            nc_o[1] = nc_l[1] = (unsigned char)(nc_o[1] | 0x0f);
            memset(dec_o, 0xa5, sizeof dec_o);
            memset(dec_l, 0x5a, sizeof dec_l);
            status_o = official_ref_dec(dec_o, nc_o, sk_o);
            status_l = official_lazy_dec(dec_l, nc_l, sk_l);
            if (status_o != 1 || status_l != 1 || memcmp(dec_o, dec_l, sizeof dec_o)) {
                fprintf(stderr, "lazy noncanonical-CT mismatch trial=%u\n", trial);
                return 1;
            }
        }
        /* Noncanonical first SK coefficient, preserving matching failure and
         * zeroization semantics. Restore for the next independent fixture. */
        unsigned char sk0=sk_o[0], sk1=sk_o[1];
        sk_o[0]=sk_l[0]=0xff;
        sk_o[1]=sk_l[1]=(unsigned char)(sk1|0x0f);
        status_o=official_ref_dec(dec_o,ct_o,sk_o);
        status_l=official_lazy_dec(dec_l,ct_l,sk_l);
        if(status_o!=status_l || memcmp(dec_o,dec_l,sizeof dec_o)) { fprintf(stderr, "lazy invalid-SK mismatch trial=%u\n", trial); return 1; }
        sk_o[0]=sk_l[0]=sk0; sk_o[1]=sk_l[1]=sk1;
    }

    /* Force one genuine g=0 BaseInv failure via test-only CBD1 input.
     * Both KEM implementations execute their unchanged retry loops. */
    seed_rng(100000);
    random_calls = 0;
    keygen_shake_calls = 0;
    force_zero_g_once = 1;
    int retry_status_o = official_ref_keypair(pk_o, sk_o);
    unsigned long long retry_calls = random_calls;
    unsigned shake_calls_o = keygen_shake_calls;
    seed_rng(100000);
    random_calls = 0;
    keygen_shake_calls = 0;
    int retry_status_l = official_lazy_keypair(pk_l, sk_l);
    force_zero_g_once = 0;
    if (retry_status_o || retry_status_l || retry_calls != 3 ||
        random_calls != retry_calls || shake_calls_o != 3 || keygen_shake_calls != 3 ||
        memcmp(pk_o, pk_l, sizeof pk_o) || memcmp(sk_o, sk_l, sizeof sk_o)) {
        fprintf(stderr, "lazy Keygen retry mismatch calls=%llu/%llu shakes=%u/%u\n",
                retry_calls, random_calls, shake_calls_o, keygen_shake_calls);
        return 1;
    }
    seed_rng(100001);
    int retry_enc_o = official_ref_enc(ct_o, ss_o, pk_o);
    seed_rng(100001);
    int retry_enc_l = official_lazy_enc(ct_l, ss_l, pk_l);
    if (retry_enc_o || retry_enc_l || memcmp(ct_o, ct_l, sizeof ct_o) ||
        memcmp(ss_o, ss_l, sizeof ss_o) ||
        official_ref_dec(dec_o, ct_o, sk_o) ||
        official_lazy_dec(dec_l, ct_l, sk_l) ||
        memcmp(dec_o, dec_l, sizeof dec_o) ||
        memcmp(dec_o, ss_o, sizeof dec_o)) {
        fputs("KEM mismatch after forced Keygen retry\n", stderr);
        return 1;
    }
    puts("Keygen forced g-inversion retry: pass (3 matching draws and byte-exact keys)");

#ifdef TEST_F_RETRY
    if (natural_f_failures[0] != natural_f_failures[1] ||
        natural_g_failures[0] != natural_g_failures[1]) {
        fputs("natural f/g BaseInv failure counts differ\n", stderr);
        return 1;
    }
    printf("natural BaseInv failures in the 100 vectors (per implementation): f=%u g=%u\n",
           natural_f_failures[0], natural_g_failures[0]);
    /* Control-flow injection on the first f BaseInv. Oracle: the injected
     * keypair must equal an uninjected keypair whose first 32-byte coin draw
     * was discarded, and consume exactly one more draw.  No reseeding between
     * Keygen and Encap: the subsequent RNG stream is checked too. */
    unsigned char pk_x[NTRUPLUS_PUBLICKEYBYTES], sk_x[NTRUPLUS_SECRETKEYBYTES];
    unsigned char discard[NTRUPLUS_SYMBYTES];
    seed_rng(300001); randombytes(discard, sizeof discard); random_calls = 0;
    if (official_ref_keypair(pk_x, sk_x)) return 1;
    unsigned long long calls_x = random_calls;
    seed_rng(300001); random_calls = 0; force_f_failure = 1;
    if (official_ref_keypair(pk_o, sk_o) || random_calls != calls_x + 1 ||
        memcmp(pk_o, pk_x, sizeof pk_o) || memcmp(sk_o, sk_x, sizeof sk_o)) {
        fputs("Official f-injection oracle mismatch\n", stderr);
        return 1;
    }
    if (official_ref_enc(ct_o, ss_o, pk_o)) return 1;
    unsigned long long calls_after_o = random_calls;
    seed_rng(300001); random_calls = 0; force_f_failure = 1;
    if (official_lazy_keypair(pk_l, sk_l) || random_calls != calls_x + 1) return 1;
    if (official_lazy_enc(ct_l, ss_l, pk_l)) return 1;
    if (injected_f_failures != 2 || random_calls != calls_after_o ||
        memcmp(pk_o,pk_l,sizeof pk_o) || memcmp(sk_o,sk_l,sizeof sk_o) ||
        memcmp(ct_o,ct_l,sizeof ct_o) || memcmp(ss_o,ss_l,sizeof ss_o) ||
        official_ref_dec(dec_o,ct_o,sk_o) || official_lazy_dec(dec_l,ct_l,sk_l) ||
        memcmp(dec_o,dec_l,sizeof dec_o) || memcmp(dec_o,ss_o,sizeof dec_o)) {
        fputs("lazy f-injection mismatch\n", stderr);
        return 1;
    }
    printf("f-injection keypair draws: %llu (= discarded-draw oracle %llu + 1)\n",
           calls_x + 1, calls_x);
    puts("f BaseInv one-shot failure injection PASS; poisoned failure output; RNG continuation exact");
#endif
    pk_o[0] = (unsigned char)NTRUPLUS_Q;
    pk_o[1] = (unsigned char)((pk_o[1] & 0xf0U) | (NTRUPLUS_Q >> 8));
    memset(ct_o, 0xa5, sizeof ct_o);
    memset(ct_l, 0xa5, sizeof ct_l);
    memset(ss_o, 0xa5, sizeof ss_o);
    memset(ss_l, 0xa5, sizeof ss_l);
    seed_rng(9001);
    int status_o = official_ref_enc(ct_o, ss_o, pk_o);
    seed_rng(9001);
    int status_l = official_lazy_enc(ct_l, ss_l, pk_o);
    unsigned char zero_ct[NTRUPLUS_CIPHERTEXTBYTES] = {0};
    unsigned char zero_ss[NTRUPLUS_SSBYTES] = {0};
    if (status_o != 1 || status_l != 1 ||
        memcmp(ct_o, zero_ct, sizeof ct_o) || memcmp(ct_l, zero_ct, sizeof ct_l) ||
        memcmp(ss_o, zero_ss, sizeof ss_o) || memcmp(ss_l, zero_ss, sizeof ss_l)) {
        fputs("lazy invalid-PK behavior mismatch\n", stderr);
        return 1;
    }
    printf("NTRU+%d Official caller-lazy KEM byte differential: pass (100 vectors pk/sk/ct/ss, "
           "invalid PK/CT/noncanonical-CT/SK matched, %llu natural Keygen retries)\n",
           NTRUPLUS_N, retries);
    return 0;
}
