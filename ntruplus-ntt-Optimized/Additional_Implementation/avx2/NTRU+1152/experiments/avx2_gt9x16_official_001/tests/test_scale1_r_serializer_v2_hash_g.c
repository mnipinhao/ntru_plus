#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "poly.h"
#include "scale1-r-serializer-v2-asm.h"
#include "scale1_r_serializer_v2_hash_g.h"
#include "symmetric.h"

#define N 1152
#define BYTES 1728
#define HASH 288
void ntruplus1152_exp001_top_split_small(int16_t *, const int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t *);
static uint64_t rng_state = UINT64_C(0x5354414745504153);
static uint32_t rnd(void) { rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17; return (uint32_t)(rng_state >> 16); }

int main(void) {
  _Alignas(32) int16_t coeff[N], state[N], copy[N];
  uint8_t bytes[BYTES], control[HASH], candidate[HASH];
  int trial, i;
  for (trial = 0; trial < 1000; ++trial) {
    for (i = 0; i < N; ++i) coeff[i] = (int16_t)((int)(rnd() % 3) - 1);
    ntruplus1152_exp001_top_split_small(state, coeff);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(state);
    memcpy(copy, state, sizeof copy);
    ntruplus1152_exp001_scale1_r_serializer_v2(bytes, state);
    hash_g(control, bytes);
    ntruplus1152_exp001_scale1_r_serializer_v2_hash_g(candidate, state);
    if (memcmp(control, candidate, HASH) || memcmp(state, copy, sizeof copy)) {
      fprintf(stderr, "Serializer V2 hash_g mismatch trial=%d\n", trial);
      return 1;
    }
  }
  puts("scale-1 Serializer V2 direct hash stage: ok");
  return 0;
}
