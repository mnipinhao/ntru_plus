#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <immintrin.h>

#include "g1c_bmscale_inverse_d1_asm.h"
#include "gt9x16-ntt9-paper-range.h"
#include "inverse_ntt9_reference.h"

#define BLOCKS 16
#define OBSERVATIONS 96
#define PAIRS 4

typedef void (*operation)(void);

static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair producer_a[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair producer_b[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair producer_scratch[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_terminal_major operand_a;
static _Alignas(32) ntruplus1152_exp001_gt_terminal_major operand_b;
static _Alignas(32) ntruplus1152_exp001_gt_terminal_major inverse16_output;
static _Alignas(32) ntruplus1152_exp001_gt_terminal_major output;
static _Alignas(32) ntruplus1152_exp001_inverse9_canonical_p canonical;
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

static void canonical_control(void) {
  ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2(
      &inverse16_output, &operand_a, &operand_b);
  ntruplus1152_exp001_inverse9_repack_canonical_p(&canonical,
                                                   &inverse16_output);
  ntruplus1152_exp001_inverse_ntt9_r2_from_canonical_p(&output, &canonical);
}

static void direct_physical_p(void) {
  ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2(
      &inverse16_output, &operand_a, &operand_b);
  ntruplus1152_exp001_inverse_ntt9_r2_direct(&output, &inverse16_output);
}

static uint64_t measure(operation selected) {
  uint64_t samples[OBSERVATIONS];
  int observation;
  for (observation = 0; observation < OBSERVATIONS; ++observation) {
    uint64_t begin = cycles_start();
    selected();
    samples[observation] = cycles_stop() - begin;
    sink ^= output.state[(observation >> 1) & 1][observation % 9]
                        [observation & 3][observation & 15];
  }
  qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
  return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

static void initialize_operand(
    ntruplus1152_exp001_gt_terminal_major *selected,
    ntruplus1152_exp001_gt_persistent_pair producer[PAIRS], int salt) {
  int lane, pair, row, stream;
  for (pair = 0; pair < PAIRS; ++pair)
    for (row = 0; row < 9; ++row)
      for (stream = 0; stream < 2; ++stream)
        for (lane = 0; lane < 16; ++lane) {
          unsigned value = (unsigned)(salt * 619 + pair * 271 + row * 43 +
                                      stream * 997 + lane * 11);
          producer[pair].state[row][stream][lane] = (int16_t)(
              NTRUPLUS1152_EXP001_PAPER_INPUT_MIN +
              value % (NTRUPLUS1152_EXP001_PAPER_INPUT_MAX -
                       NTRUPLUS1152_EXP001_PAPER_INPUT_MIN + 1));
        }
  for (pair = 0; pair < PAIRS; ++pair) {
    int branch = pair / 2;
    int terminal_pair = pair % 2;
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b1(
        &producer_scratch[pair], &producer[pair],
        &selected->state[branch][0][2 * terminal_pair][0]);
  }
}

int main(void) {
  static const int odd[4] = {0, 1, 1, 0};
  static const int even[4] = {1, 0, 0, 1};
  static operation operations[2] = {canonical_control, direct_physical_p};
  static const char *names[2] = {"A-canonical-repack-reference-inverse9",
                                 "B-direct-paper-p-reference-inverse9"};
  int block, slot;
  initialize_operand(&operand_a, producer_a, 1);
  initialize_operand(&operand_b, producer_b, 2);
  canonical_control();
  direct_physical_p();
  puts("{\"benchmark_class\":\"repository-local-inverse-tail-reference-paired-not-for-promotion\","
       "\"blocks\":16,\"observations_per_slot\":96,\"records\":[");
  for (block = 0; block < BLOCKS; ++block) {
    const int *order = (block & 1) == 0 ? odd : even;
    for (slot = 0; slot < 4; ++slot) {
      int selected = order[slot];
      printf("{\"block\":%d,\"slot\":%d,\"implementation\":\"%s\","
             "\"median_cycles\":%" PRIu64 "},\n",
             block + 1, slot + 1, names[selected],
             measure(operations[selected]));
    }
  }
  printf("{\"block\":0,\"slot\":0,\"implementation\":\"sink\","
         "\"median_cycles\":%" PRId16 "}]}\n",
         sink);
  return 0;
}
