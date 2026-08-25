#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "f0-ma1-asm1-oracle.h"
#include "f0-ma2-asm.h"

#define Q 3457
#define N 1152
#define BYTES 1728
#define TRIALS 1003
#define GUARD 16

void poly_tobytes(uint8_t output[BYTES], const int16_t input[N]);

static uint32_t state = 0x4d413200U;
static uint32_t next_random(void) {
  state ^= state << 13;
  state ^= state >> 17;
  state ^= state << 5;
  return state;
}

static int centered(int64_t value) {
  value %= Q;
  if (value > Q / 2) value -= Q;
  if (value < -Q / 2) value += Q;
  return (int)value;
}

static void oracle(int16_t output[N], const int16_t r[N],
                   const int16_t m[N], const int16_t h[N]) {
  int tile, coefficient, lane, left, right;
  memset(output, 0, N * sizeof *output);
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
        output[f0_ma1_tiles[tile].h[coefficient][lane]] =
            (int16_t)centered(value * 2593);
      }
}

static void fill(int16_t r[N], int16_t m[N], int16_t h[N], int trial) {
  int i;
  for (i = 0; i < N; ++i) {
    if (trial == 0) {
      r[i] = m[i] = h[i] = 0;
    } else if (trial == 1) {
      r[i] = (int16_t)((i & 1) ? 20753 : -20751);
      m[i] = (int16_t)((i & 2) ? -20549 : 20547);
      h[i] = (int16_t)((i & 4) ? 3456 : 0);
    } else if (trial == 2) {
      r[i] = m[i] = (int16_t)((i & 1) ? 20753 : -20751);
      h[i] = (int16_t)(i % Q);
    } else {
      r[i] = (int16_t)((int)(next_random() % 41505U) - 20751);
      m[i] = (int16_t)((int)(next_random() % 41505U) - 20751);
      h[i] = (int16_t)(next_random() % Q);
    }
  }
}

static void fail(const char *name, int trial, int index, int expected,
                 int actual) {
  fprintf(stderr, "F0-MA2 %s trial=%d index=%d expected=%d actual=%d\n",
          name, trial, index, expected, actual);
  exit(1);
}

int main(void) {
  _Alignas(32) int16_t r[N], m[N], h[N], saved_r[N], saved_m[N], saved_h[N];
  _Alignas(32) int16_t expected_poly[N];
  _Alignas(32) uint8_t expected_bytes[BYTES];
  _Alignas(32) int16_t asm0[64 + 2 * GUARD];
  _Alignas(32) int16_t scratch[128 + 2 * GUARD];
  uint8_t chunk[192 + 2 * GUARD];
  uint8_t full[BYTES + 2 * GUARD];
  int trial, i;

  if (((uintptr_t)r | (uintptr_t)m | (uintptr_t)h |
       (uintptr_t)(asm0 + GUARD) | (uintptr_t)(scratch + GUARD)) & 31U)
    fail("alignment", -1, -1, 0, 1);
  for (trial = 0; trial < TRIALS; ++trial) {
    fill(r, m, h, trial);
    memcpy(saved_r, r, sizeof r); memcpy(saved_m, m, sizeof m);
    memcpy(saved_h, h, sizeof h);
    oracle(expected_poly, r, m, h);
    poly_tobytes(expected_bytes, expected_poly);
    memset(asm0, 0x5a, sizeof asm0); memset(scratch, 0x6b, sizeof scratch);
    memset(chunk, 0xa5, sizeof chunk); memset(full, 0xc7, sizeof full);
    for (i = 0; i < GUARD; ++i) {
      asm0[i] = (int16_t)(0x1200 + i);
      asm0[GUARD + 64 + i] = (int16_t)(0x2300 + i);
      scratch[i] = (int16_t)(0x3400 + i);
      scratch[GUARD + 128 + i] = (int16_t)(0x4500 + i);
      chunk[i] = (uint8_t)(0x51 + i);
      chunk[GUARD + 192 + i] = (uint8_t)(0x71 + i);
      full[i] = (uint8_t)(0x81 + i);
      full[GUARD + BYTES + i] = (uint8_t)(0x91 + i);
    }
    ntruplus1152_exp001_f0_ma2_asm0_b0p0(asm0 + GUARD, r, m, h);
    ntruplus1152_exp001_f0_ma2_chunk0(chunk + GUARD, r, m, h,
                                      scratch + GUARD);
    ntruplus1152_exp001_f0_ma2_full(full + GUARD, r, m, h,
                                    scratch + GUARD);
    for (i = 0; i < 64; ++i) {
      int coefficient = i / 16, lane = i % 16;
      int owner = f0_ma1_tiles[0].h[coefficient][lane];
      if (centered(asm0[GUARD + i]) != centered(expected_poly[owner]))
        fail("ASM0", trial, i, centered(expected_poly[owner]),
             centered(asm0[GUARD + i]));
    }
    for (i = 0; i < 192; ++i)
      if (chunk[GUARD + i] != expected_bytes[i])
        fail("CHUNK0", trial, i, expected_bytes[i], chunk[GUARD + i]);
    for (i = 0; i < BYTES; ++i)
      if (full[GUARD + i] != expected_bytes[i])
        fail("FULL", trial, i, expected_bytes[i], full[GUARD + i]);
    if (memcmp(r, saved_r, sizeof r) || memcmp(m, saved_m, sizeof m) ||
        memcmp(h, saved_h, sizeof h))
      fail("input-immutable", trial, -1, 0, 1);
    for (i = 0; i < GUARD; ++i) {
      if (asm0[i] != (int16_t)(0x1200 + i) ||
          asm0[GUARD + 64 + i] != (int16_t)(0x2300 + i) ||
          scratch[i] != (int16_t)(0x3400 + i) ||
          scratch[GUARD + 128 + i] != (int16_t)(0x4500 + i) ||
          chunk[i] != (uint8_t)(0x51 + i) ||
          chunk[GUARD + 192 + i] != (uint8_t)(0x71 + i) ||
          full[i] != (uint8_t)(0x81 + i) ||
          full[GUARD + BYTES + i] != (uint8_t)(0x91 + i))
        fail("canary", trial, i, 0, 1);
    }
  }
  puts("F0-MA2 ASM0/CHUNK0/FULL: 1003 raw-input random/boundary cases, direct bytes, immutability, alignment, and canaries passed");
  return 0;
}
