#include <arm_neon.h>
#include <stdint.h>
#include <stdio.h>

#include "params.h"

int main(void)
{
    const int16x8_t q = vdupq_n_s16(NTRUPLUS_Q);
    unsigned p1_mismatches = 0;
    unsigned p2_mismatches = 0;
    unsigned p3_mismatches = 0;

    for (int first = -NTRUPLUS_Q; first < NTRUPLUS_Q; first += 8) {
        int16_t lanes[8];
        int16_t p1_out[8];
        int16_t p2_out[8];
        int16_t p3_out[8];
        for (int lane = 0; lane < 8; lane++) {
            int value = first + lane;
            if (value >= NTRUPLUS_Q)
                value = NTRUPLUS_Q - 1;
            lanes[lane] = (int16_t)value;
        }

        const int16x8_t x = vld1q_s16(lanes);
        const int16x8_t sign = vshrq_n_s16(x, 15);
        const int16x8_t sign_bit = vreinterpretq_s16_u16(
            vshrq_n_u16(vreinterpretq_u16_s16(x), 15));
        const int16x8_t p1 = vaddq_s16(x, vandq_s16(sign, q));
        const int16x8_t p2 = vmlsq_s16(x, sign, q);
        const int16x8_t p3 = vmlaq_s16(x, sign_bit, q);
        vst1q_s16(p1_out, p1);
        vst1q_s16(p2_out, p2);
        vst1q_s16(p3_out, p3);

        for (int lane = 0; lane < 8; lane++) {
            const int16_t want =
                (int16_t)(lanes[lane] < 0 ? lanes[lane] + NTRUPLUS_Q
                                          : lanes[lane]);
            p1_mismatches += p1_out[lane] != want;
            p2_mismatches += p2_out[lane] != want;
            p3_mismatches += p3_out[lane] != want;
        }
    }

    printf("canonical_normalize_p1_mismatches=%u\n", p1_mismatches);
    printf("canonical_normalize_p2_mismatches=%u\n", p2_mismatches);
    printf("canonical_normalize_p3_mismatches=%u\n", p3_mismatches);
    return p1_mismatches == 0 && p2_mismatches == 0 && p3_mismatches == 0
               ? 0
               : 1;
}
