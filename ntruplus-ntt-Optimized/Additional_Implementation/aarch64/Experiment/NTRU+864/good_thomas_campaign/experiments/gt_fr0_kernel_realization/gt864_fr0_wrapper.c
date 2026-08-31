#include "gt864_fr0_asm.h"

#include "../gt_boundary_cost_campaign/gt864_boundary_tables.h"

#include <stddef.h>

void gt864_boundary_fr0_asm(
    int16_t out[GT864_FR0_OUTPUT_COEFFICIENTS],
    const int16_t in[GT864_FR0_INPUT_COEFFICIENTS])
{
    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            int bank = top * 3 + component;

            for (int block = 0; block < 2; block++) {
                int first_column = block * 8;
                size_t main_offset =
                    (size_t)(((bank * 16 + first_column) * 8));
                size_t tail_offset =
                    (size_t)(768 + first_column * 8 + bank);
                int first_group = top * 18 + block;
                size_t output_offset =
                    (size_t)(24 * first_group + 8 * component);

                gt864_fr0_block_asm(
                    out + output_offset,
                    in + main_offset,
                    in + tail_offset,
                    &gt864_twist_fr_mont[top][block][0][0]);
            }
        }
    }
}
