#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt864_friso2.h"

#define N 864
#define Q 3457

extern void gt864_forward_poly_ntt_all_one_mul_b3(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_friso2(int16_t *, const int16_t *);

static uint32_t state = 0x864cf001u;

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

static int run_case(const int16_t input[N], const char *kind, int id)
{
    int16_t baseline[N] __attribute__((aligned(16)));
    int16_t expected[N] __attribute__((aligned(16)));
    int16_t candidate[N] __attribute__((aligned(16)));
    int16_t alias[N] __attribute__((aligned(16)));
    gt864_forward_poly_ntt_all_one_mul_b3(baseline, input);
    gt864_friso2_normalize(expected, baseline);
    gt864_forward_poly_ntt_friso2(candidate, input);
    memcpy(alias, input, sizeof(alias));
    gt864_forward_poly_ntt_friso2(alias, alias);
    for (int i = 0; i < N; ++i) {
        if (centered(expected[i]) != centered(candidate[i]) ||
            centered(expected[i]) != centered(alias[i])) {
            fprintf(stderr, "%s case=%d index=%d expected=%d candidate=%d alias=%d\n",
                    kind, id, i, expected[i], candidate[i], alias[i]);
            return 1;
        }
    }
    return 0;
}

int main(void)
{
    int16_t input[N];
    int cases = 0;
    memset(input, 0, sizeof(input));
    if (run_case(input, "zero", 0)) return 1;
    ++cases;
    static const int16_t constants[] = {-1728, -1, 1, 1728, 3456};
    for (unsigned k = 0; k < sizeof(constants) / sizeof(constants[0]); ++k) {
        for (int i = 0; i < N; ++i) input[i] = constants[k];
        if (run_case(input, "constant", (int)k)) return 1;
        ++cases;
    }
    for (int position = 0; position < N; ++position) {
        memset(input, 0, sizeof(input));
        input[position] = 1;
        if (run_case(input, "basis", position)) return 1;
        ++cases;
    }
    for (int trial = 0; trial < 256; ++trial) {
        for (int i = 0; i < N; ++i)
            input[i] = (int16_t)((int)(next_u32() % Q) - 1728);
        if (run_case(input, "random", trial)) return 1;
        ++cases;
    }
    printf("gt864_friso2_forward_absorption=pass cases=%d comparisons=%d alias_comparisons=%d\n",
           cases, cases * N, cases * N);
    return 0;
}
