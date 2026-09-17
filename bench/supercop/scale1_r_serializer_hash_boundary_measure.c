#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "fips202.h"
#include "measure.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"
#include "wire-monotone-kem.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "wire_bytes", "hash_bytes", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N / 4 };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define STAGE_BYTES (1 + NTRUPLUS_POLYBYTES)
#define STAGE_STRIDE ((STAGE_BYTES + 31) & ~31)
#define PREFIX "scale1_r_serializer_hash_boundary_"

static poly *coefficient, *official_state, *official_m, *wire_m;
static int16_t *wire_state;
static uint8_t *official_bytes, *wire_bytes, *official_hash, *wire_hash;
static uint8_t *official_stage, *wire_stage, *message, *native_hash;
static long long cycles[TIMINGS + 1];
static volatile uint64_t residency_sink;

#define STATE_SLOT(base, i) ((base) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(base, i) ((base) + (i) * NTRUPLUS_POLYBYTES)
#define HASH_SLOT(base, i) ((base) + (i) * (NTRUPLUS_N / 4))
#define STAGE_SLOT(base, i) ((base) + (i) * STAGE_STRIDE)
#define MSG_SLOT(base, i) ((base) + (i) * (NTRUPLUS_N / 8))

void preallocate(void) {}

void allocate(void) {
  coefficient = (poly *)alignedcalloc(BANKS * sizeof *coefficient);
  official_state = (poly *)alignedcalloc(BANKS * sizeof *official_state);
  official_m = (poly *)alignedcalloc(BANKS * sizeof *official_m);
  wire_m = (poly *)alignedcalloc(BANKS * sizeof *wire_m);
  wire_state = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_state);
  official_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  wire_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  official_hash = (uint8_t *)alignedcalloc(BANKS * (NTRUPLUS_N / 4));
  wire_hash = (uint8_t *)alignedcalloc(BANKS * (NTRUPLUS_N / 4));
  official_stage = (uint8_t *)alignedcalloc(BANKS * STAGE_STRIDE);
  wire_stage = (uint8_t *)alignedcalloc(BANKS * STAGE_STRIDE);
  message = (uint8_t *)alignedcalloc(BANKS * (NTRUPLUS_N / 8));
  native_hash = (uint8_t *)alignedcalloc(NTRUPLUS_N / 4);
}

static void prepare_states(void) {
  int i, j;
  for (i = 0; i < BANKS; ++i) {
    for (j = 0; j < NTRUPLUS_N; ++j)
      coefficient[i].coeffs[j] =
          (int16_t)(((j * 619U + i * 17U + 11U) % 3U) - 1);
    for (j = 0; j < NTRUPLUS_N / 8; ++j)
      MSG_SLOT(message, i)[j] = (uint8_t)(j * 37U + i * 13U + 5U);
    official_state[i] = coefficient[i];
    poly_ntt(official_state + i);
    ntruplus1152_exp001_top_split_small(STATE_SLOT(wire_state, i),
                                        coefficient[i].coeffs);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(
        STATE_SLOT(wire_state, i));
  }
}

static void touch_states(void) {
  uint64_t acc = 0;
  int i, j;
  for (i = 0; i < BANKS; ++i)
    for (j = 0; j < NTRUPLUS_N; j += 16) {
      acc += (uint16_t)official_state[i].coeffs[j];
      acc += (uint16_t)STATE_SLOT(wire_state, i)[j];
    }
  residency_sink ^= acc;
}

static void __attribute__((noinline, aligned(32)))
official_s0(uint8_t *bytes, const poly *state) {
  poly_tobytes(bytes, state);
}

static void __attribute__((noinline, aligned(32)))
wire_s0(uint8_t *bytes, const int16_t *state) {
  ntruplus1152_exp001_direct_serializer_wire(bytes, state);
}

static void __attribute__((noinline, aligned(32)))
stage_hash_g_input(uint8_t *stage, const uint8_t *bytes) {
  stage[0] = 0x01;
  memcpy(stage + 1, bytes, NTRUPLUS_POLYBYTES);
}

static void __attribute__((noinline, aligned(32)))
official_s1(uint8_t *bytes, uint8_t *stage, const poly *state) {
  official_s0(bytes, state);
  stage_hash_g_input(stage, bytes);
}

static void __attribute__((noinline, aligned(32)))
wire_s1(uint8_t *bytes, uint8_t *stage, const int16_t *state) {
  wire_s0(bytes, state);
  stage_hash_g_input(stage, bytes);
}

static void hash_g_from_stage(uint8_t *hash, uint8_t *stage) {
  shake256(hash, NTRUPLUS_N / 4, stage, STAGE_BYTES);
  secure_clear(stage, STAGE_BYTES);
}

static void __attribute__((noinline, aligned(32)))
official_s2(uint8_t *bytes, uint8_t *stage, uint8_t *hash, const poly *state) {
  official_s1(bytes, stage, state);
  hash_g_from_stage(hash, stage);
}

static void __attribute__((noinline, aligned(32)))
wire_s2(uint8_t *bytes, uint8_t *stage, uint8_t *hash,
        const int16_t *state) {
  wire_s1(bytes, stage, state);
  hash_g_from_stage(hash, stage);
}

static void __attribute__((noinline, aligned(32)))
official_s3(uint8_t *bytes, uint8_t *stage, uint8_t *hash, poly *m,
            const poly *state, const uint8_t *msg) {
  official_s2(bytes, stage, hash, state);
  poly_sotp_encode(m, msg, hash);
}

static void __attribute__((noinline, aligned(32)))
wire_s3(uint8_t *bytes, uint8_t *stage, uint8_t *hash, poly *m,
        const int16_t *state, const uint8_t *msg) {
  wire_s2(bytes, stage, hash, state);
  poly_sotp_encode(m, msg, hash);
}

static void preflight(void) {
  prepare_states();
  official_s0(official_bytes, official_state);
  wire_s0(wire_bytes, wire_state);
  if (memcmp(official_bytes, wire_bytes, NTRUPLUS_POLYBYTES)) abort();

  official_s1(official_bytes, official_stage, official_state);
  wire_s1(wire_bytes, wire_stage, wire_state);
  if (memcmp(official_stage, wire_stage, STAGE_BYTES)) abort();

  official_s2(official_bytes, official_stage, official_hash, official_state);
  wire_s2(wire_bytes, wire_stage, wire_hash, wire_state);
  hash_g(native_hash, official_bytes);
  if (memcmp(official_hash, wire_hash, NTRUPLUS_N / 4) ||
      memcmp(official_hash, native_hash, NTRUPLUS_N / 4)) abort();

  official_s3(official_bytes, official_stage, official_hash, official_m,
              official_state, message);
  wire_s3(wire_bytes, wire_stage, wire_hash, wire_m, wire_state, message);
  if (memcmp(official_m, wire_m, sizeof *official_m)) abort();
}

#define RUN(label, statement) do {                                      \
  for (i = 0; i <= TIMINGS; ++i) { cycles[i] = cpucycles(); statement; } \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i];  \
  printentry(-1, PREFIX label "_cycles", cycles, TIMINGS);              \
} while (0)

#define BALANCED(label, official_statement, wire_statement) do { \
  touch_states(); RUN(label "_official_first", official_statement); \
  touch_states(); RUN(label "_wire_second", wire_statement);       \
  touch_states(); RUN(label "_wire_first", wire_statement);        \
  touch_states(); RUN(label "_official_second", official_statement); \
} while (0)

void measure(void) {
  int i, loop;
  preflight();
  printf("scale1_r_serializer_hash_boundary_runtime_addresses %p %p %p %p %p %p %p %p\n",
         (void *)official_s0, (void *)wire_s0, (void *)official_s1,
         (void *)wire_s1, (void *)official_s2, (void *)wire_s2,
         (void *)official_s3, (void *)wire_s3);
  for (loop = 0; loop < LOOPS; ++loop) {
    BALANCED("s0", official_s0(BYTE_SLOT(official_bytes, i), official_state + i),
             wire_s0(BYTE_SLOT(wire_bytes, i), STATE_SLOT(wire_state, i)));
    BALANCED("s1", official_s1(BYTE_SLOT(official_bytes, i),
                                STAGE_SLOT(official_stage, i), official_state + i),
             wire_s1(BYTE_SLOT(wire_bytes, i), STAGE_SLOT(wire_stage, i),
                     STATE_SLOT(wire_state, i)));
    BALANCED("s2", official_s2(BYTE_SLOT(official_bytes, i),
                                STAGE_SLOT(official_stage, i),
                                HASH_SLOT(official_hash, i), official_state + i),
             wire_s2(BYTE_SLOT(wire_bytes, i), STAGE_SLOT(wire_stage, i),
                     HASH_SLOT(wire_hash, i), STATE_SLOT(wire_state, i)));
    BALANCED("s3", official_s3(BYTE_SLOT(official_bytes, i),
                                STAGE_SLOT(official_stage, i),
                                HASH_SLOT(official_hash, i), official_m + i,
                                official_state + i, MSG_SLOT(message, i)),
             wire_s3(BYTE_SLOT(wire_bytes, i), STAGE_SLOT(wire_stage, i),
                     HASH_SLOT(wire_hash, i), wire_m + i,
                     STATE_SLOT(wire_state, i), MSG_SLOT(message, i)));
  }
}
