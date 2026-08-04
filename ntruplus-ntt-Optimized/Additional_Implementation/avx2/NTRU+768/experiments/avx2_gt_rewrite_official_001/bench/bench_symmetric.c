#define _GNU_SOURCE
#include <errno.h>
#include <immintrin.h>
#include <inttypes.h>
#include <math.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt_backend.h"
#include "fips202/fips202.h"
#include "kat/rng.h"
#include "poly.h"
#include "symmetric.h"

enum { MAX_SAMPLES = 64, CANDIDATE_COUNT = 20 };

typedef struct {
    poly coefficient;
    poly official_frequency;
    poly gt_frequency;
    poly official_product;
    poly gt_product;
    poly official_work;
    poly gt_work;
    uint8_t encoded[NTRUPLUS_POLYBYTES];
    uint8_t buffer[NTRUPLUS_POLYBYTES];
    uint8_t message[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
} context;

typedef void (*bench_fn)(context *);

typedef struct {
    const char *name;
    bench_fn official;
    bench_fn gt;
    double official_samples[MAX_SAMPLES];
    double gt_samples[MAX_SAMPLES];
} candidate;

static volatile uint64_t checksum_sink;

static uint64_t ticks(void)
{
    unsigned aux;
    _mm_lfence();
    const uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static int pin_cpu1(void)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(1, &set);
    return sched_setaffinity(0, sizeof set, &set);
}

static int compare_double(const void *left, const void *right)
{
    const double a = *(const double *)left;
    const double b = *(const double *)right;
    return (a > b) - (a < b);
}

static double median(const double *values, unsigned count)
{
    double copy[MAX_SAMPLES];
    memcpy(copy, values, count * sizeof *copy);
    qsort(copy, count, sizeof *copy, compare_double);
    return (count & 1U) != 0 ? copy[count / 2]
        : (copy[count / 2 - 1] + copy[count / 2]) / 2.0;
}

static double mad(const double *values, unsigned count, double center)
{
    double deviations[MAX_SAMPLES];
    for (unsigned i = 0; i < count; ++i)
        deviations[i] = fabs(values[i] - center);
    return median(deviations, count);
}

static void official_ntt(context *c) { poly_ntt(&c->official_work); }
static void gt_ntt(context *c) { gt_poly_ntt(&c->gt_work); }
static void official_basemul(context *c)
{
    poly_basemul(&c->official_work, &c->official_frequency,
                 &c->official_frequency);
}
static void gt_basemul(context *c)
{
    gt_poly_basemul(&c->gt_work, &c->gt_frequency, &c->gt_frequency);
}
static void official_basemul_scale(context *c)
{
    poly_basemul_scale(&c->official_work, &c->official_frequency,
                       &c->official_frequency);
}
static void gt_basemul_scale(context *c)
{
    gt_poly_basemul_scale(&c->gt_work, &c->gt_frequency, &c->gt_frequency);
}
static void official_baseinv(context *c)
{
    (void)poly_baseinv(&c->official_work, &c->official_frequency);
}
static void gt_baseinv(context *c)
{
    (void)gt_poly_baseinv(&c->gt_work, &c->gt_frequency);
}
static void official_invntt(context *c)
{
    poly_invntt_scale(&c->official_work);
}
static void gt_invntt(context *c)
{
    gt_poly_invntt_scale(&c->gt_work);
}
static void official_tobytes(context *c)
{
    poly_tobytes(c->encoded, &c->official_frequency);
}
static void gt_tobytes(context *c)
{
    gt_poly_tobytes(c->encoded, &c->gt_frequency);
}
static void official_frombytes(context *c)
{
    (void)poly_frombytes(&c->official_work, c->encoded);
}
static void gt_frombytes(context *c)
{
    (void)gt_poly_frombytes(&c->gt_work, c->encoded);
}
static void common_add(context *c)
{
    poly_add(&c->official_work, &c->official_frequency,
             &c->official_frequency);
}
static void common_sub(context *c)
{
    poly_sub(&c->official_work, &c->official_frequency,
             &c->official_frequency);
}
static void common_cbd1(context *c)
{
    poly_cbd1(&c->official_work, c->buffer);
}
static void common_triple(context *c) { poly_triple(&c->official_work); }
static void common_crepmod3(context *c) { poly_crepmod3(&c->official_work); }
static void common_sotp_encode(context *c)
{
    poly_sotp_encode(&c->official_work, c->message, c->buffer);
}
static void common_sotp_decode(context *c)
{
    (void)poly_sotp_decode(c->message, &c->coefficient, c->buffer);
}
static void common_hash_f(context *c) { hash_f(c->buffer, c->encoded); }
static void common_hash_g(context *c) { hash_g(c->buffer, c->encoded); }
static void common_hash_h(context *c) { hash_h(c->buffer, c->message); }
static void common_shake256(context *c)
{
    shake256(c->buffer, NTRUPLUS_N / 4, c->message, 32);
}
static void common_randombytes32(context *c)
{
    (void)randombytes(c->buffer, 32);
}
static void common_randombytes96(context *c)
{
    (void)randombytes(c->buffer, NTRUPLUS_N / 8);
}

static double measure(bench_fn fn, uint64_t iterations, context *c)
{
    const uint64_t begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        fn(c);
    const uint64_t end = ticks();
    const uint16_t *words = (const uint16_t *)c;
    uint64_t checksum = 0;
    for (size_t i = 0; i < sizeof *c / sizeof *words; i += 97)
        checksum = checksum * UINT64_C(1315423911) + words[i];
    checksum_sink += checksum;
    return (double)(end - begin) / (double)iterations;
}

static int initialize(context *c)
{
    memset(c, 0, sizeof *c);
    for (size_t i = 0; i < NTRUPLUS_N; ++i)
        c->coefficient.coeffs[i] = (int16_t)((int)(i % 8U) - 3);
    for (size_t i = 0; i < sizeof c->buffer; ++i)
        c->buffer[i] = (uint8_t)(31U * i + 7U);
    for (size_t i = 0; i < sizeof c->message; ++i)
        c->message[i] = (uint8_t)(17U * i + 11U);
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; ++i)
        entropy[i] = (unsigned char)(13U * i + 5U);
    randombytes_init(entropy, NULL, 256);
    c->official_frequency = c->coefficient;
    c->gt_frequency = c->coefficient;
    poly_ntt(&c->official_frequency);
    gt_poly_ntt(&c->gt_frequency);
    uint8_t official_bytes[NTRUPLUS_POLYBYTES];
    uint8_t gt_bytes[NTRUPLUS_POLYBYTES];
    poly_tobytes(official_bytes, &c->official_frequency);
    gt_poly_tobytes(gt_bytes, &c->gt_frequency);
    if (memcmp(official_bytes, gt_bytes, sizeof official_bytes) != 0)
        return 0;
    memcpy(c->encoded, official_bytes, sizeof c->encoded);
    poly_basemul_scale(&c->official_product, &c->official_frequency,
                       &c->official_frequency);
    gt_poly_basemul_scale(&c->gt_product, &c->gt_frequency, &c->gt_frequency);
    c->official_work = c->official_frequency;
    c->gt_work = c->gt_frequency;
    return 1;
}

int main(int argc, char **argv)
{
    uint64_t iterations = UINT64_C(1000000);
    unsigned samples = 20;
    const char *selected = "all";
    const char *backend = "paired";
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--iterations") == 0 && i + 1 < argc)
            iterations = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--samples") == 0 && i + 1 < argc)
            samples = (unsigned)strtoul(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--candidate") == 0 && i + 1 < argc)
            selected = argv[++i];
        else if (strcmp(argv[i], "--backend") == 0 && i + 1 < argc)
            backend = argv[++i];
        else {
            fprintf(stderr, "usage: %s [--iterations N] [--samples N] "
                    "[--candidate all|NAME] "
                    "[--backend paired|official|gt]\n", argv[0]);
            return 2;
        }
    }
    if (iterations == 0 || samples == 0 || samples > MAX_SAMPLES) return 2;
    if (strcmp(backend, "paired") != 0 && strcmp(backend, "official") != 0
        && strcmp(backend, "gt") != 0) return 2;
    if (pin_cpu1() != 0) {
        fprintf(stderr, "sched_setaffinity(cpu=1): %s\n", strerror(errno));
        return 2;
    }

    candidate candidates[CANDIDATE_COUNT] = {
        {"ntt", official_ntt, gt_ntt, {0}, {0}},
        {"basemul", official_basemul, gt_basemul, {0}, {0}},
        {"basemul_scale", official_basemul_scale, gt_basemul_scale, {0}, {0}},
        {"baseinv", official_baseinv, gt_baseinv, {0}, {0}},
        {"invntt", official_invntt, gt_invntt, {0}, {0}},
        {"tobytes", official_tobytes, gt_tobytes, {0}, {0}},
        {"frombytes", official_frombytes, gt_frombytes, {0}, {0}},
        {"add", common_add, NULL, {0}, {0}},
        {"sub", common_sub, NULL, {0}, {0}},
        {"cbd1", common_cbd1, NULL, {0}, {0}},
        {"triple", common_triple, NULL, {0}, {0}},
        {"crepmod3", common_crepmod3, NULL, {0}, {0}},
        {"sotp_encode", common_sotp_encode, NULL, {0}, {0}},
        {"sotp_decode", common_sotp_decode, NULL, {0}, {0}},
        {"hash_f", common_hash_f, NULL, {0}, {0}},
        {"hash_g", common_hash_g, NULL, {0}, {0}},
        {"hash_h", common_hash_h, NULL, {0}, {0}},
        {"shake256", common_shake256, NULL, {0}, {0}},
        {"randombytes32", common_randombytes32, NULL, {0}, {0}},
        {"randombytes96", common_randombytes96, NULL, {0}, {0}},
    };
    context c;
    if (!initialize(&c)) return 1;

    size_t first = 0, last = CANDIDATE_COUNT;
    if (strcmp(selected, "all") != 0) {
        while (first < CANDIDATE_COUNT
               && strcmp(selected, candidates[first].name) != 0) ++first;
        if (first == CANDIDATE_COUNT) return 2;
        last = first + 1;
    }
    if (strcmp(backend, "gt") == 0) {
        for (size_t i = first; i < last; ++i)
            if (candidates[i].gt == NULL) return 2;
    }
    for (size_t i = first; i < last; ++i) {
        for (unsigned warmup = 0; warmup < 2; ++warmup) {
            if (strcmp(backend, "gt") != 0)
                (void)measure(candidates[i].official, iterations, &c);
            if (candidates[i].gt != NULL
                && strcmp(backend, "official") != 0)
                (void)measure(candidates[i].gt, iterations, &c);
        }
        for (unsigned sample = 0; sample < samples; ++sample) {
            if (strcmp(backend, "official") == 0
                || candidates[i].gt == NULL) {
                candidates[i].official_samples[sample] = measure(
                    candidates[i].official, iterations, &c);
            } else if (strcmp(backend, "gt") == 0) {
                candidates[i].gt_samples[sample] = measure(
                    candidates[i].gt, iterations, &c);
            } else if ((sample & 1U) == 0) {
                candidates[i].official_samples[sample] = measure(
                    candidates[i].official, iterations, &c);
                candidates[i].gt_samples[sample] = measure(
                    candidates[i].gt, iterations, &c);
            } else {
                candidates[i].gt_samples[sample] = measure(
                    candidates[i].gt, iterations, &c);
                candidates[i].official_samples[sample] = measure(
                    candidates[i].official, iterations, &c);
            }
        }
    }

    printf("{\n  \"schema_version\": 1,\n");
    printf("  \"candidate\": \"%s\",\n", selected);
    printf("  \"backend_mode\": \"%s\",\n", backend);
    printf("  \"cpu\": 1, \"iterations_per_sample\": %" PRIu64
           ", \"warmups\": 2, \"samples\": %u,\n", iterations, samples);
    printf("  \"costs\": {\n");
    for (size_t i = first; i < last; ++i) {
        printf("    \"%s\": {", candidates[i].name);
        int need_comma = 0;
        double om = 0.0;
        if (strcmp(backend, "gt") != 0) {
            om = median(candidates[i].official_samples, samples);
            const double oa = mad(candidates[i].official_samples, samples, om);
            printf("\"official\": {\"median_cycles\": %.3f, "
                   "\"mad_cycles\": %.3f}", om, oa);
            need_comma = 1;
        }
        if (candidates[i].gt != NULL
            && strcmp(backend, "official") != 0) {
            const double gm = median(candidates[i].gt_samples, samples);
            const double ga = mad(candidates[i].gt_samples, samples, gm);
            printf("%s\"gt\": {\"median_cycles\": %.3f, "
                   "\"mad_cycles\": %.3f}", need_comma ? ", " : "",
                   gm, ga);
            if (strcmp(backend, "paired") == 0)
                printf(", \"delta_cycles\": %.3f", gm - om);
            need_comma = 1;
        }
        if (candidates[i].gt == NULL)
            printf("%s\"classification\": \"common_kem\"",
                   need_comma ? ", " : "");
        printf("}%s\n", i + 1 == last ? "" : ",");
    }
    printf("  },\n  \"checksum\": \"%016" PRIx64 "\"\n}\n",
           checksum_sink);
    return 0;
}
