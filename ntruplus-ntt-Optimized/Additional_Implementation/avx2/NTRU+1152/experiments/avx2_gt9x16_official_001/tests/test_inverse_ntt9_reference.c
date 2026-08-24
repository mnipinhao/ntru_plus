#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "bench/g1c_m3_producer_common.h"
#include "g1c-inverse-tail-map.h"
#include "g1c_bmscale_inverse_d1_asm.h"
#include "inverse_ntt9_reference.h"
#include "inverse_ntt9_b0_asm.h"
#include "inverse_ntt9_b1_asm.h"

#define ARBITRARY_TRIALS 1003
#define PRODUCER_TRIALS 257
#define CANARY_WORDS 16

struct guarded_output {
  int16_t before[CANARY_WORDS];
  ntruplus1152_exp001_gt_terminal_major value;
  int16_t after[CANARY_WORDS];
};

static void fail(const char *name, int trial) {
  fprintf(stderr, "inverse NTT9 reference %s failed at trial %d\n", name,
          trial);
  exit(1);
}

static int16_t centered(int64_t value) {
  int64_t reduced = value % NTRUPLUS1152_EXP001_INVERSE_TAIL_Q;
  if (reduced > NTRUPLUS1152_EXP001_INVERSE_TAIL_Q / 2)
    reduced -= NTRUPLUS1152_EXP001_INVERSE_TAIL_Q;
  if (reduced < -NTRUPLUS1152_EXP001_INVERSE_TAIL_Q / 2)
    reduced += NTRUPLUS1152_EXP001_INVERSE_TAIL_Q;
  return (int16_t)reduced;
}

static int16_t power(int16_t base, int exponent) {
  int16_t result = 1;
  while (exponent > 0) {
    if (exponent & 1) result = centered((int32_t)result * base);
    base = centered((int32_t)base * base);
    exponent >>= 1;
  }
  return result;
}

static void matrix_oracle(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *input) {
  int branch, terminal, time, source_time;
  for (branch = 0; branch < 2; ++branch)
    for (terminal = 0; terminal < 4; ++terminal)
      for (time = 0; time < 16; ++time)
        for (source_time = 0; source_time < 9; ++source_time) {
          int row;
          int64_t sum = 0;
          for (row = 0; row < 9; ++row) {
            int p = ntruplus1152_exp001_inverse_tail_p[row];
            int exponent = (9 - (source_time * p) % 9) % 9;
            sum += (int32_t)input->state[branch][row][terminal][time] *
                   power(NTRUPLUS1152_EXP001_INVERSE_TAIL_RHO, exponent);
          }
          output->state[branch][source_time][terminal][time] =
              centered(4 * sum);
        }
}

static uint64_t random_state = UINT64_C(0x9c21152a55e77d31);

static uint32_t random_u32(void) {
  random_state ^= random_state << 13;
  random_state ^= random_state >> 7;
  random_state ^= random_state << 17;
  return (uint32_t)(random_state >> 19);
}

static void fill_transform_case(
    ntruplus1152_exp001_gt_terminal_major *input, int trial) {
  int branch, row, terminal, time;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (terminal = 0; terminal < 4; ++terminal)
        for (time = 0; time < 16; ++time) {
          int value;
          if (trial == 0)
            value = 0;
          else if (trial == 1)
            value = 17377;
          else if (trial == 2)
            value = -17377;
          else if (trial == 3)
            value = ((branch + row + terminal + time) & 1) ? 17377 : -17377;
          else
            value = (int)(random_u32() % 34755U) - 17377;
          input->state[branch][row][terminal][time] = (int16_t)value;
        }
}

static void compare(const char *name,
                    const ntruplus1152_exp001_gt_terminal_major *expected,
                    const ntruplus1152_exp001_gt_terminal_major *actual,
                    int trial) {
  int branch, row, terminal, time;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (terminal = 0; terminal < 4; ++terminal)
        for (time = 0; time < 16; ++time)
          if (expected->state[branch][row][terminal][time] !=
              actual->state[branch][row][terminal][time]) {
            fprintf(stderr,
                    "%s mismatch trial=%d b=%d row=%d j=%d t=%d "
                    "expected=%d actual=%d\n",
                    name, trial, branch, row, terminal, time,
                    expected->state[branch][row][terminal][time],
                    actual->state[branch][row][terminal][time]);
            exit(1);
          }
}

static void check_centered(
    const ntruplus1152_exp001_gt_terminal_major *value, int trial) {
  int branch, row, terminal, time;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (terminal = 0; terminal < 4; ++terminal)
        for (time = 0; time < 16; ++time)
          if (value->state[branch][row][terminal][time] < -1728 ||
              value->state[branch][row][terminal][time] > 1728)
            fail("centered-range", trial);
}

static void fill_canary(struct guarded_output *guarded) {
  int index;
  for (index = 0; index < CANARY_WORDS; ++index) {
    guarded->before[index] = (int16_t)(0x2140 + index);
    guarded->after[index] = (int16_t)(0x4920 + index);
  }
}

static void check_canary(const struct guarded_output *guarded) {
  int index;
  for (index = 0; index < CANARY_WORDS; ++index)
    if (guarded->before[index] != (int16_t)(0x2140 + index) ||
        guarded->after[index] != (int16_t)(0x4920 + index))
      fail("canary", -1);
}

int main(void) {
  ntruplus1152_exp001_gt_terminal_major input __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_terminal_major saved __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_terminal_major expected __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_terminal_major direct __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_terminal_major b0 __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_terminal_major b1 __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_terminal_major canonical_output __attribute__((aligned(32)));
  ntruplus1152_exp001_inverse9_canonical_p canonical __attribute__((aligned(32)));
  ntruplus1152_exp001_inverse9_vector_canonical_p vector_canonical
      __attribute__((aligned(32)));
  struct guarded_output guarded __attribute__((aligned(32)));
  g1c_m3_terminal_major a __attribute__((aligned(32)));
  g1c_m3_terminal_major b __attribute__((aligned(32)));
  int trial;

  if (g1c_m3_centered_reduce(0) != 0 || g1c_m3_absolute64(-1) != 1)
    fail("shared-oracle-smoke", -1);
  g1c_m3_fill_case(&a, &b, 0);
  g1c_m3_compute_bmscale(&saved, &a, &b);
  if (!g1c_m3_propagate_stage(&saved, 0))
    fail("shared-stage-smoke", -1);

  for (trial = 0; trial < ARBITRARY_TRIALS; ++trial) {
    fill_transform_case(&input, trial);
    saved = input;
    matrix_oracle(&expected, &input);
    ntruplus1152_exp001_inverse_ntt9_r2_direct(&direct, &input);
    compare("direct-vs-matrix", &expected, &direct, trial);
    ntruplus1152_exp001_inverse_ntt9_b0(&b0, &input);
    compare("b0-vs-matrix", &expected, &b0, trial);
    ntruplus1152_exp001_inverse_ntt9_b1(&b1, &input);
    compare("b1-vs-matrix", &expected, &b1, trial);
    compare("b1-vs-b0", &b0, &b1, trial);
    ntruplus1152_exp001_inverse9_b0_repack_vector_canonical_p(
        &vector_canonical, &input);
    ntruplus1152_exp001_inverse_ntt9_b0_from_vector_canonical_p(
        &b0, &vector_canonical);
    compare("b0-vector-canonical-vs-matrix", &expected, &b0, trial);
    compare("input-immutable", &saved, &input, trial);
    check_centered(&direct, trial);

    ntruplus1152_exp001_inverse9_repack_canonical_p(&canonical, &input);
    ntruplus1152_exp001_inverse_ntt9_r2_from_canonical_p(
        &canonical_output, &canonical);
    compare("canonical-vs-direct", &direct, &canonical_output, trial);

    direct = input;
    ntruplus1152_exp001_inverse_ntt9_r2_direct(&direct, &direct);
    compare("direct-in-place", &expected, &direct, trial);
    b0 = input;
    ntruplus1152_exp001_inverse_ntt9_b0(&b0, &b0);
    compare("b0-in-place", &expected, &b0, trial);
    b1 = input;
    ntruplus1152_exp001_inverse_ntt9_b1(&b1, &b1);
    compare("b1-in-place", &expected, &b1, trial);
  }

  for (trial = 0; trial < PRODUCER_TRIALS; ++trial) {
    g1c_m3_fill_case(&a, &b, trial);
    ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2(&input, &a, &b);
    matrix_oracle(&expected, &input);
    ntruplus1152_exp001_inverse_ntt9_r2_direct(&direct, &input);
    compare("producer-C2-direct", &expected, &direct, trial);
    ntruplus1152_exp001_inverse_ntt9_b0(&b0, &input);
    compare("producer-C2-b0", &expected, &b0, trial);
    ntruplus1152_exp001_inverse_ntt9_b1(&b1, &input);
    compare("producer-C2-b1", &expected, &b1, trial);
  }

  fill_transform_case(&input, 19);
  matrix_oracle(&expected, &input);
  fill_canary(&guarded);
  ntruplus1152_exp001_inverse_ntt9_r2_direct(&guarded.value, &input);
  compare("canary-output", &expected, &guarded.value, 19);
  check_canary(&guarded);

  fill_canary(&guarded);
  ntruplus1152_exp001_inverse_ntt9_b0(&guarded.value, &input);
  compare("b0-canary-output", &expected, &guarded.value, 19);
  check_canary(&guarded);

  fill_canary(&guarded);
  ntruplus1152_exp001_inverse_ntt9_b1(&guarded.value, &input);
  compare("b1-canary-output", &expected, &guarded.value, 19);
  check_canary(&guarded);

  for (trial = 0; trial < 9; ++trial) {
    memset(&input, 0, sizeof input);
    input.state[0][trial][0][0] = 1;
    matrix_oracle(&expected, &input);
    ntruplus1152_exp001_inverse_ntt9_b0(&b0, &input);
    compare("b0-physical-p-basis", &expected, &b0, trial);
    ntruplus1152_exp001_inverse_ntt9_b1(&b1, &input);
    compare("b1-physical-p-basis", &expected, &b1, trial);
  }

  puts("inverse NTT9 R2 direct/B0/B1: 1003 arbitrary, 257 C2-producer, 9 basis, matrix, canonical control, alias, range, and canary passed");
  return 0;
}
