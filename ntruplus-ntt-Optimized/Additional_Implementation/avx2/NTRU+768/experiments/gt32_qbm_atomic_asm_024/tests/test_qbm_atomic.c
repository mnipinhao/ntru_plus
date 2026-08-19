#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "qbm_atomic.h"
#include "quadratic-constants.h"
#include "qbm_intrinsic.h"

static uint64_t state = UINT64_C(0x6a09e667f3bcc909);

static uint32_t random32(void)
{
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

static void fill_random(int16_t values[768])
{
    for (size_t i = 0; i < 768; ++i)
        values[i] = (int16_t)((int)(random32() % 6913) - 3456);
}

static int run_case(const int16_t input_a[768], const int16_t input_b[768])
{
    _Alignas(32) int16_t reference[768];
    _Alignas(32) int16_t control[768];
    _Alignas(32) int16_t atomic[768];
    _Alignas(32) int16_t alias[768];

    round4c_qbm_vector_intrinsic(reference, input_a, input_b);
    qbm_selected_control_asm(control, input_a, input_b,
                             round4c_weight_mont, round4c_weight_qinv);
    qbm_atomic_expanded_asm(atomic, input_a, input_b,
                            round4c_weight_mont, round4c_weight_qinv);
    if (memcmp(reference, control, sizeof reference) != 0 ||
        memcmp(reference, atomic, sizeof reference) != 0)
        return 1;

    memcpy(alias, input_a, sizeof alias);
    qbm_atomic_expanded_asm(alias, alias, input_b,
                            round4c_weight_mont, round4c_weight_qinv);
    if (memcmp(reference, alias, sizeof reference) != 0)
        return 2;
    memcpy(alias, input_b, sizeof alias);
    qbm_atomic_expanded_asm(alias, input_a, alias,
                            round4c_weight_mont, round4c_weight_qinv);
    return memcmp(reference, alias, sizeof reference) != 0 ? 3 : 0;
}

int main(void)
{
    _Alignas(32) int16_t a[768];
    _Alignas(32) int16_t b[768];
    static const int16_t edges[] = {-3456, -1728, -1, 0, 1, 1728, 3456};

    for (size_t i = 0; i < 768; ++i) {
        a[i] = edges[i % (sizeof edges / sizeof edges[0])];
        b[i] = edges[(3 * i + 1) % (sizeof edges / sizeof edges[0])];
    }
    if (run_case(a, b) != 0) {
        fputs("boundary differential failed\n", stderr);
        return 1;
    }
    for (size_t trial = 0; trial < 1000; ++trial) {
        fill_random(a);
        fill_random(b);
        if (run_case(a, b) != 0) {
            fprintf(stderr, "random/alias differential failed at %zu\n", trial);
            return 1;
        }
    }
    puts("qbm selected/atomic ASM: 1000 random + boundary + alias pass");
    return 0;
}
