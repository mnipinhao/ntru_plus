/* P135 prototype: NTRU+768 poly_frombytes_encap, one output vector at a time.
 * Each 4-lane half of an output vector is four consecutive wire coefficients,
 * six contiguous bytes (encap_halves.h).  Per vector: two 16-byte loads, one
 * two-register tbl to [A0 A1 A1 A2 ... | B...] halfword byte pairs, ushl by
 * (0,-4,...) and and 0xfff, a running maximum, one 16-byte store.  The two
 * halves whose load would pass byte 1152 load the 16 bytes ending there,
 * with the index shifted. */
#include <arm_neon.h>
#include <stdint.h>
#include "encap_halves.h"

#define Q 3457
#define POLYBYTES 1152

int frombytes_encap_pairs(int16_t out[768], const uint8_t in[POLYBYTES])
{
    static const int16_t shift_pattern[8] = {0, -4, 0, -4, 0, -4, 0, -4};
    const int16x8_t sh = vld1q_s16(shift_pattern);
    const uint16x8_t low12 = vdupq_n_u16(0x0fff);
    uint16x8_t hi = vdupq_n_u16(0);

#pragma GCC unroll 96
    for (int v = 0; v < 96; v++) {
        int oa = encap_half_off[v][0], ob = encap_half_off[v][1];
        int la = oa + 16 <= POLYBYTES ? oa : POLYBYTES - 16;
        int lb = ob + 16 <= POLYBYTES ? ob : POLYBYTES - 16;
        int da = oa - la, db = ob - lb;                   /* 0 except near the end */
        const uint8x16_t idx = {
            (uint8_t)(da + 0), (uint8_t)(da + 1), (uint8_t)(da + 1), (uint8_t)(da + 2),
            (uint8_t)(da + 3), (uint8_t)(da + 4), (uint8_t)(da + 4), (uint8_t)(da + 5),
            (uint8_t)(16 + db + 0), (uint8_t)(16 + db + 1), (uint8_t)(16 + db + 1), (uint8_t)(16 + db + 2),
            (uint8_t)(16 + db + 3), (uint8_t)(16 + db + 4), (uint8_t)(16 + db + 4), (uint8_t)(16 + db + 5)};
        uint8x16x2_t t = {{ vld1q_u8(in + la), vld1q_u8(in + lb) }};
        uint16x8_t w = vreinterpretq_u16_u8(vqtbl2q_u8(t, idx));
        uint16x8_t c = vandq_u16(vshlq_u16(w, sh), low12);
        hi = vmaxq_u16(hi, c);
        vst1q_s16(out + 8 * v, vreinterpretq_s16_u16(c));
    }
    return vmaxvq_u16(hi) >= Q;
}
