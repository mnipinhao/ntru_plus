#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "f0-official-to-f0.h"
#include "f0_forward_for_ma2.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "ciphertext_bytes", "f0_words", 0 };
const long long sizes[] = { 1728, 1152 };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PERF_REPETITIONS 4096

static poly *input_a;
static poly *input_b;
static int16_t *output_a;
static int16_t *output_b;
static volatile uint16_t diagnostic_sink;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  input_a = (poly *)alignedcalloc(BANKS * sizeof *input_a);
  input_b = (poly *)alignedcalloc(BANKS * sizeof *input_b);
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
ntruplus1152_exp001_f0_prod1_legacy_1x(int16_t *output, poly *input) {
  poly_ntt(input);
  ntruplus1152_exp001_official_to_f0(output, input->coeffs);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_f0_prod1_p1h_1x(int16_t *output, const poly *input) {
  ntruplus1152_exp001_f0_forward_for_ma2_p1h(output, input->coeffs);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_f0_prod1_legacy_2x(int16_t *out_a, int16_t *out_b,
                                      poly *in_a, poly *in_b) {
  ntruplus1152_exp001_f0_prod1_legacy_1x(out_a, in_a);
  ntruplus1152_exp001_f0_prod1_legacy_1x(out_b, in_b);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_f0_prod1_p1h_2x(int16_t *out_a, int16_t *out_b,
                                   const poly *in_a, const poly *in_b) {
  ntruplus1152_exp001_f0_prod1_p1h_1x(out_a, in_a);
  ntruplus1152_exp001_f0_prod1_p1h_1x(out_b, in_b);
}

#define OUT_A(i) (output_a + (i) * 1152)
#define OUT_B(i) (output_b + (i) * 1152)
#define MEASURE_ENTRY(label, statement) do {                           \
  for (i = 0; i <= TIMINGS; ++i) {                                    \
    cycles[i] = cpucycles();                                          \
    statement;                                                        \
  }                                                                   \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, label, cycles, TIMINGS);                              \
} while (0)

static int diagnostic_mode(const char *mode) {
  int repetition, slot;
  if (!mode || !*mode)
    return 0;
  if (!strcmp(mode, "baseline1x")) {
    for (repetition = 0; repetition < PERF_REPETITIONS; ++repetition) {
      slot = repetition % BANKS;
      reset_poly(input_a + slot, 11U, (unsigned int)slot);
      diagnostic_sink ^= (uint16_t)input_a[slot].coeffs[repetition % 1152];
    }
  } else if (!strcmp(mode, "legacy1x")) {
    for (repetition = 0; repetition < PERF_REPETITIONS; ++repetition) {
      slot = repetition % BANKS;
      reset_poly(input_a + slot, 11U, (unsigned int)slot);
      ntruplus1152_exp001_f0_prod1_legacy_1x(OUT_A(slot), input_a + slot);
      diagnostic_sink ^= (uint16_t)OUT_A(slot)[repetition % 1152];
    }
  } else if (!strcmp(mode, "p1h1x")) {
    for (repetition = 0; repetition < PERF_REPETITIONS; ++repetition) {
      slot = repetition % BANKS;
      reset_poly(input_a + slot, 11U, (unsigned int)slot);
      ntruplus1152_exp001_f0_prod1_p1h_1x(OUT_A(slot), input_a + slot);
      diagnostic_sink ^= (uint16_t)OUT_A(slot)[repetition % 1152];
    }
  } else if (!strcmp(mode, "baseline2x")) {
    for (repetition = 0; repetition < PERF_REPETITIONS; ++repetition) {
      slot = repetition % BANKS;
      reset_poly(input_a + slot, 11U, (unsigned int)slot);
      reset_poly(input_b + slot, 29U, (unsigned int)slot);
      diagnostic_sink ^= (uint16_t)(input_a[slot].coeffs[repetition % 1152] +
                                    input_b[slot].coeffs[repetition % 1152]);
    }
  } else if (!strcmp(mode, "legacy2x")) {
    for (repetition = 0; repetition < PERF_REPETITIONS; ++repetition) {
      slot = repetition % BANKS;
      reset_poly(input_a + slot, 11U, (unsigned int)slot);
      reset_poly(input_b + slot, 29U, (unsigned int)slot);
      ntruplus1152_exp001_f0_prod1_legacy_2x(
          OUT_A(slot), OUT_B(slot), input_a + slot, input_b + slot);
      diagnostic_sink ^= (uint16_t)(OUT_A(slot)[repetition % 1152] +
                                    OUT_B(slot)[repetition % 1152]);
    }
  } else if (!strcmp(mode, "p1h2x")) {
    for (repetition = 0; repetition < PERF_REPETITIONS; ++repetition) {
      slot = repetition % BANKS;
      reset_poly(input_a + slot, 11U, (unsigned int)slot);
      reset_poly(input_b + slot, 29U, (unsigned int)slot);
      ntruplus1152_exp001_f0_prod1_p1h_2x(
          OUT_A(slot), OUT_B(slot), input_a + slot, input_b + slot);
      diagnostic_sink ^= (uint16_t)(OUT_A(slot)[repetition % 1152] +
                                    OUT_B(slot)[repetition % 1152]);
    }
  } else {
    return 0;
  }
  return 1;
}

void measure(void) {
  const char *perf_mode = getenv("NTRUPLUS_F0_PROD1_PERF");
  int i, loop;
  if (diagnostic_mode(perf_mode))
    return;
  for (loop = 0; loop < LOOPS; ++loop) {
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("f0_prod1_1x_legacy_first_cycles",
      ntruplus1152_exp001_f0_prod1_legacy_1x(OUT_A(i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("f0_prod1_1x_p1h_second_cycles",
      ntruplus1152_exp001_f0_prod1_p1h_1x(OUT_A(i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("f0_prod1_1x_p1h_first_cycles",
      ntruplus1152_exp001_f0_prod1_p1h_1x(OUT_A(i), input_a + i));
    reset_bank(input_a, 11U);
    MEASURE_ENTRY("f0_prod1_1x_legacy_second_cycles",
      ntruplus1152_exp001_f0_prod1_legacy_1x(OUT_A(i), input_a + i));

    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("f0_prod1_2x_legacy_first_cycles",
      ntruplus1152_exp001_f0_prod1_legacy_2x(
        OUT_A(i), OUT_B(i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("f0_prod1_2x_p1h_second_cycles",
      ntruplus1152_exp001_f0_prod1_p1h_2x(
        OUT_A(i), OUT_B(i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("f0_prod1_2x_p1h_first_cycles",
      ntruplus1152_exp001_f0_prod1_p1h_2x(
        OUT_A(i), OUT_B(i), input_a + i, input_b + i));
    reset_bank(input_a, 11U);
    reset_bank(input_b, 29U);
    MEASURE_ENTRY("f0_prod1_2x_legacy_second_cycles",
      ntruplus1152_exp001_f0_prod1_legacy_2x(
        OUT_A(i), OUT_B(i), input_a + i, input_b + i));
  }
}
