#include <arm_neon.h>
#include <stdint.h>

#include "gather.h"
#include "tables.h"

void p3b11_baseline_c1_from(int16_t out[864], const uint8_t in[1296]);

void p3b11_baseline_c1_from(int16_t out[864], const uint8_t in[1296])
{
    for (int q = 0; q < 108; q += 4) {
        uint16x8_t value[4];
        gather4_r(value, in, addr_r + 8 * q, shift_r + 8 * q);
        for (int j = 0; j < 4; j++)
            vst1q_u16((uint16_t *)out + 8 * (q + j), value[j]);
    }
}
