#ifndef GT864_FR0_ASM_H
#define GT864_FR0_ASM_H

#include <stdint.h>

#define GT864_FR0_INPUT_COEFFICIENTS 896
#define GT864_FR0_OUTPUT_COEFFICIENTS 864

/* Full 12-transform wrapper around the no-stack one-block assembly kernel. */
void gt864_boundary_fr0_asm(
    int16_t out[GT864_FR0_OUTPUT_COEFFICIENTS],
    const int16_t in[GT864_FR0_INPUT_COEFFICIENTS]);

/*
 * One (top,component,column-block) transform.
 *
 * out:   component vector for physical row 0; following rows are +96 bytes
 * main:  eight contiguous q registers R_c=[U_0(c),...,U_7(c)]
 * tail:  scalar s=8 for the first column; following columns are +16 bytes
 * twist: [9][8] centered Montgomery constants, one q register per s
 */
void gt864_fr0_block_asm(int16_t *out, const int16_t *main,
                         const int16_t *tail, const int16_t *twist);

#endif
