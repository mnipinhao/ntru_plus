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
#define PREFIX "gt9x16_prod3_encap_tail_attribution_v1_"

static poly *input_r, *input_m, *input_h;
static poly *official_r, *official_m, *official_h, *official_out;
static int16_t *gt_r, *gt_m, *gt_out, *gt_projected_h;
static uint8_t *official_bytes, *gt_bytes, *production_bytes;
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
  gt_projected_h =
      (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *gt_projected_h);
  official_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  gt_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  production_bytes = (uint8_t *)alignedcalloc(NTRUPLUS_POLYBYTES);
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
ntruplus1152_exp001_tail_v1_official_resident_h(const poly *h) {
  __asm__ __volatile__("" : : "r"(h) : "memory");
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_tail_v1_gt_resident_h(int16_t *out, const poly *h) {
  ntruplus1152_exp001_project_h_natural_q(out, h->coeffs);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_tail_v1_official_t1(poly *out, const poly *r,
                                        const poly *m, const poly *h) {
  poly_basemul(out, h, r);
  poly_add(out, out, m);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_tail_v1_gt_t1(int16_t *out, const int16_t *r,
                                  const int16_t *m, const poly *h) {
  ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4(
      out, r, m, h->coeffs);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_tail_v1_official_t2(
    uint8_t *bytes, poly *out, const poly *r, const poly *m, const poly *h) {
  ntruplus1152_exp001_tail_v1_official_t1(out, r, m, h);
  poly_tobytes(bytes, out);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_tail_v1_gt_t2(
    uint8_t *bytes, int16_t *out, const int16_t *r, const int16_t *m,
    const poly *h) {
  ntruplus1152_exp001_tail_v1_gt_t1(out, r, m, h);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(bytes, out);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_tail_v1_gt_producer(int16_t *out, const poly *input) {
  ntruplus1152_exp001_top_split_small(out, input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(out);
}

#define WORD_SLOT(bank, i) ((bank) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(bank, i) ((bank) + (i) * NTRUPLUS_POLYBYTES)

static void prepare_tail_inputs(void) {
  int i;
  for (i = 0; i < BANKS; ++i) {
    poly_ntt(official_r + i);
    poly_ntt(official_m + i);
    poly_ntt(official_h + i);
    ntruplus1152_exp001_tail_v1_gt_producer(WORD_SLOT(gt_r, i), input_r + i);
    ntruplus1152_exp001_tail_v1_gt_producer(WORD_SLOT(gt_m, i), input_m + i);
  }
}

static void preflight(void) {
  int i;
  reset_coefficients();
  prepare_tail_inputs();

  ntruplus1152_exp001_tail_v1_gt_resident_h(gt_projected_h, official_h);
  for (i = 0; i < NTRUPLUS_N; ++i) {
    int source = ntruplus1152_exp001_qnat_h_source[i];
    if (gt_projected_h[i] != official_h->coeffs[source]) {
      fprintf(stderr, "tail V1 resident-h map mismatch at cell %d\n", i);
      abort();
    }
  }

  ntruplus1152_exp001_tail_v1_official_t1(
      official_out, official_r, official_m, official_h);
  poly_tobytes(official_bytes, official_out);
  ntruplus1152_exp001_tail_v1_gt_t1(gt_out, gt_r, gt_m, official_h);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(gt_bytes, gt_out);
  if (memcmp(official_bytes, gt_bytes, NTRUPLUS_POLYBYTES)) {
    fprintf(stderr, "tail V1 T1 semantic mismatch\n");
    abort();
  }

  ntruplus1152_exp001_tail_v1_official_t2(
      official_bytes, official_out, official_r, official_m, official_h);
  ntruplus1152_exp001_tail_v1_gt_t2(
      gt_bytes, gt_out, gt_r, gt_m, official_h);
  ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4(
      gt_projected_h, gt_r, gt_m, official_h->coeffs);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(
      production_bytes, gt_projected_h);
  if (memcmp(official_bytes, gt_bytes, NTRUPLUS_POLYBYTES) ||
      memcmp(gt_bytes, production_bytes, NTRUPLUS_POLYBYTES)) {
    fprintf(stderr, "tail V1 T2 production/Official byte mismatch\n");
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
  printf("gt9x16_prod3_encap_tail_attribution_v1_runtime_addresses"
         " %p %p %p %p %p %p %p %p %p %p\n",
         (void *)ntruplus1152_exp001_tail_v1_official_resident_h,
         (void *)ntruplus1152_exp001_tail_v1_gt_resident_h,
         (void *)ntruplus1152_exp001_tail_v1_official_t1,
         (void *)ntruplus1152_exp001_tail_v1_gt_t1,
         (void *)ntruplus1152_exp001_tail_v1_official_t2,
         (void *)ntruplus1152_exp001_tail_v1_gt_t2,
         (void *)poly_basemul,
         (void *)ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4,
         (void *)poly_tobytes,
         (void *)ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q);
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_BALANCED("t0", (reset_coefficients(), prepare_tail_inputs()),
      ntruplus1152_exp001_tail_v1_official_resident_h(official_h+i),
      ntruplus1152_exp001_tail_v1_gt_resident_h(
        WORD_SLOT(gt_projected_h, i), official_h+i));
    MEASURE_BALANCED("t1", (reset_coefficients(), prepare_tail_inputs()),
      ntruplus1152_exp001_tail_v1_official_t1(
        official_out+i, official_r+i, official_m+i, official_h+i),
      ntruplus1152_exp001_tail_v1_gt_t1(
        WORD_SLOT(gt_out, i), WORD_SLOT(gt_r, i), WORD_SLOT(gt_m, i),
        official_h+i));
    MEASURE_BALANCED("t2", (reset_coefficients(), prepare_tail_inputs()),
      ntruplus1152_exp001_tail_v1_official_t2(
        BYTE_SLOT(official_bytes, i), official_out+i,
        official_r+i, official_m+i, official_h+i),
      ntruplus1152_exp001_tail_v1_gt_t2(
        BYTE_SLOT(gt_bytes, i), WORD_SLOT(gt_out, i),
        WORD_SLOT(gt_r, i), WORD_SLOT(gt_m, i), official_h+i));
  }
}
