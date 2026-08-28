#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "encap-h4-m3b-exact-egress.h"
#include "encap-h-ingress-ma2-h3.h"
#include "gt9x16-prod3-ma2-qorder-natural-asm.h"
#include "gt9x16_forward.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "encap_lazy_h4_factorial_price_"

void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(
    int16_t state[1152]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_lazy_reduce(
    int16_t state[1152]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(
    int16_t state[1152]);

static uint8_t *pk;
static uint8_t *ct[4];
static poly *encoded_h, *r_coeff, *m_coeff;
static int16_t *r_work[4], *m_work[4], *scratch[4];
static long long cycles[TIMINGS + 1];
static volatile unsigned int public_reject_sink;

void preallocate(void) {}

void allocate(void) {
  int variant;
  pk = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  encoded_h = (poly *)alignedcalloc(BANKS * sizeof *encoded_h);
  r_coeff = (poly *)alignedcalloc(BANKS * sizeof *r_coeff);
  m_coeff = (poly *)alignedcalloc(BANKS * sizeof *m_coeff);
  for (variant = 0; variant < 4; ++variant) {
    ct[variant] = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
    r_work[variant] =
        (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof **r_work);
    m_work[variant] =
        (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof **m_work);
    scratch[variant] =
        (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof **scratch);
  }
}

#define WORD_SLOT(base, i) ((base) + (i) * NTRUPLUS_N)
#define BYTE_SLOT(base, i) ((base) + (i) * NTRUPLUS_POLYBYTES)

static void reset_inputs(void) {
  int bank, j;
  for (bank = 0; bank < BANKS; ++bank) {
    for (j = 0; j < NTRUPLUS_N; ++j) {
      encoded_h[bank].coeffs[j] =
          (int16_t)(((unsigned int)j * 619U +
                     (unsigned int)bank * 37U + 11U) % 3457U);
      r_coeff[bank].coeffs[j] =
          (int16_t)((int)(((unsigned int)j * 43U +
                           (unsigned int)bank * 19U) % 3U) - 1);
      m_coeff[bank].coeffs[j] =
          (int16_t)((int)(((unsigned int)j * 71U +
                           (unsigned int)bank * 23U) % 3U) - 1);
    }
    poly_tobytes(BYTE_SLOT(pk, bank), encoded_h + bank);
  }
}

typedef void (*forward_fn)(int16_t state[1152]);

static int run_scale4(uint8_t output[1728], const uint8_t input[1728],
                      const poly *r, const poly *m, int16_t r_state[1152],
                      int16_t m_state[1152], int16_t out_state[1152],
                      forward_fn forward) {
  int reject;
  ntruplus1152_exp001_top_split_small(r_state, r->coeffs);
  forward(r_state);
  ntruplus1152_exp001_top_split_small(m_state, m->coeffs);
  forward(m_state);
  reject = ntruplus1152_exp001_encap_h_ingress_ma2_h3(
      out_state, input, r_state, m_state);
  ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(output, out_state);
  return reject;
}

static int run_scale1(uint8_t output[1728], const uint8_t input[1728],
                      const poly *r, const poly *m, int16_t r_state[1152],
                      int16_t m_state[1152], int16_t out_state[1152],
                      forward_fn forward) {
  ntruplus1152_exp001_top_split_small(r_state, r->coeffs);
  forward(r_state);
  ntruplus1152_exp001_top_split_small(m_state, m->coeffs);
  forward(m_state);
  return ntruplus1152_exp001_encap_h4_m3b_exact_egress(
      output, input, r_state, m_state, out_state);
}

#define DEFINE_VARIANT(name, body)                                      \
  static int __attribute__((noinline, aligned(32))) name(                \
      uint8_t output[1728], const uint8_t input[1728], const poly *r,    \
      const poly *m, int16_t r_state[1152], int16_t m_state[1152],      \
      int16_t out_state[1152]) { return (body); }

DEFINE_VARIANT(c00,
  run_scale4(output, input, r, m, r_state, m_state, out_state,
             ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta))
DEFINE_VARIANT(c10,
  run_scale4(output, input, r, m, r_state, m_state, out_state,
             ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_lazy_reduce))
DEFINE_VARIANT(c01,
  run_scale1(output, input, r, m, r_state, m_state, out_state,
             ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1))
DEFINE_VARIANT(c11,
  run_scale1(output, input, r, m, r_state, m_state, out_state,
             ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce))

typedef int (*variant_fn)(uint8_t *, const uint8_t *, const poly *,
                          const poly *, int16_t *, int16_t *, int16_t *);
static variant_fn variants[4] = {c00, c10, c01, c11};
static const char *variant_names[4] = {"c00", "c10", "c01", "c11"};

static int invoke(int variant, int bank) {
  return variants[variant](
      BYTE_SLOT(ct[variant], bank), BYTE_SLOT(pk, bank), r_coeff + bank,
      m_coeff + bank, WORD_SLOT(r_work[variant], bank),
      WORD_SLOT(m_work[variant], bank), WORD_SLOT(scratch[variant], bank));
}

static void preflight(void) {
  int variant;
  poly h_official, r_official, m_official, c_official;
  uint8_t expected[NTRUPLUS_POLYBYTES];
  reset_inputs();
  if (poly_frombytes(&h_official, pk)) {
    fprintf(stderr, "2x2 price Official preflight rejected valid PK\n");
    abort();
  }
  r_official = r_coeff[0];
  m_official = m_coeff[0];
  poly_ntt(&r_official);
  poly_ntt(&m_official);
  poly_basemul(&c_official, &h_official, &r_official);
  poly_add(&c_official, &c_official, &m_official);
  poly_tobytes(expected, &c_official);
  for (variant = 0; variant < 4; ++variant) {
    if (invoke(variant, 0)) {
      fprintf(stderr, "2x2 price preflight rejected valid PK in C%d\n", variant);
      abort();
    }
    if (memcmp(expected, ct[variant], NTRUPLUS_POLYBYTES)) {
      int byte;
      for (byte = 0; byte < NTRUPLUS_POLYBYTES; ++byte)
        if (expected[byte] != ct[variant][byte]) break;
      fprintf(stderr, "2x2 price Official ciphertext mismatch in %s at %d"
                      " expected=%u actual=%u\n",
              variant_names[variant], byte, expected[byte], ct[variant][byte]);
      abort();
    }
  }
}

#define MEASURE_ENTRY(variant, position) do {                           \
  for (i = 0; i <= TIMINGS; ++i) {                                     \
    cycles[i] = cpucycles();                                           \
    public_reject_sink |= (unsigned int)invoke((variant), i);           \
  }                                                                    \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  {                                                                    \
    char label[96];                                                     \
    snprintf(label, sizeof label, PREFIX "%s_pos%d_cycles",           \
             variant_names[(variant)], (position));                    \
    printentry(-1, label, cycles, TIMINGS);                             \
  }                                                                    \
} while (0)

void measure(void) {
  static const int rotations[4][4] = {
    {0, 1, 2, 3}, {1, 2, 3, 0}, {2, 3, 0, 1}, {3, 0, 1, 2}
  };
  int i, loop, rotation, position;
  preflight();
  printf("encap_lazy_h4_factorial_price_runtime_addresses %p %p %p %p\n",
         (void *)c00, (void *)c10, (void *)c01, (void *)c11);
  for (loop = 0; loop < LOOPS; ++loop) {
    for (rotation = 0; rotation < 4; ++rotation) {
      reset_inputs();
      for (position = 0; position < 4; ++position)
        MEASURE_ENTRY(rotations[rotation][position], position);
    }
  }
}
