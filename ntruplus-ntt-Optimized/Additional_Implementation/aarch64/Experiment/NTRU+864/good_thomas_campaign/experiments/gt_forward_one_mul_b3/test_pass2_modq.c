#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt864_forward_compose.h"

#define Q 3457
extern void gt864_forward_six_bank_pass2(int16_t out[864], const int16_t p8[896]);
static uint32_t state = 0x8645a11u;

static uint32_t next_u32(void)
{
    uint32_t x = state;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return state = x;
}

static int centered(int value)
{
    value %= Q;
    if (value < 0) value += Q;
    return value > Q / 2 ? value - Q : value;
}

static int is_padding(int i) { return i >= 768 && (i & 7) >= 6; }
static int meaningful_index(int basis)
{
    if (basis < 768) return basis;
    basis -= 768;
    return 768 + 8 * (basis / 6) + basis % 6;
}

static int run_case(int id, int16_t p8[896])
{
    int16_t expected[864] __attribute__((aligned(16)));
    int16_t actual[864] __attribute__((aligned(16)));
    int16_t changed[896] __attribute__((aligned(16)));
    int16_t changed_out[864] __attribute__((aligned(16)));
    gt864_forward_compose_barrett(expected, p8);
    gt864_forward_six_bank_pass2(actual, p8);
    for (int i = 0; i < 864; i++)
        if (centered(expected[i]) != centered(actual[i])) {
            fprintf(stderr, "case=%d index=%d expected=%d actual=%d\n",
                    id, i, expected[i], actual[i]);
            return 1;
        }
    memcpy(changed, p8, sizeof changed);
    for (int i = 0; i < 896; i++)
        if (is_padding(i)) changed[i] = (int16_t)(0x5a00 ^ i);
    gt864_forward_six_bank_pass2(changed_out, changed);
    if (memcmp(actual, changed_out, sizeof actual) != 0) {
        fprintf(stderr, "case=%d padding affected output\n", id);
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
        p8[i] = is_padding(i) ? (int16_t)0x6b6b : (int16_t)((i & 1) ? 15752 : -15752);
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
    printf("gt864_forward_six_bank_pass2_modq_gate=pass\n");
    printf("modq_cases=%d\n", cases);
    printf("modq_comparisons=%d\n", cases * 864);
    printf("padding_dependency_mismatches=0\n");
    return 0;
}
