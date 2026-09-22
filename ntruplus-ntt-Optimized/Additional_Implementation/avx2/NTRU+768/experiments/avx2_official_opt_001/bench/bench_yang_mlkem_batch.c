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
int official_yang_pair32_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_yang_stage5reuse_dec(unsigned char *, const unsigned char *, const unsigned char *);
void ntruplus768_officialopt_invntt_yang_pair32(poly *);
void ntruplus768_officialopt_invntt_yang_stage5reuse(poly *);

enum { BANKS = 16 };
static poly inverse_input[BANKS], inverse_output[2][BANKS];
static unsigned char pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static unsigned char sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static unsigned char ct[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static unsigned char ss_output[2][BANKS][NTRUPLUS_SSBYTES];
static volatile int status_sink;
static volatile uint16_t output_sink;
static uint64_t state = UINT64_C(0x768c720260923);

struct arm { unsigned variant; };
static struct arm control = { 0U }, candidate = { 1U };

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
        inverse_output[0][b] = inverse_output[1][b] = inverse_input[b];
        ntruplus768_officialopt_invntt_yang_pair32(&inverse_output[0][b]);
        ntruplus768_officialopt_invntt_yang_stage5reuse(&inverse_output[1][b]);
        if (memcmp(&inverse_output[0][b], &inverse_output[1][b], sizeof(poly))) __builtin_trap();
        int a = official_yang_pair32_dec(ss_output[0][b], ct[b], sk[b]);
        int c = official_yang_stage5reuse_dec(ss_output[1][b], ct[b], sk[b]);
        if (a != c || memcmp(ss_output[0][b], ss_output[1][b], NTRUPLUS_SSBYTES)) __builtin_trap();
    }
    fputs("preflight=pass\n", stderr);
}

static uint64_t cyclecounter(void) { return (uint64_t)cpucycles(); }
static void prepare(void *opaque, unsigned test) {
    const struct arm *arm = opaque;
    for (unsigned b = 0; b < BANKS; b++) {
        inverse_output[arm->variant][b] = inverse_input[b];
        memset(ss_output[arm->variant][b], 0, NTRUPLUS_SSBYTES);
    }
    (void)test;
}
static void inverse_control(void *opaque, unsigned iteration) {
    const struct arm *arm = opaque;
    unsigned b = iteration & (BANKS - 1U);
    inverse_output[arm->variant][b] = inverse_input[b];
    ntruplus768_officialopt_invntt_yang_pair32(&inverse_output[arm->variant][b]);
}
static void inverse_candidate(void *opaque, unsigned iteration) {
    const struct arm *arm = opaque;
    unsigned b = iteration & (BANKS - 1U);
    inverse_output[arm->variant][b] = inverse_input[b];
    ntruplus768_officialopt_invntt_yang_stage5reuse(&inverse_output[arm->variant][b]);
}
static void decap_control(void *opaque, unsigned iteration) {
    const struct arm *arm = opaque;
    unsigned b = iteration & (BANKS - 1U);
    status_sink = official_yang_pair32_dec(ss_output[arm->variant][b], ct[b], sk[b]);
}
static void decap_candidate(void *opaque, unsigned iteration) {
    const struct arm *arm = opaque;
    unsigned b = iteration & (BANKS - 1U);
    status_sink = official_yang_stage5reuse_dec(ss_output[arm->variant][b], ct[b], sk[b]);
}

static void measure_region(const char *label,
                           ntruplus_batch_operation run_control,
                           ntruplus_batch_operation run_candidate) {
    const ntruplus_batch_config config = {
        NTRUPLUS_BATCH_WARMUP, NTRUPLUS_BATCH_ITERATIONS, NTRUPLUS_BATCH_TESTS
    };
    ntruplus_batch_result result;
    if (ntruplus_batch_pair(&config, cyclecounter, prepare, run_control, &control,
                           prepare, run_candidate, &candidate, &result)) __builtin_trap();
    printf("%s control cycles=%" PRIu64 "\n", label, result.control_cycles_per_operation);
    printf("%s candidate cycles=%" PRIu64 "\n", label, result.candidate_cycles_per_operation);
    for (unsigned test = 0; test < config.tests; test++)
        printf("raw,%s,%u,%" PRIu64 ",%" PRIu64 "\n", label, test,
               result.control_totals[test], result.candidate_totals[test]);
    output_sink ^= (uint16_t)inverse_output[0][0].coeffs[0];
    output_sink ^= (uint16_t)inverse_output[1][0].coeffs[0];
}

int main(void) {
    fixture();
    preflight();
    cpucycles_tracesetup();
    fprintf(stderr, "cpucycles=%s persecond=%lld\n",
            cpucycles_implementation(), cpucycles_persecond());
    fprintf(stderr, "batch=mlkem-native-inspired warmup=%u iterations=%u tests=%u\n",
            NTRUPLUS_BATCH_WARMUP, NTRUPLUS_BATCH_ITERATIONS, NTRUPLUS_BATCH_TESTS);
    measure_region("copy_plus_inverse", inverse_control, inverse_candidate);
    measure_region("complete_decap", decap_control, decap_candidate);
    return 0;
}
