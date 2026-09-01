#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt864_forward_compose.h"

extern void gt864_forward_six_bank_pass2(int16_t out[864],
                                          const int16_t p8[896]);

static uint32_t rng_state = 0x8645a11u;

static uint32_t next_u32(void)
{
    uint32_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rng_state = x;
    return x;
}

static int is_padding(int index)
{
    return index >= 768 && (index & 7) >= 6;
}

static int meaningful_index(int basis)
{
    if (basis < 768)
        return basis;
    basis -= 768;
    return 768 + 8 * (basis / 6) + basis % 6;
}

static int run_case(int case_id, int16_t p8[896])
{
    int16_t expected[864] __attribute__((aligned(16)));
    int16_t actual[864] __attribute__((aligned(16)));
    int16_t changed_padding[896] __attribute__((aligned(16)));
    int16_t changed_output[864] __attribute__((aligned(16)));

    gt864_forward_compose_barrett(expected, p8);
    gt864_forward_six_bank_pass2(actual, p8);
    if (memcmp(expected, actual, sizeof expected) != 0) {
        for (int i = 0; i < 864; i++)
            if (expected[i] != actual[i]) {
                fprintf(stderr, "case=%d index=%d expected=%d actual=%d\n",
                        case_id, i, expected[i], actual[i]);
                break;
            }
        return 1;
    }

    memcpy(changed_padding, p8, sizeof changed_padding);
    for (int i = 0; i < 896; i++)
        if (is_padding(i))
            changed_padding[i] = (int16_t)(0x5a00 ^ i);
    gt864_forward_six_bank_pass2(changed_output, changed_padding);
    if (memcmp(actual, changed_output, sizeof actual) != 0) {
        fprintf(stderr, "case=%d padding affected output\n", case_id);
        return 1;
    }
    return 0;
}

int main(void)
{
    int16_t p8[896] __attribute__((aligned(16)));
    int cases = 0;

    memset(p8, 0, sizeof p8);
    if (run_case(cases++, p8)) return 1;

    for (int i = 0; i < 896; i++)
        p8[i] = is_padding(i) ? (int16_t)0x6b6b
                             : (int16_t)((i & 1) ? 15752 : -15752);
    if (run_case(cases++, p8)) return 1;

    for (int basis = 0; basis < 864; basis++) {
        memset(p8, 0, sizeof p8);
        p8[meaningful_index(basis)] = (int16_t)((basis & 1) ? 1 : -1);
        if (run_case(cases++, p8)) return 1;
    }

    for (int test = 0; test < 256; test++) {
        for (int i = 0; i < 896; i++)
            p8[i] = is_padding(i) ? (int16_t)next_u32()
                                  : (int16_t)((int)(next_u32() % 31505u) - 15752);
        if (run_case(cases++, p8)) return 1;
    }

    printf("gt864_forward_six_bank_pass2_gate=pass\n");
    printf("exact_representative_cases=%d\n", cases);
    printf("exact_representative_mismatches=0\n");
    printf("padding_dependency_mismatches=0\n");
    printf("meaningful_input_halfwords=864\n");
    printf("output_halfwords=864\n");
    printf("production_linked=0\n");
    return 0;
}
