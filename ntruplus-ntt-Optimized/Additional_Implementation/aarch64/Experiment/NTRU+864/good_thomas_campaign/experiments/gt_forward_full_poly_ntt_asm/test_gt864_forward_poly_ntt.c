#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt864_fr0_to_official_map.h"

#define N 864
#define Q 3457

extern void poly_ntt(int16_t *out, const int16_t *in);
extern void gt864_forward_poly_ntt_experiment(int16_t *out, const int16_t *in);

static uint32_t rng_state = 0x8645f00du;

static uint32_t random_u32(void) {
    uint32_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rng_state = x;
    return x;
}

static int centered(int value) {
    value %= Q;
    if (value < 0) value += Q;
    if (value > Q / 2) value -= Q;
    return value;
}

static int run_case(const int16_t input[N], const char *kind, int id) {
    int16_t official[N];
    int16_t fr0[N];
    poly_ntt(official, input);
    gt864_forward_poly_ntt_experiment(fr0, input);

    for (int i = 0; i < N; ++i) {
        const int candidate = fr0[gt864_fr0_for_official[i]];
        if (centered(official[i]) != centered(candidate)) {
            fprintf(stderr,
                    "%s case %d offset %d map %u: official=%d candidate=%d\n",
                    kind, id, i, gt864_fr0_for_official[i],
                    official[i], candidate);
            return 0;
        }
    }
    return 1;
}

int main(void) {
    int16_t input[N];
    int cases = 0;

    memset(input, 0, sizeof(input));
    if (!run_case(input, "zero", 0)) return 1;
    ++cases;

    static const int16_t constants[] = {-1728, -1, 1, 1728, 3456};
    for (unsigned k = 0; k < sizeof(constants) / sizeof(constants[0]); ++k) {
        for (int i = 0; i < N; ++i) input[i] = constants[k];
        if (!run_case(input, "constant", (int)k)) return 1;
        ++cases;
    }

    for (int position = 0; position < N; ++position) {
        memset(input, 0, sizeof(input));
        input[position] = 1;
        if (!run_case(input, "basis", position)) return 1;
        ++cases;
    }

    for (int trial = 0; trial < 256; ++trial) {
        for (int i = 0; i < N; ++i)
            input[i] = (int16_t)((int)(random_u32() % 3457u) - 1728);
        if (!run_case(input, "centered-random", trial)) return 1;
        ++cases;
    }

    for (int trial = 0; trial < 128; ++trial) {
        for (int i = 0; i < N; ++i)
            input[i] = (int16_t)(random_u32() % 3457u);
        if (!run_case(input, "canonical-random", trial)) return 1;
        ++cases;
    }

    printf("gt864_forward_full_poly_ntt_m5o=pass cases=%d comparisons=%d\n",
           cases, cases * N);
    return 0;
}
