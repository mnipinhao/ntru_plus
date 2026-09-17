#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 1152
#define Q 3457
#define GUARD 8

void ntruplus1152_exp001_top_split_small(int16_t out[N], const int16_t in[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(
    int16_t state[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce_w1(
    int16_t state[N]);

static uint64_t rng_state = UINT64_C(0x57314e5454395831);

static uint32_t rnd(void) {
  uint64_t x = rng_state;
  x ^= x << 13;
  x ^= x >> 7;
  x ^= x << 17;
  rng_state = x;
  return (uint32_t)(x >> 16);
}

static int canonical(int value) {
  value %= Q;
  return value < 0 ? value + Q : value;
}

static int run_case(const int16_t input[N], int case_index) {
  _Alignas(32) int16_t control_backing[N + 2 * GUARD + 16];
  _Alignas(32) int16_t candidate_backing[N + 2 * GUARD + 16];
  int16_t *control = control_backing + GUARD;
  int16_t *candidate = candidate_backing + GUARD;
  int i;

  for (i = 0; i < N + 2 * GUARD + 16; ++i) {
    control_backing[i] = (int16_t)0x5a5a;
    candidate_backing[i] = (int16_t)0x5a5a;
  }
  ntruplus1152_exp001_top_split_small(control, input);
  memcpy(candidate, control, N * sizeof *control);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(control);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce_w1(candidate);

  for (i = 0; i < N; ++i) {
    if (control[i] != candidate[i]) {
      fprintf(stderr,
              "W1 raw mismatch case=%d cell=%d control=%d candidate=%d residues=%d/%d\n",
              case_index, i, control[i], candidate[i],
              canonical(control[i]), canonical(candidate[i]));
      return 1;
    }
    if (candidate[i] < -21469 || candidate[i] > 21469) {
      fprintf(stderr, "W1 range case=%d cell=%d value=%d\n",
              case_index, i, candidate[i]);
      return 1;
    }
  }
  for (i = 0; i < GUARD; ++i) {
    if (control_backing[i] != (int16_t)0x5a5a ||
        candidate_backing[i] != (int16_t)0x5a5a ||
        control_backing[N + GUARD + i] != (int16_t)0x5a5a ||
        candidate_backing[N + GUARD + i] != (int16_t)0x5a5a) {
      fprintf(stderr, "W1 canary case=%d guard=%d\n", case_index, i);
      return 1;
    }
  }
  return 0;
}

int main(void) {
  _Alignas(32) int16_t input[N];
  int trial, i;

  memset(input, 0, sizeof input);
  if (run_case(input, 0)) return 1;
  for (i = 0; i < N; ++i) input[i] = (i & 1) ? 1 : -1;
  if (run_case(input, 1)) return 1;
  for (trial = 0; trial < 1003; ++trial) {
    for (i = 0; i < N; ++i) input[i] = (int16_t)((int)(rnd() % 3) - 1);
    if (run_case(input, trial + 2)) return 1;
  }
  for (i = 0; i < N; ++i) {
    memset(input, 0, sizeof input);
    input[i] = 1;
    if (run_case(input, 1005 + 2 * i)) return 1;
    input[i] = -1;
    if (run_case(input, 1006 + 2 * i)) return 1;
  }
  puts("NTT9 wavefront W1: raw/range/canary differential passed");
  return 0;
}
