#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "f0-ma0-adapter.h"
#include "f0-official-to-f0.h"
#define N 1152
static uint32_t state = 0x4f324630U;
static uint32_t random32(void) { state ^= state<<13; state ^= state>>17; state ^= state<<5; return state; }
int main(void) {
  _Alignas(32) int16_t official[N], f0[N], roundtrip[N];
  int trial, i;
  for (trial = 0; trial < 1003; ++trial) {
    for (i = 0; i < N; ++i)
      official[i] = trial == 0 ? 0 : trial == 1 ? (int16_t)i : (int16_t)random32();
    ntruplus1152_exp001_official_to_f0(f0, official);
    ntruplus1152_exp001_f0_ma0_to_official(roundtrip, f0);
    for (i = 0; i < N; ++i)
      if (roundtrip[i] != (int16_t)(4U * (uint16_t)official[i])) {
        fprintf(stderr, "Official/F0 scaled inverse mismatch trial=%d index=%d\n", trial, i);
        return 1;
      }
  }
  puts("Official->scale4-F0->Official: 1003 exact representation cases passed");
  return 0;
}
