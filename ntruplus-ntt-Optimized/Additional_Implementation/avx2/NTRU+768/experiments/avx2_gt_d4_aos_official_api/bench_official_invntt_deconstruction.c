#define _GNU_SOURCE

#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum {
    N = 768,
    Q = 3457,
    CPU = 3,
    FIXTURES = 32,
    SAMPLES = 10001,
    RANDOM_DIFFERENTIALS = 10000,
    RANGE_SAMPLES = 10000,
    WARMUP = 2048,
    REGIONS = 4
};

typedef struct {
    int16_t coeffs[N];
} poly __attribute__((aligned(32)));

extern void poly_ntt(poly *value);
extern void poly_basemul_scale(poly *out, const poly *left, const poly *right);
extern void poly_invntt_scale(poly *value);
extern void official_invntt_instrumented(poly *value);
extern void official_invntt_trace_calibrate(void);
extern uint64_t official_invntt_trace[5];

static poly fixtures[FIXTURES];
static poly output;
static uint32_t random_word = 0x9e3779b9U;

static uint32_t next_random(void)
{
    random_word = 1664525U * random_word + 1013904223U;
    return random_word;
}

static uint64_t begin_tsc(void)
{
    unsigned int low;
    unsigned int high;

    __asm__ volatile("lfence\n\trdtsc" : "=a"(low), "=d"(high) :: "memory");
    return ((uint64_t)high << 32) | low;
}

static uint64_t end_tsc(void)
{
    unsigned int low;
    unsigned int high;
    unsigned int auxiliary;

    __asm__ volatile("rdtscp\n\tlfence"
                     : "=a"(low), "=d"(high), "=c"(auxiliary) :: "memory");
    return ((uint64_t)high << 32) | low;
}

static int compare_u64(const void *left, const void *right)
{
    const uint64_t a = *(const uint64_t *)left;
    const uint64_t b = *(const uint64_t *)right;

    return (a > b) - (a < b);
}

static int mod_q(int value)
{
    value %= Q;
    return value < 0 ? value + Q : value;
}

static int clone_differential(void)
{
    poly official;
    poly clone;

    for (int lane = 0; lane < N; ++lane) {
        memset(&official, 0, sizeof(official));
        official.coeffs[lane] = 1;
        clone = official;
        poly_invntt_scale(&official);
        official_invntt_instrumented(&clone);
        if (memcmp(&official, &clone, sizeof(official)) != 0) {
            fprintf(stderr, "clone mismatch basis lane=%d\n", lane);
            return 0;
        }
    }
    for (int test = 0; test < RANDOM_DIFFERENTIALS; ++test) {
        for (int lane = 0; lane < N; ++lane) {
            official.coeffs[lane] = (int16_t)next_random();
        }
        clone = official;
        poly_invntt_scale(&official);
        official_invntt_instrumented(&clone);
        if (memcmp(&official, &clone, sizeof(official)) != 0) {
            fprintf(stderr, "clone mismatch random test=%d\n", test);
            return 0;
        }
    }
    return 1;
}

static int contract_observation(void)
{
    int ntt_min = 32767;
    int ntt_max = -32768;
    int basemul_min = 32767;
    int basemul_max = -32768;
    int inverse_min = 32767;
    int inverse_max = -32768;
    int alias_left_supported = 1;
    int alias_right_supported = 1;

    for (int test = 0; test < RANGE_SAMPLES; ++test) {
        poly left;
        poly right;
        poly product;
        poly alias_left;
        poly alias_right;

        for (int lane = 0; lane < N; ++lane) {
            left.coeffs[lane] = (int16_t)((int)(next_random() % 7U) - 3);
            right.coeffs[lane] = (int16_t)((int)(next_random() % 7U) - 3);
        }
        poly_ntt(&left);
        poly_ntt(&right);
        for (int lane = 0; lane < N; ++lane) {
            if (left.coeffs[lane] < ntt_min) {
                ntt_min = left.coeffs[lane];
            }
            if (left.coeffs[lane] > ntt_max) {
                ntt_max = left.coeffs[lane];
            }
        }
        poly_basemul_scale(&product, &left, &right);
        alias_left = left;
        alias_right = right;
        poly_basemul_scale(&alias_left, &alias_left, &right);
        poly_basemul_scale(&alias_right, &left, &alias_right);
        alias_left_supported &= memcmp(&product, &alias_left, sizeof(product)) == 0;
        alias_right_supported &= memcmp(&product, &alias_right, sizeof(product)) == 0;
        for (int lane = 0; lane < N; ++lane) {
            if (product.coeffs[lane] < basemul_min) {
                basemul_min = product.coeffs[lane];
            }
            if (product.coeffs[lane] > basemul_max) {
                basemul_max = product.coeffs[lane];
            }
        }
        poly_invntt_scale(&product);
        for (int lane = 0; lane < N; ++lane) {
            if (product.coeffs[lane] < inverse_min) {
                inverse_min = product.coeffs[lane];
            }
            if (product.coeffs[lane] > inverse_max) {
                inverse_max = product.coeffs[lane];
            }
            if (mod_q(product.coeffs[lane]) >= Q) {
                return 0;
            }
        }
    }
    printf("contract-observed ntt=[%d,%d] basemul-scale=[%d,%d] inverse=[%d,%d] "
           "basemul-alias-left=%s basemul-alias-right=%s invntt-inplace=required\n",
           ntt_min, ntt_max, basemul_min, basemul_max, inverse_min, inverse_max,
           alias_left_supported ? "supported" : "unsupported",
           alias_right_supported ? "supported" : "unsupported");
    return 1;
}

static int benchmark(void)
{
    static uint64_t official_samples[SAMPLES];
    static uint64_t clone_samples[SAMPLES];
    static uint64_t region_samples[REGIONS][SAMPLES];
    static uint64_t overhead_samples[REGIONS][SAMPLES];
    cpu_set_t affinity;

    CPU_ZERO(&affinity);
    CPU_SET(CPU, &affinity);
    if (sched_setaffinity(0, sizeof(affinity), &affinity) != 0) {
        perror("sched_setaffinity");
        return 0;
    }
    for (int fixture = 0; fixture < FIXTURES; ++fixture) {
        poly left;
        poly right;

        for (int lane = 0; lane < N; ++lane) {
            left.coeffs[lane] = (int16_t)((int)(next_random() % 7U) - 3);
            right.coeffs[lane] = (int16_t)((int)(next_random() % 7U) - 3);
        }
        poly_ntt(&left);
        poly_ntt(&right);
        poly_basemul_scale(&fixtures[fixture], &left, &right);
    }
    for (int warm = 0; warm < WARMUP; ++warm) {
        output = fixtures[warm & (FIXTURES - 1)];
        if ((warm & 1) == 0) {
            poly_invntt_scale(&output);
        } else {
            official_invntt_instrumented(&output);
        }
    }
    for (int sample = 0; sample < SAMPLES; ++sample) {
        const int fixture = (17 * sample + 9) & (FIXTURES - 1);
        uint64_t start;

        official_invntt_trace_calibrate();
        for (int region = 0; region < REGIONS; ++region) {
            overhead_samples[region][sample] =
                official_invntt_trace[region + 1] - official_invntt_trace[region];
        }
        if ((sample & 1) == 0) {
            output = fixtures[fixture];
            start = begin_tsc();
            poly_invntt_scale(&output);
            official_samples[sample] = end_tsc() - start;
            output = fixtures[fixture];
            start = begin_tsc();
            official_invntt_instrumented(&output);
            clone_samples[sample] = end_tsc() - start;
        } else {
            output = fixtures[fixture];
            start = begin_tsc();
            official_invntt_instrumented(&output);
            clone_samples[sample] = end_tsc() - start;
            output = fixtures[fixture];
            start = begin_tsc();
            poly_invntt_scale(&output);
            official_samples[sample] = end_tsc() - start;
        }
        for (int region = 0; region < REGIONS; ++region) {
            region_samples[region][sample] =
                official_invntt_trace[region + 1] - official_invntt_trace[region];
        }
    }
    qsort(official_samples, SAMPLES, sizeof(uint64_t), compare_u64);
    qsort(clone_samples, SAMPLES, sizeof(uint64_t), compare_u64);
    printf("full-official median=%llu p10=%llu p90=%llu\n",
           (unsigned long long)official_samples[SAMPLES / 2],
           (unsigned long long)official_samples[SAMPLES / 10],
           (unsigned long long)official_samples[9 * SAMPLES / 10]);
    printf("full-instrumented median=%llu p10=%llu p90=%llu\n",
           (unsigned long long)clone_samples[SAMPLES / 2],
           (unsigned long long)clone_samples[SAMPLES / 10],
           (unsigned long long)clone_samples[9 * SAMPLES / 10]);
    for (int region = 0; region < REGIONS; ++region) {
        qsort(region_samples[region], SAMPLES, sizeof(uint64_t), compare_u64);
        qsort(overhead_samples[region], SAMPLES, sizeof(uint64_t), compare_u64);
        const uint64_t raw = region_samples[region][SAMPLES / 2];
        const uint64_t overhead = overhead_samples[region][SAMPLES / 2];

        printf("region%d raw=%llu checkpoint-overhead=%llu adjusted=%lld\n",
               region, (unsigned long long)raw, (unsigned long long)overhead,
               (long long)raw - (long long)overhead);
    }
    return 1;
}

int main(void)
{
    if (!clone_differential()) {
        return 1;
    }
    puts("instrumented-clone=byte-exact basis=768 random=10000");
    if (!contract_observation() || !benchmark()) {
        return 1;
    }
    return 0;
}
