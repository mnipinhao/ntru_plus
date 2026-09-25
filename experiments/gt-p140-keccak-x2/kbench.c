/* P140: cost of mlkem-native's AArch64 Keccak-f[1600] backends per call and per state, beside GT's
 * own x1 permutations.  SHA3 variants only where the compiler targets FEAT_SHA3 (M2).
 * Throughput of back-to-back calls on one buffer (the permutation's time does not depend on data). */
#include <stdio.h>
#include <stdint.h>
#ifdef __APPLE__
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
#define UNIT "ns"
#define START() uint64_t t0=now()
#define STOP() (double)(now()-t0)
#else
#include "perf_counter.h"
#define UNIT "cyc"
#define START() perf_counter_start()
#define STOP() (double)perf_counter_stop()
#endif
#define NS(x) PQCP_MLKEM_NATIVE_MLKEM768_##x
void NS(keccak_f1600_x1_scalar_aarch64_asm)(uint64_t *, const uint64_t *);
void NS(keccak_f1600_x4_v8a_scalar_hybrid_aarch64_asm)(uint64_t *, const uint64_t *);
void ntruplus_keccak_f1600_x1_aarch64(uint64_t *, const uint64_t *);
#ifdef __ARM_FEATURE_SHA3
void NS(keccak_f1600_x1_v84a_aarch64_asm)(uint64_t *, const uint64_t *);
void NS(keccak_f1600_x2_v84a_aarch64_asm)(uint64_t *, const uint64_t *);
void NS(keccak_f1600_x4_v8a_v84a_scalar_hybrid_aarch64_asm)(uint64_t *, const uint64_t *);
void ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t *, const uint64_t *);
#endif
static const uint64_t RC[24] = {
 0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808aULL, 0x8000000080008000ULL,
 0x000000000000808bULL, 0x0000000080000001ULL, 0x8000000080008081ULL, 0x8000000000008009ULL,
 0x000000000000008aULL, 0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000aULL,
 0x000000008000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL, 0x8000000000008003ULL,
 0x8000000000008002ULL, 0x8000000000000080ULL, 0x000000000000800aULL, 0x800000008000000aULL,
 0x8000000080008081ULL, 0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL};
static uint64_t st[100] __attribute__((aligned(64)));
static void b_x1s(void){ NS(keccak_f1600_x1_scalar_aarch64_asm)(st, RC); }
static void b_x4h(void){ NS(keccak_f1600_x4_v8a_scalar_hybrid_aarch64_asm)(st, RC); }
static void b_gts(void){ ntruplus_keccak_f1600_x1_aarch64(st, RC); }
#ifdef __ARM_FEATURE_SHA3
static void b_x1v(void){ NS(keccak_f1600_x1_v84a_aarch64_asm)(st, RC); }
static void b_x2v(void){ NS(keccak_f1600_x2_v84a_aarch64_asm)(st, RC); }
static void b_x4v(void){ NS(keccak_f1600_x4_v8a_v84a_scalar_hybrid_aarch64_asm)(st, RC); }
static void b_gtv(void){ ntruplus_keccak_f1600_x1_v84a_aarch64(st, RC); }
#endif
static double best(void (*f)(void)){ double b = 1e30; for (int w = 0; w < 2000; w++) f();
  for (int k = 0; k < 300; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < b) b = d; } return b; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) b_x1s(); }
#else
  if (perf_counter_open()) return 2;
#endif
  for (int i = 0; i < 100; i++) st[i] = 0x0123456789abcdefULL * (uint64_t)(i + 1);
  struct { const char *n; int k; void (*f)(void); } r[] = {
    {"GT x1 scalar (keccakf1600.S)", 1, b_gts}, {"mlkem-native x1 scalar", 1, b_x1s}, {"mlkem-native x4 v8a+scalar hybrid", 4, b_x4h},
#ifdef __ARM_FEATURE_SHA3
    {"GT x1 v84a (keccakf1600_v84a.S)", 1, b_gtv}, {"mlkem-native x1 v84a", 1, b_x1v}, {"mlkem-native x2 v84a", 2, b_x2v},
    {"mlkem-native x4 v8a+v84a+scalar hybrid", 4, b_x4v},
#endif
  };
  for (unsigned i = 0; i < sizeof r / sizeof r[0]; i++) { double t = best(r[i].f);
    printf("  %-40s %8.1f %s a call, %8.1f a state\n", r[i].n, t, UNIT, t / r[i].k); }
  return 0; }
