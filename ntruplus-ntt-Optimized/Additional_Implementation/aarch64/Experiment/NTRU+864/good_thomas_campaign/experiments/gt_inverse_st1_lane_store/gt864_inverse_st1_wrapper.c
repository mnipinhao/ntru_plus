#include "gt864_fr0_inverse_barrett_tables.h"

#include <stdint.h>
#include <stddef.h>

void gt864_inverse16_main_block_st1_asm(
    int16_t *, const int16_t *, const int16_t *,
    const int16_t [4][16], const int16_t [16][2][8]);
void gt864_inverse16_tail_block_st1_asm(
    int16_t *, const int16_t *, const int16_t *,
    const int16_t [4][16], const int16_t [16][2][8]);

static size_t p8_main_index(int top, int component, int column)
{
    return (size_t)(((top * 3 + component) * 16 + column) * 8);
}

void gt864_fr0_inverse_finish_st1(int16_t out[864], const int16_t in[896])
{
    for (int component = 0; component < 3; component++) {
        for (int half_s = 0; half_s < 2; half_s++) {
            gt864_inverse16_main_block_st1_asm(
                out + 3 * (4 * half_s) + component,
                in + p8_main_index(0, component, 0) + 4 * half_s,
                in + p8_main_index(1, component, 0) + 4 * half_s,
                gt864_inverse16_stage_barrett,
                gt864_inverse16_main_scale_barrett);
        }
    }
    gt864_inverse16_tail_block_st1_asm(
        out + 3 * 8, in + 768, 0,
        gt864_inverse16_stage_barrett,
        gt864_inverse16_tail_scale_barrett);
}
