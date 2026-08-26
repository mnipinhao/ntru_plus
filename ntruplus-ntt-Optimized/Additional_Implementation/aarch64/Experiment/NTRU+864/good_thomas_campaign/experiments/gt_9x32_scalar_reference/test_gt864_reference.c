#include "gt864_reference.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint32_t random_state = 0x8649U;
static int failures;
static int forward_cases;
static int roundtrip_cases;
static int multiplication_cases;
static int alias_cases;

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

static void compare(const char *label, int case_id,
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

static void fill_case(int16_t value[GT864_N], int kind)
{
    for (int i = 0; i < GT864_N; i++) {
        switch (kind) {
        case 0:
            value[i] = 0;
            break;
        case 1:
            value[i] = 1;
            break;
        case 2:
            value[i] = (int16_t)(i & 1 ? GT864_Q - 1 : 1);
            break;
        case 3:
            value[i] = 1728;
            break;
        case 4:
            value[i] = canonical(-1728);
            break;
        default:
            value[i] = (int16_t)(next_u32() % GT864_Q);
            break;
        }
    }
}

static void check_transform_case(const int16_t input[GT864_N], int case_id)
{
    int16_t direct[GT864_N];
    int16_t factorized[GT864_N];
    int16_t roundtrip[GT864_N];
    int16_t expected[GT864_N];
    int16_t alias[GT864_N];

    for (int i = 0; i < GT864_N; i++)
        expected[i] = canonical(input[i]);

    gt864_forward_direct(direct, input);
    gt864_forward(factorized, input);
    compare("forward_direct", case_id, factorized, direct);
    forward_cases++;

    gt864_inverse(roundtrip, factorized);
    compare("roundtrip", case_id, roundtrip, expected);
    roundtrip_cases++;

    memcpy(alias, input, sizeof alias);
    gt864_forward(alias, alias);
    compare("forward_alias", case_id, alias, factorized);
    gt864_inverse(alias, alias);
    compare("inverse_alias", case_id, alias, expected);
    alias_cases += 2;
}

static void check_multiplication_case(const int16_t a[GT864_N],
                                      const int16_t b[GT864_N], int case_id)
{
    int16_t got[GT864_N];
    int16_t expected[GT864_N];
    int16_t alias[GT864_N];

    gt864_mul(got, a, b);
    gt864_schoolbook_mul(expected, a, b);
    compare("multiplication", case_id, got, expected);
    multiplication_cases++;

    memcpy(alias, a, sizeof alias);
    gt864_mul(alias, alias, b);
    compare("multiplication_alias", case_id, alias, expected);
    alias_cases++;
}

int main(void)
{
    int16_t a[GT864_N];
    int16_t b[GT864_N];
    const int impulses[] = {0, 1, 2, 3, 431, 432, 863};
    int case_id = 0;

    for (int kind = 0; kind < 5; kind++) {
        fill_case(a, kind);
        check_transform_case(a, case_id++);
    }

    for (size_t i = 0; i < sizeof impulses / sizeof impulses[0]; i++) {
        memset(a, 0, sizeof a);
        a[impulses[i]] = 1;
        check_transform_case(a, case_id++);
    }

    for (int i = 0; i < 24; i++) {
        fill_case(a, 5);
        check_transform_case(a, case_id++);
    }

    for (int kind = 0; kind < 5; kind++) {
        fill_case(a, kind);
        fill_case(b, 4 - kind);
        check_multiplication_case(a, b, case_id++);
    }

    for (int i = 0; i < 16; i++) {
        fill_case(a, 5);
        fill_case(b, 5);
        check_multiplication_case(a, b, case_id++);
    }

    printf("gt864_scalar_reference,total_mismatches=%d\n", failures);
    printf("forward_direct_cases=%d\n", forward_cases);
    printf("roundtrip_cases=%d\n", roundtrip_cases);
    printf("multiplication_schoolbook_cases=%d\n", multiplication_cases);
    printf("alias_cases=%d\n", alias_cases);
    return failures != 0;
}
