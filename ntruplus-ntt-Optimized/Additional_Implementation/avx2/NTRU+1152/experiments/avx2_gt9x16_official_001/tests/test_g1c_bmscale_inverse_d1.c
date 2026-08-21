#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "g1c-bmscale-live-tail.h"
#include "gt9x16-ntt9-paper-range.h"
#include "g1c_bmscale_inverse_d1_asm.h"

#define Q 3457
#define QINV 12929
#define R_MOD_Q 3310
#define TRIALS 1003

typedef ntruplus1152_exp001_gt_terminal_major terminal_major;

static uint64_t random_state = UINT64_C(0x1152c2feed19a5d1);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static int16_t wrap16(int64_t value) {
  uint16_t reduced = (uint16_t)value;
  return reduced < UINT16_C(0x8000) ? (int16_t)reduced
                                    : (int16_t)((int32_t)reduced - 65536);
}

static int16_t high16(int16_t left, int16_t right) {
  int32_t product = (int32_t)left * (int32_t)right;
  int32_t quotient = product / 65536;
  if (product < 0 && product % 65536 != 0) --quotient;
  return (int16_t)quotient;
}

static int16_t montgomery_mul(int16_t left, int16_t right) {
  int16_t low_qinv = wrap16((int32_t)left * QINV);
  int16_t low_product = wrap16((int32_t)low_qinv * right);
  return wrap16((int32_t)high16(left, right) - high16(low_product, Q));
}

static int16_t add16(int16_t left, int16_t right) {
  return wrap16((int32_t)left + right);
}

static int16_t sub16(int16_t left, int16_t right) {
  return wrap16((int32_t)left - right);
}

static int16_t centered_factor(int factor) {
  int value = (factor * R_MOD_Q) % Q;
  if (value > Q / 2) value -= Q;
  return (int16_t)value;
}

static void scalar_bmscale_vector(int16_t output[4], const int16_t a[4],
                                  const int16_t b[4], int16_t factor) {
  int16_t p13 = montgomery_mul(a[1], b[3]);
  int16_t p31 = montgomery_mul(a[3], b[1]);
  int16_t p33 = montgomery_mul(a[3], b[3]);
  int16_t p22 = montgomery_mul(a[2], b[2]);
  int16_t p23 = montgomery_mul(a[2], b[3]);
  int16_t p32 = montgomery_mul(a[3], b[2]);
  int16_t c0_high = add16(add16(p13, p31), p22);
  int16_t c1_high = add16(p23, p32);
  int16_t c0 = montgomery_mul(c0_high, factor);
  int16_t c1 = montgomery_mul(c1_high, factor);
  int16_t c2 = montgomery_mul(p33, factor);

  c0 = add16(c0, montgomery_mul(a[0], b[0]));
  c2 = add16(c2, montgomery_mul(a[0], b[2]));
  c2 = add16(c2, montgomery_mul(a[2], b[0]));
  c1 = add16(c1, montgomery_mul(a[0], b[1]));
  c1 = add16(c1, montgomery_mul(a[1], b[0]));
  c2 = add16(c2, montgomery_mul(a[1], b[1]));

  output[0] = c0;
  output[1] = c1;
  output[2] = c2;
  output[3] = add16(add16(montgomery_mul(a[0], b[3]),
                          montgomery_mul(a[1], b[2])),
                    add16(montgomery_mul(a[2], b[1]),
                          montgomery_mul(a[3], b[0])));
}

static void scalar_reference(terminal_major *raw, terminal_major *linked,
                             const terminal_major *a, const terminal_major *b,
                             int *maximum_raw, int *maximum_sum) {
  int branch, coefficient, lane, row;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row) {
      int16_t factor[16];
      for (lane = 0; lane < 16; ++lane)
        factor[lane] = centered_factor(
            ntruplus1152_exp001_g1c_bmscale_factor_mod_q[branch][row][lane]);
      for (lane = 0; lane < 16; ++lane) {
        int16_t av[4], bv[4], cv[4];
        for (coefficient = 0; coefficient < 4; ++coefficient) {
          av[coefficient] = a->state[branch][row][coefficient][lane];
          bv[coefficient] = b->state[branch][row][coefficient][lane];
        }
        scalar_bmscale_vector(cv, av, bv, factor[lane]);
        for (coefficient = 0; coefficient < 4; ++coefficient) {
          int absolute = cv[coefficient] < 0 ? -cv[coefficient] : cv[coefficient];
          raw->state[branch][row][coefficient][lane] = cv[coefficient];
          if (absolute > *maximum_raw) *maximum_raw = absolute;
        }
      }
      for (coefficient = 0; coefficient < 4; ++coefficient)
        for (lane = 0; lane < 16; lane += 2) {
          int16_t left = raw->state[branch][row][coefficient][lane];
          int16_t right = raw->state[branch][row][coefficient][lane + 1];
          int16_t sum = add16(left, right);
          int16_t difference = sub16(left, right);
          int16_t twisted = montgomery_mul(
              difference,
              ntruplus1152_exp001_g1c_bmscale_direct_d1_zeta[row][lane]);
          int absolute = sum < 0 ? -sum : sum;
          linked->state[branch][row][coefficient][lane] = sum;
          linked->state[branch][row][coefficient][lane + 1] = twisted;
          if (absolute > *maximum_sum) *maximum_sum = absolute;
        }
    }
}

static void fill_producer_input(ntruplus1152_exp001_gt_persistent_pair input[4],
                                int trial, int salt) {
  const int minimum = NTRUPLUS1152_EXP001_PAPER_INPUT_MIN;
  const int maximum = NTRUPLUS1152_EXP001_PAPER_INPUT_MAX;
  int lane, pair, row, stream;
  for (pair = 0; pair < 4; ++pair)
    for (row = 0; row < 9; ++row)
      for (stream = 0; stream < 2; ++stream)
        for (lane = 0; lane < 16; ++lane) {
          int value;
          if (trial == 0) value = 0;
          else if (trial == 1) value = minimum;
          else if (trial == 2) value = maximum;
          else if (trial == 3)
            value = ((salt + pair + row + stream + lane) & 1) ? minimum : maximum;
          else
            value = minimum + (int)(random_u32() % (unsigned)(maximum - minimum + 1));
          input[pair].state[row][stream][lane] = (int16_t)value;
        }
}

static void run_producer(terminal_major *output,
                         const ntruplus1152_exp001_gt_persistent_pair input[4]) {
  ntruplus1152_exp001_gt_persistent_pair scratch[4];
  int pair;
  for (pair = 0; pair < 4; ++pair) {
    int branch = pair / 2;
    int terminal_pair = pair % 2;
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b1(
        &scratch[pair], &input[pair],
        &output->state[branch][0][2 * terminal_pair][0]);
  }
}

static void fill_case(terminal_major *a, terminal_major *b, int trial) {
  ntruplus1152_exp001_gt_persistent_pair input_a[4] __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_persistent_pair input_b[4] __attribute__((aligned(32)));
  fill_producer_input(input_a, trial, 0);
  fill_producer_input(input_b, trial, 1);
  run_producer(a, input_a);
  run_producer(b, input_b);
}

static void compare(const char *label, int trial, const terminal_major *expected,
                    const terminal_major *actual) {
  int branch, coefficient, lane, row;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (coefficient = 0; coefficient < 4; ++coefficient)
        for (lane = 0; lane < 16; ++lane)
          if (expected->state[branch][row][coefficient][lane] !=
              actual->state[branch][row][coefficient][lane]) {
            fprintf(stderr,
                    "%s trial=%d branch=%d row=%d c=%d lane=%d expected=%" PRId16
                    " actual=%" PRId16 "\n",
                    label, trial, branch, row, coefficient, lane,
                    expected->state[branch][row][coefficient][lane],
                    actual->state[branch][row][coefficient][lane]);
            exit(1);
          }
}

static void test_canary(void) {
  struct guarded {
    uint64_t before[4];
    terminal_major value;
    uint64_t after[4];
  } __attribute__((aligned(32))) raw, materialized, linked;
  terminal_major a __attribute__((aligned(32)));
  terminal_major b __attribute__((aligned(32)));
  int index;
  fill_case(&a, &b, 17);
  for (index = 0; index < 4; ++index) {
    raw.before[index] = materialized.before[index] = linked.before[index] =
        UINT64_C(0x0123456789abcdef) ^ (uint64_t)index;
    raw.after[index] = materialized.after[index] = linked.after[index] =
        UINT64_C(0xfedcba9876543210) ^ (uint64_t)index;
  }
  ntruplus1152_exp001_gt9x16_bmscale_raw(&raw.value, &a, &b);
  ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_materialized(
      &materialized.value, &a, &b);
  ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l(&linked.value, &a, &b);
  for (index = 0; index < 4; ++index)
    if (raw.before[index] != (UINT64_C(0x0123456789abcdef) ^ (uint64_t)index) ||
        raw.after[index] != (UINT64_C(0xfedcba9876543210) ^ (uint64_t)index) ||
        materialized.before[index] != (UINT64_C(0x0123456789abcdef) ^ (uint64_t)index) ||
        materialized.after[index] != (UINT64_C(0xfedcba9876543210) ^ (uint64_t)index) ||
        linked.before[index] != (UINT64_C(0x0123456789abcdef) ^ (uint64_t)index) ||
        linked.after[index] != (UINT64_C(0xfedcba9876543210) ^ (uint64_t)index)) {
      fputs("G1C-M2 materialized/C2-L canary corruption\n", stderr);
      exit(1);
    }
}

int main(void) {
  terminal_major a __attribute__((aligned(32)));
  terminal_major b __attribute__((aligned(32)));
  terminal_major a_copy __attribute__((aligned(32)));
  terminal_major b_copy __attribute__((aligned(32)));
  terminal_major expected_raw __attribute__((aligned(32)));
  terminal_major expected_linked __attribute__((aligned(32)));
  terminal_major actual_raw __attribute__((aligned(32)));
  terminal_major actual_materialized __attribute__((aligned(32)));
  terminal_major actual_linked __attribute__((aligned(32)));
  int maximum_raw = 0, maximum_sum = 0, trial;

  for (trial = 0; trial < TRIALS; ++trial) {
    fill_case(&a, &b, trial);
    memcpy(&a_copy, &a, sizeof a);
    memcpy(&b_copy, &b, sizeof b);
    scalar_reference(&expected_raw, &expected_linked, &a, &b,
                     &maximum_raw, &maximum_sum);
    ntruplus1152_exp001_gt9x16_bmscale_raw(&actual_raw, &a, &b);
    ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_materialized(
        &actual_materialized, &a, &b);
    ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l(&actual_linked, &a, &b);
    compare("BMScale", trial, &expected_raw, &actual_raw);
    compare("BMScale+materialized-inverse-d1", trial,
            &expected_linked, &actual_materialized);
    compare("BMScale+inverse-d1", trial, &expected_linked, &actual_linked);
    if (memcmp(&a, &a_copy, sizeof a) != 0 || memcmp(&b, &b_copy, sizeof b) != 0) {
      fprintf(stderr, "G1C input mutation trial=%d\n", trial);
      return 1;
    }
  }
  test_canary();
  if (maximum_raw > 13824 || maximum_sum > 27648) {
    fprintf(stderr, "G1C range failure raw=%d sum=%d\n", maximum_raw, maximum_sum);
    return 1;
  }
  printf("G1C-M2 materialized/C2-L: %d cases x 1152 cells bit-exact, raw<=%d sum<=%d, canary passed\n",
         TRIALS, maximum_raw, maximum_sum);
  return 0;
}
