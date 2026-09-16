#ifndef GT864_D1_P2_COMPONENTS_H
#define GT864_D1_P2_COMPONENTS_H

#include "poly.h"

void gt_p2_official_to_fr0(poly *r, const poly *a);
void gt_p2_fr0_to_official_raw(poly *r, const poly *a);
void gt_p2_fr0_to_official_nonnegative(poly *r, const poly *a);
void gt_p2_fr0_to_official_centered(poly *r, const poly *a);
void gt_p2_normalize_nonnegative(poly *r, const poly *a);
void gt_p2_normalize_centered(poly *r, const poly *a);
void gt_p2_inverse_raw(poly *r, const poly *a);

#endif
