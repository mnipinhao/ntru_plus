#include <stdint.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "f0-ma2-asm.h"
#include "f0_forward_for_ma2.h"
#include "f0_generic_to_ma2_planes.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "ciphertext_bytes", "f0_words", 0 };
const long long sizes[] = { 1728, 1152 };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)

static poly *input_r;
static poly *input_m;
static int16_t *generic_r;
static int16_t *generic_m;
static int16_t *planes_r;
static int16_t *planes_m;
static int16_t *resident_h;
static int16_t *scratch;
static uint8_t *ciphertext;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  int i;
  input_r = (poly *)alignedcalloc(BANKS * sizeof *input_r);
  input_m = (poly *)alignedcalloc(BANKS * sizeof *input_m);
  generic_r = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *generic_r);
  generic_m = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *generic_m);
  planes_r = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *planes_r);
  planes_m = (int16_t *)alignedcalloc(BANKS * 1152 * sizeof *planes_m);
  resident_h = (int16_t *)alignedcalloc(1152 * sizeof *resident_h);
  scratch = (int16_t *)alignedcalloc(BANKS * 128 * sizeof *scratch);
  ciphertext = (uint8_t *)alignedcalloc(BANKS * 1728 * sizeof *ciphertext);
  for (i = 0; i < 1152; ++i)
    resident_h[i] = (int16_t)((i * 43 + 5) % 3457);
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
ntruplus1152_exp001_f0_prod2_consumer_control(
    uint8_t *output, int16_t *work_r, int16_t *work_m,
    int16_t *native_r, int16_t *native_m, int16_t *ma2_scratch,
    const poly *r, const poly *m, const int16_t *h) {
  ntruplus1152_exp001_f0_forward_for_ma2_p1h(work_r, r->coeffs);
  ntruplus1152_exp001_f0_forward_for_ma2_p1h(work_m, m->coeffs);
  ntruplus1152_exp001_f0_generic_to_ma2_planes(native_r, work_r);
  ntruplus1152_exp001_f0_generic_to_ma2_planes(native_m, work_m);
  ntruplus1152_exp001_f0_ma2_native_full(
      output, native_r, native_m, h, ma2_scratch);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_f0_prod2_consumer_candidate(
    uint8_t *output, int16_t *native_r, int16_t *native_m,
    int16_t *ma2_scratch, const poly *r, const poly *m, const int16_t *h) {
  ntruplus1152_exp001_f0_forward_for_ma2_p2b(native_r, r->coeffs);
  ntruplus1152_exp001_f0_forward_for_ma2_p2b(native_m, m->coeffs);
  ntruplus1152_exp001_f0_ma2_native_full(
      output, native_r, native_m, h, ma2_scratch);
}

#define WORD_SLOT(bank, i, words) ((bank) + (i) * (words))
#define BYTE_SLOT(bank, i, bytes) ((bank) + (i) * (bytes))
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
    reset_bank(input_r, 11U);
    reset_bank(input_m, 29U);
    MEASURE_ENTRY("f0_prod2_consumer_control_first_cycles",
      ntruplus1152_exp001_f0_prod2_consumer_control(
        BYTE_SLOT(ciphertext, i, 1728), WORD_SLOT(generic_r, i, 1152),
        WORD_SLOT(generic_m, i, 1152), WORD_SLOT(planes_r, i, 1152),
        WORD_SLOT(planes_m, i, 1152), WORD_SLOT(scratch, i, 128),
        input_r + i, input_m + i, resident_h));
    reset_bank(input_r, 11U);
    reset_bank(input_m, 29U);
    MEASURE_ENTRY("f0_prod2_consumer_candidate_second_cycles",
      ntruplus1152_exp001_f0_prod2_consumer_candidate(
        BYTE_SLOT(ciphertext, i, 1728), WORD_SLOT(planes_r, i, 1152),
        WORD_SLOT(planes_m, i, 1152), WORD_SLOT(scratch, i, 128),
        input_r + i, input_m + i, resident_h));
    reset_bank(input_r, 11U);
    reset_bank(input_m, 29U);
    MEASURE_ENTRY("f0_prod2_consumer_candidate_first_cycles",
      ntruplus1152_exp001_f0_prod2_consumer_candidate(
        BYTE_SLOT(ciphertext, i, 1728), WORD_SLOT(planes_r, i, 1152),
        WORD_SLOT(planes_m, i, 1152), WORD_SLOT(scratch, i, 128),
        input_r + i, input_m + i, resident_h));
    reset_bank(input_r, 11U);
    reset_bank(input_m, 29U);
    MEASURE_ENTRY("f0_prod2_consumer_control_second_cycles",
      ntruplus1152_exp001_f0_prod2_consumer_control(
        BYTE_SLOT(ciphertext, i, 1728), WORD_SLOT(generic_r, i, 1152),
        WORD_SLOT(generic_m, i, 1152), WORD_SLOT(planes_r, i, 1152),
        WORD_SLOT(planes_m, i, 1152), WORD_SLOT(scratch, i, 128),
        input_r + i, input_m + i, resident_h));
  }
}
