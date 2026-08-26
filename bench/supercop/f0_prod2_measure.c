#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "f0_forward_for_ma2.h"
#include "f0_generic_to_ma2_planes.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "ciphertext_bytes", "f0_words", 0 };
const long long sizes[] = { 1728, 1152 };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)

static poly *input_a;
static poly *input_b;
static int16_t *generic_a;
static int16_t *generic_b;
static int16_t *planes_a;
static int16_t *planes_b;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  input_a = (poly *)alignedcalloc(BANKS * sizeof *input_a);
  input_b = (poly *)alignedcalloc(BANKS * sizeof *input_b);
  generic_a = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *generic_a);
  generic_b = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *generic_b);
  planes_a = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *planes_a);
  planes_b = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *planes_b);
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
ntruplus1152_exp001_f0_prod2_control_1x(int16_t *planes, int16_t *generic,
                                        const poly *input) {
  ntruplus1152_exp001_f0_forward_for_ma2_p1h(generic, input->coeffs);
  ntruplus1152_exp001_f0_generic_to_ma2_planes(planes, generic);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_f0_prod2_candidate_1x(int16_t *planes,
                                          const poly *input) {
  ntruplus1152_exp001_f0_forward_for_ma2_p2b(planes, input->coeffs);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_f0_prod2_control_2x(
    int16_t *planes0, int16_t *planes1, int16_t *generic0, int16_t *generic1,
    const poly *input0, const poly *input1) {
  ntruplus1152_exp001_f0_prod2_control_1x(planes0, generic0, input0);
  ntruplus1152_exp001_f0_prod2_control_1x(planes1, generic1, input1);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_f0_prod2_candidate_2x(
    int16_t *planes0, int16_t *planes1, const poly *input0,
    const poly *input1) {
  ntruplus1152_exp001_f0_prod2_candidate_1x(planes0, input0);
  ntruplus1152_exp001_f0_prod2_candidate_1x(planes1, input1);
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
  for (loop = 0; loop < LOOPS; ++loop) {
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("f0_prod2_1x_control_first_cycles",
      ntruplus1152_exp001_f0_prod2_control_1x(
        SLOT(planes_a, i), SLOT(generic_a, i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("f0_prod2_1x_candidate_second_cycles",
      ntruplus1152_exp001_f0_prod2_candidate_1x(
        SLOT(planes_a, i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("f0_prod2_1x_candidate_first_cycles",
      ntruplus1152_exp001_f0_prod2_candidate_1x(
        SLOT(planes_a, i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("f0_prod2_1x_control_second_cycles",
      ntruplus1152_exp001_f0_prod2_control_1x(
        SLOT(planes_a, i), SLOT(generic_a, i), input_a + i));

    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("f0_prod2_2x_control_first_cycles",
      ntruplus1152_exp001_f0_prod2_control_2x(
        SLOT(planes_a, i), SLOT(planes_b, i), SLOT(generic_a, i),
        SLOT(generic_b, i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("f0_prod2_2x_candidate_second_cycles",
      ntruplus1152_exp001_f0_prod2_candidate_2x(
        SLOT(planes_a, i), SLOT(planes_b, i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("f0_prod2_2x_candidate_first_cycles",
      ntruplus1152_exp001_f0_prod2_candidate_2x(
        SLOT(planes_a, i), SLOT(planes_b, i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("f0_prod2_2x_control_second_cycles",
      ntruplus1152_exp001_f0_prod2_control_2x(
        SLOT(planes_a, i), SLOT(planes_b, i), SLOT(generic_a, i),
        SLOT(generic_b, i), input_a + i, input_b + i));
  }
}
