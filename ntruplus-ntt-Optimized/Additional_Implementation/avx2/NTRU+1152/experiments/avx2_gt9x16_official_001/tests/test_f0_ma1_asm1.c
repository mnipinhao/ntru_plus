#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "f0-ma1-asm1.h"
#include "f0-ma1-asm1-oracle.h"
#include "f0_ma0_control.h"

#define Q 3457
#define N 1152
#define BYTES 1728
#define TRIALS 1003
#define GUARD 16

void poly_tobytes(uint8_t output[BYTES], const int16_t input[N]);

struct guarded_scratch {
  int16_t before[GUARD];
  _Alignas(32) int16_t value[256];
  int16_t after[GUARD];
};

struct guarded_bytes {
  uint8_t before[GUARD];
  uint8_t value[BYTES];
  uint8_t after[GUARD];
};

static uint32_t random_state = 0x4d413131U;

static uint32_t next_random(void) {
  random_state ^= random_state << 13;
  random_state ^= random_state >> 17;
  random_state ^= random_state << 5;
  return random_state;
}

static int centered(int64_t value) {
  value %= Q;
  if (value > Q / 2) value -= Q;
  if (value < -Q / 2) value += Q;
  return (int)value;
}

static void oracle(int16_t official[N], const int16_t r[N],
                   const int16_t m[N], const int16_t h[N]) {
  const int inv4 = 2593;
  int tile, coefficient, lane, left, right;
  memset(official, 0, N * sizeof *official);
  for (tile = 0; tile < 18; ++tile)
    for (coefficient = 0; coefficient < 4; ++coefficient)
      for (lane = 0; lane < 16; ++lane) {
        int64_t value = m[f0_ma1_tiles[tile].f0[coefficient][lane]];
        for (left = 0; left < 4; ++left)
          for (right = 0; right < 4; ++right)
            if ((left + right) % 4 == coefficient) {
              int64_t term =
                  (int64_t)h[f0_ma1_tiles[tile].h[left][lane]] *
                  r[f0_ma1_tiles[tile].f0[right][lane]];
              if (left + right >= 4)
                term *= f0_ma1_tiles[tile].lambda[lane];
              value += term;
            }
        official[f0_ma1_tiles[tile].h[coefficient][lane]] =
            (int16_t)centered(value * inv4);
      }
}

static void fill_case(int16_t r[N], int16_t m[N], int16_t h[N], int trial) {
  int index;
  for (index = 0; index < N; ++index) {
    if (trial == 0) {
      r[index] = m[index] = h[index] = 0;
    } else if (trial == 1) {
      r[index] = 0;
      m[index] = (int16_t)((index & 2) ? -20549 : 20547);
      h[index] = 0;
    } else if (trial == 2) {
      r[index] = (int16_t)((index & 1) ? 20753 : -20751);
      m[index] = (int16_t)((index & 2) ? -20549 : 20547);
      h[index] = (int16_t)((index & 4) ? 3456 : 0);
    } else {
      r[index] = (int16_t)((int)(next_random() % 41505U) - 20751);
      m[index] = (int16_t)((int)(next_random() % 41505U) - 20751);
      h[index] = (int16_t)(next_random() % Q);
    }
  }
}

static void fail(const char *what, int trial, int index, int expected,
                 int actual) {
  fprintf(stderr,
          "F0-MA1-ASM1 %s trial=%d index=%d expected=%d actual=%d\n",
          what, trial, index, expected, actual);
  exit(1);
}

static void set_guards(struct guarded_bytes *output,
                       struct guarded_scratch *scratch, int salt) {
  int index;
  for (index = 0; index < GUARD; ++index) {
    output->before[index] = (uint8_t)(0x31 + index + salt);
    output->after[index] = (uint8_t)(0x59 + index + salt);
    scratch->before[index] = (int16_t)(0x1230 + index + salt);
    scratch->after[index] = (int16_t)(0x4560 + index + salt);
  }
  memset(output->value, 0xa5, sizeof output->value);
  memset(scratch->value, 0x5a, sizeof scratch->value);
}

static void check_guards(const struct guarded_bytes *output,
                         const struct guarded_scratch *scratch, int salt,
                         int trial, const char *name) {
  int index;
  for (index = 0; index < GUARD; ++index) {
    if (output->before[index] != (uint8_t)(0x31 + index + salt) ||
        output->after[index] != (uint8_t)(0x59 + index + salt))
      fail(name, trial, index, 0, 1);
    if (scratch->before[index] != (int16_t)(0x1230 + index + salt) ||
        scratch->after[index] != (int16_t)(0x4560 + index + salt))
      fail(name, trial, index, 0, 1);
  }
}

int main(void) {
  _Alignas(32) int16_t r[N], m[N], h[N], saved_r[N], saved_m[N], saved_h[N];
  _Alignas(32) uint8_t expected[BYTES];
  _Alignas(32) int16_t expected_official[N];
  struct guarded_scratch scratch0 __attribute__((aligned(32)));
  struct guarded_scratch scratch1 __attribute__((aligned(32)));
  _Alignas(32) int16_t scratch_ma0[3456 + 2 * GUARD];
  struct guarded_bytes output0, output1;
  struct guarded_bytes output2;
  int trial, index;

  if (((uintptr_t)r | (uintptr_t)m | (uintptr_t)h |
       (uintptr_t)scratch0.value | (uintptr_t)scratch1.value |
       (uintptr_t)(scratch_ma0 + GUARD)) & 31U)
    fail("test-alignment", -1, -1, 0, 1);

  for (trial = 0; trial < TRIALS; ++trial) {
    fill_case(r, m, h, trial);
    memcpy(saved_r, r, sizeof r);
    memcpy(saved_m, m, sizeof m);
    memcpy(saved_h, h, sizeof h);
    oracle(expected_official, r, m, h);
    poly_tobytes(expected, expected_official);
    set_guards(&output0, &scratch0, 0);
    set_guards(&output1, &scratch1, 7);
    memset(&output2, 0xa5, sizeof output2);
    memset(scratch_ma0, 0x5a, sizeof scratch_ma0);
    for (index = 0; index < GUARD; ++index) {
      output2.before[index] = (uint8_t)(0x41 + index);
      output2.after[index] = (uint8_t)(0x69 + index);
      scratch_ma0[index] = (int16_t)(0x2230 + index);
      scratch_ma0[GUARD + 3456 + index] = (int16_t)(0x5560 + index);
    }
    ntruplus1152_exp001_f0_ma1_asm1_c0(output0.value, r, m, h,
                                        scratch0.value);
    ntruplus1152_exp001_f0_ma1_asm1_c1(output1.value, r, m, h,
                                        scratch1.value);
    ntruplus1152_exp001_f0_ma0_control(output2.value, r, m, h,
                                       scratch_ma0 + GUARD);
    for (index = 0; index < 128; ++index) {
      if (centered(scratch0.value[128 + index]) !=
          centered(expected_official[1024 + index]))
        fail("C0-last-chunk", trial, index,
             centered(expected_official[1024 + index]),
             centered(scratch0.value[128 + index]));
      if (centered(scratch1.value[128 + index]) !=
          centered(expected_official[1024 + index]))
        fail("C1-last-chunk", trial, index,
             centered(expected_official[1024 + index]),
             centered(scratch1.value[128 + index]));
    }
    for (index = 0; index < BYTES; ++index) {
      if (output0.value[index] != expected[index])
        fail("C0-differential", trial, index, expected[index],
             output0.value[index]);
      if (output1.value[index] != expected[index])
        fail("C1-differential", trial, index, expected[index],
             output1.value[index]);
      if (output2.value[index] != expected[index])
        fail("MA0-differential", trial, index, expected[index],
             output2.value[index]);
    }
    if (memcmp(output0.value, output1.value, BYTES))
      fail("C0-C1", trial, -1, 0, 1);
    if (memcmp(r, saved_r, sizeof r) || memcmp(m, saved_m, sizeof m) ||
        memcmp(h, saved_h, sizeof h))
      fail("input-immutable", trial, -1, 0, 1);
    check_guards(&output0, &scratch0, 0, trial, "C0-canary");
    check_guards(&output1, &scratch1, 7, trial, "C1-canary");
    for (index = 0; index < GUARD; ++index) {
      if (output2.before[index] != (uint8_t)(0x41 + index) ||
          output2.after[index] != (uint8_t)(0x69 + index) ||
          scratch_ma0[index] != (int16_t)(0x2230 + index) ||
          scratch_ma0[GUARD + 3456 + index] != (int16_t)(0x5560 + index))
        fail("MA0-canary", trial, index, 0, 1);
    }
  }

  puts("F0-MA1-ASM1 C0/C1/MA0: 1003 full random/boundary byte-exact cases, input immutability, alignment, and canaries passed");
  return 0;
}
