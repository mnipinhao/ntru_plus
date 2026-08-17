#include "inverse_stage1_intrinsic.h"

#include <stdint.h>
#include <string.h>

static int16_t alias_a[768] __attribute__((aligned(32)));
static int16_t alias_b[768] __attribute__((aligned(32)));

void round4c_qbm_inverse_stage1_fused(int16_t out[768],
                                      const int16_t a[768],
                                      const int16_t b[768])
{
    if (out == a) {
        memcpy(alias_a, a, sizeof(alias_a));
        a = alias_a;
    }
    if (out == b) {
        memcpy(alias_b, b, sizeof(alias_b));
        b = alias_b;
    }
    round4c_qbm_inverse_stage1_fused_asm(out, a, b);
}
