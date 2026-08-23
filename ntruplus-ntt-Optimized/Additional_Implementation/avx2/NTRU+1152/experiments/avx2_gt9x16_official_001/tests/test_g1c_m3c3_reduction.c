#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "g1c_m3c3_reduction.h"

#define Q 3457
#define VALUES NTRUPLUS1152_EXP001_M3C3_VALUES
#define CANARY 16

typedef void (*reducer)(int16_t *, const int16_t *);

struct guarded {
  _Alignas(32) int16_t pre[CANARY];
  _Alignas(32) int16_t values[VALUES];
  _Alignas(32) int16_t post[CANARY];
};

static int centered(int value) {
  value %= Q;
  if (value > Q / 2) value -= Q;
  if (value < -Q / 2) value += Q;
  return value;
}

static void fail(const char *name, int index, int input, int output) {
  fprintf(stderr, "%s failure at %d: input=%d output=%d\n",
          name, index, input, output);
  exit(1);
}

static void reset_canary(struct guarded *value) {
  int index;
  for (index = 0; index < CANARY; ++index) {
    value->pre[index] = (int16_t)0x5a5a;
    value->post[index] = (int16_t)0xa5a5;
  }
}

static void check_canary(const char *name, const struct guarded *value) {
  int index;
  for (index = 0; index < CANARY; ++index)
    if (value->pre[index] != (int16_t)0x5a5a ||
        value->post[index] != (int16_t)0xa5a5)
      fail(name, index, value->pre[index], value->post[index]);
}

static void check_reducer(const char *name, reducer selected,
                          int minimum, int maximum) {
  struct guarded input, output, alias;
  int base;
  reset_canary(&input);
  reset_canary(&output);
  reset_canary(&alias);
  for (base = -32768; base < 32768; base += VALUES) {
    int index;
    for (index = 0; index < VALUES; ++index) {
      int value = base + index;
      if (value > 32767) value = 32767;
      input.values[index] = (int16_t)value;
      alias.values[index] = (int16_t)value;
      output.values[index] = 0;
    }
    selected(output.values, input.values);
    selected(alias.values, alias.values);
    for (index = 0; index < VALUES; ++index) {
      int original = input.values[index];
      int got = output.values[index];
      if (got < minimum || got > maximum ||
          centered(got) != centered(original) || alias.values[index] != got)
        fail(name, index, original, got);
    }
    check_canary(name, &input);
    check_canary(name, &output);
    check_canary(name, &alias);
  }
}

int main(void) {
  check_reducer("signed-Barrett", ntruplus1152_exp001_g1c_m3c3_reduce_barrett,
                -1728, 1728);
  check_reducer("Montgomery-identity",
                ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity,
                -1794, 1802);
  puts("G1C-M3C3 reducers: all 65536 i16 values, congruence, alias, range, and canary passed");
  return 0;
}
