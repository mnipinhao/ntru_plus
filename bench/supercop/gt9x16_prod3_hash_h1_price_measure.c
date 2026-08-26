#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "f0_prod3_hash_bridge.h"
#include "gt9x16-prod3-ma2-hash-h1.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "hash_bytes", "state_words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "gt9x16_prod3_hash_h1_price_"

static int16_t *planes;
static poly *generic_scratch;
static poly *official_scratch;
static uint8_t *hash_bytes;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void) {
  planes = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *planes);
  generic_scratch = (poly *)alignedcalloc(BANKS * sizeof *generic_scratch);
  official_scratch = (poly *)alignedcalloc(BANKS * sizeof *official_scratch);
  hash_bytes = (uint8_t *)alignedcalloc(2 * BANKS * NTRUPLUS_POLYBYTES);
}

static void reset_planes(unsigned int salt) {
  int i, j;
  for (i = 0; i < BANKS; ++i)
    for (j = 0; j < NTRUPLUS_N; ++j)
      planes[i * NTRUPLUS_N + j] =
          (int16_t)((int)((unsigned int)(j * 619) +
                          (unsigned int)i * 17U + salt) % 41505U - 20751);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_prod3_hash_h1_price_h0(
    uint8_t output[NTRUPLUS_POLYBYTES], const int16_t input[NTRUPLUS_N],
    poly *generic, poly *official) {
  ntruplus1152_exp001_prod3_hash_bytes(output, input, generic, official);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_prod3_hash_h1_price_h1(
    uint8_t output[NTRUPLUS_POLYBYTES], const int16_t input[NTRUPLUS_N]) {
  ntruplus1152_exp001_prod3_ma2_hash_h1(output, input);
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
  reset_planes(11U);
  ntruplus1152_exp001_prod3_hash_h1_price_h0(
      hash_bytes, planes, generic_scratch, official_scratch);
  ntruplus1152_exp001_prod3_hash_h1_price_h1(
      hash_bytes + BANKS * NTRUPLUS_POLYBYTES, planes);
  if (memcmp(hash_bytes, hash_bytes + BANKS * NTRUPLUS_POLYBYTES,
             NTRUPLUS_POLYBYTES) != 0) {
    fprintf(stderr, "H0/H1 installed-source preflight mismatch\n");
    abort();
  }
  printf("gt9x16_prod3_hash_h1_price_runtime_addresses %p %p %p %p\n",
         (void *)ntruplus1152_exp001_prod3_hash_h1_price_h0,
         (void *)ntruplus1152_exp001_prod3_hash_h1_price_h1,
         (void *)ntruplus1152_exp001_prod3_hash_bytes,
         (void *)ntruplus1152_exp001_prod3_ma2_hash_h1);
  for (loop = 0; loop < LOOPS; ++loop) {
    /* Both variants occupy every one of four measurement positions. */
    reset_planes(11U);
    MEASURE_ENTRY("h0_pos1",
      ntruplus1152_exp001_prod3_hash_h1_price_h0(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i),
        generic_scratch + i, official_scratch + i));
    reset_planes(11U);
    MEASURE_ENTRY("h1_pos2",
      ntruplus1152_exp001_prod3_hash_h1_price_h1(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i)));
    reset_planes(11U);
    MEASURE_ENTRY("h1_pos3",
      ntruplus1152_exp001_prod3_hash_h1_price_h1(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i)));
    reset_planes(11U);
    MEASURE_ENTRY("h0_pos4",
      ntruplus1152_exp001_prod3_hash_h1_price_h0(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i),
        generic_scratch + i, official_scratch + i));

    reset_planes(11U);
    MEASURE_ENTRY("h1_pos1",
      ntruplus1152_exp001_prod3_hash_h1_price_h1(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i)));
    reset_planes(11U);
    MEASURE_ENTRY("h0_pos2",
      ntruplus1152_exp001_prod3_hash_h1_price_h0(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i),
        generic_scratch + i, official_scratch + i));
    reset_planes(11U);
    MEASURE_ENTRY("h0_pos3",
      ntruplus1152_exp001_prod3_hash_h1_price_h0(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i),
        generic_scratch + i, official_scratch + i));
    reset_planes(11U);
    MEASURE_ENTRY("h1_pos4",
      ntruplus1152_exp001_prod3_hash_h1_price_h1(
        BYTE_SLOT(hash_bytes, i), WORD_SLOT(planes, i)));
  }
}
