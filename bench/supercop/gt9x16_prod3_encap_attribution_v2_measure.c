#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "gt9x16-prod3-cumulative-ma2.h"
#include "gt9x16-prod3-ma2-qorder-natural-asm.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "gt9x16_prod3_encap_attribution_v2_"

static poly *input_r, *input_m, *input_h;
static poly *official_r, *official_m, *official_h, *official_out;
static int16_t *gt_r, *gt_m, *gt_out;
static uint8_t *official_bytes, *gt_bytes;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  input_r = (poly *)alignedcalloc(BANKS * sizeof *input_r);
  input_m = (poly *)alignedcalloc(BANKS * sizeof *input_m);
  input_h = (poly *)alignedcalloc(BANKS * sizeof *input_h);
  official_r = (poly *)alignedcalloc(BANKS * sizeof *official_r);
  official_m = (poly *)alignedcalloc(BANKS * sizeof *official_m);
  official_h = (poly *)alignedcalloc(BANKS * sizeof *official_h);
  official_out = (poly *)alignedcalloc(BANKS * sizeof *official_out);
  gt_r = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *gt_r);
  gt_m = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *gt_m);
  gt_out = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *gt_out);
  official_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  gt_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
}

static void reset_poly(poly *value, unsigned int salt, unsigned int slot,
                       unsigned int modulus) {
  int j;
  for (j = 0; j < NTRUPLUS_N; ++j)
    value->coeffs[j] = (int16_t)((int)((unsigned int)(j * 619) +
                                      slot * 17U + salt) % modulus -
                                 (int)(modulus / 2U));
}

static void reset_coefficients(void) {
  int i;
  for (i = 0; i < BANKS; ++i) {
    reset_poly(input_r + i, 11U, (unsigned int)i, 3U);
    reset_poly(input_m + i, 29U, (unsigned int)i, 3U);
    reset_poly(input_h + i, 47U, (unsigned int)i, 17U);
    reset_poly(official_r + i, 11U, (unsigned int)i, 3U);
    reset_poly(official_m + i, 29U, (unsigned int)i, 3U);
    reset_poly(official_h + i, 47U, (unsigned int)i, 17U);
  }
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_attr_v2_official_producer(poly *inout) {
  poly_ntt(inout);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_attr_v2_gt_producer(int16_t *out, const poly *input) {
  ntruplus1152_exp001_top_split_small(out, input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(out);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_attr_v2_official_dual(
    poly *state, uint8_t *bytes) {
  ntruplus1152_exp001_attr_v2_official_producer(state);
  poly_tobytes(bytes, state);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_attr_v2_gt_dual(
    int16_t *state, uint8_t *bytes, const poly *input) {
  ntruplus1152_exp001_attr_v2_gt_producer(state, input);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(bytes, state);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_attr_v2_official_tail(
    uint8_t *bytes, poly *out, const poly *r, const poly *m, const poly *h) {
  poly_basemul(out, h, r);
  poly_add(out, out, m);
  poly_tobytes(bytes, out);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_attr_v2_gt_tail(
    uint8_t *bytes, int16_t *out, const int16_t *r, const int16_t *m,
    const poly *h) {
  ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4(
      out, r, m, h->coeffs);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(bytes, out);
}

#define WORD_SLOT(bank, i) ((bank) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(bank, i) ((bank) + (i) * NTRUPLUS_POLYBYTES)

static void prepare_tail_inputs(void) {
  int i;
  for (i = 0; i < BANKS; ++i) {
    ntruplus1152_exp001_attr_v2_official_producer(official_r + i);
    ntruplus1152_exp001_attr_v2_official_producer(official_m + i);
    ntruplus1152_exp001_attr_v2_official_producer(official_h + i);
    ntruplus1152_exp001_attr_v2_gt_producer(WORD_SLOT(gt_r, i), input_r + i);
    ntruplus1152_exp001_attr_v2_gt_producer(WORD_SLOT(gt_m, i), input_m + i);
  }
}

static void preflight(void) {
  int i;
  ntruplus1152_exp001_attr_v2_official_dual(
      official_r, official_bytes);
  ntruplus1152_exp001_attr_v2_gt_dual(gt_r, gt_bytes, input_r);
  if (memcmp(official_bytes, gt_bytes, NTRUPLUS_POLYBYTES)) {
    fprintf(stderr, "attribution V2 producer/dual semantic mismatch\n");
    abort();
  }
  reset_coefficients();
  prepare_tail_inputs();
  ntruplus1152_exp001_attr_v2_official_tail(
      official_bytes, official_out, official_r, official_m, official_h);
  ntruplus1152_exp001_attr_v2_gt_tail(
      gt_bytes, gt_out, gt_r, gt_m, official_h);
  if (memcmp(official_bytes, gt_bytes, NTRUPLUS_POLYBYTES)) {
    for (i = 0; i < NTRUPLUS_POLYBYTES; ++i)
      if (official_bytes[i] != gt_bytes[i]) break;
    fprintf(stderr, "attribution V2 tail mismatch at byte %d\n", i);
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

#define MEASURE_BALANCED(label, preparation, official_statement, gt_statement) do { \
  preparation;                                                         \
  MEASURE_ENTRY(label "_official_first", official_statement);          \
  preparation;                                                         \
  MEASURE_ENTRY(label "_gt_second", gt_statement);                     \
  preparation;                                                         \
  MEASURE_ENTRY(label "_gt_first", gt_statement);                      \
  preparation;                                                         \
  MEASURE_ENTRY(label "_official_second", official_statement);        \
} while (0)

void measure(void) {
  int i, loop;
  reset_coefficients();
  preflight();
  printf("gt9x16_prod3_encap_attribution_v2_runtime_addresses"
         " %p %p %p %p %p %p %p %p %p %p\n",
         (void *)ntruplus1152_exp001_attr_v2_official_producer,
         (void *)ntruplus1152_exp001_attr_v2_gt_producer,
         (void *)ntruplus1152_exp001_attr_v2_official_dual,
         (void *)ntruplus1152_exp001_attr_v2_gt_dual,
         (void *)ntruplus1152_exp001_attr_v2_official_tail,
         (void *)ntruplus1152_exp001_attr_v2_gt_tail,
         (void *)poly_ntt,
         (void *)ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta,
         (void *)poly_basemul,
         (void *)ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4);
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_BALANCED("producer_r", reset_coefficients(),
      ntruplus1152_exp001_attr_v2_official_producer(official_r+i),
      ntruplus1152_exp001_attr_v2_gt_producer(WORD_SLOT(gt_r, i), input_r+i));
    MEASURE_BALANCED("producer_m", reset_coefficients(),
      ntruplus1152_exp001_attr_v2_official_producer(official_m+i),
      ntruplus1152_exp001_attr_v2_gt_producer(WORD_SLOT(gt_m, i), input_m+i));
    MEASURE_BALANCED("dual_r", reset_coefficients(),
      ntruplus1152_exp001_attr_v2_official_dual(
        official_r+i, BYTE_SLOT(official_bytes, i)),
      ntruplus1152_exp001_attr_v2_gt_dual(
        WORD_SLOT(gt_r, i), BYTE_SLOT(gt_bytes, i), input_r+i));
    MEASURE_BALANCED("tail", (reset_coefficients(), prepare_tail_inputs()),
      ntruplus1152_exp001_attr_v2_official_tail(
        BYTE_SLOT(official_bytes, i), official_out+i,
        official_r+i, official_m+i, official_h+i),
      ntruplus1152_exp001_attr_v2_gt_tail(
        BYTE_SLOT(gt_bytes, i), WORD_SLOT(gt_out, i),
        WORD_SLOT(gt_r, i), WORD_SLOT(gt_m, i), official_h+i));
  }
}
