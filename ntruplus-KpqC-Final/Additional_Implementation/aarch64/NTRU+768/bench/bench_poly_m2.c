// bench_poly_m2.c
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include "../poly.h"

// from your m1cycles.c
void __m1_setup_rdtsc(void);
unsigned long long __m1_rdtsc(void);

#define WARMUP 20000
#define ITERS  200000
#define RUNS   31

static volatile uint64_t sink64;
static volatile int sinki;

static int cmp_u64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

static inline uint64_t rdcycle(void) {
    return (uint64_t)__m1_rdtsc();
}

static uint64_t empty_loop_cost(void) {
    uint64_t t0 = rdcycle();
    for (int i = 0; i < ITERS; i++) {
        sink64 += (uint64_t)i;
    }
    uint64_t t1 = rdcycle();
    return (t1 - t0);
}

static uint64_t bench_poly_cbd1(const uint8_t buf[NTRUPLUS_N / 4], uint64_t base) {
    poly r;
    for (int i = 0; i < WARMUP; i++) poly_cbd1(&r, buf);

    uint64_t t0 = rdcycle();
    for (int i = 0; i < ITERS; i++) {
        poly_cbd1(&r, buf);
        sink64 += (uint16_t)r.coeffs[i & (NTRUPLUS_N - 1)];
    }
    uint64_t t1 = rdcycle();

    uint64_t total = t1 - t0;
    if (total > base) total -= base;
    return total / ITERS;
}

static uint64_t bench_poly_sotp_encode(const uint8_t msg[NTRUPLUS_N / 8],
                                       const uint8_t buf[NTRUPLUS_N / 4],
                                       uint64_t base) {
    poly r;
    for (int i = 0; i < WARMUP; i++) poly_sotp_encode(&r, msg, buf);

    uint64_t t0 = rdcycle();
    for (int i = 0; i < ITERS; i++) {
        poly_sotp_encode(&r, msg, buf);
        sink64 += (uint16_t)r.coeffs[(i * 7) & (NTRUPLUS_N - 1)];
    }
    uint64_t t1 = rdcycle();

    uint64_t total = t1 - t0;
    if (total > base) total -= base;
    return total / ITERS;
}

static uint64_t bench_poly_sotp_decode(const poly *a,
                                       const uint8_t buf[NTRUPLUS_N / 4],
                                       uint64_t base) {
    uint8_t msg[NTRUPLUS_N / 8];
    memset(msg, 0, sizeof msg);

    for (int i = 0; i < WARMUP; i++) sinki ^= poly_sotp_decode(msg, a, buf);

    uint64_t t0 = rdcycle();
    for (int i = 0; i < ITERS; i++) {
        int ret = poly_sotp_decode(msg, a, buf);
        sinki ^= ret;
        sink64 += msg[i & ((NTRUPLUS_N / 8) - 1)];
    }
    uint64_t t1 = rdcycle();

    uint64_t total = t1 - t0;
    if (total > base) total -= base;
    return total / ITERS;
}

int main(void) {
    // bias to P-cores
    pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
    __m1_setup_rdtsc();

    uint8_t buf[NTRUPLUS_N / 4];
    uint8_t msg[NTRUPLUS_N / 8];
    poly a;

    for (size_t i = 0; i < sizeof buf; i++) buf[i] = (uint8_t)(i * 13 + 7);
    for (size_t i = 0; i < sizeof msg; i++) msg[i] = (uint8_t)(i * 29 + 3);

    poly_sotp_encode(&a, msg, buf); // create plausible input poly for decode

    uint64_t cbd[RUNS], enc[RUNS], dec[RUNS];
    for (int r = 0; r < RUNS; r++) {
        uint64_t base = empty_loop_cost();
        cbd[r] = bench_poly_cbd1(buf, base);
        enc[r] = bench_poly_sotp_encode(msg, buf, base);
        dec[r] = bench_poly_sotp_decode(&a, buf, base);
    }

    qsort(cbd, RUNS, sizeof(uint64_t), cmp_u64);
    qsort(enc, RUNS, sizeof(uint64_t), cmp_u64);
    qsort(dec, RUNS, sizeof(uint64_t), cmp_u64);

    printf("poly_cbd1        median cycles/call: %llu\n", (unsigned long long)cbd[RUNS / 2]);
    printf("poly_sotp_encode median cycles/call: %llu\n", (unsigned long long)enc[RUNS / 2]);
    printf("poly_sotp_decode median cycles/call: %llu\n", (unsigned long long)dec[RUNS / 2]);

    return (int)(sink64 ^ (uint64_t)sinki);
}