#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full_price.h"
#include "gt9x16-prod3-ma2-hash-h1.h"
#include "gt9x16-prod3-ma2-qorder-natural-asm.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "gt9x16_prod3_qorder_price_"

static poly *input_r, *input_m;
static int16_t *r_planes, *m_planes, *ma2_planes;
static int16_t *resident_h;
static uint8_t *ciphertext, *hash_bytes;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  int i;
  input_r = (poly *)alignedcalloc(BANKS * sizeof *input_r);
  input_m = (poly *)alignedcalloc(BANKS * sizeof *input_m);
  r_planes = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *r_planes);
  m_planes = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *m_planes);
  ma2_planes = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *ma2_planes);
  resident_h = (int16_t *)alignedcalloc(NTRUPLUS_N * sizeof *resident_h);
  ciphertext = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  hash_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  for (i = 0; i < NTRUPLUS_N; ++i)
    resident_h[i] = (int16_t)((i * 43 + 5) % NTRUPLUS_Q);
}

static void reset_poly(poly *value, unsigned int salt, unsigned int slot) {
  int j;
  for (j = 0; j < NTRUPLUS_N; ++j)
    value->coeffs[j] = (int16_t)((int)((unsigned int)(j * 619) +
                                      slot * 17U + salt) % 3 - 1);
}

static void reset_inputs(void) {
  int i;
  for (i = 0; i < BANKS; ++i) {
    reset_poly(input_r + i, 11U, (unsigned int)i);
    reset_poly(input_m + i, 29U, (unsigned int)i);
  }
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_qorder_price_current(
    uint8_t *ct, uint8_t *hash, int16_t *r, int16_t *m, int16_t *product,
    const poly *r_input, const poly *m_input, const int16_t *h) {
  ntruplus1152_exp001_top_split_small(r, r_input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_price(r);
  ntruplus1152_exp001_top_split_small(m, m_input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_price(m);
  ntruplus1152_exp001_f0_ma2_planes_current_q(product, r, m, h);
  ntruplus1152_exp001_prod3_ma2_hash_h1(ct, product);
  ntruplus1152_exp001_prod3_ma2_hash_h1(hash, r);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_qorder_price_natural(
    uint8_t *ct, uint8_t *hash, int16_t *r, int16_t *m, int16_t *product,
    const poly *r_input, const poly *m_input, const int16_t *h) {
  ntruplus1152_exp001_top_split_small(r, r_input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q(r);
  ntruplus1152_exp001_top_split_small(m, m_input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q(m);
  ntruplus1152_exp001_f0_ma2_planes_natural_q(product, r, m, h);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(ct, product);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(hash, r);
}

#define WORD_SLOT(bank, i) ((bank) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(bank, i) ((bank) + (i) * NTRUPLUS_POLYBYTES)
#define MEASURE_ENTRY(label, statement) do {                            \
  for (i = 0; i <= TIMINGS; ++i) {                                     \
    cycles[i] = cpucycles();                                           \
    statement;                                                         \
  }                                                                    \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, PREFIX label "_cycles", cycles, TIMINGS);             \
} while (0)

void measure(void) {
  int i, loop;
  reset_inputs();
  ntruplus1152_exp001_qorder_price_current(
      ciphertext, hash_bytes, r_planes, m_planes, ma2_planes,
      input_r, input_m, resident_h);
  ntruplus1152_exp001_qorder_price_natural(
      ciphertext + NTRUPLUS_POLYBYTES, hash_bytes + NTRUPLUS_POLYBYTES,
      r_planes + NTRUPLUS_N, m_planes + NTRUPLUS_N,
      ma2_planes + NTRUPLUS_N, input_r, input_m, resident_h);
  if (memcmp(ciphertext, ciphertext + NTRUPLUS_POLYBYTES,
             NTRUPLUS_POLYBYTES) ||
      memcmp(hash_bytes, hash_bytes + NTRUPLUS_POLYBYTES,
             NTRUPLUS_POLYBYTES)) {
    fprintf(stderr, "current-Q/natural-Q caller preflight mismatch\n");
    abort();
  }
  printf("gt9x16_prod3_qorder_price_runtime_addresses %p %p %p %p %p %p\n",
         (void *)ntruplus1152_exp001_qorder_price_current,
         (void *)ntruplus1152_exp001_qorder_price_natural,
         (void *)ntruplus1152_exp001_gt9x16_prod3_aos_full_price,
         (void *)ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q,
         (void *)ntruplus1152_exp001_prod3_ma2_hash_h1,
         (void *)ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q);
  for (loop = 0; loop < LOOPS; ++loop) {
    reset_inputs();
    MEASURE_ENTRY("current_first", ntruplus1152_exp001_qorder_price_current(
      BYTE_SLOT(ciphertext, i), BYTE_SLOT(hash_bytes, i), WORD_SLOT(r_planes, i),
      WORD_SLOT(m_planes, i), WORD_SLOT(ma2_planes, i), input_r+i, input_m+i, resident_h));
    reset_inputs();
    MEASURE_ENTRY("natural_second", ntruplus1152_exp001_qorder_price_natural(
      BYTE_SLOT(ciphertext, i), BYTE_SLOT(hash_bytes, i), WORD_SLOT(r_planes, i),
      WORD_SLOT(m_planes, i), WORD_SLOT(ma2_planes, i), input_r+i, input_m+i, resident_h));
    reset_inputs();
    MEASURE_ENTRY("natural_first", ntruplus1152_exp001_qorder_price_natural(
      BYTE_SLOT(ciphertext, i), BYTE_SLOT(hash_bytes, i), WORD_SLOT(r_planes, i),
      WORD_SLOT(m_planes, i), WORD_SLOT(ma2_planes, i), input_r+i, input_m+i, resident_h));
    reset_inputs();
    MEASURE_ENTRY("current_second", ntruplus1152_exp001_qorder_price_current(
      BYTE_SLOT(ciphertext, i), BYTE_SLOT(hash_bytes, i), WORD_SLOT(r_planes, i),
      WORD_SLOT(m_planes, i), WORD_SLOT(ma2_planes, i), input_r+i, input_m+i, resident_h));
  }
}
