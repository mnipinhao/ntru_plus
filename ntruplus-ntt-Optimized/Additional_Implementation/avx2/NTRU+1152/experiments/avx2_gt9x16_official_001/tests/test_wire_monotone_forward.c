#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 1152
#define Q 3457

void ntruplus1152_exp001_top_split_small(int16_t out[N], const int16_t in[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(int16_t state[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t state[N]);

static const uint16_t source_to_wire[N] = {
#include "wire-monotone-source-to-wire.inc"
};

static uint64_t rng_state = UINT64_C(0x574952454d413231);
static uint32_t rnd(void) {
  uint64_t x = rng_state;
  x ^= x << 13; x ^= x >> 7; x ^= x << 17;
  rng_state = x;
  return (uint32_t)(x >> 16);
}
int main(void) {
  _Alignas(32) int16_t coefficient[N], split[N], natural[N], wire[N];
  int trial, i;
  for (trial = 0; trial < 400; ++trial) {
    for (i = 0; i < N; ++i) {
      if (trial == 0) coefficient[i] = 0;
      else if (trial == 1) coefficient[i] = (i & 1) ? 1 : -1;
      else coefficient[i] = (int16_t)((int)(rnd() % 3) - 1);
    }
    ntruplus1152_exp001_top_split_small(split, coefficient);
    memcpy(natural, split, sizeof split);
    memcpy(wire, split, sizeof split);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(natural);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(wire);
    for (i = 0; i < N; ++i) {
      int target_index = source_to_wire[i];
      if (natural[i] != wire[target_index]) {
        fprintf(stderr, "wire forward mismatch trial=%d source=%d target-index=%d\n",
                trial, i, target_index);
        return 1;
      }
    }
  }
  puts("wire-monotone forward: ok");
  return 0;
}
