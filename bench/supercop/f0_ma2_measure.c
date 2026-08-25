#include <stdint.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "f0-ma2-asm.h"
#include "f0_ma0_control.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "ciphertext_bytes", "f0_words", 0 };
const long long sizes[] = { 1728, 1152 };

static uint8_t *output;
static int16_t *r_f0, *m_f0, *h_official, *ma0_scratch, *ma2_scratch;

void preallocate(void) {}
void allocate(void) {
  int i;
  output = (uint8_t *)alignedcalloc(1728);
  r_f0 = (int16_t *)alignedcalloc(1152 * sizeof *r_f0);
  m_f0 = (int16_t *)alignedcalloc(1152 * sizeof *m_f0);
  h_official = (int16_t *)alignedcalloc(1152 * sizeof *h_official);
  ma0_scratch = (int16_t *)alignedcalloc(3456 * sizeof *ma0_scratch);
  ma2_scratch = (int16_t *)alignedcalloc(128 * sizeof *ma2_scratch);
  for (i = 0; i < 1152; ++i) {
    r_f0[i] = (int16_t)(((i * 619 + 17) % 41505) - 20751);
    m_f0[i] = (int16_t)(((i * 271 + 29) % 41505) - 20751);
    h_official[i] = (int16_t)((i * 43 + 5) % 3457);
  }
}

#define TIMINGS 32
static long long cycles[TIMINGS + 1];
#define MEASURE_ENTRY(label, statement) do {                            \
  for (i = 0; i <= TIMINGS; ++i) { cycles[i] = cpucycles(); statement; } \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, label, cycles, TIMINGS);                               \
} while (0)
#define MA0() ntruplus1152_exp001_f0_ma0_control(                       \
    output, r_f0, m_f0, h_official, ma0_scratch)
#define MA2() ntruplus1152_exp001_f0_ma2_full(                          \
    output, r_f0, m_f0, h_official, ma2_scratch)

void measure(void) {
  int i, loop;
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_ENTRY("f0_ma0_first_cycles", MA0());
    MEASURE_ENTRY("f0_ma2_second_cycles", MA2());
    MEASURE_ENTRY("f0_ma2_first_cycles", MA2());
    MEASURE_ENTRY("f0_ma0_second_cycles", MA0());
  }
}
