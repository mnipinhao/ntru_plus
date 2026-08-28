#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef TEST_H4_M3B
#include "encap-h4-m3b-exact-egress.h"
#define H4_FUNCTION ntruplus1152_exp001_encap_h4_m3b_exact_egress
typedef int16_t scratch_element;
#define SCRATCH_ELEMENTS N
#else
#include "encap-h4-m3.h"
#define H4_FUNCTION ntruplus1152_exp001_encap_h4_m3
typedef int16_t scratch_element;
#define SCRATCH_ELEMENTS N
#endif
#include "encap-h-ingress-ma2-h3.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full.h"
#include "poly.h"

#define N 1152
#define BYTES 1728
#define Q 3457

void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(
    int16_t state[N]);
#ifdef TEST_H4_M3B
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(
    int16_t state[N]);
#endif

typedef struct {
  _Alignas(32) uint8_t pre[32];
  _Alignas(32) scratch_element value[SCRATCH_ELEMENTS];
  uint8_t post[32];
} guarded_scratch;

typedef struct {
  _Alignas(32) uint8_t pre[32];
  uint8_t value[BYTES];
  uint8_t post[32];
} guarded_bytes;

static uint64_t rng_state = UINT64_C(0x48345f4d335f4153);

static uint32_t rnd(void) {
  uint64_t x = rng_state;
  x ^= x << 13;
  x ^= x >> 7;
  x ^= x << 17;
  rng_state = x;
  return (uint32_t)(x >> 16);
}

static int canonical(int value) {
  value %= Q;
  return value < 0 ? value + Q : value;
}

static void fail(const char *what, int trial, int index) {
  fprintf(stderr, "H4-M3 %s trial=%d index=%d\n", what, trial, index);
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

static void guarded_scratch_init(guarded_scratch *value) {
  memset(value, 0, sizeof(*value));
  memset(value->pre, 0xa5, sizeof(value->pre));
  memset(value->post, 0x5a, sizeof(value->post));
}

static void guarded_bytes_init(guarded_bytes *value) {
  memset(value, 0, sizeof(*value));
  memset(value->pre, 0x3c, sizeof(value->pre));
  memset(value->post, 0xc3, sizeof(value->post));
}

static void check_guards(const guarded_scratch *scratch,
                         const guarded_bytes *ct, int trial) {
  int i;
  for (i = 0; i < 32; ++i) {
    if (scratch->pre[i] != 0xa5 || scratch->post[i] != 0x5a)
      fail("scratch-canary", trial, i);
    if (ct->pre[i] != 0x3c || ct->post[i] != 0xc3)
      fail("ct-canary", trial, i);
  }
}

static void make_scale_states(int16_t scale4[N], int16_t scale1[N],
                              const int16_t coefficient[N], int trial) {
  _Alignas(32) int16_t split[N];
  int i;
  ntruplus1152_exp001_top_split_small(split, coefficient);
  memcpy(scale4, split, sizeof(split));
  memcpy(scale1, split, sizeof(split));
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(scale4);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1(scale1);
  for (i = 0; i < N; ++i)
    if (canonical(scale4[i]) != canonical(4 * (int)scale1[i]))
      fail("producer-scale1-semantic", trial, i);
}

static void test_overlaps(const uint8_t pk[BYTES], const int16_t r[N],
                          const int16_t m[N], const uint8_t expected[BYTES],
                          int trial) {
  _Alignas(32) uint8_t arena[2 * BYTES + 64];
  _Alignas(32) scratch_element scratch[SCRATCH_ELEMENTS];
  static const int delta[] = {0, 16, -16};
  int which;
  for (which = 0; which < 3; ++which) {
    uint8_t *pk_alias = arena + 32 + (delta[which] < 0 ? 16 : 0);
    uint8_t *ct_alias = pk_alias + delta[which];
    memset(arena, 0x6d, sizeof(arena));
    memcpy(pk_alias, pk, BYTES);
    if (H4_FUNCTION(
            ct_alias, pk_alias, r, m, scratch) != 0)
      fail("overlap-return", trial, which);
    if (memcmp(ct_alias, expected, BYTES) != 0)
      fail("overlap-bytes", trial, which);
  }
}

static void run_valid(const uint16_t h_values[N], const int16_t r_coeff[N],
                      const int16_t m_coeff[N], int trial, int overlap) {
  _Alignas(32) uint8_t pk[BYTES], pk_before[BYTES], expected_ct[BYTES];
  _Alignas(32) int16_t r4[N], r1[N], m4[N], m1[N], raw[N];
#ifdef TEST_H4_M3B
  _Alignas(32) int16_t r1_lazy[N], m1_lazy[N];
#endif
  _Alignas(32) int16_t r_before[N], m_before[N];
  poly h_official, r_official, m_official, c_official;
  guarded_scratch scratch;
  guarded_bytes ct;
  int i, result;

  encode12(pk, h_values);
  memcpy(pk_before, pk, BYTES);
  make_scale_states(r4, r1, r_coeff, trial);
  make_scale_states(m4, m1, m_coeff, trial);
#ifdef TEST_H4_M3B
  ntruplus1152_exp001_top_split_small(r1_lazy, r_coeff);
  ntruplus1152_exp001_top_split_small(m1_lazy, m_coeff);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(
      r1_lazy);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(
      m1_lazy);
  for (i = 0; i < N; ++i) {
    if (canonical(r1[i]) != canonical(r1_lazy[i]))
      fail("scale1-lazy-r-semantic", trial, i);
    if (canonical(m1[i]) != canonical(m1_lazy[i]))
      fail("scale1-lazy-m-semantic", trial, i);
  }
#endif
  memcpy(r_before, r1, sizeof(r1));
  memcpy(m_before, m1, sizeof(m1));

  if (ntruplus1152_exp001_encap_h_ingress_ma2_h3(raw, pk, r1, m1) != 0)
    fail("scale1-reference-return", trial, -1);
  if (poly_frombytes(&h_official, pk) != 0)
    fail("official-pk", trial, -1);
  memcpy(r_official.coeffs, r_coeff, sizeof(r_official.coeffs));
  memcpy(m_official.coeffs, m_coeff, sizeof(m_official.coeffs));
  poly_ntt(&r_official);
  poly_ntt(&m_official);
  poly_basemul(&c_official, &h_official, &r_official);
  poly_add(&c_official, &c_official, &m_official);
  poly_tobytes(expected_ct, &c_official);

  guarded_scratch_init(&scratch);
  guarded_bytes_init(&ct);
  result = H4_FUNCTION(
      ct.value, pk, r1, m1, scratch.value);
  if (result != 0) fail("valid-return", trial, -1);
  if (memcmp(pk, pk_before, BYTES) != 0) fail("pk-immutability", trial, -1);
  if (memcmp(r1, r_before, sizeof(r1)) != 0) fail("r-immutability", trial, -1);
  if (memcmp(m1, m_before, sizeof(m1)) != 0) fail("m-immutability", trial, -1);
  for (i = 0; i < N; ++i)
    if (scratch.value[i] != canonical(raw[i]))
      fail("canonical-scratch", trial, i);
  if (memcmp(ct.value, expected_ct, BYTES) != 0) {
    for (i = 0; i < BYTES; ++i)
      if (ct.value[i] != expected_ct[i]) {
        fprintf(stderr, "ciphertext expected=%u actual=%u\n",
                expected_ct[i], ct.value[i]);
        fail("ciphertext-bytes", trial, i);
      }
  }
  check_guards(&scratch, &ct, trial);
#ifdef TEST_H4_M3B
  guarded_scratch_init(&scratch);
  guarded_bytes_init(&ct);
  result = H4_FUNCTION(
      ct.value, pk, r1_lazy, m1_lazy, scratch.value);
  if (result != 0 || memcmp(ct.value, expected_ct, BYTES) != 0)
    fail("scale1-lazy-ciphertext", trial, -1);
  check_guards(&scratch, &ct, trial);
#endif
  if (overlap) test_overlaps(pk, r1, m1, expected_ct, trial);
}

static void run_invalid(const uint8_t pk[BYTES], const int16_t r[N],
                        const int16_t m[N], int trial) {
  _Alignas(32) uint8_t ct[BYTES];
  _Alignas(32) scratch_element scratch[SCRATCH_ELEMENTS];
  poly official;
  int expected = poly_frombytes(&official, pk);
  int actual = H4_FUNCTION(ct, pk, r, m, scratch);
  if (expected != actual) fail("invalid-decode", trial, -1);
}

int main(void) {
  _Alignas(32) uint16_t h[N];
  _Alignas(32) int16_t r[N], m[N], r1[N], m1[N];
  _Alignas(32) uint8_t pk[BYTES];
  int i, trial;

  memset(h, 0, sizeof(h));
  memset(r, 0, sizeof(r));
  memset(m, 0, sizeof(m));
  run_valid(h, r, m, 0, 1);
  for (i = 0; i < N; ++i) {
    r[i] = (i & 1) ? -1 : 1;
    m[i] = (i & 2) ? -1 : 1;
    h[i] = (uint16_t)((17 * i + 3456) % Q);
  }
  run_valid(h, r, m, 1, 1);
  for (trial = 0; trial < 1003; ++trial) {
    for (i = 0; i < N; ++i) {
      h[i] = (uint16_t)(rnd() % Q);
      r[i] = (int16_t)((int)(rnd() % 3U) - 1);
      m[i] = (int16_t)((int)(rnd() % 3U) - 1);
    }
    run_valid(h, r, m, trial + 2, (trial % 113) == 0);
  }

  /* Invalid-input acceptance remains exactly Official. */
  for (i = 0; i < N; ++i) h[i] = 0;
  encode12(pk, h);
  memset(r, 0, sizeof(r));
  memset(m, 0, sizeof(m));
  make_scale_states(r1, m1, r, 2000);
  for (i = 0; i < N; i += 127) {
    h[i] = (uint16_t)(Q + (i & 7));
    encode12(pk, h);
    run_invalid(pk, r1, m1, 2000 + i);
    h[i] = 0;
  }
  for (trial = 0; trial < 1003; ++trial) {
    for (i = 0; i < BYTES; ++i) pk[i] = (uint8_t)rnd();
    run_invalid(pk, r1, m1, 4000 + trial);
  }
#ifdef TEST_H4_M3B
  puts("H4-M3B ASM: scale1 semantic, canonical scratch, machine-probed exact ciphertext, overlap, and decoder gates passed");
#else
  puts("H4-M3 ASM: scale1 semantic, canonical scratch, exact ciphertext, overlap, and decoder gates passed");
#endif
  return 0;
}
