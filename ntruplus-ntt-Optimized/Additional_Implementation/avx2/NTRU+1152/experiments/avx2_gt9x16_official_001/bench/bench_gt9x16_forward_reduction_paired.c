#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <immintrin.h>

#include "gt9x16_forward.h"

#define N 1152
#define BLOCKS 16
#define OBSERVATIONS 96

typedef void (*forward_fn)(int16_t *);

void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_lazy_reduce(
    int16_t *);

static _Alignas(32) int16_t template_state[2][N];
static _Alignas(32) int16_t timed_state[2][N];
static volatile int16_t sink;

static uint64_t stamp(void) {
  unsigned int auxiliary;
  _mm_lfence();
  return __rdtscp(&auxiliary);
}

static int compare_u64(const void *left, const void *right) {
  uint64_t a = *(const uint64_t *)left;
  uint64_t b = *(const uint64_t *)right;
  return (a > b) - (a < b);
}

static uint64_t measure(forward_fn selected, int width) {
  uint64_t samples[OBSERVATIONS];
  int observation, operand;
  for (observation = 0; observation < OBSERVATIONS; ++observation) {
    memcpy(timed_state, template_state, sizeof timed_state);
    uint64_t begin = stamp();
    for (operand = 0; operand < width; ++operand) selected(timed_state[operand]);
    samples[observation] = stamp() - begin;
    sink ^= timed_state[observation & 1][observation % N];
  }
  qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
  return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

int main(void) {
  static const int odd[4] = {0, 1, 1, 0};
  static const int even[4] = {1, 0, 0, 1};
  _Alignas(32) int16_t coefficient[N];
  int block, index, operand, slot, width;
  for (operand = 0; operand < 2; ++operand) {
    for (index = 0; index < N; ++index)
      coefficient[index] = (int16_t)(((index * 17 + operand * 13) % 3) - 1);
    ntruplus1152_exp001_top_split_small(template_state[operand], coefficient);
  }
  puts("{\"benchmark_class\":\"repository-local-forward-reduction-paired-not-for-promotion\",\"records\":[");
  for (width = 1; width <= 2; ++width)
    for (block = 0; block < BLOCKS; ++block) {
      const int *order = (block & 1) ? even : odd;
      for (slot = 0; slot < 4; ++slot) {
        int candidate = order[slot];
        printf("{\"width\":%d,\"block\":%d,\"slot\":%d,\"implementation\":\"%s\",\"median_cycles\":%" PRIu64 "},\n",
               width, block + 1, slot + 1,
               candidate ? "lazy-40" : "control-72",
               measure(candidate ?
                   ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_lazy_reduce :
                   ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta,
                   width));
      }
    }
  printf("{\"width\":0,\"block\":0,\"slot\":0,\"implementation\":\"sink\",\"median_cycles\":%d}]}\n",
         sink);
  return 0;
}
