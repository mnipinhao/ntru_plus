#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "api.h"
#include "perf_counter.h"

#ifndef BENCH_MODE_STR
#define BENCH_MODE_STR "encap"
#endif

#ifndef BENCH_VARIANT_STR
#define BENCH_VARIANT_STR "unknown"
#endif

#ifndef NTESTS
#define NTESTS 31
#endif

#ifndef NITERATIONS
#define NITERATIONS 2000
#endif

#ifndef NWARMUP
#define NWARMUP 100
#endif

void bench_randombytes_reset(uint32_t seed);

static uint8_t fixture_pk[CRYPTO_PUBLICKEYBYTES];
static uint8_t fixture_sk[CRYPTO_SECRETKEYBYTES];
static uint8_t fixture_ct[CRYPTO_CIPHERTEXTBYTES];
static uint8_t fixture_ss[CRYPTO_BYTES];
static uint8_t output_pk[CRYPTO_PUBLICKEYBYTES];
static uint8_t output_sk[CRYPTO_SECRETKEYBYTES];
static uint8_t output_ct[CRYPTO_CIPHERTEXTBYTES];
static uint8_t output_ss[CRYPTO_BYTES];
static volatile uint64_t sink;

static int compare_u64(const void *left, const void *right)
{
    const uint64_t a = *(const uint64_t *)left;
    const uint64_t b = *(const uint64_t *)right;

    return (a > b) - (a < b);
}

static uint64_t checksum(const uint8_t *data, size_t length)
{
    uint64_t value = UINT64_C(0x9e3779b97f4a7c15);
    size_t i;

    for (i = 0; i < length; i++)
        value = (value << 7) ^ (value >> 3) ^ data[i];
    return value;
}

static int prepare_fixture(void)
{
    uint8_t decapsulated[CRYPTO_BYTES];

    bench_randombytes_reset(UINT32_C(0x10203040));
    if (crypto_kem_keypair(fixture_pk, fixture_sk) != 0)
        return -1;
    bench_randombytes_reset(UINT32_C(0x50607080));
    if (crypto_kem_enc(fixture_ct, fixture_ss, fixture_pk) != 0)
        return -1;
    if (crypto_kem_dec(decapsulated, fixture_ct, fixture_sk) != 0)
        return -1;
    if (memcmp(decapsulated, fixture_ss, CRYPTO_BYTES) != 0)
        return -1;
    return 0;
}

static int run_target(void)
{
    if (strcmp(BENCH_MODE_STR, "keygen") == 0)
        return crypto_kem_keypair(output_pk, output_sk);
    if (strcmp(BENCH_MODE_STR, "encap") == 0)
        return crypto_kem_enc(output_ct, output_ss, fixture_pk);
    if (strcmp(BENCH_MODE_STR, "decap") == 0)
        return crypto_kem_dec(output_ss, fixture_ct, fixture_sk);

    fprintf(stderr, "unknown BENCH_MODE_STR=%s\n", BENCH_MODE_STR);
    return -1;
}

static int validate_output(void)
{
    uint8_t ciphertext[CRYPTO_CIPHERTEXTBYTES];
    uint8_t encapsulated[CRYPTO_BYTES];
    uint8_t decapsulated[CRYPTO_BYTES];

    if (strcmp(BENCH_MODE_STR, "keygen") == 0) {
        bench_randombytes_reset(UINT32_C(0xc001d00d));
        if (crypto_kem_enc(ciphertext, encapsulated, output_pk) != 0)
            return -1;
        if (crypto_kem_dec(decapsulated, ciphertext, output_sk) != 0)
            return -1;
        return memcmp(encapsulated, decapsulated, CRYPTO_BYTES) == 0 ? 0 : -1;
    }
    if (strcmp(BENCH_MODE_STR, "encap") == 0) {
        if (crypto_kem_dec(decapsulated, output_ct, fixture_sk) != 0)
            return -1;
        return memcmp(output_ss, decapsulated, CRYPTO_BYTES) == 0 ? 0 : -1;
    }
    if (strcmp(BENCH_MODE_STR, "decap") == 0)
        return memcmp(output_ss, fixture_ss, CRYPTO_BYTES) == 0 ? 0 : -1;

    return -1;
}

static void print_samples(const uint64_t samples[NTESTS])
{
    size_t i;

    printf("samples=");
    for (i = 0; i < NTESTS; i++)
        printf("%s%" PRIu64, i == 0 ? "" : ",", samples[i]);
    printf("\n");
}

int main(void)
{
    uint64_t samples[NTESTS];
    int i;
    int j;

    if (prepare_fixture() != 0) {
        fprintf(stderr, "KEM fixture correctness failed\n");
        return 1;
    }
    if (perf_counter_open() != 0)
        return 1;

    for (i = 0; i < NTESTS; i++) {
        bench_randombytes_reset(UINT32_C(0xa5a50000) + (uint32_t)i);
        for (j = 0; j < NWARMUP; j++) {
            if (run_target() != 0)
                return 1;
        }

        bench_randombytes_reset(UINT32_C(0x5a5a0000) + (uint32_t)i);
        if (perf_counter_start() != 0)
            return 1;
        for (j = 0; j < NITERATIONS; j++) {
            if (run_target() != 0)
                return 1;
        }
        samples[i] = perf_counter_stop() / NITERATIONS;
    }

    perf_counter_close();
    if (validate_output() != 0) {
        fprintf(stderr, "measured %s output correctness failed\n", BENCH_MODE_STR);
        return 1;
    }
    qsort(samples, NTESTS, sizeof(samples[0]), compare_u64);

    sink ^= checksum(output_pk, sizeof(output_pk));
    sink ^= checksum(output_sk, sizeof(output_sk));
    sink ^= checksum(output_ct, sizeof(output_ct));
    sink ^= checksum(output_ss, sizeof(output_ss));

    printf("variant=%s\n", BENCH_VARIANT_STR);
    printf("mode=%s\n", BENCH_MODE_STR);
    printf("tests=%d\n", NTESTS);
    printf("iterations=%d\n", NITERATIONS);
    printf("warmups=%d\n", NWARMUP);
    printf("p10=%" PRIu64 "\n", samples[NTESTS * 10 / 100]);
    printf("p50=%" PRIu64 "\n", samples[NTESTS * 50 / 100]);
    printf("p90=%" PRIu64 "\n", samples[NTESTS * 90 / 100]);
    print_samples(samples);
    printf("sink=%" PRIu64 "\n", sink);
    return 0;
}
