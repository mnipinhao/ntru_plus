#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <immintrin.h>

#include "gt9x16_ntt16_asm.h"
#include "official_stage_partitions.h"

#define BLOCKS 16
#define OBSERVATIONS 96
#define PAIRS 4

extern void poly_ntt(int16_t value[NTRUPLUS1152_EXP001_OFFICIAL_N]);

typedef void (*operation)(void);

static _Alignas(32) int16_t natural[NTRUPLUS1152_EXP001_OFFICIAL_N];
static _Alignas(32) int16_t after_t0[NTRUPLUS1152_EXP001_OFFICIAL_N];
static _Alignas(32) int16_t after_t3x3[NTRUPLUS1152_EXP001_OFFICIAL_N];
static _Alignas(32) int16_t work[NTRUPLUS1152_EXP001_OFFICIAL_N];
static _Alignas(32) ntruplus1152_exp001_gt_row_pair gt_natural[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_row_pair gt_from_z[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair persistent[PAIRS];
static _Alignas(32) ntruplus1152_exp001_gt_persistent_pair gt_output[PAIRS];
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

static void official_full(void) {
  poly_ntt(work);
}

static void official_t0(void) {
  ntruplus1152_exp001_official_t0(work);
}

static void official_t3x3(void) {
  ntruplus1152_exp001_official_t3x3(work);
}

static void official_t2x4(void) {
  ntruplus1152_exp001_official_t2x4(work);
}

static void gt_t3x3(void) {
  int pair;
  for (pair = 0; pair < PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_ntt9_d_a(&gt_output[pair], &persistent[pair]);
}

static void gt_t2x4_from_z(void) {
  int pair;
  for (pair = 0; pair < PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined(
        &gt_output[pair], &gt_from_z[pair]);
}

static void gt_t2x4_natural(void) {
  int pair;
  for (pair = 0; pair < PAIRS; ++pair)
    ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear(
        &gt_output[pair], &gt_natural[pair]);
}

static void prepare_natural(void) { memcpy(work, natural, sizeof work); }
static void prepare_t3x3(void) { memcpy(work, after_t0, sizeof work); }
static void prepare_t2x4(void) { memcpy(work, after_t3x3, sizeof work); }
static void prepare_none(void) {}

static uint64_t measure(operation selected, operation prepare) {
  uint64_t samples[OBSERVATIONS];
  int observation;
  for (observation = 0; observation < OBSERVATIONS; ++observation) {
    prepare();
    uint64_t begin = cycles_start();
    selected();
    samples[observation] = cycles_stop() - begin;
    sink ^= work[(observation * 17) % NTRUPLUS1152_EXP001_OFFICIAL_N];
    sink ^= gt_output[observation % PAIRS].state[observation % 9]
                     [observation & 1][observation & 15];
  }
  qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
  return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

static void emit_pair(const char *partition, const char *left_name,
                      operation left, operation left_prepare,
                      const char *right_name, operation right,
                      operation right_prepare) {
  static const int odd[4] = {0, 1, 1, 0};
  static const int even[4] = {1, 0, 0, 1};
  int block, slot;
  for (block = 0; block < BLOCKS; ++block) {
    const int *order = (block & 1) == 0 ? odd : even;
    for (slot = 0; slot < 4; ++slot) {
      int choose_right = order[slot];
      printf("{\"partition\":\"%s\",\"block\":%d,\"slot\":%d,"
             "\"implementation\":\"%s\",\"median_cycles\":%" PRIu64 "},\n",
             partition, block + 1, slot + 1,
             choose_right ? right_name : left_name,
             measure(choose_right ? right : left,
                     choose_right ? right_prepare : left_prepare));
    }
  }
}

int main(void) {
  int coefficient, index, lane, pair, row;
  for (index = 0; index < NTRUPLUS1152_EXP001_OFFICIAL_N; ++index)
    natural[index] = (int16_t)(((index * 5 + 3) & 7) - 3);
  memcpy(after_t0, natural, sizeof after_t0);
  ntruplus1152_exp001_official_t0(after_t0);
  memcpy(after_t3x3, after_t0, sizeof after_t3x3);
  ntruplus1152_exp001_official_t3x3(after_t3x3);
  for (pair = 0; pair < PAIRS; ++pair) {
    for (coefficient = 0; coefficient < 2; ++coefficient) {
      for (row = 0; row < 9; ++row) {
        for (lane = 0; lane < 16; ++lane) {
          int16_t value = (int16_t)(pair * 271 + coefficient * 997 + row * 43 + lane * 11 - 1728);
          gt_natural[pair].coefficient[coefficient].values[row][lane] = value;
          gt_from_z[pair].coefficient[coefficient].values[row][lane] = value;
          persistent[pair].state[row][coefficient][lane] = value;
        }
      }
    }
  }
  puts("{\"benchmark_class\":\"repository-local-official-stage-paired-not-for-promotion\","
       "\"blocks\":16,\"observations_per_slot\":96,\"records\":[");
  emit_pair("T3x3", "official", official_t3x3, prepare_t3x3,
            "gt-d-a", gt_t3x3, prepare_none);
  emit_pair("T2x4", "official", official_t2x4, prepare_t2x4,
            "gt-c4-from-z", gt_t2x4_from_z, prepare_none);
  emit_pair("T2x4-natural", "official", official_t2x4, prepare_t2x4,
            "gt-c4-natural", gt_t2x4_natural, prepare_none);
  printf("{\"partition\":\"T0\",\"block\":0,\"slot\":0,\"implementation\":\"official\","
         "\"median_cycles\":%" PRIu64 "},\n", measure(official_t0, prepare_natural));
  printf("{\"partition\":\"full\",\"block\":0,\"slot\":0,\"implementation\":\"official\","
         "\"median_cycles\":%" PRIu64 "}],\"sink\":%" PRId16 "}\n",
         measure(official_full, prepare_natural), sink);
  return 0;
}
