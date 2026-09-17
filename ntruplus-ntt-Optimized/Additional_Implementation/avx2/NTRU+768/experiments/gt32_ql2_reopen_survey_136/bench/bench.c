#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "cpucycles.h"

#define N 768
#define SAMPLES 31
#define ITERS 2048

void gt135_basemul_general_ql2_native_e0(int16_t *, const int16_t *, const int16_t *);
void gt136_basemul_general_ql2_native_em1(int16_t *, const int16_t *, const int16_t *);
static _Alignas(64) int16_t a[N], b[N], out[N];
static volatile uint64_t sink;
static uint64_t state = 136;
static uint32_t rnd(void) { state ^= state << 13; state ^= state >> 7; state ^= state << 17; return (uint32_t)state; }
static int cmp(const void *x, const void *y) { double a = *(const double *)x, b = *(const double *)y; return (a > b) - (a < b); }
static double median(double *x) { qsort(x, SAMPLES, sizeof(*x), cmp); return x[SAMPLES / 2]; }

int main(int argc, char **argv) {
  int flip = argc > 1 ? atoi(argv[1]) : 0;
  cpu_set_t set; CPU_ZERO(&set); CPU_SET(1, &set); sched_setaffinity(0, sizeof(set), &set);
  for (int i = 0; i < N; i++) { a[i] = (int16_t)((int)(rnd() % 3457) - 1728); b[i] = (int16_t)((int)(rnd() % 3457) - 1728); }
  double e0[SAMPLES], em1[SAMPLES];
  for (int s = 0; s < SAMPLES; s++) {
    int first = (s + flip) & 1;
    for (int side = 0; side < 2; side++) {
      int natural = first ? 1 - side : side;
      uint64_t x = cpucycles();
      for (int z = 0; z < ITERS; z++) {
        if (natural) gt136_basemul_general_ql2_native_em1(out, a, b);
        else gt135_basemul_general_ql2_native_e0(out, a, b);
        sink += (uint16_t)out[z % N];
      }
      uint64_t y = cpucycles();
      (natural ? em1 : e0)[s] = (double)(y - x) / ITERS;
    }
  }
  double x = median(e0), y = median(em1);
  printf("{\"e0\":%.6f,\"em1\":%.6f,\"em1_minus_e0\":%.6f,\"sink\":%llu}\n", x, y, y - x, (unsigned long long)sink);
  return 0;
}
