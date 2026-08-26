#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "f0-ma2-asm.h"
#include "f0-prod2-ma2-asm.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full_price.h"

#define N 1152
#define CT_BYTES 1728
#define TRIALS 257

static uint64_t state = UINT64_C(0x5033434f4e53554d);

static uint32_t random_u32(void) {
  state ^= state << 13;
  state ^= state >> 7;
  state ^= state << 17;
  return (uint32_t)(state >> 16);
}

static void fill_small(int16_t value[N], int trial, int salt) {
  int i;
  for (i = 0; i < N; ++i) {
    if (trial == 0)
      value[i] = 0;
    else if (trial == 1)
      value[i] = (int16_t)(((i + salt) & 1) ? -1 : 1);
    else
      value[i] = (int16_t)((int)(random_u32() % 3) - 1);
  }
}

static void form_control(int16_t planes[N], int16_t split[N],
                         const int16_t input[N]) {
  ntruplus1152_exp001_top_split_small(split, input);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(planes, split, 0, 0);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(planes, split, 0, 1);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(planes, split, 1, 0);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(planes, split, 1, 1);
}

static void form_candidate(int16_t planes[N], const int16_t input[N]) {
  ntruplus1152_exp001_top_split_small(planes, input);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_price(planes);
}

int main(void) {
  _Alignas(32) int16_t r[N], m[N], saved_r[N], saved_m[N], h[N], saved_h[N];
  _Alignas(32) int16_t control_r[N], control_m[N], candidate_r[N], candidate_m[N];
  _Alignas(32) int16_t split_r[N], split_m[N], scratch0[128], scratch1[128];
  uint8_t control_ct[CT_BYTES], candidate_ct[CT_BYTES];
  int trial, i;

  for (trial = 0; trial < TRIALS; ++trial) {
    fill_small(r, trial, 0);
    fill_small(m, trial, 1);
    memcpy(saved_r, r, sizeof r);
    memcpy(saved_m, m, sizeof m);
    for (i = 0; i < N; ++i)
      h[i] = (int16_t)(random_u32() % 3457U);
    memcpy(saved_h, h, sizeof h);

    form_control(control_r, split_r, r);
    form_control(control_m, split_m, m);
    form_candidate(candidate_r, r);
    form_candidate(candidate_m, m);
    if (memcmp(control_r, candidate_r, sizeof control_r) != 0 ||
        memcmp(control_m, candidate_m, sizeof control_m) != 0) {
      fprintf(stderr, "PROD3 consumer raw plane mismatch trial=%d\n", trial);
      return 1;
    }

    ntruplus1152_exp001_f0_ma2_native_full(
        control_ct, control_r, control_m, h, scratch0);
    ntruplus1152_exp001_f0_ma2_native_full(
        candidate_ct, candidate_r, candidate_m, h, scratch1);
    if (memcmp(control_ct, candidate_ct, sizeof control_ct) != 0) {
      fprintf(stderr, "PROD3 consumer ciphertext mismatch trial=%d\n", trial);
      return 1;
    }
    if (memcmp(r, saved_r, sizeof r) != 0 ||
        memcmp(m, saved_m, sizeof m) != 0 ||
        memcmp(h, saved_h, sizeof h) != 0) {
      fprintf(stderr, "PROD3 consumer input mutation trial=%d\n", trial);
      return 1;
    }
  }
  printf("GT9X16-PROD3-AOS-CONSUMER: %d raw-plane and ciphertext-exact cases passed\n",
         TRIALS);
  return 0;
}
