#include "route9.h"

#include <arm_neon.h>
#include <stdint.h>

void p3b5_baseline_r9_to(uint8_t out[1296], const int16_t fr0[864]);

extern void stock_to(uint8_t *, const int16_t *);
extern void stock_shuffle2(int16_t *, const int16_t *);

static inline int16x8_t canonical_mod_q(int16x8_t value)
{
    const int16x8_t q = vdupq_n_s16(3457);
    int16x8_t quotient = vqrdmulhq_s16(value, vdupq_n_s16(9));
    int16x8_t residual = vmlsq_s16(value, quotient, q);
    int16x8_t negative = vshrq_n_s16(residual, 15);
    return vaddq_s16(residual, vandq_s16(negative, q));
}

void p3b5_baseline_r9_to(uint8_t out[1296], const int16_t fr0[864])
{
    int16_t official[864];
    int16_t post[864];

    p3b1_r9a_f2o(official, fr0);
    for (int index = 0; index < 864; index += 8) {
        int16x8_t value = vld1q_s16(official + index);
        vst1q_s16(official + index, canonical_mod_q(value));
    }
    stock_shuffle2(post, official);
    stock_to(out, post);
}
