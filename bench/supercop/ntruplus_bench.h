#ifndef NTRUPLUS_BENCH_H
#define NTRUPLUS_BENCH_H

#include "poly.h"

void ntruplus_bench_forward(poly *r, const poly *a);
void ntruplus_bench_forward_inplace(poly *a);
void ntruplus_bench_basemul_unscaled(poly *r, const poly *a, const poly *b);
void ntruplus_bench_basemul(poly *r, const poly *a, const poly *b);
void ntruplus_bench_inverse(poly *r, const poly *a);
int ntruplus_bench_baseinv(poly *r, const poly *a);
void ntruplus_bench_mul(poly *r, const poly *a, const poly *b);
int ntruplus_bench_frombytes(poly *r, const uint8_t *a);
void ntruplus_bench_tobytes(uint8_t *r, const poly *a);
void ntruplus_bench_cbd1(poly *r, const uint8_t *a);
void ntruplus_bench_crepmod3(poly *r, const poly *a);
void ntruplus_bench_add(poly *r, const poly *a, const poly *b);
void ntruplus_bench_sub(poly *r, const poly *a, const poly *b);
void ntruplus_bench_sotp_encode(poly *r, const uint8_t *msg,
                               const uint8_t *mask);
int ntruplus_bench_sotp_decode(uint8_t *msg, const poly *a,
                              const uint8_t *mask);
void ntruplus_bench_hash_f(uint8_t *r, const uint8_t *a);
void ntruplus_bench_hash_g(uint8_t *r, const uint8_t *a);
void ntruplus_bench_hash_h(uint8_t *r, const uint8_t *a);

#endif
