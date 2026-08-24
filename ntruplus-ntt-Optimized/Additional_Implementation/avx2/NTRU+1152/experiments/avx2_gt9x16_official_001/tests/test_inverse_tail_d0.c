#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "bench/g1c_m3_producer_common.h"
#include "g1c_bmscale_inverse_d1_asm.h"
#include "inverse_ntt9_b1_asm.h"
#include "inverse_tail_d0_asm.h"

#define TRIALS 1003
#define CANARY_WORDS 16

struct guarded_state {
  int16_t before[CANARY_WORDS];
  g1c_m3_terminal_major value;
  int16_t after[CANARY_WORDS];
};

static void fail(const char *name, int trial) {
  fprintf(stderr, "ITAIL-D0 %s failed at trial %d\n", name, trial);
  exit(1);
}

static void compare(const char *name, const g1c_m3_terminal_major *expected,
                    const g1c_m3_terminal_major *actual, int trial) {
  int branch, coefficient, lane, row;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (coefficient = 0; coefficient < 4; ++coefficient)
        for (lane = 0; lane < 16; ++lane)
          if (expected->state[branch][row][coefficient][lane] !=
              actual->state[branch][row][coefficient][lane]) {
            fprintf(stderr,
                    "%s mismatch trial=%d branch=%d row=%d j=%d lane=%d "
                    "expected=%d actual=%d\n",
                    name, trial, branch, row, coefficient, lane,
                    expected->state[branch][row][coefficient][lane],
                    actual->state[branch][row][coefficient][lane]);
            exit(1);
          }
}

static void fill_canary(struct guarded_state *state) {
  int index;
  for (index = 0; index < CANARY_WORDS; ++index) {
    state->before[index] = (int16_t)(0x2610 + index);
    state->after[index] = (int16_t)(0x4b20 + index);
  }
}

static void check_canary(const struct guarded_state *state) {
  int index;
  for (index = 0; index < CANARY_WORDS; ++index)
    if (state->before[index] != (int16_t)(0x2610 + index) ||
        state->after[index] != (int16_t)(0x4b20 + index))
      fail("canary", -1);
}

static void produce_repaired_d1(g1c_m3_terminal_major *output,
                                const g1c_m3_terminal_major *a,
                                const g1c_m3_terminal_major *b) {
  int branch, coefficient, lane, row;
  g1c_m3_compute_bmscale(output, a, b);
  if (!g1c_m3_propagate_stage(output, 0)) fail("producer-D1-range", -1);
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (coefficient = 0; coefficient < 4; ++coefficient)
        for (lane = 0; lane < 16; lane += 2)
          output->state[branch][row][coefficient][lane] =
              g1c_m3_montgomery_mul(
                  output->state[branch][row][coefficient][lane],
                  g1c_m3_centered_factor(1));
}

int main(void) {
  g1c_m3_terminal_major a __attribute__((aligned(32)));
  g1c_m3_terminal_major b __attribute__((aligned(32)));
  g1c_m3_terminal_major repaired_d1 __attribute__((aligned(32)));
  g1c_m3_terminal_major saved_d1 __attribute__((aligned(32)));
  g1c_m3_terminal_major inverse16 __attribute__((aligned(32)));
  g1c_m3_terminal_major expected __attribute__((aligned(32)));
  g1c_m3_terminal_major m0 __attribute__((aligned(32)));
  g1c_m3_terminal_major m1 __attribute__((aligned(32)));
  g1c_m3_terminal_major alias __attribute__((aligned(32)));
  struct guarded_state guarded __attribute__((aligned(32)));
  int trial;

  /* Keep every shared scalar-oracle helper warning-clean under -Werror. */
  (void)g1c_m3_centered_reduce(0);
  (void)g1c_m3_absolute64(-1);

  for (trial = 0; trial < TRIALS; ++trial) {
    g1c_m3_fill_case(&a, &b, trial);
    produce_repaired_d1(&repaired_d1, &a, &b);
    saved_d1 = repaired_d1;
    ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2(
        &inverse16, &a, &b);
    ntruplus1152_exp001_inverse_ntt9_b1(&expected, &inverse16);
    ntruplus1152_exp001_inverse_tail_d0_m0(&m0, &repaired_d1);
    ntruplus1152_exp001_inverse_tail_d0_m1(&m1, &repaired_d1);
    compare("M0-control", &expected, &m0, trial);
    compare("M1-linked", &expected, &m1, trial);
    compare("M1-vs-M0", &m0, &m1, trial);
    compare("input-immutable", &saved_d1, &repaired_d1, trial);

    alias = repaired_d1;
    ntruplus1152_exp001_inverse_tail_d0_m0(&alias, &alias);
    compare("M0-in-place", &expected, &alias, trial);
    alias = repaired_d1;
    ntruplus1152_exp001_inverse_tail_d0_m1(&alias, &alias);
    compare("M1-in-place", &expected, &alias, trial);
  }

  g1c_m3_fill_case(&a, &b, 23);
  produce_repaired_d1(&repaired_d1, &a, &b);
  ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2(
      &inverse16, &a, &b);
  ntruplus1152_exp001_inverse_ntt9_b1(&expected, &inverse16);
  fill_canary(&guarded);
  ntruplus1152_exp001_inverse_tail_d0_m1(&guarded.value, &repaired_d1);
  compare("M1-canary-output", &expected, &guarded.value, 23);
  check_canary(&guarded);

  puts("ITAIL-D0 M0/M1: 1003 producer-real cases, exact C2+B1 DAG, alias, immutability, range, and canary passed");
  return 0;
}
