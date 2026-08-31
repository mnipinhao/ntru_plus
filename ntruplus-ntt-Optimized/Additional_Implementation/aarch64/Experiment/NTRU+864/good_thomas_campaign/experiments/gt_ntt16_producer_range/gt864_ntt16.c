#include "gt864_ntt16.h"
#include "gt864_ntt16_tables.h"

#include <arm_neon.h>
#include <stddef.h>

static const int16_t mod_consts[8] __attribute__((aligned(16))) = {
    3457, 0, -12929, 0, 0, 0, 0, 0
};

static const uint8_t bit_reverse4[16] = {
    0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15
};

/* R0 x times public cR -> bounded R0, identical to the M5A reduction. */
static inline int16x8_t fqmul_public(int16x8_t x, int16x8_t c,
                                     int16x8_t mod)
{
    int32x4_t low = vmull_s16(vget_low_s16(x), vget_low_s16(c));
    int32x4_t high = vmull_high_s16(x, c);
    int16x8_t quotient;

    quotient = vuzp1q_s16(vreinterpretq_s16_s32(low),
                          vreinterpretq_s16_s32(high));
    quotient = vmulq_laneq_s16(quotient, mod, 2);
    low = vmlal_lane_s16(low, vget_low_s16(quotient),
                         vget_low_s16(mod), 0);
    high = vmlal_high_lane_s16(high, quotient,
                               vget_low_s16(mod), 0);
    return vuzp2q_s16(vreinterpretq_s16_s32(low),
                      vreinterpretq_s16_s32(high));
}

static inline void radix2_layers(int16x8_t value[16], int16x8_t mod)
{
    for (int stage = 0, length = 2; stage < 4; stage++, length <<= 1) {
        int half = length >> 1;

        for (int start = 0; start < 16; start += length) {
            for (int j = 0; j < half; j++) {
                int left = start + j;
                int right = left + half;
                int16x8_t u = value[left];
                int16x8_t twiddle = vdupq_n_s16(
                    gt864_ntt16_stage_twiddle_mont[stage][j]);
                int16x8_t v = fqmul_public(value[right], twiddle, mod);

                value[left] = vaddq_s16(u, v);
                value[right] = vsubq_s16(u, v);
            }
        }
    }
}

static void ntt16_uniform_bank(int16_t *bank, int top, int16x8_t mod)
{
    int16x8_t value[16];

    /* Public bit-reversed register placement; input memory remains t-natural. */
    for (int t = 0; t < 16; t++) {
        int16x8_t input = vld1q_s16(bank + 8 * t);
        int16x8_t twist = vdupq_n_s16(gt864_ntt16_twist_mont[top][t]);
        value[bit_reverse4[t]] = fqmul_public(input, twist, mod);
    }
    radix2_layers(value, mod);
    for (int column = 0; column < 16; column++)
        vst1q_s16(bank + 8 * column, value[column]);
}

static void ntt16_mixed_tail(int16_t *tail, int16x8_t mod)
{
    int16x8_t value[16];

    for (int t = 0; t < 16; t++) {
        int16x8_t input = vld1q_s16(tail + 8 * t);
        value[bit_reverse4[t]] = fqmul_public(
            input, vld1q_s16(gt864_ntt16_tail_twist_mont[t]), mod);
    }
    radix2_layers(value, mod);
    for (int column = 0; column < 16; column++)
        vst1q_s16(tail + 8 * column, value[column]);
}

void gt864_ntt16_p8_neon(
    int16_t io[GT864_NTT16_PADDED_COEFFICIENTS])
{
    int16x8_t mod = vld1q_s16(mod_consts);

    for (int bank = 0; bank < 6; bank++)
        ntt16_uniform_bank(io + 128 * bank, bank / 3, mod);
    ntt16_mixed_tail(io + GT864_NTT16_MAIN_COEFFICIENTS, mod);
}
