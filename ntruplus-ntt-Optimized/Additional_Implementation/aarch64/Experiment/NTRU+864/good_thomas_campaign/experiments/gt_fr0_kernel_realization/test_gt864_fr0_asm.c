#include "gt864_fr0_asm.h"
#include "../gt_boundary_cost_campaign/gt864_boundary.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457

static uint32_t random_state = 1;

static int16_t random_centered(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % Q) - Q / 2);
}

static int check_case(const int16_t *input, const char *label)
{
    int16_t expected[GT864_FR0_OUTPUT_COEFFICIENTS];
    int16_t actual[GT864_FR0_OUTPUT_COEFFICIENTS];
    int mismatches = 0;

    memset(expected, 0x5a, sizeof(expected));
    memset(actual, 0xa5, sizeof(actual));
    gt864_boundary_fr0(expected, input);
    gt864_boundary_fr0_asm(actual, input);
    for (int index = 0; index < GT864_FR0_OUTPUT_COEFFICIENTS; index++) {
        if (actual[index] != expected[index]) {
            if (mismatches < 12)
                fprintf(stderr, "%s mismatch index=%d actual=%d expected=%d\n",
                        label, index, actual[index], expected[index]);
            mismatches++;
        }
    }
    return mismatches;
}

int main(void)
{
    int16_t input[GT864_FR0_INPUT_COEFFICIENTS] = {0};
    int mismatches = 0;
    int cases = 0;

    for (int i = 0; i < GT864_FR0_INPUT_COEFFICIENTS; i++)
        input[i] = (int16_t)((i % Q) - Q / 2);
    mismatches += check_case(input, "tags");
    cases++;

    for (int boundary = 0; boundary < 5; boundary++) {
        static const int16_t values[5] = {-15752, 15752, -1728, 1728, 3456};
        for (int i = 0; i < GT864_FR0_INPUT_COEFFICIENTS; i++)
            input[i] = values[boundary];
        mismatches += check_case(input, "range-boundary");
        cases++;
    }

    for (int trial = 0; trial < 100; trial++) {
        for (int i = 0; i < GT864_FR0_INPUT_COEFFICIENTS; i++)
            input[i] = random_centered();
        for (int column = 0; column < 16; column++) {
            input[768 + column * 8 + 6] = 0;
            input[768 + column * 8 + 7] = 0;
        }
        mismatches += check_case(input, "random-centered");
        cases++;
    }

    printf("gt864_fr0_asm_differential=%s\n",
           mismatches == 0 ? "pass" : "fail");
    printf("cases=%d\n", cases);
    printf("exact_representative_mismatches=%d\n", mismatches);
    printf("production_linked=0\n");
    return mismatches != 0;
}
