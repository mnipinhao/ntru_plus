#include "gt864_ntt16.h"
#include "gt864_ntt16_tables.h"
#include "../gt_2x9x16_ld3_top_split/gt864_top_split.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457
#define QINV 12929
#define THETA 9

static uint32_t random_state = 0x16U;
static int exact_mismatches;
static int algebra_mismatches;
static int cases;
static int maximum_observed;

static int16_t centered(int32_t value)
{
    value %= Q;
    if (value < 0)
        value += Q;
    if (value > Q / 2)
        value -= Q;
    return (int16_t)value;
}

static int16_t montgomery_reduce(int32_t value)
{
    int16_t quotient = (int16_t)value * QINV;
    return (int16_t)((value - (int32_t)quotient * Q) >> 16);
}

static int16_t fqmul_public(int16_t value, int16_t constant)
{
    return montgomery_reduce((int32_t)value * constant);
}

static int16_t powmod(int16_t base, int exponent)
{
    int16_t result = 1;
    while (exponent != 0) {
        if (exponent & 1)
            result = centered((int32_t)result * base);
        base = centered((int32_t)base * base);
        exponent >>= 1;
    }
    return result;
}

static size_t p8_index(int top, int branch, int x, int s)
{
    if (s < 8)
        return (size_t)(((top * 3 + branch) * 16 + x) * 8 + s);
    return (size_t)(GT864_NTT16_MAIN_COEFFICIENTS + 8 * x +
                    3 * top + branch);
}

static void scalar_exact_ntt16(int16_t out[GT864_NTT16_PADDED_COEFFICIENTS],
                               const int16_t in[GT864_NTT16_PADDED_COEFFICIENTS])
{
    static const uint8_t reverse[16] = {
        0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15
    };
    memset(out, 0, GT864_NTT16_PADDED_COEFFICIENTS * sizeof(int16_t));

    for (int top = 0; top < 2; top++)
        for (int branch = 0; branch < 3; branch++)
            for (int s = 0; s < 9; s++) {
                int16_t value[16];
                for (int t = 0; t < 16; t++)
                    value[reverse[t]] = fqmul_public(
                        in[p8_index(top, branch, t, s)],
                        gt864_ntt16_twist_mont[top][t]);
                for (int stage = 0, length = 2; stage < 4;
                     stage++, length <<= 1) {
                    int half = length >> 1;
                    for (int start = 0; start < 16; start += length)
                        for (int j = 0; j < half; j++) {
                            int left = start + j;
                            int right = left + half;
                            int16_t u = value[left];
                            int16_t v = fqmul_public(
                                value[right],
                                gt864_ntt16_stage_twiddle_mont[stage][j]);
                            value[left] = (int16_t)(u + v);
                            value[right] = (int16_t)(u - v);
                        }
                }
                for (int c = 0; c < 16; c++)
                    out[p8_index(top, branch, c, s)] = value[c];
            }
}

static void check_case(const int16_t input[864], const char *label)
{
    int16_t split[GT864_NTT16_PADDED_COEFFICIENTS];
    int16_t expected[GT864_NTT16_PADDED_COEFFICIENTS];

    gt864_top_split_ld3(split, input);
    scalar_exact_ntt16(expected, split);
    gt864_ntt16_p8_neon(split);

    for (int i = 0; i < GT864_NTT16_PADDED_COEFFICIENTS; i++) {
        int magnitude = split[i] < 0 ? -split[i] : split[i];
        if (magnitude > maximum_observed)
            maximum_observed = magnitude;
        if (split[i] != expected[i]) {
            if (exact_mismatches < 8)
                fprintf(stderr, "%s exact mismatch i=%d got=%d expected=%d\n",
                        label, i, split[i], expected[i]);
            exact_mismatches++;
        }
    }

    for (int top = 0; top < 2; top++) {
        int residue = top == 0 ? 1 : 5;
        int16_t zeta = powmod(THETA, 9 * residue);
        int16_t omega = powmod(THETA, 54);

        for (int branch = 0; branch < 3; branch++)
            for (int s = 0; s < 9; s++)
                for (int c = 0; c < 16; c++) {
                    int16_t z = centered((int32_t)zeta * powmod(omega, c));
                    int16_t power = 1;
                    int32_t sum = 0;

                    for (int t = 0; t < 32; t++) {
                        sum += (int32_t)input[3 * (s + 9 * t) + branch] * power;
                        power = centered((int32_t)power * z);
                        sum %= Q;
                    }
                    if (centered(split[p8_index(top, branch, c, s)]) !=
                        centered(sum)) {
                        if (algebra_mismatches < 8)
                            fprintf(stderr,
                                    "%s algebra mismatch h=%d b=%d s=%d c=%d\n",
                                    label, top, branch, s, c);
                        algebra_mismatches++;
                    }
                }
    }
    cases++;
}

static int16_t random_centered(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % Q) - Q / 2);
}

static int16_t random_wide(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % 6913U) - 3456);
}

int main(void)
{
    int16_t input[864];
    static const int16_t boundaries[] = {
        -3456, 3456, -1728, 1728, 0, 1, -1
    };

    for (size_t k = 0; k < sizeof(boundaries) / sizeof(boundaries[0]); k++) {
        for (int i = 0; i < 864; i++)
            input[i] = boundaries[k];
        check_case(input, "boundary");
    }
    for (int impulse = 0; impulse < 8; impulse++) {
        static const int positions[8] = {0,1,2,3,431,432,862,863};
        memset(input, 0, sizeof(input));
        input[positions[impulse]] = (int16_t)(impulse & 1 ? -1728 : 1728);
        check_case(input, "impulse");
    }
    for (int trial = 0; trial < 40; trial++) {
        for (int i = 0; i < 864; i++)
            input[i] = random_centered();
        check_case(input, "random");
    }
    for (int trial = 0; trial < 20; trial++) {
        for (int i = 0; i < 864; i++)
            input[i] = random_wide();
        check_case(input, "random-wide");
    }

    printf("gt864_ntt16_producer_gate=%s\n",
           exact_mismatches + algebra_mismatches == 0 ? "pass" : "fail");
    printf("cases=%d\n", cases);
    printf("exact_representative_mismatches=%d\n", exact_mismatches);
    printf("direct_evaluation_modq_mismatches=%d\n", algebra_mismatches);
    printf("maximum_observed_abs=%d\n", maximum_observed);
    printf("production_linked=0\n");
    return exact_mismatches + algebra_mismatches != 0;
}
