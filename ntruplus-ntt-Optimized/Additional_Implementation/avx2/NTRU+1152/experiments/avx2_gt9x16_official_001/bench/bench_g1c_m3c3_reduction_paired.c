#include <immintrin.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "g1c_m3c3_reduction.h"

#define BLOCKS 16
#define OBSERVATIONS 96
#define INNER 64
#define VALUES NTRUPLUS1152_EXP001_M3C3_VALUES

typedef void (*reducer)(int16_t *, const int16_t *);

static _Alignas(32) int16_t input[VALUES];
static _Alignas(32) int16_t output[VALUES];
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

static uint64_t measure(reducer selected) {
  uint64_t samples[OBSERVATIONS];
  int observation;
  for (observation = 0; observation < OBSERVATIONS; ++observation) {
    uint64_t begin = cycles_start();
    int iteration;
    for (iteration = 0; iteration < INNER; ++iteration)
      selected(output, input);
    samples[observation] = (cycles_stop() - begin + INNER / 2) / INNER;
    sink ^= output[(observation * 17) % VALUES];
  }
  qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
  return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

int main(void) {
  static const int odd[4] = {0, 1, 1, 0};
  static const int even[4] = {1, 0, 0, 1};
  reducer implementations[2] = {
      ntruplus1152_exp001_g1c_m3c3_reduce_barrett,
      ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity};
  const char *names[2] = {"signed-Barrett", "Montgomery-identity"};
  int block, index, slot;
  for (index = 0; index < VALUES; ++index)
    input[index] = (int16_t)(index * 4051u + 0x8123u);
  implementations[0](output, input);
  implementations[1](output, input);
  puts("{\"benchmark_class\":\"repository-local-g1c-m3c3-reduction-paired-not-for-promotion\","
       "\"blocks\":16,\"observations_per_slot\":96,\"inner_calls\":64,\"records\":[");
  for (block = 0; block < BLOCKS; ++block) {
    const int *order = (block & 1) == 0 ? odd : even;
    for (slot = 0; slot < 4; ++slot) {
      int selected = order[slot];
      printf("{\"comparison\":\"full-D4-reduction\",\"block\":%d,\"slot\":%d,"
             "\"implementation\":\"%s\",\"median_cycles\":%" PRIu64 "},\n",
             block + 1, slot + 1, names[selected],
             measure(implementations[selected]));
    }
  }
  printf("{\"comparison\":\"sink\",\"block\":0,\"slot\":0,"
         "\"implementation\":\"none\",\"median_cycles\":%" PRId16 "}]}\n",
         sink);
  return 0;
}
