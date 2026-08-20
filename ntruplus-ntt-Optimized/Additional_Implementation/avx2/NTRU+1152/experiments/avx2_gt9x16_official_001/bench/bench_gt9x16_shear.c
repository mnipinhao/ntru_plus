#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <immintrin.h>

#include "gt9x16_oracle.h"
#include "gt9x16_shear.h"
#include "gt9x16-stage8-tables.h"

#define SAMPLES 201
#define CALLS_PER_SAMPLE 2000

typedef void (*shear_function)(ntruplus1152_exp001_gt_rows *,
                               const ntruplus1152_exp001_gt_rows *);

static void fused_stage8_branch0(ntruplus1152_exp001_gt_rows *output,
                                 const ntruplus1152_exp001_gt_rows *input) {
  ntruplus1152_exp001_gt9x16_shear_stage8(
      output, input, ntruplus1152_exp001_stage8_zeta[0],
      ntruplus1152_exp001_stage8_qinv[0]);
}

static void fused_stage8_branch1(ntruplus1152_exp001_gt_rows *output,
                                 const ntruplus1152_exp001_gt_rows *input) {
  ntruplus1152_exp001_gt9x16_shear_stage8(
      output, input, ntruplus1152_exp001_stage8_zeta[1],
      ntruplus1152_exp001_stage8_qinv[1]);
}

static void full_ntt16(ntruplus1152_exp001_gt_rows *output,
                       const ntruplus1152_exp001_gt_rows *input, int branch) {
  ntruplus1152_exp001_gt_rows stage8;
  int row;
  ntruplus1152_exp001_gt9x16_shear_stage8(
      &stage8, input, ntruplus1152_exp001_stage8_zeta[branch],
      ntruplus1152_exp001_stage8_qinv[branch]);
  for (row = 0; row < 9; ++row) {
    ntruplus1152_exp001_ntt16_row_tables tables = {
        ntruplus1152_exp001_stage4_zeta[branch][row],
        ntruplus1152_exp001_stage4_qinv[branch][row],
        ntruplus1152_exp001_stage2_zeta[branch][row],
        ntruplus1152_exp001_stage2_qinv[branch][row],
        ntruplus1152_exp001_stage1_zeta[branch][row],
        ntruplus1152_exp001_stage1_qinv[branch][row]};
    ntruplus1152_exp001_gt9x16_ntt16_finish_row(
        output->values[row], stage8.values[row], &tables);
  }
}

static void full_ntt16_branch0(ntruplus1152_exp001_gt_rows *output,
                               const ntruplus1152_exp001_gt_rows *input) {
  full_ntt16(output, input, 0);
}

static void full_ntt16_branch1(ntruplus1152_exp001_gt_rows *output,
                               const ntruplus1152_exp001_gt_rows *input) {
  full_ntt16(output, input, 1);
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

static uint64_t measure(shear_function function) {
  ntruplus1152_exp001_gt_rows a, b;
  uint64_t samples[SAMPLES];
  int call, lane, row, sample;
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    for (lane = 0; lane < NTRUPLUS1152_EXP001_GT_LANES; ++lane) {
      a.values[row][lane] = (int16_t)(row * 131 + lane * 17 - 1728);
    }
  }
  for (sample = 0; sample < SAMPLES; ++sample) {
    uint64_t start = cycles_start();
    for (call = 0; call < CALLS_PER_SAMPLE; call += 2) {
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

static void print_result(const char *name, uint64_t cycles) {
  printf("  \"%s\": {\"batch_cycles_median\": %" PRIu64
         ", \"calls_per_batch\": %d, \"cycles_per_call\": %.3f}",
         name, cycles, CALLS_PER_SAMPLE, (double)cycles / CALLS_PER_SAMPLE);
}

int main(void) {
  uint64_t oracle = measure(ntruplus1152_exp001_gt9x16_oracle_y);
  uint64_t shear = measure(ntruplus1152_exp001_gt9x16_shear_z);
  uint64_t materialized = measure(ntruplus1152_exp001_gt9x16_shear_materialized);
  uint64_t stage8_branch0 = measure(fused_stage8_branch0);
  uint64_t stage8_branch1 = measure(fused_stage8_branch1);
  uint64_t ntt16_branch0 = measure(full_ntt16_branch0);
  uint64_t ntt16_branch1 = measure(full_ntt16_branch1);
  puts("{");
  puts("  \"benchmark_class\": \"repository-local-diagnostic\",");
  printf("  \"samples\": %d,\n", SAMPLES);
  print_result("scalar_materialized_y", oracle);
  puts(",");
  print_result("avx2_27_blend_z", shear);
  puts(",");
  print_result("avx2_materialized_y", materialized);
  puts(",");
  print_result("avx2_27_blend_fused_stage8_branch0", stage8_branch0);
  puts(",");
  print_result("avx2_27_blend_fused_stage8_branch1", stage8_branch1);
  puts(",");
  print_result("avx2_27_blend_full_ntt16_branch0", ntt16_branch0);
  puts(",");
  print_result("avx2_27_blend_full_ntt16_branch1", ntt16_branch1);
  puts("\n}");
  return 0;
}
