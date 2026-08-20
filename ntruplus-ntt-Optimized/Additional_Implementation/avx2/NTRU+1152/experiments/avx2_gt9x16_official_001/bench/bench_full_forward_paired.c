#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <immintrin.h>

#include "gt9x16_forward.h"

#define BLOCKS 16
#define OBSERVATIONS 96

extern void poly_ntt(int16_t value[NTRUPLUS1152_EXP001_N]);

typedef enum { OFFICIAL, CANDIDATE } implementation;

static _Alignas(32) int16_t fixed_input[NTRUPLUS1152_EXP001_N];
static _Alignas(32) int16_t work[NTRUPLUS1152_EXP001_N];
static volatile int16_t sink;

static uint64_t cycles_start(void) {
  unsigned int auxiliary;
  _mm_lfence();
  return __rdtscp(&auxiliary);
}

static uint64_t cycles_stop(void) {
  unsigned int auxiliary;
  uint64_t value = __rdtscp(&auxiliary);
  _mm_lfence();
  return value;
}

static int compare_u64(const void *left, const void *right) {
  uint64_t a = *(const uint64_t *)left;
  uint64_t b = *(const uint64_t *)right;
  return (a > b) - (a < b);
}

static uint64_t measure(implementation selected) {
  uint64_t samples[OBSERVATIONS];
  int observation;
  for (observation = 0; observation < OBSERVATIONS; ++observation) {
    uint64_t begin, end;
    memcpy(work, fixed_input, sizeof work);
    begin = cycles_start();
    if (selected == OFFICIAL) {
      poly_ntt(work);
    } else {
      ntruplus1152_exp001_gt9x16_forward_small(work, work);
    }
    end = cycles_stop();
    samples[observation] = end - begin;
    sink ^= work[(observation * 137) % NTRUPLUS1152_EXP001_N];
  }
  qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
  return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

int main(void) {
  static const implementation odd[4] = {OFFICIAL, CANDIDATE, CANDIDATE, OFFICIAL};
  static const implementation even[4] = {CANDIDATE, OFFICIAL, OFFICIAL, CANDIDATE};
  int block, index, slot;
  for (index = 0; index < NTRUPLUS1152_EXP001_N; ++index) {
    fixed_input[index] = (int16_t)(((index * 5 + 3) & 7) - 3);
  }
  puts("{\"benchmark_class\":\"repository-local-transform-paired-not-for-promotion\","
       "\"blocks\":16,\"observations_per_slot\":96,\"records\":[");
  for (block = 0; block < BLOCKS; ++block) {
    const implementation *order = (block & 1) == 0 ? odd : even;
    for (slot = 0; slot < 4; ++slot) {
      uint64_t cycles = measure(order[slot]);
      printf("{\"block\":%d,\"slot\":%d,\"implementation\":\"%s\","
             "\"median_cycles\":%" PRIu64 "}%s\n",
             block + 1, slot + 1, order[slot] == OFFICIAL ? "official" : "gt",
             cycles, block + 1 == BLOCKS && slot == 3 ? "" : ",");
    }
  }
  printf("] ,\"sink\":%" PRId16 "}\n", sink);
  return 0;
}
