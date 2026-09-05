#include "../gt_fr0_inverse_consumer/gt864_fr0_inverse.h"
#ifdef HAVE_ASM
#include "gt864_fr0_inverse_asm.h"
#endif

#include <mach/mach_time.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define SAMPLES 31
#define ITERATIONS 2000

static uint32_t random_state = 0x5eU;
static volatile uint32_t checksum;

static int compare_double(const void *left, const void *right)
{
    double a = *(const double *)left;
    double b = *(const double *)right;
    return (a > b) - (a < b);
}

static double ticks_to_ns(uint64_t ticks)
{
    static mach_timebase_info_data_t info;
    if (info.denom == 0)
        mach_timebase_info(&info);
    return (double)ticks * info.numer / info.denom;
}

static void report(const char *name, double values[SAMPLES])
{
    qsort(values, SAMPLES, sizeof(values[0]), compare_double);
    printf("%s,q1_ns=%.3f,median_ns=%.3f,q3_ns=%.3f\n",
           name, values[SAMPLES / 4], values[SAMPLES / 2],
           values[3 * SAMPLES / 4]);
}

int main(void)
{
    static int16_t fr0[864] __attribute__((aligned(64)));
    static int16_t p8[896] __attribute__((aligned(64)));
    static int16_t out[864] __attribute__((aligned(64)));
    double pass1[SAMPLES];
    double pass2[SAMPLES];
    double combined[SAMPLES];
#ifdef HAVE_ASM
    double asm_pass1[SAMPLES];
    double asm_pass2[SAMPLES];
    double asm_combined[SAMPLES];
#endif

    for (int i = 0; i < 864; i++) {
        random_state = random_state * 1664525u + 1013904223u;
        fr0[i] = (int16_t)((int32_t)(random_state % 4411U) - 2205);
    }
    gt864_fr0_inverse_ntt9_neon(p8, fr0);

    for (int sample = 0; sample < SAMPLES; sample++) {
        uint64_t start = mach_continuous_time();
        for (int i = 0; i < ITERATIONS; i++)
            gt864_fr0_inverse_ntt9_neon(p8, fr0);
        uint64_t stop = mach_continuous_time();
        pass1[sample] = ticks_to_ns(stop - start) / ITERATIONS;
        checksum += (uint16_t)p8[(sample * 29) % 864];

        start = mach_continuous_time();
        for (int i = 0; i < ITERATIONS; i++)
            gt864_fr0_inverse_finish_neon(out, p8);
        stop = mach_continuous_time();
        pass2[sample] = ticks_to_ns(stop - start) / ITERATIONS;
        checksum += (uint16_t)out[(sample * 31) % 864];

        start = mach_continuous_time();
        for (int i = 0; i < ITERATIONS; i++) {
            gt864_fr0_inverse_ntt9_neon(p8, fr0);
            gt864_fr0_inverse_finish_neon(out, p8);
        }
        stop = mach_continuous_time();
        combined[sample] = ticks_to_ns(stop - start) / ITERATIONS;
        checksum += (uint16_t)out[(sample * 37) % 864];

#ifdef HAVE_ASM
        start = mach_continuous_time();
        for (int i = 0; i < ITERATIONS; i++)
            gt864_fr0_inverse_ntt9_asm(p8, fr0);
        stop = mach_continuous_time();
        asm_pass1[sample] = ticks_to_ns(stop - start) / ITERATIONS;
        checksum += (uint16_t)p8[(sample * 41) % 864];

        start = mach_continuous_time();
        for (int i = 0; i < ITERATIONS; i++)
            gt864_fr0_inverse_finish_asm(out, p8);
        stop = mach_continuous_time();
        asm_pass2[sample] = ticks_to_ns(stop - start) / ITERATIONS;
        checksum += (uint16_t)out[(sample * 43) % 864];

        start = mach_continuous_time();
        for (int i = 0; i < ITERATIONS; i++) {
            gt864_fr0_inverse_ntt9_asm(p8, fr0);
            gt864_fr0_inverse_finish_asm(out, p8);
        }
        stop = mach_continuous_time();
        asm_combined[sample] = ticks_to_ns(stop - start) / ITERATIONS;
        checksum += (uint16_t)out[(sample * 47) % 864];
#endif
    }

    report("intrinsic_pass1", pass1);
    report("intrinsic_pass2", pass2);
    report("intrinsic_combined", combined);
#ifdef HAVE_ASM
    report("assembly_pass1", asm_pass1);
    report("assembly_pass2", asm_pass2);
    report("assembly_combined", asm_combined);
#endif
    printf("iterations_per_sample=%d\n", ITERATIONS);
    printf("samples=%d\n", SAMPLES);
    printf("checksum=%u\n", checksum);
    return 0;
}
