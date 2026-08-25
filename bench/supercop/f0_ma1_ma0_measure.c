#include <stdint.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "f0-ma1-asm1.h"
#include "f0_ma0_control.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "ciphertext_bytes", "f0_words", 0 };
const long long sizes[] = { 1728, 1152 };

static uint8_t *output;
static int16_t *r_f0;
static int16_t *m_f0;
static int16_t *h_official;
static int16_t *ma1_scratch;
static int16_t *ma0_scratch;

void preallocate(void) {}

void allocate(void) {
  int i;
  output = (uint8_t *)alignedcalloc(1728);
  r_f0 = (int16_t *)alignedcalloc(1152 * sizeof *r_f0);
  m_f0 = (int16_t *)alignedcalloc(1152 * sizeof *m_f0);
  h_official = (int16_t *)alignedcalloc(1152 * sizeof *h_official);
  ma1_scratch = (int16_t *)alignedcalloc(256 * sizeof *ma1_scratch);
  ma0_scratch = (int16_t *)alignedcalloc(3456 * sizeof *ma0_scratch);
  for (i = 0; i < 1152; ++i) {
    r_f0[i] = (int16_t)(((i * 619 + 17) % 41505) - 20751);
    m_f0[i] = (int16_t)(((i * 271 + 29) % 41505) - 20751);
    h_official[i] = (int16_t)((i * 43 + 5) % 3457);
  }
}

#define TIMINGS 32
static long long cycles[TIMINGS + 1];
#define MEASURE_ENTRY(label, statement) do {                         \
  for (i = 0; i <= TIMINGS; ++i) {                                  \
    cycles[i] = cpucycles();                                        \
    statement;                                                      \
  }                                                                 \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, label, cycles, TIMINGS);                            \
} while (0)

#define C0() ntruplus1152_exp001_f0_ma1_asm1_c0(                     \
    output, r_f0, m_f0, h_official, ma1_scratch)
#define C1() ntruplus1152_exp001_f0_ma1_asm1_c1(                     \
    output, r_f0, m_f0, h_official, ma1_scratch)
#define MA0() ntruplus1152_exp001_f0_ma0_control(                    \
    output, r_f0, m_f0, h_official, ma0_scratch)

void measure(void) {
  int i, loop;
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_ENTRY("f0_ma1_c0_first_cycles", C0());
    MEASURE_ENTRY("f0_ma1_c1_second_cycles", C1());
    MEASURE_ENTRY("f0_ma0_third_cycles", MA0());
    MEASURE_ENTRY("f0_ma0_first_cycles", MA0());
    MEASURE_ENTRY("f0_ma1_c0_second_cycles", C0());
    MEASURE_ENTRY("f0_ma1_c1_third_cycles", C1());
    MEASURE_ENTRY("f0_ma1_c1_first_cycles", C1());
    MEASURE_ENTRY("f0_ma0_second_cycles", MA0());
    MEASURE_ENTRY("f0_ma1_c0_third_cycles", C0());
  }
}
