#ifndef GT864_POLY_API_H
#define GT864_POLY_API_H

#include "poly.h"

void gt_old_poly_ntt(poly *r, const poly *a);
void gt_old_poly_invntt(poly *r, const poly *a);
int gt_old_poly_baseinv(poly *r, const poly *a);
void gt_old_poly_basemul(poly *r, const poly *a, const poly *b);
void gt_old_poly_basemul_add(poly *r, const poly *a, const poly *b,
                            const poly *c);
void gt_old_poly_tobytes(uint8_t *r, const poly *a);
void gt_old_poly_frombytes(poly *r, const uint8_t *a);

void gt_d1_poly_ntt(poly *r, const poly *a);
void gt_d1_poly_invntt(poly *r, const poly *a);
int gt_d1_poly_baseinv(poly *r, const poly *a);
void gt_d1_poly_basemul(poly *r, const poly *a, const poly *b);
void gt_d1_poly_basemul_add(poly *r, const poly *a, const poly *b,
                           const poly *c);
void gt_d1_poly_tobytes(uint8_t *r, const poly *a);
void gt_d1_poly_frombytes(poly *r, const uint8_t *a);

#endif
