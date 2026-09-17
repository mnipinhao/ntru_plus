#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "params.h"
#include "poly.h"
#include "gt9x16-prod3-ma2-qorder-natural-asm.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "wire_monotone_tail_attr_v2_"

void ntruplus1152_exp001_top_split_small(int16_t *, const int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t *);
void ntruplus1152_exp001_direct_serializer_wire(uint8_t *, const int16_t *);
int ntruplus1152_exp001_poly_frombytes_h_natural_q(int16_t *, const uint8_t *);
int ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire(
    int16_t *, const uint8_t *, const int16_t *, const int16_t *);
int ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(
    uint8_t *, const uint8_t *, const int16_t *, const int16_t *, int16_t *);

static poly *input_r, *input_m, *input_h;
static poly *official_r, *official_m, *official_h, *official_out;
static int16_t *wire_r, *wire_m, *wire_h, *wire_out;
static uint8_t *pk, *official_bytes, *wire_bytes;
static long long cycles[TIMINGS + 1];
static volatile unsigned int reject_sink;

#define WORD_SLOT(base, i) ((base) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(base, i) ((base) + (i) * NTRUPLUS_POLYBYTES)

void preallocate(void) {}

void allocate(void) {
  input_r = (poly *)alignedcalloc(BANKS * sizeof *input_r);
  input_m = (poly *)alignedcalloc(BANKS * sizeof *input_m);
  input_h = (poly *)alignedcalloc(BANKS * sizeof *input_h);
  official_r = (poly *)alignedcalloc(BANKS * sizeof *official_r);
  official_m = (poly *)alignedcalloc(BANKS * sizeof *official_m);
  official_h = (poly *)alignedcalloc(BANKS * sizeof *official_h);
  official_out = (poly *)alignedcalloc(BANKS * sizeof *official_out);
  wire_r = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_r);
  wire_m = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_m);
  wire_h = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_h);
  wire_out = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_out);
  pk = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  official_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  wire_bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
}

static void reset_inputs(void) {
  int i, j;
  for (i = 0; i < BANKS; ++i) {
    for (j = 0; j < NTRUPLUS_N; ++j) {
      input_r[i].coeffs[j] = (int16_t)(((j * 619 + i * 17 + 11) % 3) - 1);
      input_m[i].coeffs[j] = (int16_t)(((j * 433 + i * 23 + 7) % 3) - 1);
      input_h[i].coeffs[j] =
          (int16_t)((j * 991 + i * 29 + 47) % NTRUPLUS_Q);
    }
    poly_tobytes(BYTE_SLOT(pk, i), input_h + i);
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

static void prepare_states(void) {
  int i;
  for (i = 0; i < BANKS; ++i) {
    official_forward(official_r + i, input_r + i);
    official_forward(official_m + i, input_m + i);
    wire_forward(WORD_SLOT(wire_r, i), input_r + i);
    wire_forward(WORD_SLOT(wire_m, i), input_m + i);
  }
}

static int __attribute__((noinline, aligned(32)))
official_t0(poly *h, const uint8_t *public_key) {
  return poly_frombytes(h, public_key);
}

/* Materialized diagnostic proxy for the interleaved wire ingress.  Gate 3
 * proves identical loads/routes and mask-only differences versus wire H3. */
static int __attribute__((noinline, aligned(32)))
wire_t0(int16_t *h, const uint8_t *public_key) {
  return ntruplus1152_exp001_poly_frombytes_h_natural_q(h, public_key);
}

static int __attribute__((noinline, aligned(32)))
official_t1(poly *out, const uint8_t *public_key,
            const poly *r, const poly *m) {
  poly h;
  int reject = poly_frombytes(&h, public_key);
  poly_basemul(out, &h, r);
  poly_add(out, out, m);
  return reject;
}

static int __attribute__((noinline, aligned(32)))
wire_t1(int16_t *out, const uint8_t *public_key,
        const int16_t *r, const int16_t *m) {
  return ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire(
      out, public_key, r, m);
}

static int __attribute__((noinline, aligned(32)))
official_t2(uint8_t *bytes, poly *out, const uint8_t *public_key,
            const poly *r, const poly *m) {
  int reject = official_t1(out, public_key, r, m);
  poly_tobytes(bytes, out);
  return reject;
}

static int __attribute__((noinline, aligned(32)))
wire_t2(uint8_t *bytes, int16_t *scratch, const uint8_t *public_key,
        const int16_t *r, const int16_t *m) {
  return ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(
      bytes, public_key, r, m, scratch);
}

static void preflight(void) {
  int i;
  reset_inputs();
  prepare_states();
  if (official_t0(official_h, pk) || wire_t0(wire_h, pk)) abort();
  for (i = 0; i < NTRUPLUS_N; ++i)
    if (wire_h[i] != official_h->coeffs[ntruplus1152_exp001_qnat_h_source[i]])
      abort();
  if (official_t1(official_out, pk, official_r, official_m) ||
      wire_t1(wire_out, pk, wire_r, wire_m)) abort();
  poly_tobytes(official_bytes, official_out);
  ntruplus1152_exp001_direct_serializer_wire(wire_bytes, wire_out);
  if (memcmp(official_bytes, wire_bytes, NTRUPLUS_POLYBYTES)) abort();
  if (official_t2(official_bytes, official_out, pk, official_r, official_m) ||
      wire_t2(wire_bytes, wire_out, pk, wire_r, wire_m) ||
      memcmp(official_bytes, wire_bytes, NTRUPLUS_POLYBYTES)) abort();
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
  printf("wire_monotone_tail_attr_v2_runtime_addresses %p %p %p %p %p %p\n",
         (void *)official_t0, (void *)wire_t0, (void *)official_t1,
         (void *)wire_t1, (void *)official_t2, (void *)wire_t2);
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_BALANCED("t0", (reset_inputs(), prepare_states()),
      reject_sink |= (unsigned int)official_t0(official_h+i, BYTE_SLOT(pk,i)),
      reject_sink |= (unsigned int)wire_t0(WORD_SLOT(wire_h,i), BYTE_SLOT(pk,i)));
    MEASURE_BALANCED("t1", (reset_inputs(), prepare_states()),
      reject_sink |= (unsigned int)official_t1(official_out+i, BYTE_SLOT(pk,i),
                                               official_r+i, official_m+i),
      reject_sink |= (unsigned int)wire_t1(WORD_SLOT(wire_out,i), BYTE_SLOT(pk,i),
                                           WORD_SLOT(wire_r,i), WORD_SLOT(wire_m,i)));
    MEASURE_BALANCED("t2", (reset_inputs(), prepare_states()),
      reject_sink |= (unsigned int)official_t2(BYTE_SLOT(official_bytes,i),
          official_out+i, BYTE_SLOT(pk,i), official_r+i, official_m+i),
      reject_sink |= (unsigned int)wire_t2(BYTE_SLOT(wire_bytes,i),
          WORD_SLOT(wire_out,i), BYTE_SLOT(pk,i), WORD_SLOT(wire_r,i),
          WORD_SLOT(wire_m,i)));
  }
}
