#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <immintrin.h>

#include "gt9x16-full-forward-tables.h"
#include "gt9x16_ntt16_asm.h"
#include "gt9x16_shear.h"

#define SAMPLES 201
#define LEAF_TRANSFORMS 2048
#define BODY_REPETITIONS 128
#define BODY_BATCHES 16

typedef void (*leaf_function)(ntruplus1152_exp001_gt_rows *,
                              const ntruplus1152_exp001_gt_rows *);

static void __attribute__((noinline)) reference_ntt16(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input) {
  const int16_t zeta8[9] = {-147, -147, -147, -147, -147, -147, -147, -147, -147};
  const int16_t qinv8[9] = {-19, -19, -19, -19, -19, -19, -19, -19, -19};
  const ntruplus1152_exp001_ntt16_row_tables tables = {
      ntruplus1152_exp001_gt_stage4_zeta,
      ntruplus1152_exp001_gt_stage4_qinv,
      ntruplus1152_exp001_gt_stage2_zeta,
      ntruplus1152_exp001_gt_stage2_qinv,
      ntruplus1152_exp001_gt_stage1_zeta,
      ntruplus1152_exp001_gt_stage1_qinv};
  ntruplus1152_exp001_gt_rows stage8;
  int row;
  ntruplus1152_exp001_gt9x16_shear_stage8(&stage8, input, zeta8, qinv8);
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    ntruplus1152_exp001_gt9x16_ntt16_finish_row(
        output->values[row], stage8.values[row], &tables);
  }
}

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

static void initialize(ntruplus1152_exp001_gt_rows *rows) {
  int lane, row;
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    for (lane = 0; lane < NTRUPLUS1152_EXP001_GT_LANES; ++lane) {
      rows->values[row][lane] = (int16_t)(row * 131 + lane * 17 - 1728);
    }
  }
}

static uint64_t measure_leaf(leaf_function function) {
  ntruplus1152_exp001_gt_rows a, b;
  uint64_t samples[SAMPLES];
  int transform, sample;
  initialize(&a);
  for (sample = 0; sample < SAMPLES; ++sample) {
    uint64_t start = cycles_start();
    for (transform = 0; transform < LEAF_TRANSFORMS; transform += 2) {
      function(&b, &a);
      function(&a, &b);
    }
    samples[sample] = cycles_stop() - start;
  }
  qsort(samples, SAMPLES, sizeof samples[0], compare_u64);
  if (a.values[sample % 9][sample % 16] == INT16_C(0x5a5a)) {
    fputs("unreachable benchmark sink\n", stderr);
  }
  return samples[SAMPLES / 2];
}

static uint64_t measure_c0_body(void) {
  ntruplus1152_exp001_gt_rows a, b;
  uint64_t samples[SAMPLES];
  int batch, sample;
  initialize(&a);
  for (sample = 0; sample < SAMPLES; ++sample) {
    uint64_t start = cycles_start();
    for (batch = 0; batch < BODY_BATCHES; batch += 2) {
      ntruplus1152_exp001_gt9x16_ntt16_c0_repeat(&b, &a, BODY_REPETITIONS);
      ntruplus1152_exp001_gt9x16_ntt16_c0_repeat(&a, &b, BODY_REPETITIONS);
    }
    samples[sample] = cycles_stop() - start;
  }
  qsort(samples, SAMPLES, sizeof samples[0], compare_u64);
  if (a.values[sample % 9][sample % 16] == INT16_C(0x5a5a)) {
    fputs("unreachable benchmark sink\n", stderr);
  }
  return samples[SAMPLES / 2];
}

static void print_result(const char *name, uint64_t cycles, int transforms) {
  printf("  \"%s\": {\"batch_cycles_median\": %" PRIu64
         ", \"transforms_per_batch\": %d, \"cycles_per_transform\": %.3f}",
         name, cycles, transforms, (double)cycles / transforms);
}

int main(void) {
  const uint64_t reference = measure_leaf(reference_ntt16);
  const uint64_t c0_leaf = measure_leaf(ntruplus1152_exp001_gt9x16_ntt16_c0);
  const uint64_t c0_body = measure_c0_body();
  const uint64_t c1_leaf = measure_leaf(ntruplus1152_exp001_gt9x16_ntt16_c1);
  puts("{");
  puts("  \"benchmark_class\": \"repository-local-diagnostic-not-for-promotion\",");
  printf("  \"samples\": %d,\n", SAMPLES);
  print_result("c_reference", reference, LEAF_TRANSFORMS);
  puts(",");
  print_result("c0_leaf_load_store", c0_leaf, LEAF_TRANSFORMS);
  puts(",");
  print_result("c0_arithmetic_body", c0_body, BODY_REPETITIONS * BODY_BATCHES);
  puts(",");
  print_result("c1_split_leaf_load_store", c1_leaf, LEAF_TRANSFORMS);
  puts("\n}");
  return 0;
}
