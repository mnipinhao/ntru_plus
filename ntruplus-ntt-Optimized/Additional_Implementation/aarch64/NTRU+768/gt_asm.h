#ifndef GT_ASM_H
#define GT_ASM_H

#include "poly.h"

void poly_ntt_gt_ref(poly *r, const poly *a);
void poly_ntt_gt_asm(poly *r, const poly *a);

#endif
