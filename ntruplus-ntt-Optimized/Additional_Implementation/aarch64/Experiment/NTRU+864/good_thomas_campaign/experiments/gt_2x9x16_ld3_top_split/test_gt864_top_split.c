#include "gt864_top_split.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457
#define ALPHA (-722)
#define ALPHA_RECIPROCAL (-6844)

static int16_t wrap16(int32_t value)
{
    return (int16_t)(uint16_t)value;
}

/* Exact SQRDMULH semantics for this non-saturating constant. */
static int16_t sqrdmulh_s16(int16_t left, int16_t right)
{
    int64_t numerator = 2 * (int64_t)left * right + 32768;
    int64_t quotient;

    if (numerator >= 0)
        quotient = numerator / 65536;
    else
        quotient = -((-numerator + 65535) / 65536);
    return (int16_t)quotient;
}

static int16_t fixed_alpha(int16_t value)
{
    int16_t low = wrap16((int32_t)value * ALPHA);
    int16_t quotient = sqrdmulh_s16(value, ALPHA_RECIPROCAL);
    return wrap16((int32_t)low - (int32_t)quotient * Q);
}

static size_t output_index(int top, int branch, int t, int s)
{
    if (s < 8)
        return (size_t)(((top * 3 + branch) * 16 + t) * 8 + s);
    return (size_t)(GT864_TOP_SPLIT_MAIN_COEFFICIENTS + t * 8 +
                    top * 3 + branch);
}

static uint32_t random_state = 1;

static int16_t random_centered(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % Q) - Q / 2);
}

static int check_case(const int16_t input[GT864_TOP_SPLIT_INPUT_COEFFICIENTS],
                      const char *label)
{
    int16_t output[GT864_TOP_SPLIT_OUTPUT_COEFFICIENTS];
    int mismatches = 0;

    memset(output, 0x5a, sizeof(output));
    gt864_top_split_ld3(output, input);

    for (int t = 0; t < 16; t++) {
        for (int s = 0; s < 9; s++) {
            for (int branch = 0; branch < 3; branch++) {
                int low_m = s + 9 * t;
                int high_m = low_m + 144;
                int16_t low = input[3 * low_m + branch];
                int16_t high = input[3 * high_m + branch];
                int16_t product = fixed_alpha(high);
                int16_t expected_alpha = wrap16((int32_t)low + product);
                int16_t expected_beta =
                    wrap16((int32_t)low + high - product);
                int16_t actual_alpha = output[output_index(0, branch, t, s)];
                int16_t actual_beta = output[output_index(1, branch, t, s)];

                if (actual_alpha != expected_alpha ||
                    actual_beta != expected_beta) {
                    if (mismatches < 8)
                        fprintf(stderr,
                                "%s mismatch t=%d s=%d b=%d: "
                                "alpha=%d/%d beta=%d/%d\n",
                                label, t, s, branch, actual_alpha,
                                expected_alpha, actual_beta, expected_beta);
                    mismatches++;
                }
            }
        }
        if (output[GT864_TOP_SPLIT_MAIN_COEFFICIENTS + t * 8 + 6] != 0 ||
            output[GT864_TOP_SPLIT_MAIN_COEFFICIENTS + t * 8 + 7] != 0) {
            fprintf(stderr, "%s nonzero padding at t=%d\n", label, t);
            mismatches++;
        }
    }
    return mismatches;
}

int main(void)
{
    int16_t input[GT864_TOP_SPLIT_INPUT_COEFFICIENTS] = {0};
    int mismatches = 0;
    int cases = 0;
    int fixed_mul_checks = 0;

    /* Exhaust the two input conventions relevant to the current callers. */
    for (int value = -1728; value <= 3456; value++) {
        int16_t reduced = fixed_alpha((int16_t)value);
        int32_t difference = (int32_t)reduced - (int32_t)value * ALPHA;
        if (difference % Q != 0) {
            fprintf(stderr, "fixed multiply mismatch at %d\n", value);
            mismatches++;
            break;
        }
        fixed_mul_checks++;
    }

    /* Low-only tags expose every LD3 branch/lane and output index. */
    for (int m = 0; m < 144; m++)
        for (int branch = 0; branch < 3; branch++)
            input[3 * m + branch] = (int16_t)(3 * m + branch - 216);
    mismatches += check_case(input, "low-tags");
    cases++;

    /* High-only tags expose the +432 coefficient pairing. */
    memset(input, 0, sizeof(input));
    for (int m = 144; m < 288; m++)
        for (int branch = 0; branch < 3; branch++)
            input[3 * m + branch] = (int16_t)(3 * (m - 144) + branch - 216);
    mismatches += check_case(input, "high-tags");
    cases++;

    for (int boundary = 0; boundary < 4; boundary++) {
        static const int16_t values[4] = {-1728, 1728, 0, 3456};
        for (size_t i = 0; i < GT864_TOP_SPLIT_INPUT_COEFFICIENTS; i++)
            input[i] = values[boundary];
        mismatches += check_case(input, "range-boundary");
        cases++;
    }

    for (int trial = 0; trial < 100; trial++) {
        for (size_t i = 0; i < GT864_TOP_SPLIT_INPUT_COEFFICIENTS; i++)
            input[i] = random_centered();
        mismatches += check_case(input, "random-centered");
        cases++;
    }

    printf("gt864_top_split_ld3,total_mismatches=%d\n", mismatches);
    printf("differential_cases=%d\n", cases);
    printf("fixed_mul_checks=%d\n", fixed_mul_checks);
    printf("output_coefficients=%d\n", GT864_TOP_SPLIT_OUTPUT_COEFFICIENTS);
    return mismatches != 0;
}
