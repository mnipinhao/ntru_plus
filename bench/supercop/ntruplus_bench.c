#include "ntruplus_bench.h"
#include "symmetric.h"

void ntruplus_bench_forward(poly *r, const poly *a) {
  *r = *a;
  poly_ntt(r);
}

void ntruplus_bench_forward_inplace(poly *a) { poly_ntt(a); }

void ntruplus_bench_basemul_unscaled(poly *r, const poly *a, const poly *b) {
  poly_basemul(r, a, b);
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

int ntruplus_bench_frombytes(poly *r, const uint8_t *a) {
  return poly_frombytes(r, a);
}

void ntruplus_bench_tobytes(uint8_t *r, const poly *a) {
  poly_tobytes(r, a);
}

void ntruplus_bench_cbd1(poly *r, const uint8_t *a) {
  poly_cbd1(r, a);
}

void ntruplus_bench_crepmod3(poly *r, const poly *a) {
  *r = *a;
  poly_crepmod3(r);
}

void ntruplus_bench_add(poly *r, const poly *a, const poly *b) {
  poly_add(r, a, b);
}

void ntruplus_bench_sub(poly *r, const poly *a, const poly *b) {
  poly_sub(r, a, b);
}

void ntruplus_bench_sotp_encode(poly *r, const uint8_t *msg,
                               const uint8_t *mask) {
  poly_sotp_encode(r, msg, mask);
}

int ntruplus_bench_sotp_decode(uint8_t *msg, const poly *a,
                              const uint8_t *mask) {
  return poly_sotp_decode(msg, a, mask);
}

void ntruplus_bench_hash_f(uint8_t *r, const uint8_t *a) { hash_f(r, a); }
void ntruplus_bench_hash_g(uint8_t *r, const uint8_t *a) { hash_g(r, a); }
void ntruplus_bench_hash_h(uint8_t *r, const uint8_t *a) { hash_h(r, a); }
