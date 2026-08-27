#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16-prod3-ma2-hash-h1.h"
#include "gt9x16-prod3-ma2-qorder-natural-asm.h"
#include "gt9x16_prod3_aos_full.h"
#include "gt9x16_forward.h"

#define N 1152
#define BYTES 1728
#define TRIALS 257

static uint64_t state = UINT64_C(0x514e41545f41534d);
static uint32_t rnd(void) {
  uint64_t x = state;
  x ^= x << 13; x ^= x >> 7; x ^= x << 17; state = x;
  return (uint32_t)(x >> 16);
}

static void die(const char *layer, int trial, int index, int expected, int actual) {
  fprintf(stderr, "natural-Q %s trial=%d index=%d expected=%d actual=%d\n",
          layer, trial, index, expected, actual);
  exit(1);
}

static void permute_q(int16_t out[N], const int16_t in[N]) {
  int vector, lane;
  for (vector = 0; vector < 72; ++vector)
    for (lane = 0; lane < 16; ++lane)
      out[16 * vector + lane] =
          in[16 * vector + ntruplus1152_exp001_qnat_lane_from_current[lane]];
}

static void compare_i16(const char *layer, int trial,
                        const int16_t expected[N], const int16_t actual[N]) {
  int i;
  for (i = 0; i < N; ++i)
    if (expected[i] != actual[i]) die(layer, trial, i, expected[i], actual[i]);
}

static void run(int trial, const int16_t source[N]) {
  _Alignas(32) int16_t current[N], natural[N], expected[N];
  _Alignas(32) int16_t h[N], hcurrent[N], hnat[N], hexpected[N];
  _Alignas(32) int16_t mcurrent[N], mnatural[N];
  _Alignas(32) int16_t macurrent[N], manatural[N], maexpected[N];
  uint8_t bytes_current[BYTES], bytes_natural[BYTES];
  int i;

  memcpy(current, source, sizeof current);
  memcpy(natural, source, sizeof natural);
  ntruplus1152_exp001_gt9x16_prod3_aos_full(current);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q(natural);
  permute_q(expected, current);
  compare_i16("producer-raw-permutation", trial, expected, natural);

  for (i = 0; i < N; ++i) h[i] = (int16_t)(rnd() % 3457U);
  ntruplus1152_exp001_project_h_natural_q(hnat, h);
  for (i = 0; i < N; ++i) {
    int vector = i / 16, natural_lane = i % 16;
    int current_lane = ntruplus1152_exp001_qnat_lane_from_current[natural_lane];
    hcurrent[16 * vector + current_lane] =
        h[ntruplus1152_exp001_qnat_h_source[i]];
  }
  permute_q(hexpected, hcurrent);
  compare_i16("resident-h-raw-permutation", trial, hexpected, hnat);

  for (i = 0; i < N; ++i) mcurrent[i] = (int16_t)((int)(rnd() % 41505U) - 20751);
  permute_q(mnatural, mcurrent);
  ntruplus1152_exp001_f0_ma2_planes_current_q(macurrent, current, mcurrent, h);
  ntruplus1152_exp001_f0_ma2_planes_natural_q(manatural, natural, mnatural, h);
  permute_q(maexpected, macurrent);
  compare_i16("ma2-lane-equivariance", trial, maexpected, manatural);

  ntruplus1152_exp001_prod3_ma2_hash_h1(bytes_current, current);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(bytes_natural, natural);
  for (i = 0; i < BYTES; ++i)
    if (bytes_current[i] != bytes_natural[i])
      die("H1-byte-exact", trial, i, bytes_current[i], bytes_natural[i]);
}

int main(void) {
  _Alignas(32) int16_t input[N];
  int i, trial;
  memset(input, 0, sizeof input); run(0, input);
  for (i = 0; i < N; ++i) input[i] = (int16_t)((i & 1) ? -1 : 1);
  run(1, input);
  for (trial = 2; trial < TRIALS; ++trial) {
    for (i = 0; i < N; ++i) input[i] = (int16_t)((int)(rnd() % 3U) - 1);
    run(trial, input);
  }
  puts("natural-Q ASM0: producer/h/MA2/H1 exact permutation gates passed");
  return 0;
}
