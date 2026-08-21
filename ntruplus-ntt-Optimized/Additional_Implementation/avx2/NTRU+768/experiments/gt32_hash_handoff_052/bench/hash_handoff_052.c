#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "params.h"
#include "poly.h"
#include "symmetric.h"
#include "internal.h"

#define SAMPLES 1024
#define MODES 3

void off_poly_ntt(poly *a);
void off_poly_tobytes(uint8_t *out, const poly *a);

typedef struct __attribute__((aligned(64))) {
    poly coefficient;
    poly official_ntt;
    int16_t frontend[NTRUPLUS_N];
    int16_t gt_ntt[NTRUPLUS_N];
    uint8_t producer_bytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
    uint8_t hash_bytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
} state_t;

static volatile uint64_t sink;

static inline uint64_t begin_ticks(void) {
    _mm_lfence();
    return __rdtsc();
}

static inline uint64_t end_ticks(void) {
    unsigned aux;
    uint64_t x = __rdtscp(&aux);
    _mm_lfence();
    return x;
}

static int cmp64(const void *aa, const void *bb) {
    uint64_t a = *(const uint64_t *)aa, b = *(const uint64_t *)bb;
    return a > b ? 1 : a < b ? -1 : 0;
}

__attribute__((noinline, target("avx2")))
static void common_copy(uint8_t *dst, const uint8_t *src) {
    for (size_t i = 0; i < NTRUPLUS_POLYBYTES; i += 32) {
        __m256i x = _mm256_load_si256((const __m256i *)(const void *)(src + i));
        _mm256_store_si256((__m256i *)(void *)(dst + i), x);
    }
}

static void official_producer(state_t *s, uint8_t *out) {
    s->official_ntt = s->coefficient;
    off_poly_ntt(&s->official_ntt);
    off_poly_tobytes(out, &s->official_ntt);
}

static void gt_producer(state_t *s, uint8_t *out) {
    ntruplus768_ntt_frontend_avx2(s->frontend, s->coefficient.coeffs);
    ntruplus768_ntt_m_avx2(s->gt_ntt, s->frontend);
    ntruplus768_pack_m_lazy10788_avx2(out, s->gt_ntt);
}

static uint64_t measure_one(state_t *s, int producer, int mode) {
    uint8_t *produced = mode == 2 ? s->producer_bytes : s->hash_bytes;
    if (producer == 0)
        official_producer(s, produced);
    else
        gt_producer(s, produced);

    if (mode == 1)
        _mm_mfence();
    else if (mode == 2)
        common_copy(s->hash_bytes, s->producer_bytes);

    uint64_t a = begin_ticks();
    hash_g(s->hash_bytes, s->hash_bytes);
    uint64_t b = end_ticks();
    sink ^= s->hash_bytes[(producer * 31 + mode * 17) % HASH_G_OUTBYTES];
    return b - a;
}

int main(void) {
    state_t *s = aligned_alloc(64, sizeof(*s));
    if (!s) return 1;
    memset(s, 0, sizeof(*s));

    /* A deterministic real CBD1-domain polynomial. */
    uint8_t cbd[NTRUPLUS_N / 4];
    for (size_t i = 0; i < sizeof(cbd); i++) cbd[i] = (uint8_t)(29 * i + 7);
    poly_cbd1(&s->coefficient, cbd);

    uint8_t ob[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
    uint8_t gb[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
    official_producer(s, ob);
    gt_producer(s, gb);
    if (memcmp(ob, gb, sizeof(ob)) != 0) {
        fprintf(stderr, "producer byte mismatch\n");
        return 2;
    }

    uint8_t oh[NTRUPLUS_POLYBYTES], gh[NTRUPLUS_POLYBYTES];
    memcpy(oh, ob, sizeof(ob)); memcpy(gh, gb, sizeof(gb));
    hash_g(oh, oh); hash_g(gh, gh);
    if (memcmp(oh, gh, HASH_G_OUTBYTES) != 0) {
        fprintf(stderr, "hash mismatch\n");
        return 3;
    }

    uint64_t values[MODES][2][SAMPLES];
    for (int i = 0; i < SAMPLES; i++) {
        for (int mode = 0; mode < MODES; mode++) {
            int first = (i + mode) & 1;
            values[mode][first][i] = measure_one(s, first, mode);
            values[mode][first ^ 1][i] = measure_one(s, first ^ 1, mode);
        }
    }

    const char *names[MODES] = {"raw", "mfence", "common_copy"};
    for (int mode = 0; mode < MODES; mode++) {
        for (int producer = 0; producer < 2; producer++) {
            qsort(values[mode][producer], SAMPLES, sizeof(uint64_t), cmp64);
            uint64_t median = (values[mode][producer][SAMPLES / 2 - 1] +
                               values[mode][producer][SAMPLES / 2]) / 2;
            printf("%s_%s %llu\n", names[mode], producer ? "gt" : "official",
                   (unsigned long long)median);
        }
    }
    free(s);
    return sink == UINT64_MAX;
}

