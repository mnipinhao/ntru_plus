#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <immintrin.h>

#include "gt9x16-ntt9-paper-range.h"
#include "gt9x16_ntt16_asm.h"

#define BLOCKS 16
#define OBSERVATIONS 96
#define PAIRS 4

typedef void (*operation)(void);

static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair input[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair scratch[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair f0_output[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_terminal_major f1_output;
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

static void f0(void) {
  int pair;
  for (pair = 0; pair < PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1(&f0_output[pair], &input[pair]);
}

static void f1_b0(void) {
  int pair;
  for (pair = 0; pair < PAIRS; ++pair) {
    int branch = pair / 2;
    int terminal_pair = pair % 2;
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b0(
        &scratch[pair], &input[pair], &f1_output.state[branch][0][2 * terminal_pair][0]);
  }
}

static void f1_b1(void) {
  int pair;
  for (pair = 0; pair < PAIRS; ++pair) {
    int branch = pair / 2;
    int terminal_pair = pair % 2;
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b1(
        &scratch[pair], &input[pair], &f1_output.state[branch][0][2 * terminal_pair][0]);
  }
}

static uint64_t measure(operation selected) {
  uint64_t samples[OBSERVATIONS];
  int observation;
  for (observation = 0; observation < OBSERVATIONS; ++observation) {
    uint64_t begin = cycles_start();
    selected();
    samples[observation] = cycles_stop() - begin;
    sink ^= f0_output[observation % PAIRS]
                .state[observation % 9][observation & 1][observation & 15];
    sink ^= f1_output.state[(observation >> 1) & 1][observation % 9]
                           [observation & 3][observation & 15];
  }
  qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
  return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

static void emit_pair(const char *comparison, const char *left_name, operation left,
                      const char *right_name, operation right) {
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
  for (pair = 0; pair < PAIRS; ++pair)
    for (row = 0; row < 9; ++row)
      for (stream = 0; stream < 2; ++stream)
        for (lane = 0; lane < 16; ++lane) {
          unsigned value = (unsigned)(pair * 271 + row * 43 + stream * 997 + lane * 11);
          input[pair].state[row][stream][lane] = (int16_t)(
              NTRUPLUS1152_EXP001_PAPER_INPUT_MIN +
              value % (NTRUPLUS1152_EXP001_PAPER_INPUT_MAX -
                       NTRUPLUS1152_EXP001_PAPER_INPUT_MIN + 1));
        }
  puts("{\"benchmark_class\":\"repository-local-g1b-f1-tail-paired-not-for-promotion\","
       "\"blocks\":16,\"observations_per_slot\":96,\"records\":[");
  emit_pair("F0-to-F1-B0", "F0-D1-persistent", f0, "F1-B0-terminal-major", f1_b0);
  emit_pair("F1-B0-to-B1", "F1-B0-terminal-major", f1_b0,
            "F1-B1-fused-terminal-major", f1_b1);
  emit_pair("F0-to-F1-B1", "F0-D1-persistent", f0,
            "F1-B1-fused-terminal-major", f1_b1);
  printf("{\"comparison\":\"sink\",\"block\":0,\"slot\":0,"
         "\"implementation\":\"none\",\"median_cycles\":%" PRId16 "}]}\n", sink);
  return 0;
}
