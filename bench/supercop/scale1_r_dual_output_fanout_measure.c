#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "r_words", "hash_bytes", 0 };
const long long sizes[] = { NTRUPLUS_N, NTRUPLUS_POLYBYTES };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "scale1_r_dual_output_fanout_"

void ntruplus1152_exp001_scale1_r_fanout_control(
    uint8_t *, poly *, int16_t *, const poly *, const uint8_t *);
void ntruplus1152_exp001_scale1_r_fanout_candidate(
    uint8_t *, poly *, int16_t *, const poly *, const uint8_t *);

static poly *input, *m_control, *m_candidate;
static int16_t *r_control, *r_candidate;
static uint8_t *bytes_control, *bytes_candidate, *messages;
static long long cycles[TIMINGS + 1];

void preallocate(void) {}
void allocate(void) {
  input = (poly *)alignedcalloc(BANKS * sizeof *input);
  m_control = (poly *)alignedcalloc(BANKS * sizeof *m_control);
  m_candidate = (poly *)alignedcalloc(BANKS * sizeof *m_candidate);
  r_control = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *r_control);
  r_candidate = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *r_candidate);
  bytes_control = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  bytes_candidate = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  messages = (uint8_t *)alignedcalloc(BANKS * (NTRUPLUS_N / 8));
}

static void reset(unsigned salt) {
  for (int bank = 0; bank < BANKS; ++bank) {
    for (int j = 0; j < NTRUPLUS_N; ++j)
      input[bank].coeffs[j] = (int16_t)((j * 619U + bank * 17U + salt) % 3U) - 1;
    for (int j = 0; j < NTRUPLUS_N / 8; ++j)
      messages[bank * (NTRUPLUS_N / 8) + j] = (uint8_t)(j * 29U + bank + salt);
  }
}

#define R_SLOT(base, bank) ((base) + (bank) * NTRUPLUS_N)
#define B_SLOT(base, bank) ((base) + (bank) * NTRUPLUS_POLYBYTES)
#define MSG_SLOT(bank) (messages + (bank) * (NTRUPLUS_N / 8))
#define RUN(label, statement) do {                                     \
  for (i = 0; i <= TIMINGS; ++i) { cycles[i] = cpucycles(); statement; } \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, PREFIX label "_cycles", cycles, TIMINGS);             \
} while (0)

void measure(void) {
  int i, loop;
  reset(7);
  ntruplus1152_exp001_scale1_r_fanout_control(
      bytes_control, m_control, r_control, input, messages);
  ntruplus1152_exp001_scale1_r_fanout_candidate(
      bytes_candidate, m_candidate, r_candidate, input, messages);
  if (memcmp(r_control, r_candidate, NTRUPLUS_N * sizeof *r_control)) {
    fprintf(stderr, "scale1 dual-output preflight: retained r mismatch\n");
    abort();
  }
  if (memcmp(bytes_control, bytes_candidate, NTRUPLUS_N / 4)) {
    fprintf(stderr, "scale1 dual-output preflight: hash_g output mismatch\n");
    abort();
  }
  if (memcmp(m_control, m_candidate, sizeof *m_control)) {
    int j;
    for (j = 0; j < NTRUPLUS_N; ++j)
      if (m_control->coeffs[j] != m_candidate->coeffs[j]) break;
    fprintf(stderr, "scale1 dual-output preflight: SOTP m mismatch at %d: %d != %d\n",
            j, j < NTRUPLUS_N ? m_control->coeffs[j] : 0,
            j < NTRUPLUS_N ? m_candidate->coeffs[j] : 0);
    abort();
  }

  printf("scale1_r_dual_output_fanout_runtime_addresses %p %p %p\n",
         (void *)ntruplus1152_exp001_scale1_r_fanout_control,
         (void *)ntruplus1152_exp001_scale1_r_fanout_candidate,
         (void *)input);
  for (loop = 0; loop < LOOPS; ++loop) {
    reset(11U);
    RUN("control_first", ntruplus1152_exp001_scale1_r_fanout_control(
        B_SLOT(bytes_control, i), m_control + i, R_SLOT(r_control, i), input + i, MSG_SLOT(i)));
    reset(11U);
    RUN("candidate_second", ntruplus1152_exp001_scale1_r_fanout_candidate(
        B_SLOT(bytes_candidate, i), m_candidate + i, R_SLOT(r_candidate, i), input + i, MSG_SLOT(i)));
    reset(11U);
    RUN("candidate_first", ntruplus1152_exp001_scale1_r_fanout_candidate(
        B_SLOT(bytes_candidate, i), m_candidate + i, R_SLOT(r_candidate, i), input + i, MSG_SLOT(i)));
    reset(11U);
    RUN("control_second", ntruplus1152_exp001_scale1_r_fanout_control(
        B_SLOT(bytes_control, i), m_control + i, R_SLOT(r_control, i), input + i, MSG_SLOT(i)));
  }
}
