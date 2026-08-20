#include "ntruplus_bench.h"

void ntruplus_bench_forward(poly *r, const poly *a) {
  *r = *a;
  poly_ntt(r);
}

void ntruplus_bench_basemul(poly *r, const poly *a, const poly *b) {
  poly_basemul_scale(r, a, b);
}

void ntruplus_bench_inverse(poly *r, const poly *a) {
  *r = *a;
  poly_invntt_scale(r);
}

int ntruplus_bench_baseinv(poly *r, const poly *a) {
  return poly_baseinv(r, a);
}

void ntruplus_bench_mul(poly *r, const poly *a, const poly *b) {
  poly left = *a;
  poly right = *b;
  poly_ntt(&left);
  poly_ntt(&right);
  poly_basemul_scale(r, &left, &right);
  poly_invntt_scale(r);
}
