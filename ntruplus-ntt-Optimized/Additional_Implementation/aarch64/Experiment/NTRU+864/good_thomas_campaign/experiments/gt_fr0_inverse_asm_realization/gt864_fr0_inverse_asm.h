#ifndef GT864_FR0_INVERSE_ASM_H
#define GT864_FR0_INVERSE_ASM_H

#include <stdint.h>

void gt864_fr0_inverse_ntt9_asm(int16_t out[896], const int16_t in[864]);
void gt864_fr0_inverse_finish_asm(int16_t out[864], const int16_t in[896]);

void gt864_fr0_inverse9_block_asm(int16_t *main_out, int16_t *tail_out,
                                  const int16_t *rows,
                                  const int16_t inverse_twist[9][8]);
void gt864_inverse16_main_block_asm(int16_t *out_base,
                                    const int16_t *alpha,
                                    const int16_t *beta,
                                    const int16_t stage[4][8],
                                    const int16_t scale[16][8]);
void gt864_inverse16_tail_block_asm(int16_t *out_s8,
                                    const int16_t *tail,
                                    const int16_t *unused,
                                    const int16_t stage[4][8],
                                    const int16_t scale[16][8]);

#endif
