#include <string.h>

#include "ntt9_reference.h"
#include "gt9x16-full-forward-tables.h"

static int16_t montgomery_reduce(int32_t value) {
  int16_t low = (int16_t)value * 12929;
  return (int16_t)((value - (int32_t)low * 3457) >> 16);
}

static int16_t multiply(int16_t left, int16_t right) {
  return montgomery_reduce((int32_t)left * right);
}

static void radix3(int16_t *a, int16_t *b, int16_t *c,
                   int16_t zeta1, int16_t zeta2) {
  int16_t original_a = *a;
  int16_t t1 = multiply(zeta1, *b);
  int16_t t2 = multiply(zeta2, *c);
  int16_t t3 = multiply(-886, (int16_t)(t1 - t2));
  *a = (int16_t)(original_a + t1 + t2);
  *b = (int16_t)(original_a - t2 + t3);
  *c = (int16_t)(original_a - t1 - t3);
}

void ntruplus1152_exp001_ntt9_reference(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input) {
  ntruplus1152_exp001_gt_rows values;
  int group, lane;
  memcpy(&values, input, sizeof values);
  for (lane = 0; lane < 16; ++lane) {
    for (group = 0; group < 3; ++group) {
      radix3(&values.values[group][lane], &values.values[group + 3][lane],
             &values.values[group + 6][lane],
             ntruplus1152_exp001_ntt9_zeta[0],
             ntruplus1152_exp001_ntt9_zeta[1]);
    }
    for (group = 0; group < 3; ++group) {
      radix3(&values.values[3 * group][lane],
             &values.values[3 * group + 1][lane],
             &values.values[3 * group + 2][lane],
             ntruplus1152_exp001_ntt9_zeta[2 + 2 * group],
             ntruplus1152_exp001_ntt9_zeta[3 + 2 * group]);
    }
  }
  memcpy(output, &values, sizeof values);
}

static int16_t barrett_reduce(int16_t value) {
  int16_t quotient = (int16_t)(((int32_t)value * 9 + (1 << 14)) >> 15);
  return (int16_t)(value - quotient * 3457);
}

static void paper_radix3(int16_t *a, int16_t *b, int16_t *c) {
  int16_t sum = (int16_t)(*b + *c);
  int16_t difference = (int16_t)(*b - *c);
  int16_t product = multiply(ntruplus1152_exp001_paper_kappa[0], difference);
  int16_t twice_a = (int16_t)(*a + *a);
  int16_t base = (int16_t)(twice_a - sum);
  *a = (int16_t)(twice_a + sum + sum);
  *b = (int16_t)(base + product);
  *c = (int16_t)(base - product);
}

static void paper_first(int16_t values[9], int in0, int in1, int in2,
                        int out0, int out1, int out2) {
  int16_t a = values[in0], b = values[in1], c = values[in2];
  paper_radix3(&a, &b, &c);
  values[out0] = barrett_reduce(a);
  values[out1] = barrett_reduce(b);
  values[out2] = barrett_reduce(c);
}

static void paper_second(int16_t values[9], int row0, int row1, int row2,
                         int16_t zeta1, int16_t zeta2) {
  int16_t a = values[row0];
  int16_t b = zeta1 == 0 ? values[row1] : multiply(zeta1, values[row1]);
  int16_t c = zeta2 == 0 ? values[row2] : multiply(zeta2, values[row2]);
  paper_radix3(&a, &b, &c);
  values[row0] = a;
  values[row1] = b;
  values[row2] = c;
}

static void paper_reference(ntruplus1152_exp001_gt_rows *output,
                            const ntruplus1152_exp001_gt_rows *input,
                            int rotated) {
  int lane;
  for (lane = 0; lane < 16; ++lane) {
    int row;
    int16_t values[9];
    for (row = 0; row < 9; ++row)
      values[row] = input->values[row][lane];
    paper_first(values, 0, 3, 6, 0, 3, 6);
    paper_first(values, 1, 4, 7, 1, 4, 7);
    if (rotated)
      paper_first(values, 8, 2, 5, 2, 5, 8);
    else
      paper_first(values, 2, 5, 8, 2, 5, 8);
    paper_second(values, 0, 1, 2, 0, 0);
    if (rotated) {
      paper_second(values, 3, 4, 5,
                   ntruplus1152_exp001_ntt9_zeta[4],
                   ntruplus1152_exp001_paper_rhoinv[0]);
      paper_second(values, 6, 7, 8,
                   ntruplus1152_exp001_paper_rhoinv[0],
                   ntruplus1152_exp001_ntt9_zeta[4]);
    } else {
      paper_second(values, 3, 4, 5,
                   ntruplus1152_exp001_ntt9_zeta[4],
                   ntruplus1152_exp001_ntt9_zeta[5]);
      paper_second(values, 6, 7, 8,
                   ntruplus1152_exp001_ntt9_zeta[6],
                   ntruplus1152_exp001_ntt9_zeta[7]);
    }
    for (row = 0; row < 9; ++row)
      output->values[row][lane] = values[row];
  }
}

void ntruplus1152_exp001_ntt9_r1_reference(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input) {
  paper_reference(output, input, 0);
}

void ntruplus1152_exp001_ntt9_r2_reference(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input) {
  paper_reference(output, input, 1);
}
