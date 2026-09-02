#include "gt864_friso2_inverse.h"
#include "gt864_friso2_inverse_tables.h"

/*
 * Reuse M5D's frozen FR-0 inverse implementation in this experimental
 * translation unit.  Its static helpers define the exact arithmetic and P8
 * boundary consumed below; the new public entry point changes only the leaf
 * basis consumed by inverse NTT9.
 */
#include "../gt_fr0_inverse_consumer/gt864_fr0_inverse.c"

/* Algorithm 10: fixed-public-constant Barrett-Shoup multiplication. */
static inline int16x8_t barrett_mul_public(int16x8_t x, int16_t constant,
                                          int16_t reciprocal)
{
    int16x8_t product = vmulq_s16(x, vdupq_n_s16(constant));
    int16x8_t quotient = vqrdmulhq_s16(x, vdupq_n_s16(reciprocal));
    return vmlsq_s16(product, quotient, vdupq_n_s16(3457));
}

void gt864_friso2_inverse_ntt9_neon(int16_t out[GT864_INVERSE_P8_PADDED],
                                    const int16_t in[GT864_FR0_COEFFICIENTS])
{
    int16x8_t mod = vld1q_s16(mod_consts);

    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            int bank = top * 3 + component;
            for (int block = 0; block < 2; block++) {
                int first_column = 8 * block;
                vectors9 rows;
                vectors8 first8;
                vectors8 columns;

                for (int row = 0; row < 9; row++) {
                    rows.v[row] = vld1q_s16(
                        in + fr_index(top, row, first_column, component));
                    /*
                     * tau(top,row,column)^j
                     *   = delta(top,column)^j * gamma^(j*row).
                     * Remove only the row-dependent factor here.  Row zero
                     * and all of component zero are exact no-ops.
                     */
                    if (component != 0 && row != 0)
                        rows.v[row] = barrett_mul_public(
                            rows.v[row],
                            gt864_friso2_inverse_row_barrett[component][row][0],
                            gt864_friso2_inverse_row_barrett[component][row][1]);
                }

                /* delta(top,column)^(-j) is already fused into this table. */
                rows = intt9_fr(
                    rows,
                    gt864_friso2_inverse9_twist_mont
                        [top][component][block],
                    mod);
                for (int s = 0; s < 8; s++)
                    first8.v[s] = rows.v[s];
                columns = transpose8x8_s16(first8);
                for (int lane = 0; lane < 8; lane++)
                    vst1q_s16(out + p8_main_index(
                        top, component, first_column + lane), columns.v[lane]);

#define STORE_TAIL(lane)                                                     \
                vst1q_lane_s16(out + GT864_INVERSE_P8_MAIN +                \
                    8 * (first_column + (lane)) + bank, rows.v[8], (lane))
                STORE_TAIL(0); STORE_TAIL(1); STORE_TAIL(2); STORE_TAIL(3);
                STORE_TAIL(4); STORE_TAIL(5); STORE_TAIL(6); STORE_TAIL(7);
#undef STORE_TAIL
            }
        }
    }
}
