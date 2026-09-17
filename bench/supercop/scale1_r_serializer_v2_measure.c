#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "params.h"
#include "poly.h"
#include "wire-monotone-kem.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "wire_bytes", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "scale1_r_serializer_v2_"

static poly *coefficient;
static int16_t *wire_state;
static uint8_t *control_bytes, *candidate_bytes;
static long long cycles[TIMINGS + 1];
static volatile uint64_t residency_sink;

void ntruplus1152_exp001_scale1_r_serializer_v2(uint8_t *, const int16_t *);
void preallocate(void) {}
void allocate(void) {
  coefficient = (poly *)alignedcalloc(BANKS * sizeof *coefficient);
  wire_state = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_state);
  control_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  candidate_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
}

static int16_t *state_slot(int i) { return wire_state + i * NTRUPLUS_N; }
static uint8_t *byte_slot(uint8_t *base, int i) { return base + i * NTRUPLUS_POLYBYTES; }

static void prepare(void) {
  int i, j;
  for (i = 0; i < BANKS; ++i) {
    for (j = 0; j < NTRUPLUS_N; ++j)
      coefficient[i].coeffs[j] = (int16_t)(((j * 619U + i * 17U + 11U) % 3U) - 1);
    ntruplus1152_exp001_top_split_small(state_slot(i), coefficient[i].coeffs);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(state_slot(i));
  }
}

static void touch(void) {
  uint64_t acc = 0; int i, j;
  for (i = 0; i < BANKS; ++i)
    for (j = 0; j < NTRUPLUS_N; j += 16) acc += (uint16_t)state_slot(i)[j];
  residency_sink ^= acc;
}

static void __attribute__((noinline, aligned(32)))
control(uint8_t *out, const int16_t *state) {
  ntruplus1152_exp001_direct_serializer_wire(out, state);
}

static void __attribute__((noinline, aligned(32)))
candidate(uint8_t *out, const int16_t *state) {
  ntruplus1152_exp001_scale1_r_serializer_v2(out, state);
}

static void preflight(void) {
  int i;
  prepare();
  for (i = 0; i < BANKS; ++i) {
    control(byte_slot(control_bytes, i), state_slot(i));
    candidate(byte_slot(candidate_bytes, i), state_slot(i));
    if (memcmp(byte_slot(control_bytes, i), byte_slot(candidate_bytes, i),
               NTRUPLUS_POLYBYTES)) abort();
  }
}

#define RUN(label, statement) do {                                      \
  for (i = 0; i <= TIMINGS; ++i) { cycles[i] = cpucycles(); statement; } \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i];  \
  printentry(-1, PREFIX label "_cycles", cycles, TIMINGS);              \
} while (0)

void measure(void) {
  int i, loop;
  preflight();
  printf("scale1_r_serializer_v2_runtime_addresses %p %p\n",
         (void *)control, (void *)candidate);
  for (loop = 0; loop < LOOPS; ++loop) {
    touch(); RUN("control_first", control(byte_slot(control_bytes, i), state_slot(i)));
    touch(); RUN("candidate_second", candidate(byte_slot(candidate_bytes, i), state_slot(i)));
    touch(); RUN("candidate_first", candidate(byte_slot(candidate_bytes, i), state_slot(i)));
    touch(); RUN("control_second", control(byte_slot(control_bytes, i), state_slot(i)));
  }
}
