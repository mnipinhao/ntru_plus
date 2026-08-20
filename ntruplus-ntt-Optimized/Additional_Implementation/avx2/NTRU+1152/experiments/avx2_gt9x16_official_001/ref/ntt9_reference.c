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
