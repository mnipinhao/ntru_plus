#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "scale1-r-serializer-v2-asm.h"
#include "poly.h"

#define N 1152
#define BYTES 1728
void ntruplus1152_exp001_direct_serializer_wire(uint8_t out[BYTES], const int16_t state[N]);
void ntruplus1152_exp001_top_split_small(int16_t out[N], const int16_t in[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t state[N]);

static uint64_t rng_state = UINT64_C(0x56325041434b4554);
static uint32_t rnd(void) {
  rng_state ^= rng_state << 13;
  rng_state ^= rng_state >> 7;
  rng_state ^= rng_state << 17;
  return (uint32_t)(rng_state >> 16);
}

static int one(const int16_t coeff[N], int trial) {
  struct { uint8_t pre[32], out[BYTES], post[32]; } a, b;
  _Alignas(32) int16_t state[N], copy[N];
  poly official_poly;
  uint8_t official[BYTES];
  memset(&a, 0xa5, sizeof a); memset(&b, 0xa5, sizeof b);
  ntruplus1152_exp001_top_split_small(state, coeff);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(state);
  memcpy(copy, state, sizeof copy);
  memcpy(official_poly.coeffs, coeff, sizeof official_poly.coeffs);
  poly_ntt(&official_poly); poly_tobytes(official, &official_poly);
  ntruplus1152_exp001_direct_serializer_wire(a.out, state);
  ntruplus1152_exp001_scale1_r_serializer_v2(b.out, state);
  if (memcmp(a.out, b.out, BYTES) || memcmp(b.out, official, BYTES) ||
      memcmp(state, copy, sizeof copy) ||
      memcmp(a.pre, b.pre, 32) || memcmp(a.post, b.post, 32)) {
    int byte;
    for (byte = 0; byte < BYTES && a.out[byte] == b.out[byte]; ++byte) {}
    if (byte < BYTES)
      fprintf(stderr, "first byte difference=%d control=%u candidate=%u\n",
              byte, (unsigned)a.out[byte], (unsigned)b.out[byte]);
    fprintf(stderr, "serializer V2 mismatch/corruption trial=%d\n", trial);
    return 1;
  }
  return 0;
}

int main(void) {
  _Alignas(32) int16_t input[N];
  int trial, i;
  for (i = 0; i < N; ++i) input[i] = 0;
  if (one(input, 0)) return 1;
  for (trial = 0; trial < 6; ++trial) {
    for (i = 0; i < N; ++i)
      input[i] = (int16_t)(trial == 0 ? 1 : trial == 1 ? -1 :
                           trial == 2 ? (i & 1 ? 1 : -1) :
                           trial == 3 ? (i == 0 ? 1 : 0) :
                           trial == 4 ? (i == N - 1 ? -1 : 0) : 0);
    if (one(input, trial + 1)) return 1;
  }
  for (trial = 0; trial < 1000; ++trial) {
    for (i = 0; i < N; ++i) input[i] = (int16_t)((int)(rnd() % 3) - 1);
    if (one(input, trial + 100)) return 1;
  }
  puts("scale-1 serializer V2 ASM: ok");
  return 0;
}
