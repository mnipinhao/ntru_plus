#include "gt864_boundary.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define Q 3457

static uint32_t random_state = 1;

static int16_t random_centered(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % Q) - Q / 2);
}

static int canonical(int value)
{
    value %= Q;
    return value < 0 ? value + Q : value;
}

static size_t main_index(int top, int component, int column, int row)
{
    return (size_t)((((top * 3 + component) * 16 + column) * 8) + row);
}

static size_t tail_index(int top, int component, int column)
{
    return (size_t)(GT864_BOUNDARY_MAIN_COEFFICIENTS + column * 8 +
                    top * 3 + component);
}

static size_t scratch_index(int top, int component, int block, int row,
                            int lane)
{
    return (size_t)(((((top * 3 + component) * 2 + block) * 9 + row) * 8) +
                    lane);
}

static int check_bridges(void)
{
    int16_t input[GT864_BOUNDARY_INPUT_COEFFICIENTS];
    int16_t fr[GT864_BOUNDARY_FR_SCRATCH_COEFFICIENTS];
    int16_t fc_tail[GT864_BOUNDARY_FC_TAIL_COEFFICIENTS];
    int mismatches = 0;

    for (int i = 0; i < GT864_BOUNDARY_INPUT_COEFFICIENTS; i++)
        input[i] = (int16_t)(i - 448);
    gt864_fr_bridge(fr, input);
    gt864_fc_tail_extract(fc_tail, input);

    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            int bank = top * 3 + component;
            for (int column = 0; column < 16; column++) {
                int block = column / 8;
                int lane = column % 8;

                for (int row = 0; row < 8; row++) {
                    int16_t expected =
                        input[main_index(top, component, column, row)];
                    int16_t actual =
                        fr[scratch_index(top, component, block, row, lane)];
                    if (actual != expected)
                        mismatches++;
                }
                if (fr[scratch_index(top, component, block, 8, lane)] !=
                    input[tail_index(top, component, column)])
                    mismatches++;
                if (fc_tail[(bank * 2 + block) * 8 + lane] !=
                    input[tail_index(top, component, column)])
                    mismatches++;
            }
        }
    }
    if (mismatches)
        fprintf(stderr, "bridge mismatches=%d\n", mismatches);
    return mismatches;
}

static int check_transform_case(const int16_t *input, const char *label,
                                int *max_abs_fr, int *max_abs_fc)
{
    int16_t reference[GT864_BOUNDARY_OUTPUT_COEFFICIENTS];
    int16_t fr[GT864_BOUNDARY_OUTPUT_COEFFICIENTS];
    int16_t fc[GT864_BOUNDARY_OUTPUT_COEFFICIENTS];
    int16_t fr_lane[GT864_BOUNDARY_OUTPUT_COEFFICIENTS];
    int mismatches = 0;

    memset(reference, 0x5a, sizeof(reference));
    memset(fr, 0x5a, sizeof(fr));
    memset(fc, 0x5a, sizeof(fc));
    memset(fr_lane, 0x5a, sizeof(fr_lane));
    gt864_boundary_reference_fr0(reference, input);
    gt864_boundary_fr0(fr, input);
    gt864_boundary_fc0(fc, input);
    gt864_boundary_fr_lane0(fr_lane, input);

    for (int top = 0; top < 2; top++) {
        for (int row = 0; row < 9; row++) {
            for (int column = 0; column < 16; column++) {
                for (int component = 0; component < 3; component++) {
                    int expected = gt864_boundary_fr_get(
                        reference, top, row, column, component);
                    int fr_value = gt864_boundary_fr_get(
                        fr, top, row, column, component);
                    int fc_value = gt864_boundary_fc_get(
                        fc, top, row, column, component);
                    int fr_lane_value = gt864_boundary_fr_lane0_get(
                        fr_lane, top, row, column, component);
                    int abs_fr = abs(fr_value);
                    int abs_fc = abs(fc_value);

                    if (abs_fr > *max_abs_fr)
                        *max_abs_fr = abs_fr;
                    if (abs_fc > *max_abs_fc)
                        *max_abs_fc = abs_fc;
                    if (canonical(fr_value) != canonical(expected) ||
                        canonical(fc_value) != canonical(expected) ||
                        canonical(fr_lane_value) != canonical(expected)) {
                        if (mismatches < 12)
                            fprintf(stderr,
                                    "%s mismatch h=%d r=%d c=%d j=%d "
                                    "ref=%d fr=%d fc=%d fr_lane=%d\n",
                                    label, top, row, column, component,
                                    expected, fr_value, fc_value,
                                    fr_lane_value);
                        mismatches++;
                    }
                }
            }
        }
    }
    return mismatches;
}

int main(void)
{
    int16_t input[GT864_BOUNDARY_INPUT_COEFFICIENTS] = {0};
    int mismatches = check_bridges();
    int max_abs_fr = 0;
    int max_abs_fc = 0;
    int cases = 0;

    for (int i = 0; i < GT864_BOUNDARY_INPUT_COEFFICIENTS; i++)
        input[i] = (int16_t)((i % Q) - Q / 2);
    mismatches += check_transform_case(input, "tags", &max_abs_fr,
                                       &max_abs_fc);
    cases++;

    for (int boundary = 0; boundary < 4; boundary++) {
        static const int16_t values[4] = {-1728, 1728, 0, 3456};
        for (int i = 0; i < GT864_BOUNDARY_INPUT_COEFFICIENTS; i++)
            input[i] = values[boundary];
        mismatches += check_transform_case(input, "boundary", &max_abs_fr,
                                           &max_abs_fc);
        cases++;
    }

    for (int trial = 0; trial < 100; trial++) {
        for (int i = 0; i < GT864_BOUNDARY_INPUT_COEFFICIENTS; i++)
            input[i] = random_centered();
        /* P8+tail padding lanes are not logical data and stay zero. */
        for (int column = 0; column < 16; column++) {
            input[GT864_BOUNDARY_MAIN_COEFFICIENTS + column * 8 + 6] = 0;
            input[GT864_BOUNDARY_MAIN_COEFFICIENTS + column * 8 + 7] = 0;
        }
        mismatches += check_transform_case(input, "random", &max_abs_fr,
                                           &max_abs_fc);
        cases++;
    }

    printf("gt864_boundary_cost_campaign=%s\n",
           mismatches == 0 ? "pass" : "fail");
    printf("common_input=P8_plus_tail_896\n");
    printf("common_output=BaseMul_SoA_864\n");
    printf("differential_cases=%d\n", cases);
    printf("total_mismatches=%d\n", mismatches);
    printf("observed_max_abs_fr0=%d\n", max_abs_fr);
    printf("observed_max_abs_fc0=%d\n", max_abs_fc);
    printf("production_linked=0\n");
    return mismatches != 0;
}
