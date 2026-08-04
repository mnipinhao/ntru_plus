#include "forward_intrinsic.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "quadratic-constants.h"

enum { Q = 3457, CENTER = 1728, R_INVERSE = 2775 };

typedef void (*forward_kernel)(int16_t *, const int16_t *);

static uint32_t rng_state = 0x46313634u;

static uint32_t random32(void)
{
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 17;
    rng_state ^= rng_state << 5;
    return rng_state;
}

static int modq(int64_t value)
{
    int result = (int)(value % Q);
    return result < 0 ? result + Q : result;
}

static int standard_constant(int16_t mont)
{
    return modq((int64_t)mont * R_INVERSE);
}

static void scalar_forward_quadratic(int16_t out[768], const int16_t in[768])
{
    for (size_t k3 = 0; k3 < 3; ++k3) {
        for (size_t k16 = 0; k16 < 16; ++k16) {
            const size_t vector = 16 * k3 + k16;
            for (size_t branch = 0; branch < 4; ++branch) {
                const size_t lane = 4 * branch;
                const int root = standard_constant(
                    round4c_split_mont[vector][lane]);
                const int alpha = modq((int64_t)root * root);
                int value[4] = {0, 0, 0, 0};
                for (size_t degree = 0; degree < 4; ++degree) {
                    int power = 1;
                    int64_t accumulator = 0;
                    for (size_t n = 0; n < 192; ++n) {
                        accumulator += (int64_t)in[4 * n + degree] * power;
                        power = modq((int64_t)power * alpha);
                    }
                    value[degree] = modq(accumulator);
                }
                out[16 * vector + lane + 0] = (int16_t)modq(
                    value[0] + (int64_t)root * value[2]);
                out[16 * vector + lane + 1] = (int16_t)modq(
                    value[1] + (int64_t)root * value[3]);
                out[16 * vector + lane + 2] = (int16_t)modq(
                    value[0] - (int64_t)root * value[2]);
                out[16 * vector + lane + 3] = (int16_t)modq(
                    value[1] - (int64_t)root * value[3]);
            }
        }
    }
}

static int congruent(const int16_t got[768], const int16_t want[768],
                     const char *label, int *maximum)
{
    for (size_t i = 0; i < 768; ++i) {
        const int absolute = got[i] < 0 ? -got[i] : got[i];
        if (absolute > *maximum)
            *maximum = absolute;
        if (modq(got[i]) != modq(want[i])) {
            fprintf(stderr, "%s mismatch i=%zu got=%d want=%d\n",
                    label, i, got[i], want[i]);
            return 1;
        }
    }
    return 0;
}

static int check_case(const int16_t input[768], size_t case_index,
                      int *maximum)
{
    static const forward_kernel kernels[4] = {
        round4c_forward_f0_materialized,
        round4c_forward_f0_fused,
        round4c_forward_f1_materialized,
        round4c_forward_f1_fused,
    };
    static const char *const labels[4] = {
        "F0-M", "F0-F", "F1-M", "F1-F",
    };
    int16_t want[768] __attribute__((aligned(32)));
    int16_t outputs[4][768] __attribute__((aligned(32)));
    int16_t alias[768] __attribute__((aligned(32)));
    scalar_forward_quadratic(want, input);
    for (size_t candidate = 0; candidate < 4; ++candidate) {
        kernels[candidate](outputs[candidate], input);
        if (congruent(outputs[candidate], want, labels[candidate], maximum)) {
            fprintf(stderr, "case=%zu\n", case_index);
            return 1;
        }
        memcpy(alias, input, sizeof(alias));
        kernels[candidate](alias, alias);
        if (memcmp(alias, outputs[candidate], sizeof(alias)) != 0) {
            fprintf(stderr, "%s alias mismatch case=%zu\n",
                    labels[candidate], case_index);
            return 1;
        }
    }
    if (memcmp(outputs[0], outputs[1], sizeof(outputs[0])) != 0 ||
        memcmp(outputs[2], outputs[3], sizeof(outputs[2])) != 0) {
        fprintf(stderr, "materialized/fused representative mismatch case=%zu\n",
                case_index);
        return 1;
    }
    return 0;
}

int main(void)
{
    int16_t input[768] __attribute__((aligned(32)));
    int maximum = 0;
    size_t cases = 0;
    const int16_t boundaries[] = {-3, 4};
    memset(input, 0, sizeof(input));
    if (check_case(input, cases++, &maximum))
        return 1;
    for (size_t impulse = 0; impulse < 8; ++impulse) {
        memset(input, 0, sizeof(input));
        input[(impulse * 109) % 768] = (impulse & 1) ? -3 : 4;
        if (check_case(input, cases++, &maximum))
            return 1;
    }
    for (size_t pattern = 0; pattern < 4; ++pattern) {
        for (size_t i = 0; i < 768; ++i)
            input[i] = boundaries[(i + pattern) & 1];
        if (check_case(input, cases++, &maximum))
            return 1;
    }
    for (size_t random_case = 0; random_case < 64; ++random_case) {
        for (size_t i = 0; i < 768; ++i)
            input[i] = (int16_t)((int)(random32() & 7) - 3);
        if (check_case(input, cases++, &maximum))
            return 1;
    }
    printf("forward intrinsic cases=%zu candidates=4 alias=pass max_abs=%d failures=0\n",
           cases, maximum);
    return 0;
}
