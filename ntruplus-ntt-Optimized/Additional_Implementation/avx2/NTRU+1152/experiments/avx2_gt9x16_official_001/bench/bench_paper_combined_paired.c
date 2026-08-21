#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <immintrin.h>

#include "gt9x16-ntt9-paper-range.h"
#include "gt9x16_ntt16_asm.h"
#include "official_stage_partitions.h"

#define BLOCKS 16
#define OBSERVATIONS 96
#define TERMINAL_PAIRS 4

typedef void (*operation)(void);

static _Alignas(32) int16_t official_input[NTRUPLUS1152_EXP001_OFFICIAL_N];
static _Alignas(32) int16_t official_work[NTRUPLUS1152_EXP001_OFFICIAL_N];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair input[TERMINAL_PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair after_r2[TERMINAL_PAIRS];
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

static void official_body(void) {
  ntruplus1152_exp001_official_t3x3_t2x4(official_work);
}

static void r2_cached(void) {
  int pair;
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_ntt9_r2_cached(&output[pair], &input[pair]);
}

static void adjusted_only(void) {
  int pair;
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16(&output[pair], &after_r2[pair]);
}

static void adjusted_d0(void) {
  int pair;
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16_d0(&output[pair], &after_r2[pair]);
}

static void adjusted_d1(void) {
  int pair;
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16_d1(&output[pair], &after_r2[pair]);
}

static void combined(void) {
  int pair;
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body(&output[pair], &input[pair]);
}

static void combined_d0(void) {
  int pair;
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d0(&output[pair], &input[pair]);
}

static void combined_d1(void) {
  int pair;
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1(&output[pair], &input[pair]);
}

static void prepare_official(void) { memcpy(official_work, official_input, sizeof official_work); }
static void prepare_none(void) {}

static uint64_t measure(operation selected, operation prepare) {
  uint64_t samples[OBSERVATIONS];
  int observation;
  for (observation = 0; observation < OBSERVATIONS; ++observation) {
    prepare();
    uint64_t begin = cycles_start();
    selected();
    samples[observation] = cycles_stop() - begin;
    sink ^= official_work[(observation * 17) % NTRUPLUS1152_EXP001_OFFICIAL_N];
    sink ^= output[observation % TERMINAL_PAIRS]
                  .state[observation % 9][observation & 1][observation & 15];
  }
  qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
  return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

static void emit_pair(const char *comparison,
                      const char *left_name, operation left, operation left_prepare,
                      const char *right_name, operation right, operation right_prepare) {
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
             measure(choose_right ? right : left,
                     choose_right ? right_prepare : left_prepare));
    }
  }
}

int main(void) {
  int index, lane, pair, row, stream;
  for (index = 0; index < NTRUPLUS1152_EXP001_OFFICIAL_N; ++index)
    official_input[index] = (int16_t)(((index * 5 + 3) & 7) - 3);
  /* Benchmark the exact real-data-flow entry to levels 1--6. */
  ntruplus1152_exp001_official_t0(official_input);
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
  for (pair = 0; pair < TERMINAL_PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_ntt9_r2_cached(&after_r2[pair], &input[pair]);
  puts("{\"benchmark_class\":\"repository-local-f-r3c-combined-paired-not-for-promotion\","
       "\"blocks\":16,\"observations_per_slot\":96,"
       "\"ntt9_instances_per_observation\":8,\"records\":[");
  emit_pair("isolated-components", "R2-cached", r2_cached, prepare_none,
            "adjusted-NTT16", adjusted_only, prepare_none);
  emit_pair("transform-body", "Official-T3x3+T2x4", official_body, prepare_official,
            "R2+adjusted-NTT16", combined, prepare_none);
  emit_pair("adjusted-C-to-D0", "adjusted-C", adjusted_only, prepare_none,
            "adjusted-D0", adjusted_d0, prepare_none);
  emit_pair("adjusted-D0-to-D1", "adjusted-D0", adjusted_d0, prepare_none,
            "adjusted-D1", adjusted_d1, prepare_none);
  emit_pair("combined-C-to-D0", "combined-C", combined, prepare_none,
            "combined-D0", combined_d0, prepare_none);
  emit_pair("combined-D0-to-D1", "combined-D0", combined_d0, prepare_none,
            "combined-D1", combined_d1, prepare_none);
  emit_pair("official-to-D1", "Official-T3x3+T2x4", official_body, prepare_official,
            "combined-D1", combined_d1, prepare_none);
  printf("{\"comparison\":\"sink\",\"block\":0,\"slot\":0,"
         "\"implementation\":\"none\",\"median_cycles\":%" PRId16 "}]}\n", sink);
  return 0;
}
