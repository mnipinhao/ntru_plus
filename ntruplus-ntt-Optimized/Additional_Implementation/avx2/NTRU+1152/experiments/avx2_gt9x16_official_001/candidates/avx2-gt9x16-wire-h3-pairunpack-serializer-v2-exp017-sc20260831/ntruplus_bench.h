#ifndef NTRUPLUS_BENCH_H
#define NTRUPLUS_BENCH_H

#include "poly.h"

void ntruplus_bench_forward(poly *r, const poly *a);
void ntruplus_bench_basemul(poly *r, const poly *a, const poly *b);
void ntruplus_bench_inverse(poly *r, const poly *a);
int ntruplus_bench_baseinv(poly *r, const poly *a);
void ntruplus_bench_mul(poly *r, const poly *a, const poly *b);

#endif
