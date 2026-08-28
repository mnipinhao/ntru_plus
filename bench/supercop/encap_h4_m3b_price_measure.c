#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "encap-h4-m3.h"
#include "encap-h4-m3b-exact-egress.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "encap_h4_m3b_price_"

static uint8_t *pk, *ct_control, *ct_candidate;
static int16_t *r_state, *m_state, *scratch_control, *scratch_candidate;
static poly *encoded_h;
static long long cycles[TIMINGS + 1];
static volatile unsigned int public_reject_sink;

void preallocate(void) {}

void allocate(void) {
  pk = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  ct_control = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  ct_candidate = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  r_state = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *r_state);
  m_state = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *m_state);
  scratch_control =
      (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *scratch_control);
  scratch_candidate =
      (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *scratch_candidate);
  encoded_h = (poly *)alignedcalloc(BANKS * sizeof *encoded_h);
}

#define WORD_SLOT(base, i) ((base) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(base, i) ((base) + (i) * NTRUPLUS_POLYBYTES)

static void reset_inputs(void) {
  int bank, j;
  for (bank = 0; bank < BANKS; ++bank) {
    for (j = 0; j < NTRUPLUS_N; ++j) {
      encoded_h[bank].coeffs[j] =
          (int16_t)(((unsigned int)j * 619U +
                     (unsigned int)bank * 37U + 11U) % 3457U);
      WORD_SLOT(r_state, bank)[j] =
          (int16_t)((int)(((unsigned int)j * 43U +
                           (unsigned int)bank * 19U) % 3U) - 1);
      WORD_SLOT(m_state, bank)[j] =
          (int16_t)((int)(((unsigned int)j * 71U +
                           (unsigned int)bank * 23U) % 3U) - 1);
    }
    poly_tobytes(BYTE_SLOT(pk, bank), encoded_h + bank);
  }
}

static void preflight(void) {
  int control_reject, candidate_reject;
  reset_inputs();
  control_reject = ntruplus1152_exp001_encap_h4_m3(
      ct_control, pk, r_state, m_state, scratch_control);
  candidate_reject = ntruplus1152_exp001_encap_h4_m3b_exact_egress(
      ct_candidate, pk, r_state, m_state, scratch_candidate);
  if (control_reject || candidate_reject ||
      memcmp(ct_control, ct_candidate, NTRUPLUS_POLYBYTES) ||
      memcmp(scratch_control, scratch_candidate,
             NTRUPLUS_N * sizeof *scratch_control)) {
    fprintf(stderr, "H4-M3B price preflight failed\n");
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

#define MEASURE_BALANCED(preparation, control_statement, candidate_statement) do { \
  preparation;                                                                  \
  MEASURE_ENTRY("control_first", control_statement);                            \
  preparation;                                                                  \
  MEASURE_ENTRY("candidate_second", candidate_statement);                      \
  preparation;                                                                  \
  MEASURE_ENTRY("candidate_first", candidate_statement);                       \
  preparation;                                                                  \
  MEASURE_ENTRY("control_second", control_statement);                          \
} while (0)

void measure(void) {
  int i, loop;
  preflight();
  printf("encap_h4_m3b_price_runtime_addresses %p %p\n",
         (void *)ntruplus1152_exp001_encap_h4_m3,
         (void *)ntruplus1152_exp001_encap_h4_m3b_exact_egress);
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_BALANCED(reset_inputs(),
      public_reject_sink |= (unsigned int)ntruplus1152_exp001_encap_h4_m3(
        BYTE_SLOT(ct_control, i), BYTE_SLOT(pk, i), WORD_SLOT(r_state, i),
        WORD_SLOT(m_state, i), WORD_SLOT(scratch_control, i)),
      public_reject_sink |=
        (unsigned int)ntruplus1152_exp001_encap_h4_m3b_exact_egress(
          BYTE_SLOT(ct_candidate, i), BYTE_SLOT(pk, i), WORD_SLOT(r_state, i),
          WORD_SLOT(m_state, i), WORD_SLOT(scratch_candidate, i)));
  }
}
