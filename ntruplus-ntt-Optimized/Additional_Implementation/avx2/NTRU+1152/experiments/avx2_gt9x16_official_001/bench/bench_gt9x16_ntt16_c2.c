#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>
#include "gt9x16_ntt16_asm.h"

#define SAMPLES 201
#define PAIRS_PER_SAMPLE 1024

typedef void (*pair_function)(ntruplus1152_exp001_gt_row_pair *,
                              const ntruplus1152_exp001_gt_row_pair *);

static uint64_t start_cycles(void) { unsigned int a; _mm_lfence(); return __rdtscp(&a); }
static uint64_t stop_cycles(void) { unsigned int a; uint64_t v = __rdtscp(&a); _mm_lfence(); return v; }
static int compare_u64(const void *a, const void *b) {
  uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
  return (x > y) - (x < y);
}

static uint64_t measure(pair_function function) {
  ntruplus1152_exp001_gt_row_pair a, b;
  uint64_t samples[SAMPLES];
  int coefficient, lane, pair, row, sample;
  for (coefficient = 0; coefficient < 2; ++coefficient)
    for (row = 0; row < 9; ++row)
      for (lane = 0; lane < 16; ++lane)
        a.coefficient[coefficient].values[row][lane] =
            (int16_t)(coefficient * 997 + row * 131 + lane * 17 - 1728);
  for (sample = 0; sample < SAMPLES; ++sample) {
    uint64_t start = start_cycles();
    for (pair = 0; pair < PAIRS_PER_SAMPLE; pair += 2) {
      function(&b, &a);
      function(&a, &b);
    }
    samples[sample] = stop_cycles() - start;
  }
  qsort(samples, SAMPLES, sizeof samples[0], compare_u64);
  if (a.coefficient[sample & 1].values[sample % 9][sample % 16] == INT16_C(0x5a5a))
    fputs("unreachable benchmark sink\n", stderr);
  return samples[SAMPLES / 2];
}

static void print_result(const char *name, uint64_t cycles) {
  printf("  \"%s\": {\"batch_cycles_median\": %" PRIu64
         ", \"pairs_per_batch\": %d, \"cycles_per_two_islands\": %.3f}",
         name, cycles, PAIRS_PER_SAMPLE, (double)cycles / PAIRS_PER_SAMPLE);
}

int main(void) {
  uint64_t d8_c0 = measure(ntruplus1152_exp001_gt9x16_stage8_c0_pair);
  uint64_t d8_c2 = measure(ntruplus1152_exp001_gt9x16_stage8_c2_pair);
  uint64_t full_c0 = measure(ntruplus1152_exp001_gt9x16_ntt16_c0_pair);
  uint64_t full_c2 = measure(ntruplus1152_exp001_gt9x16_ntt16_c2_pair);
  puts("{");
  puts("  \"benchmark_class\": \"repository-local-diagnostic-not-for-promotion\",");
  printf("  \"samples\": %d,\n", SAMPLES);
  print_result("distance8_c0_two_islands", d8_c0); puts(",");
  print_result("distance8_c2_pair_packed", d8_c2); puts(",");
  print_result("full_ntt16_c0_two_islands", full_c0); puts(",");
  print_result("full_ntt16_c2_pair_packed", full_c2); puts("\n}");
  return 0;
}
