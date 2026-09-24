/* P133 prototype: NTRU+864 frombytes as the exact inverse of the run-based
 * serializer (pack.c).  Group p, lane j of vector pack6_vec[p][i] holds
 * coefficient i of the nine-byte run at byte pack6_off[p][j].
 *
 * Per group: one 16-byte load per run at its own offset, one tbl expanding the
 * nine bytes into six halfwords [b0 b1][b1 b2][b3 b4][b4 b5][b6 b7][b7 b8], an
 * 8x8 halfword transpose so vector i holds halfword i of all eight runs, and
 * one and/ushr per vector (the same for every lane: even i keeps the low 12
 * bits, odd i drops the low 4).  The only run whose 16-byte load would pass
 * byte 1296 (offset 1287) loads the 16 bytes ending at the end instead, with
 * the index shifted by seven. */
#include <arm_neon.h>
#include <stdint.h>
#include "pack6.h"

#define Q 3457
#define POLYBYTES 1296

static const uint8_t run_index[16] __attribute__((aligned(16))) =
    {0, 1, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 0xff, 0xff, 0xff, 0xff};
static const uint8_t run_index_end[16] __attribute__((aligned(16))) =
    {7, 8, 8, 9, 10, 11, 11, 12, 13, 14, 14, 15, 0xff, 0xff, 0xff, 0xff};

#define S32(x) vreinterpretq_s32_u16(x)
#define U16_32(x) vreinterpretq_u16_s32(x)
#define S64(x) vreinterpretq_s64_u16(x)
#define U16_64(x) vreinterpretq_u16_s64(x)

static inline void transpose8(uint16x8_t v[8])
{
    uint16x8_t a0 = vtrn1q_u16(v[0], v[1]), a1 = vtrn2q_u16(v[0], v[1]);
    uint16x8_t a2 = vtrn1q_u16(v[2], v[3]), a3 = vtrn2q_u16(v[2], v[3]);
    uint16x8_t a4 = vtrn1q_u16(v[4], v[5]), a5 = vtrn2q_u16(v[4], v[5]);
    uint16x8_t a6 = vtrn1q_u16(v[6], v[7]), a7 = vtrn2q_u16(v[6], v[7]);
    uint16x8_t b0 = U16_32(vtrn1q_s32(S32(a0), S32(a2)));
    uint16x8_t b2 = U16_32(vtrn2q_s32(S32(a0), S32(a2)));
    uint16x8_t b1 = U16_32(vtrn1q_s32(S32(a1), S32(a3)));
    uint16x8_t b3 = U16_32(vtrn2q_s32(S32(a1), S32(a3)));
    uint16x8_t b4 = U16_32(vtrn1q_s32(S32(a4), S32(a6)));
    uint16x8_t b6 = U16_32(vtrn2q_s32(S32(a4), S32(a6)));
    uint16x8_t b5 = U16_32(vtrn1q_s32(S32(a5), S32(a7)));
    uint16x8_t b7 = U16_32(vtrn2q_s32(S32(a5), S32(a7)));
    v[0] = U16_64(vtrn1q_s64(S64(b0), S64(b4)));
    v[4] = U16_64(vtrn2q_s64(S64(b0), S64(b4)));
    v[1] = U16_64(vtrn1q_s64(S64(b1), S64(b5)));
    v[5] = U16_64(vtrn2q_s64(S64(b1), S64(b5)));
    v[2] = U16_64(vtrn1q_s64(S64(b2), S64(b6)));
    v[3] = U16_64(vtrn1q_s64(S64(b3), S64(b7)));
    /* rows 6 and 7 would be halfwords 6 and 7 of the runs: never used */
}

int frombytes_runs(int16_t out[864], const uint8_t in[POLYBYTES])
{
    const uint8x16_t idx = vld1q_u8(run_index), idx_end = vld1q_u8(run_index_end);
    const uint16x8_t mask = vdupq_n_u16(0x0fff);
    uint16x8_t hi = vdupq_n_u16(0);

#pragma GCC unroll 18
    for (int p = 0; p < PACK6_GROUPS; p++) {
        const unsigned short *w = pack6_off[p];
        const unsigned char *vi = pack6_vec[p];
        uint16x8_t v[8];
#pragma GCC unroll 8
        for (int j = 0; j < 8; j++) {
            if (w[j] + 16 <= POLYBYTES)
                v[j] = vreinterpretq_u16_u8(vqtbl1q_u8(vld1q_u8(in + w[j]), idx));
            else
                v[j] = vreinterpretq_u16_u8(vqtbl1q_u8(vld1q_u8(in + POLYBYTES - 16), idx_end));
        }
        transpose8(v);
        uint16x8_t c[6];
        c[0] = vandq_u16(v[0], mask); c[1] = vshrq_n_u16(v[1], 4);
        c[2] = vandq_u16(v[2], mask); c[3] = vshrq_n_u16(v[3], 4);
        c[4] = vandq_u16(v[4], mask); c[5] = vshrq_n_u16(v[5], 4);
        hi = vmaxq_u16(hi, vmaxq_u16(vmaxq_u16(vmaxq_u16(c[0], c[1]), vmaxq_u16(c[2], c[3])),
                                     vmaxq_u16(c[4], c[5])));
        for (int i = 0; i < 6; i++) vst1q_s16(out + 8 * vi[i], vreinterpretq_s16_u16(c[i]));
    }
    return vmaxvq_u16(hi) >= Q;
}
