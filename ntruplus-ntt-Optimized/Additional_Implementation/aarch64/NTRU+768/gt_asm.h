#ifndef GT_ASM_H
#define GT_ASM_H

#include <stdint.h>
#include "poly.h"

void poly_ntt_gt_ref(poly *r, const poly *a);
void poly_ntt_gt_asm(poly *r, const poly *a);
void ntt32_radix2_asm(int16_t out[32], const int16_t in[32]);

#endif
