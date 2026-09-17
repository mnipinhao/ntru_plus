#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "poly.h"

#define N 1152
#define BYTES 1728
void ntruplus1152_exp001_top_split_small(int16_t out[N], const int16_t in[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(int16_t state[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t state[N]);
void ntruplus1152_exp001_direct_serializer_natural(uint8_t out[BYTES], const int16_t state[N]);
void ntruplus1152_exp001_direct_serializer_wire(uint8_t out[BYTES], const int16_t state[N]);
static uint64_t state = UINT64_C(0x5345525749524531);
static uint32_t rnd(void) { state ^= state << 13; state ^= state >> 7; state ^= state << 17; return (uint32_t)(state >> 16); }
int main(void) {
  _Alignas(32) int16_t coeff[N], natural[N], wire[N];
  _Alignas(32) uint8_t a[BYTES], b[BYTES], official[BYTES];
  poly p;
  int trial, i;
  for (trial = 0; trial < 240; ++trial) {
    for (i = 0; i < N; ++i) coeff[i] = (int16_t)((int)(rnd() % 3) - 1);
    ntruplus1152_exp001_top_split_small(natural, coeff); memcpy(wire, natural, sizeof natural);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(natural);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(wire);
    ntruplus1152_exp001_direct_serializer_natural(a, natural);
    ntruplus1152_exp001_direct_serializer_wire(b, wire);
    memcpy(p.coeffs, coeff, sizeof coeff); poly_ntt(&p); poly_tobytes(official, &p);
    if (memcmp(a, b, BYTES) || memcmp(a, official, BYTES)) {
      fprintf(stderr, "wire serializer mismatch trial=%d\n", trial); return 1;
    }
  }
  puts("wire-monotone serializer: ok");
  return 0;
}
