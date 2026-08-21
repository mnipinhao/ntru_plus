#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "official_stage_partitions.h"

#define TRIALS 10003

extern void poly_ntt(int16_t value[NTRUPLUS1152_EXP001_OFFICIAL_N]);

static uint64_t state = UINT64_C(0xd00d1152c0decafe);

static int16_t random_i16(void) {
  state ^= state << 13;
  state ^= state >> 7;
  state ^= state << 17;
  return (int16_t)(state >> 16);
}

int main(void) {
  _Alignas(32) int16_t official[NTRUPLUS1152_EXP001_OFFICIAL_N];
  _Alignas(32) int16_t partitioned[NTRUPLUS1152_EXP001_OFFICIAL_N];
  _Alignas(32) int16_t combined[NTRUPLUS1152_EXP001_OFFICIAL_N];
  int index, trial;
  for (trial = 0; trial < TRIALS; ++trial) {
    for (index = 0; index < NTRUPLUS1152_EXP001_OFFICIAL_N; ++index) {
      int16_t value = trial < 3
          ? (int16_t)(((index + trial) & 7) - 3)
          : random_i16();
      official[index] = value;
      partitioned[index] = value;
      combined[index] = value;
    }
    poly_ntt(official);
    ntruplus1152_exp001_official_t0(partitioned);
    ntruplus1152_exp001_official_t3x3(partitioned);
    ntruplus1152_exp001_official_t2x4(partitioned);
    ntruplus1152_exp001_official_t0(combined);
    ntruplus1152_exp001_official_t3x3_t2x4(combined);
    if (memcmp(official, partitioned, sizeof official) != 0) {
      for (index = 0; index < NTRUPLUS1152_EXP001_OFFICIAL_N; ++index) {
        if (official[index] != partitioned[index]) {
          fprintf(stderr, "Official partition mismatch trial=%d index=%d expected=%" PRId16
                          " actual=%" PRId16 "\n",
                  trial, index, official[index], partitioned[index]);
          return 1;
        }
      }
    }
    if (memcmp(official, combined, sizeof official) != 0) {
      fprintf(stderr, "Official combined-body mismatch trial=%d\n", trial);
      return 1;
    }
  }
  puts("Official T0/T3x3/T2x4 and contiguous combined extraction: 10003 bit-exact cases passed");
  return 0;
}
