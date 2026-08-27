#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "encap-h-decode-natural-q-asm.h"
#include "encap-h-ingress-ma2-h3.h"
#include "gt9x16-prod3-cumulative-ma2.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "encap_h_ingress_ma2_h3_price_"

static uint8_t *pk;
static int16_t *r_state, *m_state, *out_current, *out_h1, *out_h3;
static poly *encoded_h;
static long long cycles[TIMINGS + 1];
static volatile unsigned int public_reject_sink;

void preallocate(void) {}

void allocate(void) {
  pk = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  r_state = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *r_state);
  m_state = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *m_state);
  out_current = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *out_current);
  out_h1 = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *out_h1);
  out_h3 = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *out_h3);
  encoded_h = (poly *)alignedcalloc(BANKS * sizeof *encoded_h);
}

#define WORD_SLOT(base, i) ((base) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(base, i) ((base) + (i) * NTRUPLUS_POLYBYTES)

static void reset_inputs(void) {
  int bank, j;
  for (bank = 0; bank < BANKS; ++bank) {
    for (j = 0; j < NTRUPLUS_N; ++j) {
      encoded_h[bank].coeffs[j] =
          (int16_t)(((unsigned int)j * 619U + (unsigned int)bank * 37U + 11U) % 3457U);
      WORD_SLOT(r_state, bank)[j] =
          (int16_t)((int)(((unsigned int)j * 43U + (unsigned int)bank * 19U) % 4001U) - 2000);
      WORD_SLOT(m_state, bank)[j] =
          (int16_t)((int)(((unsigned int)j * 71U + (unsigned int)bank * 23U) % 4001U) - 2000);
    }
    poly_tobytes(BYTE_SLOT(pk, bank), encoded_h + bank);
  }
}

int __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_h3_price_current(
    int16_t out[1152], const uint8_t input[1728],
    const int16_t r[1152], const int16_t m[1152]) {
  poly h;
  int reject = poly_frombytes(&h, input);
  ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4(out, r, m, h.coeffs);
  return reject;
}

int __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_h3_price_h1(
    int16_t out[1152], const uint8_t input[1728],
    const int16_t r[1152], const int16_t m[1152]) {
  poly h;
  int reject = ntruplus1152_exp001_poly_frombytes_h_natural_q(h.coeffs, input);
  ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h(
      out, r, m, h.coeffs);
  return reject;
}

int __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_h3_price_h3(
    int16_t out[1152], const uint8_t input[1728],
    const int16_t r[1152], const int16_t m[1152]) {
  return ntruplus1152_exp001_encap_h_ingress_ma2_h3(out, input, r, m);
}

static void preflight(void) {
  int current_reject, h1_reject, h3_reject;
  reset_inputs();
  current_reject = ntruplus1152_exp001_h3_price_current(
      out_current, pk, r_state, m_state);
  h1_reject = ntruplus1152_exp001_h3_price_h1(
      out_h1, pk, r_state, m_state);
  h3_reject = ntruplus1152_exp001_h3_price_h3(
      out_h3, pk, r_state, m_state);
  if (current_reject || h1_reject || h3_reject ||
      memcmp(out_current, out_h1, NTRUPLUS_N * sizeof *out_current) ||
      memcmp(out_current, out_h3, NTRUPLUS_N * sizeof *out_current)) {
    fprintf(stderr, "H3 price preflight failed\n");
    abort();
  }
}

#define MEASURE_ENTRY(label, statement) do {                            \
  for (i = 0; i <= TIMINGS; ++i) {                                     \
    cycles[i] = cpucycles();                                           \
    statement;                                                         \
  }                                                                    \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, PREFIX label "_cycles", cycles, TIMINGS);             \
} while (0)

#define MEASURE_BALANCED(label, preparation, control_statement, h3_statement) do { \
  preparation;                                                         \
  MEASURE_ENTRY(label "_control_first", control_statement);            \
  preparation;                                                         \
  MEASURE_ENTRY(label "_h3_second", h3_statement);                     \
  preparation;                                                         \
  MEASURE_ENTRY(label "_h3_first", h3_statement);                      \
  preparation;                                                         \
  MEASURE_ENTRY(label "_control_second", control_statement);           \
} while (0)

void measure(void) {
  int i, loop;
  preflight();
  printf("encap_h_ingress_ma2_h3_price_runtime_addresses"
         " %p %p %p %p %p %p\n",
         (void *)ntruplus1152_exp001_h3_price_current,
         (void *)ntruplus1152_exp001_h3_price_h1,
         (void *)ntruplus1152_exp001_h3_price_h3,
         (void *)poly_frombytes,
         (void *)ntruplus1152_exp001_poly_frombytes_h_natural_q,
         (void *)ntruplus1152_exp001_encap_h_ingress_ma2_h3);
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_BALANCED("current", reset_inputs(),
      public_reject_sink |= (unsigned int)ntruplus1152_exp001_h3_price_current(
        WORD_SLOT(out_current, i), BYTE_SLOT(pk, i),
        WORD_SLOT(r_state, i), WORD_SLOT(m_state, i)),
      public_reject_sink |= (unsigned int)ntruplus1152_exp001_h3_price_h3(
        WORD_SLOT(out_h3, i), BYTE_SLOT(pk, i),
        WORD_SLOT(r_state, i), WORD_SLOT(m_state, i)));
    MEASURE_BALANCED("h1", reset_inputs(),
      public_reject_sink |= (unsigned int)ntruplus1152_exp001_h3_price_h1(
        WORD_SLOT(out_h1, i), BYTE_SLOT(pk, i),
        WORD_SLOT(r_state, i), WORD_SLOT(m_state, i)),
      public_reject_sink |= (unsigned int)ntruplus1152_exp001_h3_price_h3(
        WORD_SLOT(out_h3, i), BYTE_SLOT(pk, i),
        WORD_SLOT(r_state, i), WORD_SLOT(m_state, i)));
  }
}
