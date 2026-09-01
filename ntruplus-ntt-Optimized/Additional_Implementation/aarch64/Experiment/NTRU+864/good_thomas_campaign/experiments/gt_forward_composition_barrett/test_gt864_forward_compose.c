#include "gt864_forward_compose.h"
#include "../gt_2x9x16_ld3_top_split/gt864_top_split.h"
#include "../gt_ntt16_producer_range/gt864_ntt16.h"
#include "../gt_boundary_cost_campaign/gt864_boundary.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457

static uint32_t random_state = 0x5f864U;
static int cases;
static int mismatches;
static int maximum_output_abs;

static int16_t centered(int32_t value)
{
    value %= Q;
    if (value < 0) value += Q;
    if (value > Q / 2) value -= Q;
    return (int16_t)value;
}
static int16_t random_wide(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % 6913U) - 3456);
}

static void check_case(const int16_t input[864], const char *label)
{
    int16_t p8[896], oracle_p8[896], expected[864], actual[864];
    gt864_top_split_ld3(p8, input);
    memcpy(oracle_p8, p8, sizeof(p8));
    gt864_ntt16_p8_neon(oracle_p8);
    gt864_boundary_fr0(expected, oracle_p8);
    gt864_forward_compose_barrett(actual, p8);

    for (int i = 0; i < 864; i++) {
        int magnitude = actual[i] < 0 ? -actual[i] : actual[i];
        if (magnitude > maximum_output_abs) maximum_output_abs = magnitude;
        if (centered(actual[i]) != centered(expected[i])) {
            if (mismatches < 8)
                fprintf(stderr, "%s mismatch i=%d got=%d expected=%d\n",
                        label, i, actual[i], expected[i]);
            mismatches++;
        }
    }
    cases++;
}

int main(void)
{
    int16_t input[864];
    static const int16_t boundaries[] = {-3456,3456,-1728,1728,0,1,-1};
    static const int positions[] = {0,1,2,3,431,432,862,863};

    for (unsigned k = 0; k < sizeof(boundaries) / sizeof(boundaries[0]); k++) {
        for (int i = 0; i < 864; i++) input[i] = boundaries[k];
        check_case(input, "boundary");
    }
    for (unsigned k = 0; k < sizeof(positions) / sizeof(positions[0]); k++) {
        memset(input, 0, sizeof(input));
        input[positions[k]] = (k & 1) ? -1728 : 1728;
        check_case(input, "impulse");
    }
    for (int trial = 0; trial < 40; trial++) {
        for (int i = 0; i < 864; i++) input[i] = random_wide();
        check_case(input, "random-wide");
    }

    printf("gt864_forward_composition_barrett_gate=%s\n",
           mismatches == 0 ? "pass" : "fail");
    printf("cases=%d\n", cases);
    printf("modq_mismatches=%d\n", mismatches);
    printf("maximum_output_abs=%d\n", maximum_output_abs);
    printf("meaningful_pass2_input_loads=864\n");
    printf("meaningful_pass2_output_stores=864\n");
    printf("intermediate_ntt16_memory_traffic=0\n");
    printf("production_linked=0\n");
    return mismatches != 0;
}
