#include "inverse_ntt9_reference.h"

#include "g1c-inverse-tail-map.h"

#define Q NTRUPLUS1152_EXP001_INVERSE_TAIL_Q

static int16_t centered(int32_t value) {
  int32_t reduced = value % Q;
  int32_t high_mask = -(int32_t)(reduced > Q / 2);
  int32_t low_mask;
  reduced -= Q & high_mask;
  low_mask = -(int32_t)(reduced < -Q / 2);
  reduced += Q & low_mask;
  return (int16_t)reduced;
}

static int16_t multiply(int16_t left, int16_t right) {
  return centered((int32_t)left * right);
}

static void inverse_paper_radix3(int16_t *a, int16_t *b, int16_t *c) {
  int16_t sum = centered((int32_t)*b + *c);
  int16_t difference = centered((int32_t)*b - *c);
  int16_t product = multiply(
      NTRUPLUS1152_EXP001_INVERSE_TAIL_KAPPA_INV, difference);
  int16_t twice_a = centered((int32_t)*a + *a);
  int16_t base = centered((int32_t)twice_a - sum);
  *a = centered((int32_t)twice_a + sum + sum);
  *b = centered((int32_t)base + product);
  *c = centered((int32_t)base - product);
}

static void inverse_second_layer(int16_t values[9], int row0, int row1,
                                 int row2, int16_t untwist1,
                                 int16_t untwist2) {
  int16_t a = values[row0];
  int16_t b = values[row1];
  int16_t c = values[row2];
  inverse_paper_radix3(&a, &b, &c);
  values[row0] = a;
  values[row1] = untwist1 == 0 ? b : multiply(untwist1, b);
  values[row2] = untwist2 == 0 ? c : multiply(untwist2, c);
}

static void inverse_first_layer(const int16_t values[9], int16_t output[9]) {
  int16_t a, b, c;
  a = values[0];
  b = values[3];
  c = values[6];
  inverse_paper_radix3(&a, &b, &c);
  output[0] = a;
  output[3] = b;
  output[6] = c;

  a = values[1];
  b = values[4];
  c = values[7];
  inverse_paper_radix3(&a, &b, &c);
  output[1] = a;
  output[4] = b;
  output[7] = c;

  a = values[2];
  b = values[5];
  c = values[8];
  inverse_paper_radix3(&a, &b, &c);
  output[8] = a;
  output[2] = b;
  output[5] = c;
}

static void inverse_lane(const int16_t input[9], int16_t output[9]) {
  int16_t values[9];
  int row;
  for (row = 0; row < 9; ++row) values[row] = centered(input[row]);

  inverse_second_layer(values, 0, 1, 2, 0, 0);
  inverse_second_layer(
      values, 3, 4, 5, NTRUPLUS1152_EXP001_INVERSE_TAIL_RHOINV,
      NTRUPLUS1152_EXP001_INVERSE_TAIL_RHO);
  inverse_second_layer(
      values, 6, 7, 8, NTRUPLUS1152_EXP001_INVERSE_TAIL_RHO,
      NTRUPLUS1152_EXP001_INVERSE_TAIL_RHOINV);
  inverse_first_layer(values, output);
}

void ntruplus1152_exp001_inverse_ntt9_r2_direct(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *input) {
  int branch, terminal, time;
  for (branch = 0; branch < 2; ++branch)
    for (terminal = 0; terminal < 4; ++terminal)
      for (time = 0; time < 16; ++time) {
        int row;
        int16_t lane_input[9], lane_output[9];
        for (row = 0; row < 9; ++row)
          lane_input[row] = input->state[branch][row][terminal][time];
        inverse_lane(lane_input, lane_output);
        for (row = 0; row < 9; ++row)
          output->state[branch][row][terminal][time] = lane_output[row];
      }
}

void ntruplus1152_exp001_inverse9_repack_canonical_p(
    ntruplus1152_exp001_inverse9_canonical_p *output,
    const ntruplus1152_exp001_gt_terminal_major *input) {
  int branch, row, terminal, time;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row) {
      int p = ntruplus1152_exp001_inverse_tail_p[row];
      for (terminal = 0; terminal < 4; ++terminal)
        for (time = 0; time < 16; ++time)
          output->state[branch][time][terminal][p] =
              input->state[branch][row][terminal][time];
    }
}

void ntruplus1152_exp001_inverse_ntt9_r2_from_canonical_p(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_inverse9_canonical_p *input) {
  int branch, terminal, time;
  for (branch = 0; branch < 2; ++branch)
    for (terminal = 0; terminal < 4; ++terminal)
      for (time = 0; time < 16; ++time) {
        int row;
        int16_t lane_input[9], lane_output[9];
        for (row = 0; row < 9; ++row)
          lane_input[row] = input->state[branch][time][terminal]
                                      [ntruplus1152_exp001_inverse_tail_p[row]];
        inverse_lane(lane_input, lane_output);
        for (row = 0; row < 9; ++row)
          output->state[branch][row][terminal][time] = lane_output[row];
      }
}
