#include "gt864_fr0_inverse_asm.h"
#include "gt864_fr0_inverse_barrett_tables.h"
#include "gt864_fr0_inverse_tables.h"

#include <stddef.h>

static size_t fr_index(int top, int row, int column, int component)
{
    int group = top * 18 + row * 2 + column / 8;
    return (size_t)(24 * group + 8 * component + column % 8);
}

static size_t p8_main_index(int top, int component, int column)
{
    return (size_t)(((top * 3 + component) * 16 + column) * 8);
}

void gt864_fr0_inverse_ntt9_asm(int16_t out[896], const int16_t in[864])
{
    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            int bank = top * 3 + component;
            for (int block = 0; block < 2; block++) {
                int first_column = 8 * block;
                gt864_fr0_inverse9_block_asm(
                    out + p8_main_index(top, component, first_column),
                    out + 768 + 8 * first_column + bank,
                    in + fr_index(top, 0, first_column, component),
                    gt864_inverse9_twist_barrett[top][block]);
            }
        }
    }
}

void gt864_fr0_inverse_finish_asm(int16_t out[864], const int16_t in[896])
{
    for (int component = 0; component < 3; component++) {
        for (int half_s = 0; half_s < 2; half_s++) {
            gt864_inverse16_main_block_asm(
                out + 3 * (4 * half_s) + component,
                in + p8_main_index(0, component, 0) + 4 * half_s,
                in + p8_main_index(1, component, 0) + 4 * half_s,
                gt864_inverse16_stage_barrett,
                gt864_inverse16_main_scale_barrett);
        }
    }
    gt864_inverse16_tail_block_asm(
        out + 3 * 8, in + 768, 0,
        gt864_inverse16_stage_barrett,
        gt864_inverse16_tail_scale_barrett);
}
