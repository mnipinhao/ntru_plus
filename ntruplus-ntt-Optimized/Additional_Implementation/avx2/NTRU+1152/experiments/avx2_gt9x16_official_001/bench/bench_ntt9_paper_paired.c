#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <immintrin.h>

#include "gt9x16_ntt16_asm.h"
#include "gt9x16-ntt9-paper-range.h"

#define BLOCKS 16
#define OBSERVATIONS 96
#define TERMINAL_PAIRS 4

typedef void (*kernel)(ntruplus1152_exp001_gt_persistent_pair *,
                       const ntruplus1152_exp001_gt_persistent_pair *);

static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair input[TERMINAL_PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair output[TERMINAL_PAIRS];
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

static uint64_t measure(kernel selected) {
  uint64_t samples[OBSERVATIONS];
  int observation, pair;
  for (observation = 0; observation < OBSERVATIONS; ++observation) {
    uint64_t begin = cycles_start();
    for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
      selected(&output[pair], &input[pair]);
    samples[observation] = cycles_stop() - begin;
    sink ^= output[observation % TERMINAL_PAIRS]
                  .state[observation % 9][observation & 1][observation & 15];
  }
  qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
  return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

static void emit_pair(const char *comparison,
                      const char *left_name, kernel left,
                      const char *right_name, kernel right) {
  static const int odd[4] = {0, 1, 1, 0};
  static const int even[4] = {1, 0, 0, 1};
  int block, slot;
  for (block = 0; block < BLOCKS; ++block) {
    const int *order = (block & 1) == 0 ? odd : even;
    for (slot = 0; slot < 4; ++slot) {
      int choose_right = order[slot];
      printf("{\"comparison\":\"%s\",\"block\":%d,\"slot\":%d,"
             "\"implementation\":\"%s\",\"median_cycles\":%" PRIu64 "},\n",
             comparison, block + 1, slot + 1,
             choose_right ? right_name : left_name,
             measure(choose_right ? right : left));
    }
  }
}

int main(void) {
  int lane, pair, row, stream;
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    for (row = 0; row < 9; ++row)
      for (stream = 0; stream < 2; ++stream)
        for (lane = 0; lane < 16; ++lane) {
          unsigned value = (unsigned)(pair * 271 + row * 43 + stream * 997 + lane * 11);
          input[pair].state[row][stream][lane] = (int16_t)(
              NTRUPLUS1152_EXP001_PAPER_INPUT_MIN +
              value % (NTRUPLUS1152_EXP001_PAPER_INPUT_MAX -
                       NTRUPLUS1152_EXP001_PAPER_INPUT_MIN + 1));
        }
  puts("{\"benchmark_class\":\"repository-local-f-r3b-paired-not-for-promotion\","
       "\"blocks\":16,\"observations_per_slot\":96,\"ntt9_instances_per_observation\":8,"
       "\"records\":[");
  emit_pair("R0-to-R1", "R0", ntruplus1152_exp001_gt9x16_ntt9_d_a,
            "R1", ntruplus1152_exp001_gt9x16_ntt9_r1);
  emit_pair("R1-to-R2-memory", "R1", ntruplus1152_exp001_gt9x16_ntt9_r1,
            "R2-memory", ntruplus1152_exp001_gt9x16_ntt9_r2_memory);
  emit_pair("R1-to-R2-cached", "R1", ntruplus1152_exp001_gt9x16_ntt9_r1,
            "R2-cached", ntruplus1152_exp001_gt9x16_ntt9_r2_cached);
  emit_pair("R2-memory-to-cached", "R2-memory",
            ntruplus1152_exp001_gt9x16_ntt9_r2_memory,
            "R2-cached", ntruplus1152_exp001_gt9x16_ntt9_r2_cached);
  printf("{\"comparison\":\"sink\",\"block\":0,\"slot\":0,"
         "\"implementation\":\"none\",\"median_cycles\":%" PRId16 "}]}\n", sink);
  return 0;
}
