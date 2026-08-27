#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "encap-h-decode-natural-q-asm.h"
#include "gt9x16-prod3-cumulative-ma2.h"
#include "gt9x16-prod3-ma2-qorder-natural-asm.h"
#include "poly.h"

#define N 1152
#define BYTES 1728
#define Q 3457

typedef struct {
  _Alignas(32) uint8_t pre[32];
  _Alignas(32) int16_t value[N];
  uint8_t post[32];
} guarded_poly;

static uint64_t rng_state = UINT64_C(0x48315f4445434f44);
static uint32_t rnd(void) {
  uint64_t x = rng_state;
  x ^= x << 13; x ^= x >> 7; x ^= x << 17; rng_state = x;
  return (uint32_t)(x >> 16);
}

static void fail(const char *what, int trial, int index) {
  fprintf(stderr, "H1 decoder %s trial=%d index=%d\n", what, trial, index);
  exit(1);
}

static void encode12(uint8_t out[BYTES], const uint16_t in[N]) {
  int i;
  memset(out, 0, BYTES);
  for (i = 0; i < N; ++i) {
    unsigned bit = 12U * (unsigned)i;
    unsigned byte = bit >> 3;
    unsigned shift = bit & 7U;
    uint32_t word = (uint32_t)in[i] << shift;
    out[byte] |= (uint8_t)word;
    if (byte + 1U < BYTES) out[byte + 1U] |= (uint8_t)(word >> 8);
    if (byte + 2U < BYTES) out[byte + 2U] |= (uint8_t)(word >> 16);
  }
}

static void check_canary(const guarded_poly *g, int trial) {
  int i;
  for (i = 0; i < 32; ++i) {
    if (g->pre[i] != 0xa5) fail("pre-canary", trial, i);
    if (g->post[i] != 0x5a) fail("post-canary", trial, i);
  }
}

static void run_decode(const uint8_t input[BYTES], int trial) {
  poly official;
  guarded_poly expected, actual;
  uint8_t copy[BYTES];
  int ro, rn, i;
  memset(&expected, 0, sizeof expected);
  memset(&actual, 0, sizeof actual);
  memset(expected.pre, 0xa5, 32); memset(expected.post, 0x5a, 32);
  memset(actual.pre, 0xa5, 32); memset(actual.post, 0x5a, 32);
  memcpy(copy, input, BYTES);
  ro = poly_frombytes(&official, input);
  ntruplus1152_exp001_project_h_natural_q(expected.value, official.coeffs);
  rn = ntruplus1152_exp001_poly_frombytes_h_natural_q(actual.value, input);
  if (ro != rn) fail("accepted-set", trial, -1);
  for (i = 0; i < N; ++i)
    if (expected.value[i] != actual.value[i]) fail("raw-natural-output", trial, i);
  if (memcmp(copy, input, BYTES) != 0) fail("input-mutation", trial, -1);
  check_canary(&expected, trial); check_canary(&actual, trial);
}

static void run_ma2(int trial) {
  _Alignas(32) int16_t r[N], m[N], h_official[N], h_natural[N];
  guarded_poly control, candidate;
  int i;
  memset(&control, 0, sizeof control); memset(&candidate, 0, sizeof candidate);
  memset(control.pre, 0xa5, 32); memset(control.post, 0x5a, 32);
  memset(candidate.pre, 0xa5, 32); memset(candidate.post, 0x5a, 32);
  for (i = 0; i < N; ++i) {
    r[i] = (int16_t)((int)(rnd() % 41505U) - 20751);
    m[i] = (int16_t)((int)(rnd() % 41505U) - 20751);
    h_official[i] = (int16_t)(rnd() % Q);
  }
  ntruplus1152_exp001_project_h_natural_q(h_natural, h_official);
  ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4(
      control.value, r, m, h_official);
  ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h(
      candidate.value, r, m, h_natural);
  for (i = 0; i < N; ++i)
    if (control.value[i] != candidate.value[i]) fail("MA2-raw", trial, i);
  check_canary(&control, trial); check_canary(&candidate, trial);
}

int main(void) {
  uint16_t values[N];
  uint8_t input[BYTES];
  int i, position, trial = 0;
  memset(values, 0, sizeof values);
  for (i = 0; i < 4096; ++i) {
    values[0] = (uint16_t)i; encode12(input, values); run_decode(input, trial++);
  }
  values[0] = 0;
  for (position = 0; position < N; ++position) {
    static const uint16_t edge[] = {3456, 3457, 3458, 4095};
    for (i = 0; i < 4; ++i) {
      values[position] = edge[i]; encode12(input, values); run_decode(input, trial++);
    }
    values[position] = 0;
  }
  for (i = 0; i < 1003; ++i) {
    int j;
    for (j = 0; j < BYTES; ++j) input[j] = (uint8_t)rnd();
    run_decode(input, trial++);
  }
  for (i = 0; i < 65; ++i) run_ma2(i);
  puts("H1 direct Natural-Q decoder: acceptance/raw output/MA2/canary gates passed");
  return 0;
}
