#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "internal.h"
#include "poly.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "words", 0 };
const long long sizes[] = { NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define SLOT(base, i) ((base) + (i) * NTRUPLUS_N)
static int16_t *coeff, *front, *m0, *m1, *p0, *p_inv, *inv_core, *out, *work;
static uint8_t *bytes;
static long long cycles[TIMINGS + 1];
static volatile unsigned int sink;
enum pmu_mode {
  PMU_BASELINE, PMU_FORWARD_M, PMU_FORWARD_P, PMU_BASEINV,
  PMU_BM_GENERAL, PMU_BM_SCALE, PMU_INVERSE, PMU_UNPACK, PMU_PACK
};
static enum pmu_mode parse_pmu_mode(const char *name) {
  if (!strcmp(name,"baseline")) return PMU_BASELINE;
  if (!strcmp(name,"forward_m_full")) return PMU_FORWARD_M;
  if (!strcmp(name,"forward_p_full")) return PMU_FORWARD_P;
  if (!strcmp(name,"baseinv_j1")) return PMU_BASEINV;
  if (!strcmp(name,"basemul_general_m")) return PMU_BM_GENERAL;
  if (!strcmp(name,"basemul_scale_m")) return PMU_BM_SCALE;
  if (!strcmp(name,"inverse_m_full")) return PMU_INVERSE;
  if (!strcmp(name,"q24_unpack_m")) return PMU_UNPACK;
  if (!strcmp(name,"q24_pack_m")) return PMU_PACK;
  abort();
}

void preallocate(void) {}
void allocate(void) {
  coeff = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *coeff);
  front = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *front);
  m0 = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *m0);
  m1 = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *m1);
  p0 = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *p0);
  p_inv = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *p_inv);
  inv_core = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *inv_core);
  out = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *out);
  work = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *work);
  bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
}
static uint8_t *bs(int i) { return bytes + i * NTRUPLUS_POLYBYTES; }
static void prepare(void) {
  int i, j;
  for (i = 0; i < BANKS; ++i) {
    for (j = 0; j < NTRUPLUS_N; ++j)
      SLOT(coeff,i)[j] = (int16_t)(((j * 1009U + i * 17U + 11U) % 3U) - 1);
    ntruplus768_ntt_frontend_avx2(SLOT(front,i), SLOT(coeff,i));
    ntruplus768_ntt_m_avx2(SLOT(m0,i), SLOT(front,i));
    ntruplus768_ntt_m_avx2(SLOT(m1,i), SLOT(front,i));
    ntruplus768_ntt_p_avx2(SLOT(p0,i), SLOT(front,i));
    if (ntruplus768_baseinv_j1_avx2(SLOT(p_inv,i), SLOT(p0,i)) != 0)
      abort();
    ntruplus768_invntt_m_avx2(SLOT(inv_core,i), SLOT(m0,i));
    ntruplus768_pack_m_centered_avx2(bs(i), SLOT(m0,i));
  }
}
#define RUN(label, statement) do {                                      \
  prepare();                                                            \
  for (i = 0; i <= TIMINGS; ++i) { cycles[i] = cpucycles(); statement; } \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i+1] - cycles[i];    \
  printentry(-1, label "_cycles", cycles, TIMINGS);                     \
} while (0)
void measure(void) {
  int i, loop;
  prepare();
  const char *pmu = getenv("NTRUPLUS_COMPONENT_PMU");
  if (pmu) {
    enum pmu_mode mode = parse_pmu_mode(pmu);
    for (i = 0; i < 4096; ++i) {
      int k = i % BANKS;
      switch (mode) {
      case PMU_BASELINE: __asm__ volatile("" ::: "memory"); break;
      case PMU_FORWARD_M: ntruplus768_ntt_frontend_avx2(SLOT(work,k),SLOT(coeff,k)); ntruplus768_ntt_m_avx2(SLOT(out,k),SLOT(work,k)); break;
      case PMU_FORWARD_P: ntruplus768_ntt_frontend_avx2(SLOT(work,k),SLOT(coeff,k)); ntruplus768_ntt_p_avx2(SLOT(out,k),SLOT(work,k)); break;
      case PMU_BASEINV: sink^=(unsigned)ntruplus768_baseinv_j1_avx2(SLOT(out,k),SLOT(p0,k)); break;
      case PMU_BM_GENERAL: ntruplus768_basemul_general_m_avx2(SLOT(out,k),SLOT(m0,k),SLOT(m1,k)); break;
      case PMU_BM_SCALE: ntruplus768_basemul_scale_m_avx2(SLOT(out,k),SLOT(m0,k),SLOT(m1,k)); break;
      case PMU_INVERSE: ntruplus768_invntt_m_avx2(SLOT(work,k),SLOT(m0,k)); ntruplus768_invntt_tail_avx2(SLOT(out,k),SLOT(work,k)); break;
      case PMU_UNPACK: sink^=(unsigned)ntruplus768_unpack_m_avx2(SLOT(out,k),bs(k)); break;
      case PMU_PACK: ntruplus768_pack_m_centered_avx2(bs(k),SLOT(m0,k)); break;
      }
    }
    return;
  }
  for (loop = 0; loop < LOOPS; ++loop) {
    RUN("forward_frontend", ntruplus768_ntt_frontend_avx2(SLOT(front,i), SLOT(coeff,i)));
    RUN("forward_m_terminal", ntruplus768_ntt_m_avx2(SLOT(out,i), SLOT(front,i)));
    RUN("forward_p_terminal", ntruplus768_ntt_p_avx2(SLOT(out,i), SLOT(front,i)));
    RUN("forward_m_full", (ntruplus768_ntt_frontend_avx2(SLOT(work,i), SLOT(coeff,i)),
                            ntruplus768_ntt_m_avx2(SLOT(out,i), SLOT(work,i))));
    RUN("forward_p_full", (ntruplus768_ntt_frontend_avx2(SLOT(work,i), SLOT(coeff,i)),
                            ntruplus768_ntt_p_avx2(SLOT(out,i), SLOT(work,i))));
    RUN("baseinv_j1", sink ^= (unsigned)ntruplus768_baseinv_j1_avx2(SLOT(out,i), SLOT(p0,i)));
    RUN("basemul_f0_j1", ntruplus768_basemul_f0_j1_avx2(SLOT(out,i), SLOT(p0,i), SLOT(p_inv,i)));
    RUN("basemul_general_m", ntruplus768_basemul_general_m_avx2(SLOT(out,i), SLOT(m0,i), SLOT(m1,i)));
    RUN("basemul_scale_m", ntruplus768_basemul_scale_m_avx2(SLOT(out,i), SLOT(m0,i), SLOT(m1,i)));
    RUN("inverse_m_core", ntruplus768_invntt_m_avx2(SLOT(out,i), SLOT(m0,i)));
    RUN("inverse_m_tail", ntruplus768_invntt_tail_avx2(SLOT(out,i), SLOT(inv_core,i)));
    RUN("inverse_m_full", (ntruplus768_invntt_m_avx2(SLOT(work,i), SLOT(m0,i)),
                            ntruplus768_invntt_tail_avx2(SLOT(out,i), SLOT(work,i))));
    RUN("q24_unpack_m", sink ^= (unsigned)ntruplus768_unpack_m_avx2(SLOT(out,i), bs(i)));
    RUN("q24_pack_m_centered", ntruplus768_pack_m_centered_avx2(bs(i), SLOT(m0,i)));
    RUN("q24_pack_m_lazy", ntruplus768_pack_m_lazy10788_avx2(bs(i), SLOT(m0,i)));
    RUN("q24_pack_m_highrange", ntruplus768_pack_m_highrange12699_avx2(bs(i), SLOT(m0,i)));
    RUN("q24_pack_p", ntruplus768_pack_p_sp1_lazy10788_avx2(bs(i), SLOT(p0,i)));
    RUN("q24_equal_m", sink ^= (unsigned)ntruplus768_equal_m_modq12699_avx2(SLOT(m0,i), SLOT(m1,i)));
  }
}
