#include "gt864_boundary.h"

#include <inttypes.h>
#include <mach/mach_time.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define SAMPLES 41
#define ITERATIONS 5000
#define VARIANTS 5

typedef void (*kernel)(int16_t *, const int16_t *);

struct variant {
    const char *name;
    kernel fn;
    size_t output_coefficients;
};

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

static volatile uint64_t sink;

static void report_variant(const struct variant *variant,
                           uint64_t samples[SAMPLES])
{
    qsort(samples, SAMPLES, sizeof(samples[0]), compare_u64);
    printf("timing,name=%s,unit=ns_per_call,q1=%.3f,median=%.3f,q3=%.3f,"
           "samples=%d,iterations=%d\n",
           variant->name,
           (double)samples[SAMPLES / 4] / ITERATIONS,
           (double)samples[SAMPLES / 2] / ITERATIONS,
           (double)samples[(3 * SAMPLES) / 4] / ITERATIONS,
           SAMPLES, ITERATIONS);
}

int main(void)
{
    static int16_t input[GT864_BOUNDARY_INPUT_COEFFICIENTS]
        __attribute__((aligned(64)));
    static int16_t output[GT864_BOUNDARY_OUTPUT_COEFFICIENTS]
        __attribute__((aligned(64)));
    static const struct variant variants[] = {
        {"M4.1_FR_bridge", gt864_fr_bridge,
         GT864_BOUNDARY_FR_SCRATCH_COEFFICIENTS},
        {"M4.1_FC_tail_only", gt864_fc_tail_extract,
         GT864_BOUNDARY_FC_TAIL_COEFFICIENTS},
        {"M4.2_FR-0_full_boundary", gt864_boundary_fr0,
         GT864_BOUNDARY_OUTPUT_COEFFICIENTS},
        {"M4.2_FC-0_full_boundary", gt864_boundary_fc0,
         GT864_BOUNDARY_OUTPUT_COEFFICIENTS},
        {"M4.3_FR-lane-0_full_boundary", gt864_boundary_fr_lane0,
         GT864_BOUNDARY_OUTPUT_COEFFICIENTS},
    };
    uint32_t state = 864;
    uint64_t samples[VARIANTS][SAMPLES];

    _Static_assert(sizeof(variants) / sizeof(variants[0]) == VARIANTS,
                   "update VARIANTS when adding a benchmark candidate");

    for (int i = 0; i < GT864_BOUNDARY_INPUT_COEFFICIENTS; i++) {
        state = state * 1664525u + 1013904223u;
        input[i] = (int16_t)((state % 3457) - 1728);
    }
    for (int column = 0; column < 16; column++) {
        input[GT864_BOUNDARY_MAIN_COEFFICIENTS + column * 8 + 6] = 0;
        input[GT864_BOUNDARY_MAIN_COEFFICIENTS + column * 8 + 7] = 0;
    }

    printf("timer=mach_continuous_time\n");
    printf("authority=diagnostic_only_not_SUPERCOP\n");
    printf("common_input=P8_plus_tail_896\n");
    printf("full_boundary_output=BaseMul_SoA_864\n");
    for (int variant = 0; variant < VARIANTS; variant++)
        for (int warmup = 0; warmup < 100; warmup++)
            variants[variant].fn(output, input);

    /* Rotate execution order every sample to avoid phase/frequency bias. */
    for (int sample = 0; sample < SAMPLES; sample++) {
        for (int slot = 0; slot < VARIANTS; slot++) {
            int variant = (sample + slot) % VARIANTS;
            uint64_t start = mach_continuous_time();

            for (int iteration = 0; iteration < ITERATIONS; iteration++)
                variants[variant].fn(output, input);
            samples[variant][sample] =
                ticks_to_ns(mach_continuous_time() - start);
            sink += (uint16_t)output[(sample * 17) %
                variants[variant].output_coefficients];
        }
    }
    printf("execution_order=sample_rotated\n");
    for (int variant = 0; variant < VARIANTS; variant++)
        report_variant(&variants[variant], samples[variant]);
    printf("sink=%" PRIu64 "\n", sink);
    return 0;
}
