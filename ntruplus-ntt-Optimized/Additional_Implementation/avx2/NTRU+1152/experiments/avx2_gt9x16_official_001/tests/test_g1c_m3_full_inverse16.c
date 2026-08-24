#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "bench/g1c_m3_producer_common.h"
#include "g1c_bmscale_inverse_d1_asm.h"

#define TRIALS 1003
#define CANARY_WORDS 16

struct guarded_state {
  int16_t before[CANARY_WORDS];
  g1c_m3_terminal_major value;
  int16_t after[CANARY_WORDS];
};

static void fail(const char *name, int trial) {
  fprintf(stderr, "G1C-M3 full inverse16 %s failed at trial %d\n", name,
          trial);
  exit(1);
}

static void fill_canary(struct guarded_state *state) {
  int index;
  for (index = 0; index < CANARY_WORDS; ++index) {
    state->before[index] = (int16_t)(0x2510 + index);
    state->after[index] = (int16_t)(0x4a20 + index);
  }
}

static void check_canary(const struct guarded_state *state, const char *name,
                         int trial) {
  int index;
  for (index = 0; index < CANARY_WORDS; ++index)
    if (state->before[index] != (int16_t)(0x2510 + index) ||
        state->after[index] != (int16_t)(0x4a20 + index))
      fail(name, trial);
}

static void reference(g1c_m3_terminal_major *output,
                      const g1c_m3_terminal_major *a,
                      const g1c_m3_terminal_major *b) {
  int branch, coefficient, lane, row;
  g1c_m3_compute_bmscale(output, a, b);
  if (!g1c_m3_propagate_stage(output, 0)) fail("reference-D1-range", -1);
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (coefficient = 0; coefficient < 4; ++coefficient)
        for (lane = 0; lane < 16; lane += 2)
          output->state[branch][row][coefficient][lane] =
              g1c_m3_montgomery_mul(
                  output->state[branch][row][coefficient][lane],
                  g1c_m3_centered_factor(1));
  if (!g1c_m3_propagate_stage(output, 1)) fail("reference-D2-range", -1);
  if (!g1c_m3_propagate_stage(output, 2)) fail("reference-D4-range", -1);
  if (!g1c_m3_propagate_stage(output, 3)) fail("reference-D8-range", -1);
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
                    "%s mismatch trial=%d branch=%d row=%d c=%d lane=%d "
                    "expected=%d actual=%d\n",
                    name, trial, branch, row, coefficient, lane,
                    expected->state[branch][row][coefficient][lane],
                    actual->state[branch][row][coefficient][lane]);
            exit(1);
          }
}

int main(void) {
  g1c_m3_terminal_major a __attribute__((aligned(32)));
  g1c_m3_terminal_major b __attribute__((aligned(32)));
  g1c_m3_terminal_major expected __attribute__((aligned(32)));
  g1c_m3_terminal_major saved_a __attribute__((aligned(32)));
  g1c_m3_terminal_major saved_b __attribute__((aligned(32)));
  g1c_m3_terminal_major c0 __attribute__((aligned(32)));
  g1c_m3_terminal_major c1 __attribute__((aligned(32)));
  g1c_m3_terminal_major c2 __attribute__((aligned(32)));
  struct guarded_state guarded __attribute__((aligned(32)));
  int trial;

  if (g1c_m3_centered_reduce(0) != 0 || g1c_m3_absolute64(-1) != 1)
    fail("shared-oracle-smoke", -1);

  for (trial = 0; trial < TRIALS; ++trial) {
    g1c_m3_fill_case(&a, &b, trial);
    reference(&expected, &a, &b);
    ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c0(&c0, &a, &b);
    ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c1(&c1, &a, &b);
    ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2(&c2, &a, &b);
    compare("C0", &expected, &c0, trial);
    compare("C1", &expected, &c1, trial);
    compare("C2", &expected, &c2, trial);
  }

  g1c_m3_fill_case(&a, &b, 19);
  saved_a = a;
  saved_b = b;
  reference(&expected, &a, &b);
  fill_canary(&guarded);
  ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2(&guarded.value, &a, &b);
  check_canary(&guarded, "C2-canary", 19);
  compare("C2-canary-output", &expected, &guarded.value, 19);
  compare("C2-input-a-immutable", &saved_a, &a, 19);
  compare("C2-input-b-immutable", &saved_b, &b, 19);

  puts("G1C-M3 C0/C1/C2: 1003 producer-real cases, exact repair, input immutability, and canary passed");
  return 0;
}
