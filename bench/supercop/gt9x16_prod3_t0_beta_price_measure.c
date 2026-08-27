#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full.h"
#include "gt9x16-prod3-ma2-hash-h1.h"
#include "gt9x16-prod3-ma2-qorder-natural-asm.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "gt9x16_prod3_t0_beta_price_"

void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(int16_t *);

static poly *input_a, *input_b;
static int16_t *planes_a, *planes_b, *scratch_a, *scratch_b, *products;
static int16_t *resident_h;
static uint8_t *ciphertext, *hash_bytes;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  int i;
  input_a = (poly *)alignedcalloc(BANKS * sizeof *input_a);
  input_b = (poly *)alignedcalloc(BANKS * sizeof *input_b);
  planes_a = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *planes_a);
  planes_b = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *planes_b);
  scratch_a = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *scratch_a);
  scratch_b = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *scratch_b);
  products = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *products);
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
    reset_poly(input_a + i, 11U, (unsigned int)i);
    reset_poly(input_b + i, 29U, (unsigned int)i);
  }
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_t0_beta_price_control_1x(int16_t *out, const poly *input) {
  ntruplus1152_exp001_top_split_small(out, input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q(out);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_t0_beta_price_candidate_1x(int16_t *out, const poly *input) {
  ntruplus1152_exp001_top_split_small(out, input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(out);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_t0_beta_price_control_2x(
    int16_t *out0, int16_t *out1, const poly *input0, const poly *input1) {
  ntruplus1152_exp001_t0_beta_price_control_1x(out0, input0);
  ntruplus1152_exp001_t0_beta_price_control_1x(out1, input1);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_t0_beta_price_candidate_2x(
    int16_t *out0, int16_t *out1, const poly *input0, const poly *input1) {
  ntruplus1152_exp001_t0_beta_price_candidate_1x(out0, input0);
  ntruplus1152_exp001_t0_beta_price_candidate_1x(out1, input1);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_t0_beta_price_control_caller(
    uint8_t *ct, uint8_t *hash, int16_t *r, int16_t *m, int16_t *product,
    const poly *r_input, const poly *m_input, const int16_t *h) {
  ntruplus1152_exp001_t0_beta_price_control_2x(r, m, r_input, m_input);
  ntruplus1152_exp001_f0_ma2_planes_natural_q(product, r, m, h);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(ct, product);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(hash, r);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_t0_beta_price_candidate_caller(
    uint8_t *ct, uint8_t *hash, int16_t *r, int16_t *m, int16_t *product,
    const poly *r_input, const poly *m_input, const int16_t *h) {
  ntruplus1152_exp001_t0_beta_price_candidate_2x(r, m, r_input, m_input);
  ntruplus1152_exp001_f0_ma2_planes_natural_q(product, r, m, h);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(ct, product);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(hash, r);
}

static int canonical(int16_t value) {
  int result = value % NTRUPLUS_Q;
  return result < 0 ? result + NTRUPLUS_Q : result;
}

static void preflight(void) {
  int i;
  ntruplus1152_exp001_t0_beta_price_control_1x(planes_a, input_a);
  ntruplus1152_exp001_t0_beta_price_candidate_1x(scratch_a, input_a);
  for (i = 0; i < NTRUPLUS_N; ++i) {
    if (canonical(planes_a[i]) != canonical(scratch_a[i]) ||
        scratch_a[i] < -21333 || scratch_a[i] > 21333) {
      fprintf(stderr, "T0-beta producer canonical/range preflight mismatch\n");
      abort();
    }
  }
  ntruplus1152_exp001_t0_beta_price_control_caller(
      ciphertext, hash_bytes, planes_a, planes_b, products,
      input_a, input_b, resident_h);
  ntruplus1152_exp001_t0_beta_price_candidate_caller(
      ciphertext + NTRUPLUS_POLYBYTES, hash_bytes + NTRUPLUS_POLYBYTES,
      scratch_a, scratch_b, products + NTRUPLUS_N,
      input_a, input_b, resident_h);
  if (memcmp(ciphertext, ciphertext + NTRUPLUS_POLYBYTES,
             NTRUPLUS_POLYBYTES) ||
      memcmp(hash_bytes, hash_bytes + NTRUPLUS_POLYBYTES,
             NTRUPLUS_POLYBYTES)) {
    fprintf(stderr, "T0-beta caller byte preflight mismatch\n");
    abort();
  }
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

#define MEASURE_BALANCED(label, control_statement, candidate_statement) do { \
  reset_inputs();                                                       \
  MEASURE_ENTRY(label "_control_first", control_statement);            \
  reset_inputs();                                                       \
  MEASURE_ENTRY(label "_candidate_second", candidate_statement);       \
  reset_inputs();                                                       \
  MEASURE_ENTRY(label "_candidate_first", candidate_statement);        \
  reset_inputs();                                                       \
  MEASURE_ENTRY(label "_control_second", control_statement);           \
} while (0)

void measure(void) {
  int i, loop;
  reset_inputs();
  preflight();
  printf("gt9x16_prod3_t0_beta_price_runtime_addresses %p %p %p %p %p %p %p %p\n",
         (void *)ntruplus1152_exp001_t0_beta_price_control_1x,
         (void *)ntruplus1152_exp001_t0_beta_price_candidate_1x,
         (void *)ntruplus1152_exp001_t0_beta_price_control_caller,
         (void *)ntruplus1152_exp001_t0_beta_price_candidate_caller,
         (void *)ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q,
         (void *)ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta,
         (void *)ntruplus1152_exp001_f0_ma2_planes_natural_q,
         (void *)ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q);
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_BALANCED("1x",
      ntruplus1152_exp001_t0_beta_price_control_1x(
        WORD_SLOT(planes_a, i), input_a+i),
      ntruplus1152_exp001_t0_beta_price_candidate_1x(
        WORD_SLOT(planes_a, i), input_a+i));
    MEASURE_BALANCED("2x",
      ntruplus1152_exp001_t0_beta_price_control_2x(
        WORD_SLOT(planes_a, i), WORD_SLOT(planes_b, i), input_a+i, input_b+i),
      ntruplus1152_exp001_t0_beta_price_candidate_2x(
        WORD_SLOT(planes_a, i), WORD_SLOT(planes_b, i), input_a+i, input_b+i));
    MEASURE_BALANCED("caller",
      ntruplus1152_exp001_t0_beta_price_control_caller(
        BYTE_SLOT(ciphertext, i), BYTE_SLOT(hash_bytes, i),
        WORD_SLOT(planes_a, i), WORD_SLOT(planes_b, i), WORD_SLOT(products, i),
        input_a+i, input_b+i, resident_h),
      ntruplus1152_exp001_t0_beta_price_candidate_caller(
        BYTE_SLOT(ciphertext, i), BYTE_SLOT(hash_bytes, i),
        WORD_SLOT(planes_a, i), WORD_SLOT(planes_b, i), WORD_SLOT(products, i),
        input_a+i, input_b+i, resident_h));
  }
}
