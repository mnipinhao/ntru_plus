#include <stdint.h>
#include <stdio.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "f0-prod2-ma2-asm.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full_price.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "f0_words", 0 };
const long long sizes[] = { 1152 };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)

static poly *input_a;
static poly *input_b;
static int16_t *split_a;
static int16_t *split_b;
static int16_t *output_a;
static int16_t *output_b;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  input_a = (poly *)alignedcalloc(BANKS * sizeof *input_a);
  input_b = (poly *)alignedcalloc(BANKS * sizeof *input_b);
  split_a = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *split_a);
  split_b = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *split_b);
  output_a = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *output_a);
  output_b = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *output_b);
}

static void reset_poly(poly *value, unsigned int salt, unsigned int slot) {
  int j;
  for (j = 0; j < 1152; ++j)
    value->coeffs[j] = (int16_t)((int)((unsigned int)(j * 619) +
                                      slot * 17U + salt) % 3 - 1);
}

static void reset_bank(poly *bank, unsigned int salt) {
  int i;
  for (i = 0; i < BANKS; ++i)
    reset_poly(bank + i, salt, (unsigned int)i);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_gt9x16_prod3_price_control_1x(
    int16_t *planes, int16_t *split, const poly *input) {
  ntruplus1152_exp001_top_split_small(split, input->coeffs);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(planes, split, 0, 0);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(planes, split, 0, 1);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(planes, split, 1, 0);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(planes, split, 1, 1);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_gt9x16_prod3_price_candidate_1x(
    int16_t *planes, const poly *input) {
  ntruplus1152_exp001_top_split_small(planes, input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_price(planes);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_gt9x16_prod3_price_control_2x(
    int16_t *planes0, int16_t *planes1, int16_t *split0, int16_t *split1,
    const poly *input0, const poly *input1) {
  ntruplus1152_exp001_gt9x16_prod3_price_control_1x(
      planes0, split0, input0);
  ntruplus1152_exp001_gt9x16_prod3_price_control_1x(
      planes1, split1, input1);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_gt9x16_prod3_price_candidate_2x(
    int16_t *planes0, int16_t *planes1, const poly *input0,
    const poly *input1) {
  ntruplus1152_exp001_gt9x16_prod3_price_candidate_1x(planes0, input0);
  ntruplus1152_exp001_gt9x16_prod3_price_candidate_1x(planes1, input1);
}

#define SLOT(bank, i) ((bank) + (i) * 1152)
#define MEASURE_ENTRY(label, statement) do {                            \
  for (i = 0; i <= TIMINGS; ++i) {                                     \
    cycles[i] = cpucycles();                                           \
    statement;                                                         \
  }                                                                    \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, label, cycles, TIMINGS);                               \
} while (0)

void measure(void) {
  int i, loop;
  printf("gt9x16_prod3_price_runtime_addresses %p %p %p %p\n",
         (void *)ntruplus1152_exp001_gt9x16_prod3_price_control_1x,
         (void *)ntruplus1152_exp001_gt9x16_prod3_price_candidate_1x,
         (void *)ntruplus1152_exp001_f0_prod2_ma2_p2b_pair,
         (void *)ntruplus1152_exp001_gt9x16_prod3_aos_full_price);
  for (loop = 0; loop < LOOPS; ++loop) {
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("gt9x16_prod3_price_1x_control_first_cycles",
      ntruplus1152_exp001_gt9x16_prod3_price_control_1x(
        SLOT(output_a, i), SLOT(split_a, i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("gt9x16_prod3_price_1x_candidate_second_cycles",
      ntruplus1152_exp001_gt9x16_prod3_price_candidate_1x(
        SLOT(output_a, i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("gt9x16_prod3_price_1x_candidate_first_cycles",
      ntruplus1152_exp001_gt9x16_prod3_price_candidate_1x(
        SLOT(output_a, i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("gt9x16_prod3_price_1x_control_second_cycles",
      ntruplus1152_exp001_gt9x16_prod3_price_control_1x(
        SLOT(output_a, i), SLOT(split_a, i), input_a + i));

    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("gt9x16_prod3_price_2x_control_first_cycles",
      ntruplus1152_exp001_gt9x16_prod3_price_control_2x(
        SLOT(output_a, i), SLOT(output_b, i), SLOT(split_a, i),
        SLOT(split_b, i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("gt9x16_prod3_price_2x_candidate_second_cycles",
      ntruplus1152_exp001_gt9x16_prod3_price_candidate_2x(
        SLOT(output_a, i), SLOT(output_b, i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("gt9x16_prod3_price_2x_candidate_first_cycles",
      ntruplus1152_exp001_gt9x16_prod3_price_candidate_2x(
        SLOT(output_a, i), SLOT(output_b, i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("gt9x16_prod3_price_2x_control_second_cycles",
      ntruplus1152_exp001_gt9x16_prod3_price_control_2x(
        SLOT(output_a, i), SLOT(output_b, i), SLOT(split_a, i),
        SLOT(split_b, i), input_a + i, input_b + i));
  }
}
