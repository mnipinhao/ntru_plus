#include "gt_schoolbook.h"

#include <stddef.h>

int16_t gt_centered_q(int64_t x)
{
    int64_t r = x % GT_Q;

    if (r < 0)
        r += GT_Q;
    if (r > (GT_Q - 1) / 2)
        r -= GT_Q;
    return (int16_t)r;
}

void gt_schoolbook_mul(int16_t r[GT_N], const int16_t a[GT_N],
                       const int16_t b[GT_N])
{
    int64_t c[2 * GT_N - 1] = {0};

    for (size_t i = 0; i < GT_N; ++i)
        for (size_t j = 0; j < GT_N; ++j)
            c[i + j] += (int64_t)a[i] * b[j];

    /* x^i = x^(i-384) - x^(i-768), processed high to low. */
    for (size_t i = 2 * GT_N - 1; i-- > GT_N;) {
        c[i - GT_N / 2] += c[i];
        c[i - GT_N] -= c[i];
    }

    for (size_t i = 0; i < GT_N; ++i)
        r[i] = gt_centered_q(c[i]);
}

int gt_equal_mod_q(const int16_t a[GT_N], const int16_t b[GT_N])
{
    for (size_t i = 0; i < GT_N; ++i)
        if (gt_centered_q((int64_t)a[i] - b[i]) != 0)
            return 0;
    return 1;
}
