#include <stdint.h>
#include <stdio.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "gt9x16_prod3_aos_full_price.h"
#include "gt9x16_prod3_hash_fanout.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "hash_bytes", "state_words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "gt9x16_prod3_hash_fanout_"

static poly *coefficient_input;
static int16_t *planes;
static poly *generic_scratch;
static poly *official_scratch;
static uint8_t *hash_bytes;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  coefficient_input = (poly *)alignedcalloc(BANKS * sizeof *coefficient_input);
  planes = (int16_t *)alignedcalloc(
      BANKS * NTRUPLUS_N * sizeof *planes);
  generic_scratch = (poly *)alignedcalloc(BANKS * sizeof *generic_scratch);
  official_scratch = (poly *)alignedcalloc(BANKS * sizeof *official_scratch);
  hash_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
}

static void reset_bank(unsigned int salt) {
  int i, j;
  for (i = 0; i < BANKS; ++i)
    for (j = 0; j < NTRUPLUS_N; ++j)
      coefficient_input[i].coeffs[j] =
          (int16_t)((int)((unsigned int)(j * 619) +
                          (unsigned int)i * 17U + salt) % 3 - 1);
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
  printf("gt9x16_prod3_hash_fanout_runtime_addresses %p %p %p %p %p\n",
         (void *)ntruplus1152_exp001_hash_fanout_o0,
         (void *)ntruplus1152_exp001_hash_fanout_o1,
         (void *)ntruplus1152_exp001_hash_fanout_c0,
         (void *)ntruplus1152_exp001_hash_fanout_c1,
         (void *)ntruplus1152_exp001_gt9x16_prod3_aos_full_price);
  for (loop = 0; loop < LOOPS; ++loop) {
    /* Four rotations form a Latin square: every variant occupies every slot. */
    reset_bank(11U);
    MEASURE_ENTRY("o0_pos1",
      ntruplus1152_exp001_hash_fanout_o0(coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("o1_pos2",
      ntruplus1152_exp001_hash_fanout_o1(
        BYTE_SLOT(hash_bytes, i), coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("c0_pos3",
      ntruplus1152_exp001_hash_fanout_c0(
        WORD_SLOT(planes, i), coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("c1_pos4",
      ntruplus1152_exp001_hash_fanout_c1(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i),
        coefficient_input + i, generic_scratch + i, official_scratch + i));

    reset_bank(11U);
    MEASURE_ENTRY("o1_pos1",
      ntruplus1152_exp001_hash_fanout_o1(
        BYTE_SLOT(hash_bytes, i), coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("c0_pos2",
      ntruplus1152_exp001_hash_fanout_c0(
        WORD_SLOT(planes, i), coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("c1_pos3",
      ntruplus1152_exp001_hash_fanout_c1(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i),
        coefficient_input + i, generic_scratch + i, official_scratch + i));
    reset_bank(11U);
    MEASURE_ENTRY("o0_pos4",
      ntruplus1152_exp001_hash_fanout_o0(coefficient_input + i));

    reset_bank(11U);
    MEASURE_ENTRY("c0_pos1",
      ntruplus1152_exp001_hash_fanout_c0(
        WORD_SLOT(planes, i), coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("c1_pos2",
      ntruplus1152_exp001_hash_fanout_c1(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i),
        coefficient_input + i, generic_scratch + i, official_scratch + i));
    reset_bank(11U);
    MEASURE_ENTRY("o0_pos3",
      ntruplus1152_exp001_hash_fanout_o0(coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("o1_pos4",
      ntruplus1152_exp001_hash_fanout_o1(
        BYTE_SLOT(hash_bytes, i), coefficient_input + i));

    reset_bank(11U);
    MEASURE_ENTRY("c1_pos1",
      ntruplus1152_exp001_hash_fanout_c1(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i),
        coefficient_input + i, generic_scratch + i, official_scratch + i));
    reset_bank(11U);
    MEASURE_ENTRY("o0_pos2",
      ntruplus1152_exp001_hash_fanout_o0(coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("o1_pos3",
      ntruplus1152_exp001_hash_fanout_o1(
        BYTE_SLOT(hash_bytes, i), coefficient_input + i));
    reset_bank(11U);
    MEASURE_ENTRY("c0_pos4",
      ntruplus1152_exp001_hash_fanout_c0(
        WORD_SLOT(planes, i), coefficient_input + i));
  }
}
