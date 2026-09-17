#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "params.h"
#include "poly.h"
#include "scale1_r_serializer_v2_hash_g.h"
#include "symmetric.h"
#include "wire-monotone-kem.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "hash_bytes", 0 };
const long long sizes[] = { NTRUPLUS_N / 4 };
#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define STAGE_BYTES (1 + NTRUPLUS_POLYBYTES)
#define STAGE_STRIDE ((STAGE_BYTES + 31) & ~31)
#define PREFIX "scale1_r_serializer_v2_stage_"
static poly *coefficient;
static int16_t *states;
static uint8_t *serialized, *control_stage, *candidate_stage;
static uint8_t *control_hash, *candidate_hash;
static long long cycles[TIMINGS + 1];
static volatile uint64_t sink;
void ntruplus1152_exp001_scale1_r_serializer_v2(uint8_t *, const int16_t *);
void preallocate(void) {}
void allocate(void) {
  coefficient = (poly *)alignedcalloc(BANKS * sizeof *coefficient);
  states = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *states);
  serialized = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  control_stage = (uint8_t *)alignedcalloc(BANKS * STAGE_STRIDE);
  candidate_stage = (uint8_t *)alignedcalloc(BANKS * STAGE_STRIDE);
  control_hash = (uint8_t *)alignedcalloc(BANKS * (NTRUPLUS_N / 4));
  candidate_hash = (uint8_t *)alignedcalloc(BANKS * (NTRUPLUS_N / 4));
}
static int16_t *st(int i) { return states + i * NTRUPLUS_N; }
static uint8_t *bytes(int i) { return serialized + i * NTRUPLUS_POLYBYTES; }
static uint8_t *stage(uint8_t *base, int i) { return base + i * STAGE_STRIDE; }
static uint8_t *hash(uint8_t *base, int i) { return base + i * (NTRUPLUS_N / 4); }
static void prepare(void) {
  int i, j;
  for (i = 0; i < BANKS; ++i) {
    for (j = 0; j < NTRUPLUS_N; ++j)
      coefficient[i].coeffs[j] = (int16_t)(((j * 619U + i * 17U + 11U) % 3U) - 1);
    ntruplus1152_exp001_top_split_small(st(i), coefficient[i].coeffs);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(st(i));
  }
}
static void touch(void) {
  uint64_t acc = 0; int i, j;
  for (i = 0; i < BANKS; ++i)
    for (j = 0; j < NTRUPLUS_N; j += 16) acc += (uint16_t)st(i)[j];
  sink ^= acc;
}
static void __attribute__((noinline, aligned(32)))
p0_control(uint8_t *out, uint8_t *tmp, const int16_t *state) {
  ntruplus1152_exp001_scale1_r_serializer_v2(tmp, state);
  out[0] = 0x01;
  memcpy(out + 1, tmp, NTRUPLUS_POLYBYTES);
}
static void __attribute__((noinline, aligned(32)))
p0_candidate(uint8_t *out, const int16_t *state) {
  out[0] = 0x01;
  ntruplus1152_exp001_scale1_r_serializer_v2(out + 1, state);
}
static void __attribute__((noinline, aligned(32)))
p1_control(uint8_t *out, uint8_t *tmp, const int16_t *state) {
  ntruplus1152_exp001_scale1_r_serializer_v2(tmp, state);
  hash_g(out, tmp);
}
static void __attribute__((noinline, aligned(32)))
p1_candidate(uint8_t *out, const int16_t *state) {
  ntruplus1152_exp001_scale1_r_serializer_v2_hash_g(out, state);
}
static void preflight(void) {
  int i; prepare();
  for (i = 0; i < BANKS; ++i) {
    p0_control(stage(control_stage, i), bytes(i), st(i));
    p0_candidate(stage(candidate_stage, i), st(i));
    if (memcmp(stage(control_stage, i), stage(candidate_stage, i), STAGE_BYTES)) abort();
    p1_control(hash(control_hash, i), bytes(i), st(i));
    p1_candidate(hash(candidate_hash, i), st(i));
    if (memcmp(hash(control_hash, i), hash(candidate_hash, i), NTRUPLUS_N / 4)) abort();
  }
}
#define RUN(label, statement) do {                                      \
  for (i = 0; i <= TIMINGS; ++i) { cycles[i] = cpucycles(); statement; } \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i];  \
  printentry(-1, PREFIX label "_cycles", cycles, TIMINGS);              \
} while (0)
void measure(void) {
  int i, loop; preflight();
  printf("scale1_r_serializer_v2_stage_runtime_addresses %p %p %p %p\n",
         (void *)p0_control, (void *)p0_candidate, (void *)p1_control, (void *)p1_candidate);
  for (loop = 0; loop < LOOPS; ++loop) {
    touch(); RUN("p0_control_first", p0_control(stage(control_stage, i), bytes(i), st(i)));
    touch(); RUN("p0_candidate_second", p0_candidate(stage(candidate_stage, i), st(i)));
    touch(); RUN("p0_candidate_first", p0_candidate(stage(candidate_stage, i), st(i)));
    touch(); RUN("p0_control_second", p0_control(stage(control_stage, i), bytes(i), st(i)));
    touch(); RUN("p1_control_first", p1_control(hash(control_hash, i), bytes(i), st(i)));
    touch(); RUN("p1_candidate_second", p1_candidate(hash(candidate_hash, i), st(i)));
    touch(); RUN("p1_candidate_first", p1_candidate(hash(candidate_hash, i), st(i)));
    touch(); RUN("p1_control_second", p1_control(hash(control_hash, i), bytes(i), st(i)));
  }
}
