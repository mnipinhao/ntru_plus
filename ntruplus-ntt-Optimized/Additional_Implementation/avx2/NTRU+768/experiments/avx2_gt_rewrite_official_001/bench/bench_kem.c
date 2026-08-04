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

#include "api.h"
#include "kat/rng.h"

int gt_crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
int gt_crypto_kem_enc(unsigned char *ct, unsigned char *ss,
                      const unsigned char *pk);
int gt_crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
                      const unsigned char *sk);

enum { DEFAULT_SAMPLES = 20, MAX_SAMPLES = 64 };

typedef struct {
    const char *name;
    int (*keypair)(unsigned char *, unsigned char *);
    int (*enc)(unsigned char *, unsigned char *, const unsigned char *);
    int (*dec)(unsigned char *, const unsigned char *, const unsigned char *);
} kem_backend;

typedef struct {
    double keypair;
    double enc;
    double dec;
    double total;
} sample_result;

static volatile uint64_t checksum_sink;

static uint64_t ticks(void)
{
    unsigned aux;
    _mm_lfence();
    const uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static void reset_rng(unsigned domain, unsigned sample)
{
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; ++i)
        entropy[i] = (unsigned char)(i + 43U * domain + 109U * sample);
    randombytes_init(entropy, NULL, 256);
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
    if ((count & 1U) != 0)
        return copy[count / 2];
    return (copy[count / 2 - 1] + copy[count / 2]) / 2.0;
}

static double mad(const double *values, unsigned count, double center)
{
    double deviations[MAX_SAMPLES];
    for (unsigned i = 0; i < count; ++i)
        deviations[i] = fabs(values[i] - center);
    return median(deviations, count);
}

static void absorb(const unsigned char *data, size_t length)
{
    uint64_t value = checksum_sink;
    for (size_t i = 0; i < length; i += 97)
        value = value * UINT64_C(1315423911) + data[i];
    checksum_sink = value;
}

static double measure_keypair(const kem_backend *backend, uint64_t iterations,
                              unsigned sample)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    reset_rng(11, sample);
    const uint64_t begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        (void)backend->keypair(pk, sk);
    const uint64_t end = ticks();
    absorb(pk, sizeof pk);
    absorb(sk, sizeof sk);
    return (double)(end - begin) / (double)iterations;
}

static double measure_enc(const kem_backend *backend, uint64_t iterations,
                          unsigned sample, const unsigned char *pk)
{
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char ss[CRYPTO_BYTES];
    reset_rng(13, sample);
    const uint64_t begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        (void)backend->enc(ct, ss, pk);
    const uint64_t end = ticks();
    absorb(ct, sizeof ct);
    absorb(ss, sizeof ss);
    return (double)(end - begin) / (double)iterations;
}

static double measure_dec(const kem_backend *backend, uint64_t iterations,
                          const unsigned char *ct, const unsigned char *sk)
{
    unsigned char ss[CRYPTO_BYTES];
    const uint64_t begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        (void)backend->dec(ss, ct, sk);
    const uint64_t end = ticks();
    absorb(ss, sizeof ss);
    return (double)(end - begin) / (double)iterations;
}

static sample_result measure_backend(const kem_backend *backend,
                                     uint64_t iterations, unsigned sample,
                                     const unsigned char *pk,
                                     const unsigned char *sk,
                                     const unsigned char *ct)
{
    sample_result result;
    result.keypair = measure_keypair(backend, iterations, sample);
    result.enc = measure_enc(backend, iterations, sample, pk);
    result.dec = measure_dec(backend, iterations, ct, sk);
    result.total = result.keypair + result.enc + result.dec;
    return result;
}

static void collect(const sample_result values[MAX_SAMPLES], unsigned count,
                    sample_result *medians, sample_result *mads)
{
    double field[MAX_SAMPLES];
#define COLLECT(member) do { \
        for (unsigned i = 0; i < count; ++i) field[i] = values[i].member; \
        medians->member = median(field, count); \
        mads->member = mad(field, count, medians->member); \
    } while (0)
    COLLECT(keypair);
    COLLECT(enc);
    COLLECT(dec);
    COLLECT(total);
#undef COLLECT
}

static double percent(double candidate, double baseline)
{
    return 100.0 * (candidate - baseline) / baseline;
}

int main(int argc, char **argv)
{
    uint64_t iterations = 100;
    unsigned samples = DEFAULT_SAMPLES;
    const char *candidate = "paired";
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--iterations") == 0 && i + 1 < argc)
            iterations = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--samples") == 0 && i + 1 < argc)
            samples = (unsigned)strtoul(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--candidate") == 0 && i + 1 < argc)
            candidate = argv[++i];
        else {
            fprintf(stderr,
                    "usage: %s [--iterations N] [--samples N] [--candidate paired|official|gt]\n",
                    argv[0]);
            return 2;
        }
    }
    if (iterations == 0 || samples == 0 || samples > MAX_SAMPLES) {
        fprintf(stderr, "invalid benchmark dimensions\n");
        return 2;
    }
    if (pin_cpu1() != 0) {
        fprintf(stderr, "sched_setaffinity(cpu=1): %s\n", strerror(errno));
        return 2;
    }

    const kem_backend official = {
        "official", crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec
    };
    const kem_backend gt = {
        "gt", gt_crypto_kem_keypair, gt_crypto_kem_enc, gt_crypto_kem_dec
    };
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char ss[CRYPTO_BYTES];
    reset_rng(17, 0);
    if (official.keypair(pk, sk) != 0) return 1;
    reset_rng(19, 0);
    if (official.enc(ct, ss, pk) != 0) return 1;

    if (strcmp(candidate, "official") == 0 || strcmp(candidate, "gt") == 0) {
        const kem_backend *selected = strcmp(candidate, "official") == 0
            ? &official : &gt;
        for (unsigned warmup = 0; warmup < 2; ++warmup)
            (void)measure_backend(selected, iterations, warmup, pk, sk, ct);
        sample_result values[MAX_SAMPLES];
        for (unsigned sample = 0; sample < samples; ++sample)
            values[sample] = measure_backend(
                selected, iterations, sample + 2, pk, sk, ct);
        sample_result medians;
        sample_result mads;
        collect(values, samples, &medians, &mads);
        printf("{\n");
        printf("  \"schema_version\": 1,\n");
        printf("  \"candidate\": \"%s\",\n", selected->name);
        printf("  \"cpu\": 1,\n");
        printf("  \"iterations_per_operation_per_sample\": %" PRIu64 ",\n",
               iterations);
        printf("  \"warmups\": 2,\n");
        printf("  \"samples\": %u,\n", samples);
        printf("  \"keypair\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
               medians.keypair, mads.keypair);
        printf("  \"encap\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
               medians.enc, mads.enc);
        printf("  \"decap\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
               medians.dec, mads.dec);
        printf("  \"total\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
               medians.total, mads.total);
        printf("  \"checksum\": \"%016" PRIx64 "\"\n", checksum_sink);
        printf("}\n");
        return 0;
    }
    if (strcmp(candidate, "paired") != 0) {
        fprintf(stderr, "candidate must be paired, official, or gt\n");
        return 2;
    }

    for (unsigned warmup = 0; warmup < 2; ++warmup) {
        (void)measure_backend(&official, iterations, warmup, pk, sk, ct);
        (void)measure_backend(&gt, iterations, warmup, pk, sk, ct);
    }

    sample_result official_samples[MAX_SAMPLES];
    sample_result gt_samples[MAX_SAMPLES];
    for (unsigned sample = 0; sample < samples; ++sample) {
        if ((sample & 1U) == 0) {
            official_samples[sample] = measure_backend(
                &official, iterations, sample + 2, pk, sk, ct);
            gt_samples[sample] = measure_backend(
                &gt, iterations, sample + 2, pk, sk, ct);
        } else {
            gt_samples[sample] = measure_backend(
                &gt, iterations, sample + 2, pk, sk, ct);
            official_samples[sample] = measure_backend(
                &official, iterations, sample + 2, pk, sk, ct);
        }
    }

    sample_result official_median;
    sample_result official_mad;
    sample_result gt_median;
    sample_result gt_mad;
    collect(official_samples, samples, &official_median, &official_mad);
    collect(gt_samples, samples, &gt_median, &gt_mad);
    const double keypair_delta = percent(gt_median.keypair, official_median.keypair);
    const double enc_delta = percent(gt_median.enc, official_median.enc);
    const double dec_delta = percent(gt_median.dec, official_median.dec);
    const double total_delta = percent(gt_median.total, official_median.total);
    const int performance_gate = total_delta < 0.0
        && keypair_delta <= 1.0 && enc_delta <= 1.0 && dec_delta <= 1.0;

    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"cpu\": 1,\n");
    printf("  \"iterations_per_operation_per_sample\": %" PRIu64 ",\n", iterations);
    printf("  \"warmups\": 2,\n");
    printf("  \"paired_samples\": %u,\n", samples);
#define PRINT_BACKEND(label, med, dispersion) \
    printf("  \"%s\": {\"keypair\": {\"median_cycles\": %.3f, " \
           "\"mad_cycles\": %.3f}, \"encap\": {\"median_cycles\": %.3f, " \
           "\"mad_cycles\": %.3f}, \"decap\": {\"median_cycles\": %.3f, " \
           "\"mad_cycles\": %.3f}, \"total\": {\"median_cycles\": %.3f, " \
           "\"mad_cycles\": %.3f}},\n", label, (med).keypair, \
           (dispersion).keypair, (med).enc, (dispersion).enc, (med).dec, \
           (dispersion).dec, (med).total, (dispersion).total)
    PRINT_BACKEND(official.name, official_median, official_mad);
    PRINT_BACKEND(gt.name, gt_median, gt_mad);
#undef PRINT_BACKEND
    printf("  \"gt_delta_percent\": {\"keypair\": %.3f, \"encap\": %.3f, "
           "\"decap\": %.3f, \"total\": %.3f},\n",
           keypair_delta, enc_delta, dec_delta, total_delta);
    printf("  \"performance_gate\": \"%s\",\n",
           performance_gate ? "pass" : "fail");
    printf("  \"checksum\": \"%016" PRIx64 "\"\n", checksum_sink);
    printf("}\n");
    return 0;
}
