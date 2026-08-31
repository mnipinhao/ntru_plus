#include "gt864_fr0_asm.h"
#include "../gt_boundary_cost_campaign/gt864_boundary.h"

#include <inttypes.h>
#include <mach/mach_time.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define SAMPLES 41
#define ITERATIONS 5000
#define VARIANTS 2
#define Q 3457

typedef void (*kernel)(int16_t *, const int16_t *);

struct variant {
    const char *name;
    kernel fn;
};

static volatile uint64_t sink;

static uint64_t ticks_to_ns(uint64_t ticks)
{
    static mach_timebase_info_data_t info;
    if (info.denom == 0)
        mach_timebase_info(&info);
    return ticks * info.numer / info.denom;
}

static int compare_u64(const void *left, const void *right)
{
    uint64_t a = *(const uint64_t *)left;
    uint64_t b = *(const uint64_t *)right;
    return (a > b) - (a < b);
}

int main(void)
{
    static int16_t input[GT864_FR0_INPUT_COEFFICIENTS]
        __attribute__((aligned(64)));
    static int16_t output[GT864_FR0_OUTPUT_COEFFICIENTS]
        __attribute__((aligned(64)));
    static const struct variant variants[VARIANTS] = {
        {"M4_FR0_intrinsic", gt864_boundary_fr0},
        {"M5A_FR0_stackless_block_asm", gt864_boundary_fr0_asm},
    };
    uint64_t samples[VARIANTS][SAMPLES];
    uint32_t state = 864;

    for (int i = 0; i < GT864_FR0_INPUT_COEFFICIENTS; i++) {
        state = state * 1664525u + 1013904223u;
        input[i] = (int16_t)((state % Q) - Q / 2);
    }
    for (int column = 0; column < 16; column++) {
        input[768 + column * 8 + 6] = 0;
        input[768 + column * 8 + 7] = 0;
    }
    for (int variant = 0; variant < VARIANTS; variant++)
        for (int warmup = 0; warmup < 100; warmup++)
            variants[variant].fn(output, input);

    for (int sample = 0; sample < SAMPLES; sample++) {
        for (int slot = 0; slot < VARIANTS; slot++) {
            int variant = (sample + slot) % VARIANTS;
            uint64_t start = mach_continuous_time();

            for (int iteration = 0; iteration < ITERATIONS; iteration++)
                variants[variant].fn(output, input);
            samples[variant][sample] =
                ticks_to_ns(mach_continuous_time() - start);
            sink += (uint16_t)output[(sample * 17) %
                                     GT864_FR0_OUTPUT_COEFFICIENTS];
        }
    }

    printf("authority=diagnostic_only_not_SUPERCOP\n");
    printf("execution_order=sample_rotated\n");
    for (int variant = 0; variant < VARIANTS; variant++) {
        qsort(samples[variant], SAMPLES, sizeof(uint64_t), compare_u64);
        printf("timing,name=%s,unit=ns_per_call,q1=%.3f,median=%.3f,q3=%.3f,"
               "samples=%d,iterations=%d\n",
               variants[variant].name,
               (double)samples[variant][SAMPLES / 4] / ITERATIONS,
               (double)samples[variant][SAMPLES / 2] / ITERATIONS,
               (double)samples[variant][3 * SAMPLES / 4] / ITERATIONS,
               SAMPLES, ITERATIONS);
    }
    printf("sink=%" PRIu64 "\n", sink);
    return 0;
}
