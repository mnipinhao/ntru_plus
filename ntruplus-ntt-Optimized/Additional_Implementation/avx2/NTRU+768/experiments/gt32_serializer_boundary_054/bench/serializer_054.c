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
#define PMU_ITERATIONS 200000

void off_poly_tobytes(uint8_t *out, const poly *a);
int poly_frombytes(poly *out, const uint8_t *in);

typedef struct __attribute__((aligned(64))) {
    int16_t h[NTRUPLUS_N];
    int16_t r[NTRUPLUS_N];
    int16_t m[NTRUPLUS_N];
    int16_t c[NTRUPLUS_N];
    int16_t frontend[NTRUPLUS_N];
    poly r_official;
    poly c_official;
    uint8_t output[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
    uint8_t expected_r[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
    uint8_t expected_c[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
} state_t;

static volatile uint64_t sink;

static inline uint64_t begin_ticks(void) {
    _mm_lfence();
    return __rdtsc();
}

static inline uint64_t end_ticks(void) {
    unsigned aux;
    uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static int cmp64(const void *aa, const void *bb) {
    uint64_t a = *(const uint64_t *)aa;
    uint64_t b = *(const uint64_t *)bb;
    return a > b ? 1 : a < b ? -1 : 0;
}

static void pack_pair(uint8_t out[3], uint16_t a, uint16_t b) {
    out[0] = (uint8_t)a;
    out[1] = (uint8_t)((a >> 8) | (b << 4));
    out[2] = (uint8_t)(b >> 4);
}

static void forward_m(int16_t out[NTRUPLUS_N], int16_t frontend[NTRUPLUS_N],
                      const int16_t in[NTRUPLUS_N]) {
    ntruplus768_ntt_frontend_avx2(frontend, in);
    ntruplus768_ntt_m_avx2(out, frontend);
}

static void prepare(state_t *s) {
    uint8_t pk[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
    uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
    uint8_t msg[HASH_H_INBYTES];
    uint8_t hashbuf[HASH_H_OUTBYTES];
    uint8_t r_hash[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
    poly coefficient;

    for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
        pack_pair(pk + 3 * i, (uint16_t)((37 * i + 11) % 3457),
                  (uint16_t)((91 * i + 7) % 3457));
    for (size_t i = 0; i < sizeof coins; i++)
        coins[i] = (uint8_t)(53 * i + 19);

    if (ntruplus768_unpack_m_avx2(s->h, pk) != 0) {
        fprintf(stderr, "valid public key rejected\n");
        exit(2);
    }

    memcpy(msg, coins, NTRUPLUS_N / 8);
    hash_f(msg + NTRUPLUS_N / 8, pk);
    hash_h(hashbuf, msg);
    poly_cbd1(&coefficient, hashbuf + NTRUPLUS_SYMBYTES);
    forward_m(s->r, s->frontend, coefficient.coeffs);

    ntruplus768_pack_m_lazy10788_avx2(s->expected_r, s->r);
    if (poly_frombytes(&s->r_official, s->expected_r) != 0) {
        fprintf(stderr, "Official rejected GT rhat serialization\n");
        exit(3);
    }

    memcpy(r_hash, s->expected_r, sizeof r_hash);
    hash_g(r_hash, r_hash);
    poly_sotp_encode(&coefficient, msg, r_hash);
    forward_m(s->m, s->frontend, coefficient.coeffs);
    ntruplus768_basemul_general_m_avx2(s->c, s->h, s->r);
    poly_add((poly *)(void *)s->c, (const poly *)(const void *)s->c,
             (const poly *)(const void *)s->m);
    ntruplus768_pack_m_highrange12699_avx2(s->expected_c, s->c);
    if (poly_frombytes(&s->c_official, s->expected_c) != 0) {
        fprintf(stderr, "Official rejected GT ciphertext serialization\n");
        exit(4);
    }

    off_poly_tobytes(s->output, &s->r_official);
    if (memcmp(s->output, s->expected_r, NTRUPLUS_POLYBYTES) != 0) {
        fprintf(stderr, "rhat Official/GT byte mismatch\n");
        exit(5);
    }
    off_poly_tobytes(s->output, &s->c_official);
    if (memcmp(s->output, s->expected_c, NTRUPLUS_POLYBYTES) != 0) {
        fprintf(stderr, "ciphertext Official/GT byte mismatch\n");
        exit(6);
    }
}

static void call_target(state_t *s, int site, int gt) {
    if (site == 0) {
        if (gt) ntruplus768_pack_m_lazy10788_avx2(s->output, s->r);
        else off_poly_tobytes(s->output, &s->r_official);
    } else {
        if (gt) ntruplus768_pack_m_highrange12699_avx2(s->output, s->c);
        else off_poly_tobytes(s->output, &s->c_official);
    }
}

static uint64_t measure_one(state_t *s, int site, int gt) {
    uint64_t a = begin_ticks();
    call_target(s, site, gt);
    uint64_t b = end_ticks();
    sink ^= s->output[(site * 101 + gt * 37) % NTRUPLUS_POLYBYTES];
    return b - a;
}

static uint64_t median(uint64_t values[SAMPLES]) {
    qsort(values, SAMPLES, sizeof(values[0]), cmp64);
    return (values[SAMPLES / 2 - 1] + values[SAMPLES / 2]) / 2;
}

static int target_from_name(const char *name, int *site, int *gt) {
    if (strcmp(name, "r_official") == 0) { *site = 0; *gt = 0; }
    else if (strcmp(name, "r_gt") == 0) { *site = 0; *gt = 1; }
    else if (strcmp(name, "c_official") == 0) { *site = 1; *gt = 0; }
    else if (strcmp(name, "c_gt") == 0) { *site = 1; *gt = 1; }
    else return 0;
    return 1;
}

int main(int argc, char **argv) {
    state_t *s = aligned_alloc(64, sizeof(*s));
    if (!s) return 1;
    memset(s, 0, sizeof(*s));
    prepare(s);

    if (argc == 2) {
        int site, gt;
        if (!target_from_name(argv[1], &site, &gt)) return 7;
        for (unsigned i = 0; i < 64; i++) call_target(s, site, gt);
        for (unsigned i = 0; i < PMU_ITERATIONS; i++) call_target(s, site, gt);
        sink ^= s->output[0];
        printf("%llu\n", (unsigned long long)sink);
        free(s);
        return 0;
    }

    uint64_t values[2][2][SAMPLES];
    for (int site = 0; site < 2; site++)
        for (int gt = 0; gt < 2; gt++)
            for (unsigned i = 0; i < 64; i++) call_target(s, site, gt);

    for (int i = 0; i < SAMPLES; i++) {
        for (int site = 0; site < 2; site++) {
            int first = (i + site) & 1;
            values[site][first][i] = measure_one(s, site, first);
            values[site][first ^ 1][i] = measure_one(s, site, first ^ 1);
        }
    }

    printf("r_official %llu\n", (unsigned long long)median(values[0][0]));
    printf("r_gt %llu\n", (unsigned long long)median(values[0][1]));
    printf("c_official %llu\n", (unsigned long long)median(values[1][0]));
    printf("c_gt %llu\n", (unsigned long long)median(values[1][1]));
    printf("off_pack_address %p\n", (void *)(uintptr_t)off_poly_tobytes);
    printf("gt_r_pack_address %p\n", (void *)(uintptr_t)ntruplus768_pack_m_lazy10788_avx2);
    printf("gt_c_pack_address %p\n", (void *)(uintptr_t)ntruplus768_pack_m_highrange12699_avx2);
    free(s);
    return sink == UINT64_MAX;
}
