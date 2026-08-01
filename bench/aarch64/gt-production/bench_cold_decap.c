#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "api.h"
#include "perf_counter.h"

#ifndef NTESTS
#define NTESTS 61
#endif

void bench_randombytes_reset(uint32_t seed);
void wave29_icache_thrash(void);

static uint8_t fixture_pk[CRYPTO_PUBLICKEYBYTES];
static uint8_t fixture_sk[CRYPTO_SECRETKEYBYTES];
static uint8_t fixture_ct[CRYPTO_CIPHERTEXTBYTES];
static uint8_t fixture_ss[CRYPTO_BYTES];
static uint8_t output_ss[CRYPTO_BYTES];
static volatile uint64_t sink;

static int compare_u64(const void *left, const void *right)
{
    const uint64_t a = *(const uint64_t *)left;
    const uint64_t b = *(const uint64_t *)right;

    return (a > b) - (a < b);
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
    return memcmp(decapsulated, fixture_ss, CRYPTO_BYTES);
}

int main(void)
{
    uint64_t samples[NTESTS];

    if (prepare_fixture() != 0 || perf_counter_open() != 0) {
        fputs("fixture/perf setup failed\n", stderr);
        return 1;
    }

    for (size_t i = 0; i < NTESTS; i++) {
        /* The thrash is intentionally outside the measured interval. */
        wave29_icache_thrash();
        if (perf_counter_start() != 0 ||
            crypto_kem_dec(output_ss, fixture_ct, fixture_sk) != 0) {
            fputs("cold decapsulation failed\n", stderr);
            return 1;
        }
        samples[i] = perf_counter_stop();
    }
    perf_counter_close();

    if (memcmp(output_ss, fixture_ss, CRYPTO_BYTES) != 0) {
        fputs("cold output mismatch\n", stderr);
        return 1;
    }

    qsort(samples, NTESTS, sizeof(samples[0]), compare_u64);
    sink ^= samples[NTESTS / 2];
    printf("mode=cold-decap tests=%d thrash_text_bytes=98304\n", NTESTS);
    printf("cycles_min=%" PRIu64 " cycles_p50=%" PRIu64
           " cycles_max=%" PRIu64 " sink=%" PRIu64 "\n",
           samples[0], samples[NTESTS / 2], samples[NTESTS - 1], sink);
    return 0;
}
