#include "gt864_radix3.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint32_t random_state = 0x9A320864U;
static int failures;
static int forward_cases;
static int current_forward_cases;
static int full_product_cases;
static int schoolbook_product_cases;
static int alias_cases;

void ntt(int16_t out[GT864_N], const int16_t in[GT864_N]);

static uint32_t next_u32(void)
{
    uint32_t x = random_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    random_state = x;
    return x;
}

static int16_t canonical(int32_t value)
{
    value %= GT864_Q;
    if (value < 0)
        value += GT864_Q;
    return (int16_t)value;
}

static int16_t centered(int32_t value)
{
    int16_t result = canonical(value);
    if (result > GT864_Q / 2)
        result = (int16_t)(result - GT864_Q);
    return result;
}

static void fill_case(int16_t value[GT864_N], int kind)
{
    for (int i = 0; i < GT864_N; i++) {
        switch (kind) {
        case 0: value[i] = 0; break;
        case 1: value[i] = 1; break;
        case 2: value[i] = (int16_t)(i & 1 ? -1 : 1); break;
        case 3: value[i] = 1728; break;
        case 4: value[i] = -1728; break;
        default: value[i] = centered((int32_t)(next_u32() % GT864_Q)); break;
        }
    }
}

static void compare_exact(const char *label, int case_id,
                          const int16_t got[GT864_N],
                          const int16_t expected[GT864_N])
{
    for (int i = 0; i < GT864_N; i++) {
        if (got[i] != expected[i]) {
            fprintf(stderr,
                    "mismatch,%s,case=%d,index=%d,got=%d,expected=%d\n",
                    label, case_id, i, got[i], expected[i]);
            failures++;
            return;
        }
    }
}

static void compare_modq(const char *label, int case_id,
                         const int16_t got[GT864_N],
                         const int16_t expected[GT864_N])
{
    for (int i = 0; i < GT864_N; i++) {
        if (canonical(got[i]) != canonical(expected[i])) {
            fprintf(stderr,
                    "mismatch_modq,%s,case=%d,index=%d,got=%d,expected=%d\n",
                    label, case_id, i, got[i], expected[i]);
            failures++;
            return;
        }
    }
}

static void check_forward(const int16_t input[GT864_N], int case_id)
{
    int16_t candidate[GT864_N];
    int16_t oracle[GT864_N];
    int16_t candidate_legacy[GT864_N];
    int16_t current[GT864_N];
    int16_t alias[GT864_N];

    gt864_radix3_forward(candidate, input);
    gt864_mont_forward(oracle, input);
    compare_exact("radix3_vs_horner_forward", case_id, candidate, oracle);
    forward_cases++;

    gt864_grid_to_legacy(candidate_legacy, candidate);
    ntt(current, input);
    compare_exact("radix3_vs_current_forward", case_id,
                  candidate_legacy, current);
    current_forward_cases++;

    memcpy(alias, input, sizeof alias);
    gt864_radix3_forward(alias, alias);
    compare_exact("radix3_forward_alias", case_id, alias, oracle);
    alias_cases++;
}

static void check_product(const int16_t a[GT864_N],
                          const int16_t b[GT864_N], int case_id)
{
    int16_t candidate[GT864_N];
    int16_t oracle[GT864_N];
    int16_t schoolbook[GT864_N];
    int16_t alias[GT864_N];

    gt864_radix3_mul(candidate, a, b);
    gt864_mont_mul(oracle, a, b);
    compare_modq("radix3_vs_horner_product", case_id, candidate, oracle);
    full_product_cases++;

    gt864_schoolbook_mul(schoolbook, a, b);
    compare_modq("radix3_vs_schoolbook_product", case_id,
                 candidate, schoolbook);
    schoolbook_product_cases++;

    memcpy(alias, a, sizeof alias);
    gt864_radix3_mul(alias, alias, b);
    compare_modq("radix3_product_alias", case_id, alias, oracle);
    alias_cases++;
}

int main(void)
{
    const int impulses[] = {0, 1, 2, 3, 8, 24, 27, 431, 432, 863};
    int16_t a[GT864_N];
    int16_t b[GT864_N];
    int case_id = 0;

    for (int kind = 0; kind < 5; kind++) {
        fill_case(a, kind);
        check_forward(a, case_id++);
    }
    for (size_t i = 0; i < sizeof impulses / sizeof impulses[0]; i++) {
        memset(a, 0, sizeof a);
        a[impulses[i]] = 1;
        check_forward(a, case_id++);
    }
    for (int i = 0; i < 24; i++) {
        fill_case(a, 5);
        check_forward(a, case_id++);
    }

    for (int kind = 0; kind < 5; kind++) {
        fill_case(a, kind);
        fill_case(b, 4 - kind);
        check_product(a, b, case_id++);
    }
    for (int i = 0; i < 16; i++) {
        fill_case(a, 5);
        fill_case(b, 5);
        check_product(a, b, case_id++);
    }

    printf("gt864_radix3_orientation,total_mismatches=%d\n", failures);
    printf("exact_horner_forward_cases=%d\n", forward_cases);
    printf("exact_current_forward_cases=%d\n", current_forward_cases);
    printf("full_product_cases=%d\n", full_product_cases);
    printf("schoolbook_product_cases=%d\n", schoolbook_product_cases);
    printf("alias_cases=%d\n", alias_cases);
    return failures != 0;
}
