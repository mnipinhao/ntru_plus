#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "encap-h-decode-natural-q-asm.h"
#include "encap-h-ingress-ma2-h3.h"
#include "poly.h"

#define N 1152
#define PK_BYTES 1728
#define Q 3457

typedef struct {
  _Alignas(32) uint8_t pre[32];
  _Alignas(32) int16_t value[N];
  uint8_t post[32];
} guarded_poly;

static uint64_t rng_state = UINT64_C(0x48335f41534d5f30);
static uint32_t rnd(void) {
  uint64_t x = rng_state;
  x ^= x << 13;
  x ^= x >> 7;
  x ^= x << 17;
  rng_state = x;
  return (uint32_t)(x >> 16);
}

static void fail(const char *what, int trial, int index) {
  fprintf(stderr, "H3 %s trial=%d index=%d\n", what, trial, index);
  exit(1);
}

static void encode12(uint8_t out[PK_BYTES], const uint16_t in[N]) {
  int i;
  memset(out, 0, PK_BYTES);
  for (i = 0; i < N; ++i) {
    unsigned bit = 12U * (unsigned)i;
    unsigned byte = bit >> 3;
    unsigned shift = bit & 7U;
    uint32_t word = (uint32_t)in[i] << shift;
    out[byte] |= (uint8_t)word;
    if (byte + 1U < PK_BYTES) out[byte + 1U] |= (uint8_t)(word >> 8);
    if (byte + 2U < PK_BYTES) out[byte + 2U] |= (uint8_t)(word >> 16);
  }
}

static void guard_init(guarded_poly *value) {
  memset(value, 0, sizeof(*value));
  memset(value->pre, 0xa5, sizeof(value->pre));
  memset(value->post, 0x5a, sizeof(value->post));
}

static void guard_check(const guarded_poly *value, int trial, const char *name) {
  int i;
  for (i = 0; i < 32; ++i) {
    if (value->pre[i] != 0xa5) fail(name, trial, -32 + i);
    if (value->post[i] != 0x5a) fail(name, trial, N + i);
  }
}

static void fill_operands(int16_t r[N], int16_t m[N]) {
  int i;
  for (i = 0; i < N; ++i) {
    r[i] = (int16_t)((int)(rnd() % 41505U) - 20751);
    m[i] = (int16_t)((int)(rnd() % 41505U) - 20751);
  }
}

static void run_case(const uint8_t pk[PK_BYTES], int trial, int test_alias) {
  _Alignas(32) int16_t r[N], m[N], h[N];
  _Alignas(32) int16_t r_copy[N], m_copy[N];
  uint8_t pk_copy[PK_BYTES];
  guarded_poly control, candidate, alias_r, alias_m;
  poly official;
  int official_reject, h1_reject, h3_reject, i;

  fill_operands(r, m);
  memcpy(r_copy, r, sizeof(r));
  memcpy(m_copy, m, sizeof(m));
  memcpy(pk_copy, pk, PK_BYTES);
  guard_init(&control);
  guard_init(&candidate);
  official_reject = poly_frombytes(&official, pk);
  h1_reject = ntruplus1152_exp001_poly_frombytes_h_natural_q(h, pk);
  h3_reject = ntruplus1152_exp001_encap_h_ingress_ma2_h3(
      candidate.value, pk, r, m);
  if (official_reject != h1_reject || official_reject != h3_reject)
    fail("acceptance", trial, -1);
  if (memcmp(pk, pk_copy, PK_BYTES) != 0) fail("pk-mutation", trial, -1);
  if (memcmp(r, r_copy, sizeof(r)) != 0) fail("r-mutation", trial, -1);
  if (memcmp(m, m_copy, sizeof(m)) != 0) fail("m-mutation", trial, -1);
  guard_check(&candidate, trial, "candidate-canary");

  if (official_reject != 0) return;
  ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h(
      control.value, r, m, h);
  for (i = 0; i < N; ++i) {
    if (control.value[i] != candidate.value[i]) {
      fprintf(stderr, "raw values control=%d candidate=%d r=%d m=%d\n",
              control.value[i], candidate.value[i], r[i], m[i]);
      fail("raw-MA2", trial, i);
    }
  }
  guard_check(&control, trial, "control-canary");

  if (!test_alias) return;
  guard_init(&alias_r);
  guard_init(&alias_m);
  memcpy(alias_r.value, r, sizeof(r));
  memcpy(alias_m.value, m, sizeof(m));
  if (ntruplus1152_exp001_encap_h_ingress_ma2_h3(
          alias_r.value, pk, alias_r.value, m) != 0)
    fail("r-alias-return", trial, -1);
  if (ntruplus1152_exp001_encap_h_ingress_ma2_h3(
          alias_m.value, pk, r, alias_m.value) != 0)
    fail("m-alias-return", trial, -1);
  for (i = 0; i < N; ++i) {
    if (alias_r.value[i] != control.value[i]) fail("r-alias", trial, i);
    if (alias_m.value[i] != control.value[i]) fail("m-alias", trial, i);
  }
  guard_check(&alias_r, trial, "r-alias-canary");
  guard_check(&alias_m, trial, "m-alias-canary");
}

int main(void) {
  uint16_t values[N];
  uint8_t pk[PK_BYTES];
  int trial = 0, value, position, i;

  memset(values, 0, sizeof(values));
  for (value = 0; value < 4096; ++value) {
    values[0] = (uint16_t)value;
    encode12(pk, values);
    run_case(pk, trial++, value < Q && (value % 257) == 0);
  }
  values[0] = 0;
  for (position = 0; position < N; ++position) {
    static const uint16_t edge[] = {3456, 3457, 3458, 4095};
    for (i = 0; i < 4; ++i) {
      values[position] = edge[i];
      encode12(pk, values);
      run_case(pk, trial++, i == 0 && (position % 127) == 0);
    }
    values[position] = 0;
  }
  for (i = 0; i < 1003; ++i) {
    int j;
    for (j = 0; j < N; ++j) values[j] = (uint16_t)(rnd() % Q);
    encode12(pk, values);
    run_case(pk, trial++, (i % 113) == 0);
  }
  for (i = 0; i < 1003; ++i) {
    int j;
    for (j = 0; j < PK_BYTES; ++j) pk[j] = (uint8_t)rnd();
    run_case(pk, trial++, 0);
  }
  puts("H3 full ASM: Official acceptance, raw H1 MA2, alias, immutability, and canary gates passed");
  return 0;
}
