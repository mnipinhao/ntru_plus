#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"
#include "wire-monotone-kem.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "wire_monotone_native_attr_v3_"

static poly *input_r, *official_r, *official_m, *official_h, *official_c;
static int16_t *wire_r, *wire_m, *wire_c;
static uint8_t *msg, *pk, *official_bytes, *wire_bytes;
static long long cycles[TIMINGS + 1];

#define WORD_SLOT(base, i) ((base) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(base, i) ((base) + (i) * NTRUPLUS_POLYBYTES)
#define MSG_SLOT(base, i) ((base) + (i) * (NTRUPLUS_N / 8))

void preallocate(void) {}

void allocate(void) {
  input_r = (poly *)alignedcalloc(BANKS * sizeof *input_r);
  official_r = (poly *)alignedcalloc(BANKS * sizeof *official_r);
  official_m = (poly *)alignedcalloc(BANKS * sizeof *official_m);
  official_h = (poly *)alignedcalloc(BANKS * sizeof *official_h);
  official_c = (poly *)alignedcalloc(BANKS * sizeof *official_c);
  wire_r = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_r);
  wire_m = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_m);
  wire_c = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_c);
  msg = (uint8_t *)alignedcalloc(BANKS * (NTRUPLUS_N / 8));
  pk = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  official_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  wire_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
}

static void reset_inputs(void) {
  int i, j;
  for (i = 0; i < BANKS; ++i) {
    for (j = 0; j < NTRUPLUS_N; ++j) {
      input_r[i].coeffs[j] = (int16_t)(((j * 619 + i * 17 + 11) % 3) - 1);
      official_h[i].coeffs[j] =
          (int16_t)((j * 991 + i * 29 + 47) % NTRUPLUS_Q);
    }
    for (j = 0; j < NTRUPLUS_N / 8; ++j)
      MSG_SLOT(msg, i)[j] = (uint8_t)(j * 37 + i * 13 + 5);
    poly_tobytes(BYTE_SLOT(pk, i), official_h + i);
  }
}

static void __attribute__((noinline, aligned(32)))
official_forward(poly *out, const poly *in) {
  memcpy(out, in, sizeof *out);
  poly_ntt(out);
}

static void __attribute__((noinline, aligned(32)))
wire_forward(int16_t *out, const poly *in) {
  ntruplus1152_exp001_top_split_small(out, in->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(out);
}

static void __attribute__((noinline, aligned(32)))
official_dual(poly *out, uint8_t *bytes, const poly *in) {
  official_forward(out, in);
  poly_tobytes(bytes, out);
}

static void __attribute__((noinline, aligned(32)))
wire_dual(int16_t *out, uint8_t *bytes, const poly *in) {
  wire_forward(out, in);
  ntruplus1152_exp001_direct_serializer_wire(bytes, out);
}

static void __attribute__((noinline, aligned(32)))
official_r_chain(poly *r, poly *m, uint8_t *bytes, const poly *in,
                 const uint8_t *message) {
  official_dual(r, bytes, in);
  hash_g(bytes, bytes);
  poly_sotp_encode(m, message, bytes);
}

static void __attribute__((noinline, aligned(32)))
wire_r_chain(int16_t *r, poly *m, uint8_t *bytes, const poly *in,
             const uint8_t *message) {
  wire_dual(r, bytes, in);
  hash_g(bytes, bytes);
  poly_sotp_encode(m, message, bytes);
}

static void __attribute__((noinline, aligned(32)))
official_tail(uint8_t *ct, poly *out, const uint8_t *public_key,
              const poly *r, const poly *m) {
  poly h;
  if (poly_frombytes(&h, public_key)) abort();
  poly_basemul(out, &h, r);
  poly_add(out, out, m);
  poly_tobytes(ct, out);
}

static void __attribute__((noinline, aligned(32)))
wire_tail(uint8_t *ct, int16_t *scratch, const uint8_t *public_key,
          const int16_t *r, const int16_t *m) {
  if (ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(
          ct, public_key, r, m, scratch)) abort();
}

static void prepare_tail_inputs(void) {
  int i;
  for (i = 0; i < BANKS; ++i) {
    official_forward(official_r + i, input_r + i);
    official_m[i] = input_r[i];
    poly_ntt(official_m + i);
    wire_forward(WORD_SLOT(wire_r, i), input_r + i);
    wire_forward(WORD_SLOT(wire_m, i), input_r + i);
  }
}

static void __attribute__((noinline, aligned(32)))
official_changed_caller(uint8_t *ct, poly *r, poly *m, poly *out,
                        const uint8_t *public_key, const poly *input,
                        const uint8_t *message) {
  official_r_chain(r, m, ct, input, message);
  poly_ntt(m);
  official_tail(ct, out, public_key, r, m);
}

static void __attribute__((noinline, aligned(32)))
wire_changed_caller(uint8_t *ct, int16_t *r, int16_t *m, int16_t *scratch,
                    poly *m_coeff, const uint8_t *public_key, const poly *input,
                    const uint8_t *message) {
  wire_r_chain(r, m_coeff, ct, input, message);
  wire_forward(m, m_coeff);
  wire_tail(ct, scratch, public_key, r, m);
}

static void preflight(void) {
  reset_inputs();
  official_dual(official_r, official_bytes, input_r);
  wire_dual(wire_r, wire_bytes, input_r);
  if (memcmp(official_bytes, wire_bytes, NTRUPLUS_POLYBYTES)) abort();
  official_changed_caller(official_bytes, official_r, official_m, official_c,
                          pk, input_r, msg);
  wire_changed_caller(wire_bytes, wire_r, wire_m, wire_c, official_h, pk,
                      input_r, msg);
  if (memcmp(official_bytes, wire_bytes, NTRUPLUS_POLYBYTES)) abort();
}

#define MEASURE_ENTRY(label, statement) do {                            \
  for (i = 0; i <= TIMINGS; ++i) {                                     \
    cycles[i] = cpucycles();                                           \
    statement;                                                         \
  }                                                                    \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, PREFIX label "_cycles", cycles, TIMINGS);             \
} while (0)

#define MEASURE_BALANCED(label, preparation, official_statement, wire_statement) do { \
  preparation; MEASURE_ENTRY(label "_official_first", official_statement);            \
  preparation; MEASURE_ENTRY(label "_wire_second", wire_statement);                   \
  preparation; MEASURE_ENTRY(label "_wire_first", wire_statement);                    \
  preparation; MEASURE_ENTRY(label "_official_second", official_statement);           \
} while (0)

void measure(void) {
  int i, loop;
  preflight();
  printf("wire_monotone_native_attr_v3_runtime_addresses %p %p %p %p %p %p\n",
         (void *)official_forward, (void *)wire_forward,
         (void *)official_dual, (void *)wire_dual,
         (void *)official_changed_caller, (void *)wire_changed_caller);
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_BALANCED("forward", reset_inputs(),
      official_forward(official_r+i, input_r+i),
      wire_forward(WORD_SLOT(wire_r,i), input_r+i));
    MEASURE_BALANCED("dual_r", reset_inputs(),
      official_dual(official_r+i, BYTE_SLOT(official_bytes,i), input_r+i),
      wire_dual(WORD_SLOT(wire_r,i), BYTE_SLOT(wire_bytes,i), input_r+i));
    MEASURE_BALANCED("r_chain", reset_inputs(),
      official_r_chain(official_r+i, official_m+i, BYTE_SLOT(official_bytes,i),
                       input_r+i, MSG_SLOT(msg,i)),
      wire_r_chain(WORD_SLOT(wire_r,i), official_h+i, BYTE_SLOT(wire_bytes,i),
                   input_r+i, MSG_SLOT(msg,i)));
    MEASURE_BALANCED("tail", (reset_inputs(), prepare_tail_inputs()),
      official_tail(BYTE_SLOT(official_bytes,i), official_c+i, BYTE_SLOT(pk,i),
                    official_r+i, official_m+i),
      wire_tail(BYTE_SLOT(wire_bytes,i), WORD_SLOT(wire_c,i), BYTE_SLOT(pk,i),
                WORD_SLOT(wire_r,i), WORD_SLOT(wire_m,i)));
    MEASURE_BALANCED("changed_caller", reset_inputs(),
      official_changed_caller(BYTE_SLOT(official_bytes,i), official_r+i,
                              official_m+i, official_c+i, BYTE_SLOT(pk,i),
                              input_r+i, MSG_SLOT(msg,i)),
      wire_changed_caller(BYTE_SLOT(wire_bytes,i), WORD_SLOT(wire_r,i),
                          WORD_SLOT(wire_m,i), WORD_SLOT(wire_c,i), official_h+i,
                          BYTE_SLOT(pk,i), input_r+i, MSG_SLOT(msg,i)));
  }
}
