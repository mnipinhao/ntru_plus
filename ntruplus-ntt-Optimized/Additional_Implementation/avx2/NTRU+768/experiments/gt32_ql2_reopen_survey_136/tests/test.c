#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 768
#define Q 3457
#define R 3310

void gt135_basemul_general_ql2_native_e0(int16_t *, const int16_t *, const int16_t *);
void gt136_basemul_general_ql2_native_em1(int16_t *, const int16_t *, const int16_t *);

static _Alignas(64) int16_t a[N], b[N], e0[N], em1[N];
static uint64_t state = 136;
static uint32_t rnd(void) { state ^= state << 13; state ^= state >> 7; state ^= state << 17; return (uint32_t)state; }
static int modq(int64_t x) { x %= Q; if (x < 0) x += Q; return (int)x; }

int main(void) {
  for (int trial = 0; trial < 1000; trial++) {
    for (int i = 0; i < N; i++) {
      a[i] = (int16_t)((int)(rnd() % Q) - Q / 2);
      b[i] = (int16_t)((int)(rnd() % Q) - Q / 2);
    }
    gt135_basemul_general_ql2_native_e0(e0, a, b);
    gt136_basemul_general_ql2_native_em1(em1, a, b);
    for (int i = 0; i < N; i++) {
      if (modq((int64_t)em1[i] * R) != modq(e0[i])) {
        fprintf(stderr, "scale mismatch trial=%d index=%d e0=%d em1=%d\n", trial, i, e0[i], em1[i]);
        return 1;
      }
    }
  }
  puts("PASS: 1000 e=-1 -> e=0 scale-equivalence trials");
  return 0;
}
