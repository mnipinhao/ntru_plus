#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "d3_vpmaddwd_tile.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "words", 0 };
const long long sizes[] = { 48 };
#define TIMINGS 32
#define BANKS (TIMINGS + 1)
static int16_t *a, *b, *zeta, *out, *scratch;
static long long cycles[TIMINGS + 1];
static volatile int16_t sink;
enum pmu_mode { PMU_BASELINE, PMU_D3_BASELINE, PMU_D3_MR32 };
static enum pmu_mode parse_pmu_mode(const char *name) {
  if (!strcmp(name, "baseline")) return PMU_BASELINE;
  if (!strcmp(name, "d3_baseline")) return PMU_D3_BASELINE;
  if (!strcmp(name, "d3_mr32")) return PMU_D3_MR32;
  abort();
}
void preallocate(void) {}
void allocate(void) {
  int i, j;
  a = (int16_t *)alignedcalloc(BANKS * 48 * sizeof *a);
  b = (int16_t *)alignedcalloc(BANKS * 48 * sizeof *b);
  zeta = (int16_t *)alignedcalloc(BANKS * 32 * sizeof *zeta);
  out = (int16_t *)alignedcalloc(BANKS * 48 * sizeof *out);
  scratch = (int16_t *)alignedcalloc(BANKS * 96 * sizeof *scratch);
  for (i = 0; i < BANKS; ++i) {
    for (j = 0; j < 48; ++j) {
      a[i*48+j] = (int16_t)((j * 2053U + i * 17U + 17U) % 3457U);
      b[i*48+j] = (int16_t)(j * 4051U + i * 29U + 0x8123U);
    }
    for (j = 0; j < 16; ++j) {
      int16_t value = (int16_t)(((j * 733U + i * 13U + 19U) % 3457U) - 1728);
      zeta[i*32+j] = (int16_t)((uint16_t)value * (uint16_t)12929);
      zeta[i*32+16+j] = value;
    }
  }
}
#define RUN(label, statement) do {                                      \
  for (i = 0; i <= TIMINGS; ++i) { cycles[i] = cpucycles(); statement; } \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i+1] - cycles[i];   \
  printentry(-1, label "_cycles", cycles, TIMINGS);                    \
} while (0)
void measure(void) {
  int i, loop;
  const char *pmu = getenv("NTRUPLUS_COMPONENT_PMU");
  const char *paired = getenv("NTRUPLUS_D3_PAIRED_MODE");
  if (pmu) {
    enum pmu_mode mode = parse_pmu_mode(pmu);
    for (i = 0; i < 4096; ++i) {
      int k = i % BANKS;
      switch (mode) {
      case PMU_BASELINE: __asm__ volatile("" ::: "memory"); break;
      case PMU_D3_BASELINE: ntruplus864_exp001_d3_tile_baseline(out+k*48,a+k*48,b+k*48,zeta+k*32,scratch+k*96); break;
      case PMU_D3_MR32: ntruplus864_exp001_d3_tile_vpmaddwd(out+k*48,a+k*48,b+k*48,zeta+k*32,scratch+k*96); break;
      }
    }
    return;
  }
  if (paired) {
    for (loop = 0; loop < LOOPS; ++loop) {
      if (!strcmp(paired, "baseline")) {
        RUN("d3_paired", ntruplus864_exp001_d3_tile_baseline(
            out+i*48, a+i*48, b+i*48, zeta+i*32, scratch+i*96));
      } else if (!strcmp(paired, "mr32")) {
        RUN("d3_paired", ntruplus864_exp001_d3_tile_vpmaddwd(
            out+i*48, a+i*48, b+i*48, zeta+i*32, scratch+i*96));
      } else {
        abort();
      }
    }
    return;
  }
  for (loop = 0; loop < LOOPS; ++loop) {
    RUN("d3_packed_t3_baseline", ntruplus864_exp001_d3_tile_baseline(
        out+i*48, a+i*48, b+i*48, zeta+i*32, scratch+i*96));
    RUN("d3_packed_t3_mr32", ntruplus864_exp001_d3_tile_vpmaddwd(
        out+i*48, a+i*48, b+i*48, zeta+i*32, scratch+i*96));
    sink ^= out[(i*48 + i) % (BANKS*48)];
  }
}
