#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "kat/rng.h"
#include "mlkem_batch.h"
#include "params.h"
#include "poly.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int official_ref_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_ref_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_fixed_dec(unsigned char *, const unsigned char *, const unsigned char *);
void ntruplus768_officialopt_invntt_yang_fixed(poly *);

enum { BANKS = 16 };
static poly inverse_input[BANKS], inverse_output[BANKS];
static unsigned char pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static unsigned char sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static unsigned char ct[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static unsigned char ss_output[BANKS][NTRUPLUS_SSBYTES];
static volatile int status_sink;
static uint64_t state = UINT64_C(0x768c720260923);

static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}
static void seed_rng(unsigned tag) {
    unsigned char entropy[48];
    for (unsigned i = 0; i < sizeof entropy; i++)
        entropy[i] = (unsigned char)(i * 31U + tag * 13U);
    randombytes_init(entropy, NULL, 256);
}
static void fixture(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        poly a, c;
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            a.coeffs[i] = (int16_t)(random_word() % NTRUPLUS_Q);
            c.coeffs[i] = (int16_t)(random_word() % NTRUPLUS_Q);
        }
        poly_basemul_scale(&inverse_input[b], &a, &c);
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (inverse_input[b].coeffs[i] < -7644 || inverse_input[b].coeffs[i] > 7644)
                __builtin_trap();
        seed_rng(2000U + b);
        if (official_ref_keypair(pk[b], sk[b])) __builtin_trap();
        seed_rng(3000U + b);
        unsigned char secret[NTRUPLUS_SSBYTES];
        if (official_ref_enc(ct[b], secret, pk[b])) __builtin_trap();
    }
}
static void preflight(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        poly reference = inverse_input[b];
        inverse_output[b] = inverse_input[b];
        poly_invntt_scale(&reference);
        ntruplus768_officialopt_invntt_yang_fixed(&inverse_output[b]);
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (((int)reference.coeffs[i] - inverse_output[b].coeffs[i]) % NTRUPLUS_Q)
                __builtin_trap();
        poly_crepmod3(&reference);
        poly_crepmod3(&inverse_output[b]);
        if (memcmp(&reference, &inverse_output[b], sizeof(poly))) __builtin_trap();
        unsigned char secret[NTRUPLUS_SSBYTES];
        int a = official_ref_dec(secret, ct[b], sk[b]);
        int c = official_fixed_dec(ss_output[b], ct[b], sk[b]);
        if (a != c || memcmp(secret, ss_output[b], sizeof secret)) __builtin_trap();
    }
    fputs("preflight=pass\n", stderr);
}
static uint64_t cyclecounter(void) { return (uint64_t)cpucycles(); }
static void prepare(void *unused, unsigned test) {
    (void)unused;
    (void)test;
    for (unsigned b = 0; b < BANKS; b++) {
        inverse_output[b] = inverse_input[b];
        memset(ss_output[b], 0, NTRUPLUS_SSBYTES);
    }
}
static void copy_inverse(void *unused, unsigned iteration) {
    (void)unused;
    unsigned b = iteration & (BANKS - 1U);
    inverse_output[b] = inverse_input[b];
    ntruplus768_officialopt_invntt_yang_fixed(&inverse_output[b]);
}
static void complete_decap(void *unused, unsigned iteration) {
    (void)unused;
    unsigned b = iteration & (BANKS - 1U);
    status_sink = official_fixed_dec(ss_output[b], ct[b], sk[b]);
}
static void measure_region(const char *name, ntruplus_batch_operation operation) {
    const ntruplus_batch_config config = {
        NTRUPLUS_BATCH_WARMUP, NTRUPLUS_BATCH_ITERATIONS, NTRUPLUS_BATCH_TESTS
    };
    ntruplus_batch_absolute_result result;
    if (ntruplus_batch_absolute(&config, cyclecounter, prepare, operation, NULL, &result))
        __builtin_trap();
    printf("%s cycles=%" PRIu64 "\n", name, result.cycles_per_operation);
    for (unsigned test = 0; test < config.tests; test++)
        printf("raw,%s,%u,%" PRIu64 "\n", name, test, result.totals[test]);
}
int main(void) {
    fixture();
    preflight();
    cpucycles_tracesetup();
    fprintf(stderr, "cpucycles=%s persecond=%lld\n",
            cpucycles_implementation(), cpucycles_persecond());
    fprintf(stderr, "batch=fixed-layout warmup=%u iterations=%u tests=%u\n",
            NTRUPLUS_BATCH_WARMUP, NTRUPLUS_BATCH_ITERATIONS, NTRUPLUS_BATCH_TESTS);
    measure_region("copy_plus_inverse", copy_inverse);
    measure_region("complete_decap", complete_decap);
    return 0;
}
